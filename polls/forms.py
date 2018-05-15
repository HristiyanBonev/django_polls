from django import forms
from .models import Question, Choice, MyUser
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage


class ChoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choice_text'].required = True

    class Meta:
        model = Choice
        fields = ('choice_text',)

    def clean_choice_text(self):
        choice_text = self.cleaned_data.get('choice_text')
        choice_text = choice_text.strip()
        return choice_text


ChoiceFormSet = forms.inlineformset_factory(Question,
                                            Choice,
                                            form=ChoiceForm,
                                            can_delete=False,
                                            max_num=5,
                                            extra=2
                                            )


class UserCreationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=16,
                                       widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)

    field_order = ('username',
                   'password',
                   'confirm_password',
                   'email_address',
                   'first_name',
                   'last_name',
                   'gender')

    class Meta:
        fields = ('username',
                  'password',
                  'confirm_password',
                  'email_address',
                  'first_name',
                  'last_name',
                  'gender')
        model = MyUser
        widgets = {
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput(),
            'email_address': forms.EmailInput()
        }

    def clean_email(self):
        email = self.cleaned_data.get('email_address')
        try:
            MyUser.objects.get(email_address=email)
        except MyUser.DoesNotExist:
            return email
        raise forms.ValidationError('This email is already in use.')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return username
        return forms.ValidationError('This username is already in use.')

    def save(self):
        username = self.clean_username
        print(username)
        object = super().save()
        object.is_active = False
        mail_subject = 'Activate your account.'
        message = render_to_string('polls/email/activation.html', {
            'domain': 'localhost:8000',
            'user': object.first_name.capitalize(),
            'uid': urlsafe_base64_encode(force_bytes(object.pk)).decode(),
            'token': account_activation_token.make_token(object),
        })
        to_email = object.email_address
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.content_subtype = 'html'
        email.send()
        return object

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        if cleaned_data['password'] != cleaned_data['confirm_password']:
            raise forms.ValidationError('Passwords don\'t match')
        return cleaned_data
