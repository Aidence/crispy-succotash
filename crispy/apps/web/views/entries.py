from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from crispy.apps.feed.models import Entry
from crispy.apps.web.forms.comment import CommentForm
from crispy.apps.web.models import Comment


class EntryDetailView(ListView, DetailView):
    # We subclass ListView to paginate entries, and overwrite the ListView's MultipleObjectMixin with
    # DetailView to get a single feed entry in get_context_data
    model = Entry
    paginate_by = 10
    template_name = 'feed/entry_detail.html'

    def get_queryset(self):
        return Comment.objects.filter(entry__id=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        self.object = Entry.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg)).first()
        context = super(EntryDetailView, self).get_context_data()
        context['entry'] = self.object
        context['comment_form'] = CommentForm(initial={'entry': self.object.id})
        return context

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user

        messages.success(self.request, 'Comment added successfully')
        form.save(commit=True)
        # Sets the redirect URL
        redirect_url = '{}#comment-{}'.format(
            reverse('entry_detail', kwargs={'pk': comment.entry_id}),
            comment.pk)
        return redirect(redirect_url)

    @method_decorator(login_required, name='dispatch')
    def post(self, request, *args, **kwargs):
        """
        Handles comment saving.
        """
        # Sets object as get_context_data needs it
        self.object_list = self.get_queryset()
        data = request.POST.dict()
        data['entry'] = self.kwargs.get(self.pk_url_kwarg)
        form = CommentForm(data=data, user=request.user)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
