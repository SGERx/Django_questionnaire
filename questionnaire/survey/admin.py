from django.contrib import admin
from .models import Answer, AnswerOption, Participant, Survey, Question, QuestionRelation


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'participants', 'created_on', 'redacted')
    search_fields = ('title',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'participants', 'answered_quantity', 'answered_rating', 'question_text', 'created_on', 'redacted')
    search_fields = ('question_text',)


class QuestionRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_question', 'child_question')
    search_fields = ('parent_question__question_text', 'child_question__question_text')


class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_text', 'created_on', 'redacted')
    search_fields = ('option_text',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_id', 'question', 'response_text', 'response_date')
    search_fields = ('response_text',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_on', 'last_login')
    search_fields = ('username', 'email')


admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerOption, AnswerOptionAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionRelation, QuestionRelationAdmin)
