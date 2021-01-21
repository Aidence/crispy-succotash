from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms.models import ModelForm
from django.forms.widgets import TextInput

from crispy.apps.feed.models import Feed


class NewFeedForm(ModelForm):
    helper = FormHelper()
    helper.method = 'post'
    helper.form_action = ''
    helper.layout = Layout('feed_url',
                           Submit('submit', 'Submit', css_class='btn btn-success'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Feed
        fields = ['feed_url', ]
        widgets = {'feed_url': TextInput()}

    def save(self, commit: bool=True):
        feed = super().save(commit=commit)
        feed.added_by = self.user

        if commit:
            feed.save()

        return feed
