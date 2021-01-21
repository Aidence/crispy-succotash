from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms.models import ModelForm
from django.forms.widgets import TextInput, HiddenInput

from crispy.apps.web.models import Comment


class CommentForm(ModelForm):
    helper = FormHelper()
    helper.method = 'post'
    helper.action = ''
    helper.layout = Layout('content',
                           Submit('submit', 'Submit', css_class='btn btn-success'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ['content', 'entry']
        widgets = {
            'content': TextInput(),
            'entry': HiddenInput(),
        }

    def save(self, commit: bool=True):
        comment = super().save(commit=False)
        comment.from_user = self.user

        if commit:
            comment.save()

        return comment
