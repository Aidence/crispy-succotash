from datetime import datetime, timedelta
import feedparser
import time
from django.utils.timezone import make_aware

from crispy.apps.core.tests import BaseTestCase
from crispy.apps.feed.exceptions import BrokenFeed, TemporaryFeedError
from crispy.apps.feed.models import Feed
from crispy.apps.feed.scraper import Scraper


def create_dynamic_parse_func(response):
    def test_parse_func(url, a=None, b=None, c=None, d=None, e=None, f=None, g=None) -> feedparser.FeedParserDict:
        return response
    return test_parse_func


class ScraperTestCase(BaseTestCase):
    def setUp(self):
        self.feed = Feed(feed_url='')

    def test_parse_ensure_broken_feed_on_404(self):
        response = feedparser.FeedParserDict()
        response.status = 404
        f = create_dynamic_parse_func(response)
        scraper = Scraper(f, self.feed)
        with self.assertRaises(BrokenFeed):
            scraper.parse(False)

    def test_parse_ensure_temporary_error_on_unknown_status(self):
        response = feedparser.FeedParserDict()
        response.status = 500
        f = create_dynamic_parse_func(response)
        scraper = Scraper(f, self.feed)
        with self.assertRaises(TemporaryFeedError):
            scraper.parse(False)

    def test_parse_ensure_proper_return_on_success(self):
        response = feedparser.FeedParserDict()
        response.status = 200
        response['feed'] = feedparser.FeedParserDict()
        response['feed']['title'] = 'Bola'
        f = create_dynamic_parse_func(response)
        scraper = Scraper(f, self.feed)
        self.assertEqual(response, scraper.parse(False))

    def test_find_last_updated(self):
        expected_time_raw = datetime.now() + timedelta(days=1)
        expected_time = make_aware(datetime.fromtimestamp(time.mktime(expected_time_raw.timetuple())))
        entry_list = [
            {'updated_parsed': datetime.now().timetuple()},
            {'published_parsed': expected_time_raw.timetuple()},
            {'created_parsed': (datetime.now() - timedelta(days=1)).timetuple()}
        ]

        scraper = Scraper(create_dynamic_parse_func(None), self.feed)
        response = scraper._find_last_updated(entry_list)
        self.assertEqual(expected_time, response)

    def test_has_updated_future(self):
        self.feed.last_updated_at = make_aware(datetime.now())
        future = datetime.now() + timedelta(days=1)
        entry_list = [
            {'updated_parsed': future.timetuple()},
        ]

        feed_dict = feedparser.FeedParserDict()
        feed_dict['entries'] = entry_list

        f = create_dynamic_parse_func(feed_dict)
        scraper = Scraper(f, self.feed)
        self.assertTrue(scraper._has_updated(feed_dict, False))

    def test_has_updated_past(self):
        self.feed.last_updated_at = make_aware(datetime.now())
        future = datetime.now() - timedelta(days=1)
        entry_list = [
            {'updated_parsed': future.timetuple()},
        ]

        feed_dict = feedparser.FeedParserDict()
        feed_dict['entries'] = entry_list

        f = create_dynamic_parse_func(feed_dict)
        scraper = Scraper(f, self.feed)
        self.assertFalse(scraper._has_updated(feed_dict, False))



