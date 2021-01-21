from datetime import datetime
from typing import List, Dict

import feedparser
from django.contrib.postgres.fields.jsonb import JSONField
from django.core.validators import URLValidator
from django.db import models

from crispy.apps.core.exceptions import CrispyException
from crispy.apps.feed import constants, managers


class Feed(models.Model):
    """
    A Feed entity
    """
    # Entity control fields
    added_by = models.ForeignKey(to='auth.User', help_text="User who added this feed",
                                 verbose_name="Added by", db_index=True, on_delete=models.CASCADE)
    broken = models.BooleanField(default=False, help_text="Denotes whether this feed is broken or not",
                                 verbose_name="Broken", db_index=True)
    error = models.TextField(blank=True, null=True, help_text="Error when a problem occurs",
                             verbose_name="Error")
    feed_url = models.TextField(validators=[URLValidator()], help_text="URL of the RSS feed",
                                verbose_name="Feed URL", unique=True)
    type = models.CharField(choices=constants.FEED_TYPES, db_index=True, max_length=30,
                            verbose_name="Type", help_text="Type of the feed")
    etag = models.CharField(blank=True, null=True, max_length=100, verbose_name="E-Tag", help_text="E-Tag header")

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date this feed has been added",
                                      verbose_name="Created at")
    last_checked_at = models.DateTimeField(auto_now_add=True, help_text="Last time the feed has been checked",
                                           verbose_name="Last checked at")
    last_updated_at = models.DateTimeField(blank=True, null=True,
                                           help_text="Last time the feed has been updated",
                                           verbose_name="Last updated at")

    # Required data fields
    title = models.TextField(help_text="Title of the feed", verbose_name="Title", db_index=True)

    # Optional data fields
    alternate_title = models.TextField(blank=True, null=True, help_text="Alternate title for the feed",
                                       verbose_name="Alternate title")
    site_url = models.TextField(blank=True, null=True, validators=[URLValidator()],
                                help_text="URL of the feed's website", verbose_name="Site URL")
    extra_data = JSONField(verbose_name="Extra data", db_index=True, null=True)

    # Manager
    objects = managers.FeedManager()

    # Methods and meta
    class Meta:
        ordering = ('title', 'last_updated_at', )

    def __str__(self):
        return self.alternate_title or self.title

    def _update_entries(self, entries: List[Dict]) -> datetime:
        """
        Adds or updates the feeds entries given an entry list
        :param entries:
        :return: Datetime of the latest entry
        """
        latest = None  # Keeps track of the latest entry

        for entry in entries:
            # Get entry entity
            entry = Entry.objects.from_raw_entry(entry)
            entry.feed = self

            # Try to match by guid, then url, then title and date
            if entry.guid:
                query = {'guid': entry.guid}
            elif entry.url:
                query = {'url': entry.url}
            elif entry.title:
                query = {
                    'title': entry.title,
                    'date': entry.date
                }
            else:
                # An Entry must contain at least one of the above
                raise CrispyException("Can't find an entry identifier, cannot import")

            # Update existing entries and delete old
            try:
                existing = self.entries.get(**query)
            except models.ObjectDoesNotExist:
                # Existing entry not found, create it
                entry.save()
            else:
                # Existing entry found
                # Updates entry if newer
                if entry.date and entry.date > existing.date:
                    existing.update(entry)

            # Update latest tracker
            if not latest or (entry.date and entry.date > latest):
                latest = entry.date
        return latest

    def _update_feed_data(self, feed_data_obj: feedparser.FeedParserDict) -> None:
        """
        Updates feed data given a "feedparser.FeedParserDict.feed" object
        :param feed_data_obj:
        :return:
        """
        self.title = feed_data_obj['title']
        site_url = feed_data_obj.get('link', None)
        if site_url:
            self.site_url = site_url

    def update_feed_data(self, parsed_feed: feedparser.FeedParserDict) -> None:
        # Set feed type
        if not self.type:
            self.type = parsed_feed.version

        # Update feed data
        self._update_feed_data(parsed_feed.feed)

    def update_feed_entries(self, entries: List[Dict]):
        # Update entries
        try:
            last_updated = self._update_entries(entries)
        except CrispyException as e:
            if self.error:
                self.error += ". \n"

            self.error += "Entry error: {}".format(e)
            return False
        else:
            # Update last updated
            self.last_updated_at = last_updated


class Entry(models.Model):
    # Entity control fields
    feed = models.ForeignKey(Feed, related_name='entries', help_text="Feed this entry belongs to", on_delete=models.CASCADE)

    # Date fields
    date = models.DateTimeField(help_text="Date this entry has been added")

    # Required data fields
    title = models.TextField(blank=True)
    content = models.TextField(blank=True)

    # Optional data fields
    author = models.TextField(blank=True, help_text="Author of this entry")
    comments_url = models.TextField(blank=True, validators=[URLValidator()],
                                    help_text="URL for HTML comment submission page")
    url = models.TextField(blank=True, validators=[URLValidator()], help_text="URL for the HTML for this entry")
    guid = models.TextField(blank=True, help_text="GUID for the entry, according to the feed")

    # Manager
    objects = managers.EntryManager()

    # Methods and meta
    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-date', )
        verbose_name_plural = 'Entries'

    def update(self, entry):
        """
        An old entry has been re-published; update with new data
        """
        fields = [
            'date', 'title', 'content', 'author', 'comments_url', 'url',
            'guid',
        ]

        for field in fields:
            setattr(self, field, getattr(entry, field))
            
        self.save()
