from django.db import models
from django.utils import timezone
import datetime


class Question(models.Model):
    '''
    '''
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Date Published', auto_now_add=True)
    creator = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return '{} \n - {}'.format(
            self.question_text,
            self.pub_date.strftime("%B %d, %Y - %H:%M:%S:%p")
            )

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    '''
    '''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
