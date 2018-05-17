from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractUser, UserManager


class MyUser(AbstractUser):
    '''
    '''
    is_active = models.BooleanField(default=False,
                                    verbose_name='account is activated')

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('K', 'Кон')
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='M'
    )
    email_address = models.CharField(max_length=200, unique=True)

    objects = UserManager()

    def __str__(self):
        return self.username


class Question(models.Model):
    '''
    '''
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('Date Published', auto_now_add=True)
    creator = models.ForeignKey(MyUser,
                                null=True,
                                related_name='created_by',
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text

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
