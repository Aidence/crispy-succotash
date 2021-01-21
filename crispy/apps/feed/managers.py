import time
from datetime import datetime
from typing import Dict

from django.apps import apps
from django.db import models


##################
# Feed
##################
from django.utils.timezone import make_aware


class FeedQuerySet(models.query.QuerySet):
    def active(self):
        """
        Filters for active feeds
        """
        return self.filter(is_active=True)

    def from_user(self, user):
        return self.filter(added_by=user)

    def from_user_bookmarks(self, user):
        return self.filter(bookmarks__user=user)


class FeedManager(models.Manager):
    def active(self):
        """
        Returns a QS of active feeds
        :return:
        """
        return self.get_queryset().filter(broken=False)

    def get_queryset(self):
        return FeedQuerySet(self.model)

    def from_user(self, user):
        return self.get_queryset().from_user(user)

    def from_user_bookmarks(self, user):
        return self.get_queryset().from_user_bookmarks(user)


##################
# Entry
##################


class EntryQuerySet(models.query.QuerySet):
    """
    EntryQuerySet
    """
    def from_user(self, user):
        """
        Filter by user
        :param user:
        :return:
        """
        return self.filter(feed__user=user)

    def feeds(self):
        """
        Get feeds associated with entries
        :return:
        """
        app_config = apps.get_app_config('feed')
        return app_config.get_model('Feed').objects.filter(
            entries__in=self
        ).distinct()

    def from_feed(self, feed):
        """
        Returns list of entries associated with a feed
        :param feed:
        :return:
        """
        return self.filter(feed=feed)


class EntryManager(models.Manager):
    def from_raw_entry(self, raw_entry: Dict):
        """
        Creates an Entry entity from a raw entry

        :param raw_entry: A raw entry
        :return: An Entry entity
        """

        entry = self.model()

        # Get title
        entry.title = raw_entry.get('title', '')

        # Get content
        content = raw_entry.get('content', [{'value': ''}])[0]['value']

        if not content:
            content = raw_entry.get('description', raw_entry.get('summary', ''))

        entry.content = content

        # Get date
        date = raw_entry.get('updated_parsed',
                             raw_entry.get('published_parsed',
                                           raw_entry.get('created_parsed', None)))

        if date:
            entry.date = make_aware(datetime.fromtimestamp(time.mktime(date)))
        else:
            entry.date = datetime.now()

        # Get URL
        entry.url = raw_entry.get('link', '')

        # Get GUID, uses URL if not found
        entry.guid = raw_entry.get('guid', entry.url)

        # Get author
        entry.author = raw_entry.get('author', '')
        entry.comments_url = raw_entry.get('comments', '')
        return entry

    def get_queryset(self):
        """
        Returns an EntryQuerySet
        :return:
        """
        return EntryQuerySet(self.model)

    def get_from_feed(self, feed):
        return self.get_query_set().from_feed(feed)
