import feedparser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from crispy.apps.feed.models import Feed, Entry
from crispy.apps.feed.scraper import Scraper
from crispy.apps.web.forms.new_feed import NewFeedForm
from crispy.apps.web.models import Bookmark


@method_decorator(login_required, name='dispatch')
class NewFeedView(FormView):
    form_class = NewFeedForm
    template_name = 'generic/form.html'

    def get_form_kwargs(self):
        """
        This injects the current user into the form
        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headline'] = 'Add a new feed'
        context['title'] = 'New feed'
        context['hide_header'] = True
        return context

    def form_valid(self, form):
        feed = form.save(commit=False)
        scraper = Scraper(feedparser.parse, feed)
        updated, parsed_feed = scraper.check_feed()

        if updated:
            feed.update_feed_data(parsed_feed)
            feed.save()
            feed.update_feed_entries(parsed_feed.entries)

        feed.save()

        # Sets success URL to the feed's detail page
        self.success_url = reverse('feed_detail', kwargs={'pk': feed.pk})

        return super().form_valid(form)


class FeedListView(ListView):
    model = Feed
    paginate_by = 10


@method_decorator(login_required, name='dispatch')
class MyFeedListView(ListView):
    model = Feed
    paginate_by = 10

    def get_queryset(self):
        return Feed.objects.from_user(self.request.user)


class FeedDetailView(ListView, DetailView):
    # We subclass ListView to paginate entries, and overwrite the ListView's MultipleObjectMixin with
    # DetailView to get a single feed entry in get_context_data
    model = Feed
    paginate_by = 12
    template_name = 'feed/feed_detail.html'

    def get_queryset(self):
        return Entry.objects.filter(feed__id=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        self.object = Feed.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg)).first()
        context = super().get_context_data()
        context['feed'] = self.object
        context['entry_list'] = context['object_list']
        context['has_bookmark'] = False

        if self.request.user and self.request.user.is_authenticated:
            context['has_bookmark'] = Bookmark.user_has_bookmark(self.request.user, self.object)

        return context


class FeedUpdateView(DetailView):
    model = Feed

    def get(self, request, *args, **kwargs):
        feed = self.get_object()
        scraper = Scraper(feedparser.parse, feed)
        updated, parsed_feed = scraper.check_feed()

        if updated:
            feed.update_feed_data(parsed_feed)
            feed.update_feed_entries(parsed_feed.entries)
            feed.save()
            messages.success(request, 'Found new updates. Enjoy!')
        else:
            messages.info(request, 'Nothing new yet...')

        return redirect(reverse('feed_detail', kwargs={'pk': feed.pk}))


@method_decorator(login_required, name='dispatch')
class ToggleBookmarkView(DetailView):
    model = Feed

    def get(self, request, *args, **kwargs):
        feed = self.get_object()
        bookmark = Bookmark.get_bookmark(user=self.request.user, feed=feed)

        if not bookmark:
            bookmark = Bookmark(user=self.request.user, feed=feed)
            bookmark.save()
        else:
            bookmark.delete()

        return redirect(reverse('feed_detail', kwargs={'pk': feed.pk}))


@method_decorator(login_required, name='dispatch')
class BookmarkedFeedsView(ListView):
    model = Feed
    paginate_by = 10

    def get_queryset(self):
        return Feed.objects.from_user_bookmarks(self.request.user)
