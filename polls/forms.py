from django import forms
from .models import Question, Choice


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
