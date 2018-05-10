from django import forms
from .models import Question, Choice


# class QuestionForm(forms.ModelForm):
#
#     class Meta:
#         model = Question


ChoiceFormSet = forms.inlineformset_factory(Question, Choice, fields=('choice_text',))
