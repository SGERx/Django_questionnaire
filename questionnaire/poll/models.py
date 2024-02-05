from django.db import models


class Participant(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password_hash = models.CharField(max_length=255)
    password_salt = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'participants'


class Poll(models.Model):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    participants = models.IntegerField(default=0)
    created_on = models.DateTimeField()
    redacted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'polls'


class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    participants = models.IntegerField(default=0)
    answered_rating = models.IntegerField(default=0)
    question_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    redacted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'questions'


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    redacted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'answer_options'


class Answer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.TextField(null=True, blank=True)
    response_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'answers'
