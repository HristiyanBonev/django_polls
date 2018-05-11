from django.contrib import admin

from .models import Question, Choice


class ChoiceInline(admin.StackedInline):
    model = Choice


class QuestionAdmin(admin.ModelAdmin):
    inlines = (ChoiceInline,)


admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)

# Register your models here.
