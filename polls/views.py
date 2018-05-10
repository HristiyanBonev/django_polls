from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Choice, Question
from .forms import ChoiceFormSet
from django.utils import timezone
from django.contrib import messages


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()
                                       ).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


class AddQuestionView(generic.ListView):
    model = Question
    template_name = 'polls/add.html'


class CreateQuestionView(generic.CreateView):
    model = Question
    template_name = 'polls/add.html'
    fields = ('question_text', 'creator',)

    def get_success_url(self):
        if getattr(self, 'instance', None):
            return reverse('polls:detail',
                           kwargs={'pk': self.object.pk})
        return reverse('polls:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if getattr(self, 'object', None):
            formset = ChoiceFormSet(instance=self.object)
        else:
            formset = ChoiceFormSet()
        context.update({
            'formset': formset,
        })
        return context

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        formset = ChoiceFormSet(request.POST, request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Question added successfully.')
            return HttpResponseRedirect(reverse('polls:index'))
        else:
            formset = ChoiceFormSet(instance=self.object)
        return response


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_answer = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Raises a warning if exception
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You didn\'t select a choice'
        })
    else:
        # Else increments the votes for this question with 1
        selected_answer.votes += 1
        selected_answer.save()
        return HttpResponseRedirect(
            reverse('polls:results',
                    kwargs={'pk': question.id})
        )
