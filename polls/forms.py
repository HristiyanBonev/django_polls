from django import forms
from .models import Question, Choice, MyUser


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
    username = forms.CharField(max_length=255, required=True)

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
        cleaned_data = super().clean()
        email = cleaned_data.get('email_address')
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

    # def clean(self):
    #     cleaned_data = super(UserCreationForm, self).clean()
    #     if cleaned_data['password'] != cleaned_data['confirm_password']:
    #         raise forms.ValidationError('Passwords don\'t match')
    #     return cleaned_data
