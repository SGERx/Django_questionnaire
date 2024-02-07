from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, User
import hashlib
from django.utils import timezone


class Survey(models.Model):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    participants = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    redacted = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'surveys'

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    user_rating = models.IntegerField(default=0)
    answered_quantity = models.IntegerField(default=0)
    answered_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    question_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    redacted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'questions'

    def __str__(self):
        return self.title


class QuestionRelation(models.Model):
    parent_question = models.ForeignKey(Question, related_name='parent_question', on_delete=models.CASCADE)
    child_question = models.ForeignKey(Question, related_name='child_question', on_delete=models.CASCADE)
    response_condition = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'question_relations'


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    redacted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'answer_options'


class UserAnswer(models.Model):
    auth_user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='auth_user_id')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.TextField(null=True, blank=True)
    response_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'user_answers'
