from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth.forms import UserCreationForm


class CrispyUserRegistration(UserCreationForm):
    helper = FormHelper()
    helper.method = 'post'
    helper.form_action = ''
    helper.layout = Layout('username',
                           'password1',
                           'password2',
                           Submit('submit', 'Submit', css_class='btn btn-success'))
