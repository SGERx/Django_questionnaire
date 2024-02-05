from django.contrib import admin
from .models import Answer, AnswerOption, Participant, Poll, Question


class PollAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'participants', 'created_on', 'redacted')
    search_fields = ('title',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'participants', 'answered_rating', 'question_text', 'created_on', 'redacted')
    search_fields = ('question_text',)


class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_text', 'created_on', 'redacted')
    search_fields = ('option_text',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant', 'question', 'response_text', 'response_date')
    search_fields = ('response_text',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_on', 'last_login')
    search_fields = ('username', 'email')


admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerOption, AnswerOptionAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
