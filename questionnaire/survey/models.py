from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
import hashlib
from django.utils import timezone


class Participant(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    password_salt = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'participants'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.password_salt:
            self.password_salt = hashlib.sha256(str(timezone.now()).encode()).hexdigest()[:10]
        self.password = hashlib.sha256((self.password_salt + self.password).encode()).hexdigest()
        super().save(*args, **kwargs)


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
    participants_rating = models.IntegerField(default=0)
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
    participants_id = models.ForeignKey(Participant, db_column='participants_id', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.TextField(null=True, blank=True)
    response_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'user_answers'