from datetime import datetime, tzinfo
from typing import Callable, Any, Optional, Iterable, Dict, Tuple, List

import time

from django.utils.timezone import make_aware

from crispy.apps.feed.exceptions import BrokenFeed, TemporaryFeedError
from crispy.apps.feed.models import Feed

import feedparser


class Scraper(object):
    """
    This class scraps feeds.
    Receives a callable parse_func (as in feedparser.parse) and a feed object
    """

    def __init__(self,
                 parse_func: Callable[[str,  # url_file_stream_or_string
                                       Optional[str],  # e-tag
                                       Optional[datetime],  # last modified
                                       Optional[str],  # agent
                                       Optional[str],  # referrer
                                       Optional[Iterable[Any]],  # handlers
                                       Optional[Dict],  # request headers
                                       Optional[Dict]],  # response headers
                                      feedparser.FeedParserDict],
                 feed: Feed) -> None:
        self.parse_func = parse_func
        self.feed = feed

    def parse(self, force: bool) -> feedparser.FeedParserDict:
        """
        Parses the feed. Set force to true to force updates.
        :param force: Forces update
        :return: a parsed FeedParserDict
        """
        if not force:
            parsed_feed = self.parse_func(self.feed.feed_url,
                                          self.feed.etag,
                                          self.feed.last_updated_at)
        else:
            parsed_feed = self.parse_func(self.feed.feed_url)

        status = parsed_feed.status
        feed = parsed_feed.get('feed', None)

        # Checks if the feed is found (404) or if its gone (410)
        if status in (404, 410):
            raise BrokenFeed('Feed not found')

        # Checks for valid statuses
        if status in (200, 301, 302, 304):
            # If feed is None the feed has been parsed but has invalid content
            if not feed or 'title' not in parsed_feed.feed:
                raise TemporaryFeedError('Invalid feed content')

            return parsed_feed

        raise TemporaryFeedError('Unrecognized status: {}'.format(status))

    def _find_last_updated(self, entries: List[Dict]) -> datetime:
        """
        Returns the last updated entry date given a list of Entries
        :param entries: entries
        :return: datetime
        """
        latest = None
        for entry in entries:
            date = entry.get('updated_parsed',
                             entry.get('published_parsed',
                                       entry.get('created_parsed', None)))
            if date:
                date_obj = make_aware(datetime.fromtimestamp(time.mktime(date)))
            else:
                continue

            if not latest or (date_obj and date_obj > latest):
                latest = date_obj

        return latest

    def _has_updated(self, parsed_feed: feedparser.FeedParserDict, force: bool) -> bool:
        """
        Checks if the field has been updated since our last record
        :return: bool
        """
        # Get updated time
        updated = self._find_last_updated(parsed_feed.entries)

        # Checks if the field hasn't been updated since our last record
        if not force and updated and self.feed.last_updated_at and updated <= self.feed.last_updated_at:
            return False

        return True

    def check_feed(self, force: Optional[bool] = False) -> Tuple[bool, feedparser.FeedParserDict]:
        """
        Checks the feed for updates and returns a boolean indicating whether
        the feed has been updated or not and the list of entries.

        :param force: force update
        :return: A list containing a "changed" boolean and a parsed FeedParserDict
        """
        try:
            parsed_feed = self.parse(force)
            for e in parsed_feed.entries:
                if hasattr(e, 'date') and e.date:
                    e.date = make_aware(e.date)
        except BrokenFeed as e:  # Checks if the feed is permanently broken
            self.feed.broken = True
            self.feed.error = e
            raise
        except TemporaryFeedError as e:  # Checks if a temporary error occurred
            self.feed.error = e
            return False, None  # Returns not updated in case of not-modified responses
        finally:
            # Always update last checked time
            self.feed.last_checked_at = make_aware(datetime.now())

        return self._has_updated(parsed_feed, force), parsed_feed

