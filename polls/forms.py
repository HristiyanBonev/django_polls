from django import forms

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Choice, MyUser, Question
from .tokens import account_activation_token


class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = ('choice_text',)

    def clean_choice_text(self):
        choice_text = self.cleaned_data.get('choice_text')
        choice_text = choice_text.strip()
        return choice_text


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('question_text',)


ChoiceFormSet = forms.inlineformset_factory(Question,
                                            Choice,
                                            form=ChoiceForm,
                                            can_delete=False,
                                            max_num=5,
                                            extra=2,
                                            )


class UserCreationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=16,
                                       widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    username = forms.CharField(max_length=50, required=True, validators=[])

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
        help_texts = {
            'username': None
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
        print(object.is_active)
        return object

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        if cleaned_data['password'] != cleaned_data['confirm_password']:
            raise forms.ValidationError('Passwords don\'t match')
        return cleaned_data
