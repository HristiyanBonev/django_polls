import json
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import generic

from .forms import ChoiceFormSet, UserCreationForm
from .models import Choice, MyUser, Question
from .tokens import account_activation_token


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()
                                       ).order_by('-pub_date')[:2]  # Change this!!!!


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # import ipdb; ipdb.set_trace()
        question = Question.objects.get(pk=self.object.pk)
        choices = Choice.objects.filter(question=question).values('choice_text', 'votes')
        context.update({
            'choices': [c for c in choices],
        })
        return context


class CreateQuestionView(LoginRequiredMixin, generic.CreateView):
    model = Question
    template_name = 'polls/add.html'
    fields = ('question_text',)

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

    def form_valid(self, form):
        # import ipdb; ipdb.set_trace()
        response = super().form_valid(form)
        self.object.creator = self.request.user
        self.object.save()
        return response

    def post(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        response = super().post(request, *args, **kwargs)
        formset = ChoiceFormSet(request.POST,
                                request.FILES,
                                instance=self.object
                                )
        print(kwargs)
        if formset.is_valid():
            if request.user.is_authenticated:
                formset.save()

            messages.success(request, 'Question added successfully.')
            return HttpResponseRedirect(reverse('polls:index'))
        else:
            formset = ChoiceFormSet(instance=self.object)
        return response

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_answer = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Raises a warning if exception
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Please select a choice'
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
        messages.success(request, """Account activated successfully!
                         <a href='/polls/sign_in/' style='color:red'><b><u>Sign in</u></b></a> in order to submit questions.""")
        return HttpResponseRedirect(reverse('polls:index'))
    else:
        return HttpResponse('Activation link is invalid!')


class CreateAccountView(generic.CreateView):
    model = MyUser
    form_class = UserCreationForm
    template_name = 'polls/sign_up.html'

    def get_success_url(self):
        if getattr(self, 'object', None):
            return HttpResponseRedirect(reverse('polls:index'))
        return reverse('polls:create_account')

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(data=request.POST)
        print(form.errors)
        if form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                form.save()
                messages.success(request, """Account created successfully!
                             We've sent activation mail at your email address <br/>
                             <u><b><a target='_blank' href=https://www.{}>Click here to check your mail</a></b></u>"""
                             .format(form.cleaned_data['email_address']
                                     .split('@')[1]))
                return HttpResponseRedirect(reverse('polls:index'))
        else:
            form = UserCreationForm()
        return super().post(request, *args, **kwargs)


class SignInView(LoginView):
    template_name = 'polls/sign_in.html'

    def get_success_url(self):
        url = 'polls:index'
        return reverse(url)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = MyUser.objects.get(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['member_id'] = request.user.username
                    messages.success(request, 'Welcome back, {}!'.format(user.username.capitalize()))
                    return HttpResponseRedirect(reverse('polls:index'))
                else:
                    messages.error(request, 'Your account is not activated')
                    return HttpResponseRedirect(reverse('polls:sign_in'))

        except MyUser.DoesNotExist:
            form = self.get_context_data()['form']

            return render(request, 'polls/sign_in.html', {
                'error_message': 'Account is not in the database.',
                'form': form
                })
