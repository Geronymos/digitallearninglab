import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import DllUser

from ..communication.tasks import send_mail


class EditUserForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ['email']


class SignUpForm(UserCreationForm):
    terms_accepted = forms.BooleanField(required=True)
    newsletter_registration = forms.BooleanField(
        label='Ja, ich möchte den Newsletter des digital.learning.labs erhalten.',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Absenden', css_class='button button--primary')
        )
        data_privacy_url = reverse_lazy('data-privacy')
        self.fields['terms_accepted'].label = f'Ja, ich stimme den <a href="/">Nutzungsbedingungen</a>- und den ' \
        f'<a href="{data_privacy_url}">Datenschutzbestimmungen</a> des digital.learning.lab zu.'
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def send_registration_email(self, token):
        context = {
            'token': token,
        }
        send_mail.delay(
            event_type_code='NEWSLETTER_CONFIRM',
            ctx=context,
            email=self.cleaned_data['email']
        )

    class Meta:
        model = DllUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'newsletter_registration',
            'terms_accepted',
            'password1',
            'password2',
        )
        labels = {
            'terms_accepted': 'Nutzungs- und Datenschutzbestimmungen'
        }


class UserProfileForm(forms.ModelForm):
    """
    This form is just used for displaying the profile info
    """
    full_name = forms.CharField(disabled=True, required=False, label=_("Name"))
    email = forms.CharField(disabled=True, required=False, label=_("E-Mail"))
    status = forms.CharField(disabled=True, required=False, label=_("Status"))
    joined = forms.CharField(disabled=True, required=False, label=_("Beigetreten"))

    class Meta:
        model = DllUser
        fields = ('full_name', 'email', 'joined', 'status')

    def __init__(self, **kwargs):
        super(UserProfileForm, self).__init__(**kwargs)
        self.fields['full_name'].initial = self.instance.full_name
        self.fields['status'].initial = ', '.join(map(str, self.instance.status_list))
        if isinstance(self.instance.doi_confirmed_date, datetime.datetime):
            self.fields['joined'].initial = self.instance.doi_confirmed_date.strftime("%d %B %Y")

    def save(self, commit=True):
        # do not save any changes here
        pass


class UserEmailsForm(forms.ModelForm):

    class Meta:
        model = DllUser
        fields = ('email',)

    def save(self, commit=True):
        # do not save any changes here
        pass


class UserPasswordChangeForm(PasswordChangeForm):

    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UserPasswordChangeForm, self).__init__(self.instance, **kwargs)

    def clean_new_password2(self):
        password2 = super(UserPasswordChangeForm, self).clean_new_password2()
        if password2 == self.cleaned_data.get('old_password'):
            raise forms.ValidationError(
                _('Old and new password must be different. Please use another new password.'),
                code='password_not_changed',
            )
        return password2


class UserAccountDeleteForm(forms.Form):
    conditions = forms.BooleanField(widget=forms.CheckboxInput,
                                    label=_("Ich habe die Bedingungen gelesen und akzeptiere sie."))

    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UserAccountDeleteForm, self).__init__(**kwargs)

    def save(self):
        self.instance.delete()
