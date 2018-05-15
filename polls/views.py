from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Choice, Question, MyUser
from .forms import ChoiceFormSet, UserCreationForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib.auth.views import LoginView


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
            fields = ('first_name',
                      'last_name',
                      'email_address',
                      'gender',
                      'password')
            formset = ChoiceFormSet(instance=self.object)
        else:
            formset = ChoiceFormSet()
        context.update({
            'formset': formset,
        })
        return context

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        formset = ChoiceFormSet(request.POST,
                                request.FILES,
                                instance=self.object
                                )
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


def activate(request, uidb64, token):
    print(request)
    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=id)
    except(TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'polls/index.html', {
            'successful_activation': 'Thank you for your email confirmation. Now you can login your account.'})
    else:
        return HttpResponse('Activation link is invalid!')


class CreateAccountView(generic.CreateView):
    model = MyUser
    form_class = UserCreationForm
    template_name = 'polls/sign_up.html'

    def get_success_url(self):
        if getattr(self, 'object', None):
            return reverse('polls:index')
        return reverse('polls:create_account')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        form = UserCreationForm(data=request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            form.cleaned_data['username'] = self.cleaned_data['username']
            return HttpResponseRedirect(reverse('polls:index'))
        else:
            form = UserCreationForm()
        return response


class SignInView(LoginView):
    template_name = 'polls/sign_in.html'

    def get_success_url(self):
        url = 'polls:index'
        return reverse(url)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = MyUser.objects.get(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'polls/index.html')
            else:
                return render(request, 'polls/sign_in.html', {
                    'error_message': 'It seems that your account is not activated. Please check your inbox'
                })
        else:
            form = self.get_context_data()['form']
            # form = ??????????????????????????????????????????????
            return render(request, 'polls/sign_in.html', {
                'error_message': 'Account is not in the database.',
                'form': form
            })
