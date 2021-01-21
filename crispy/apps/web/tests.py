from datetime import datetime

from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse

from crispy.apps.core.tests import BaseTestCase
from crispy.apps.feed.models import Feed, Entry
from crispy.apps.web.forms.comment import CommentForm
from crispy.apps.web.models import Comment
from crispy.apps.web.views.entries import EntryDetailView
from crispy.apps.web.views.feeds import FeedDetailView, NewFeedView


class TestOtherViews(BaseTestCase):
    def test_home(self):
        self._test_view_for_status_code('home')

    def test_register(self):
        self._test_view_for_status_code('register')

    def test_login(self):
        self._test_view_for_status_code('login')

    def test_logout(self):
        self._test_view_for_status_code('logout', status_code=302)


class TestFeedViews(BaseTestCase):
    user = None
    feed = None

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='u', email='a@a.com', password='asd')
        cls.feed = Feed.objects.create(added_by=cls.user, feed_url='http://test.com', title='title')

    def test_new_feed_view_get(self):
        # Test unauthenticated user
        self._test_view_for_status_code('new_feed', status_code=302)

        # Test authenticated user
        url = reverse('new_feed')
        request = self.factory.get(url)
        request.user = self.user

        view = NewFeedView()
        view.request = request
        response = view.get(request)

        self.assertEqual(200, response.status_code)

    def test_feed_list(self):
        self._test_view_for_status_code('feed_list')

    def test_feed_details(self):
        self._test_view_for_status_code('feed_detail', {'pk': self.feed.pk})

    def test_feed_details_context(self):
        kw = {'pk': self.feed.pk}
        url = reverse('feed_detail', kwargs=kw)

        request = self.factory.get(url)
        request.user = self.user

        view = FeedDetailView()
        view.request =request
        view.kwargs = kw

        response = view.get(request)
        context = response.context_data

        self.assertEqual(0, len(context['entry_list']))
        self.assertFalse(context['has_bookmark'])
        self.assertEqual(self.feed, context['object'])


class TestEntryViews(BaseTestCase):
    user = None
    feed = None
    entry = None
    comment = None

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='u', email='a@a.com', password='asd')
        cls.feed = Feed.objects.create(added_by=cls.user, feed_url='http://test.com', title='title')
        cls.entry = Entry.objects.create(feed=cls.feed, date=datetime.utcnow(), title='title', content='content')
        cls.comment = Comment.objects.create(entry=cls.entry, user=cls.user, content='comment')

    def test_entry_view(self):
        self._test_view_for_status_code('entry_detail', url_kwargs={'pk': self.entry.pk})

    def test_entry_view_context(self):
        kw = {'pk': self.entry.pk}
        url = reverse('entry_detail', kwargs=kw)

        request = self.factory.get(url)
        request.user = self.user

        view = EntryDetailView()
        view.request = request
        view.kwargs = kw

        response = view.get(request)
        context = response.context_data
        self.assertEqual(self.entry, context['object'])
        self.assertIsInstance(context['comment_form'], CommentForm)
        self.assertEqual(self.comment, context['comment_list'][0])
