from django.contrib import admin
from .models import AnswerOption, Participant, Question, QuestionRelation, Survey, UserAnswer
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'participants', 'created_on', 'redacted')
    search_fields = ('title',)
    fields = ('title', 'description', 'participants')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'title', 'participants_rating', 'answered_quantity', 'answered_rating', 'question_text', 'created_on', 'redacted')
    search_fields = ('question_text',)
    fields = ('survey', 'title', 'question_text')


@admin.register(QuestionRelation)
class QuestionRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_question', 'child_question', 'response_condition')
    search_fields = ('parent_question__question_text', 'child_question__question_text')
    fields = ('parent_question', 'child_question', 'response_condition')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_text', 'created_on', 'redacted')
    search_fields = ('option_text',)
    fields = ('question', 'option_text',)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_id', 'question', 'response_text', 'response_date')
    search_fields = ('response_text',)


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_on', 'last_login')
    search_fields = ('username', 'email')
    exclude = ('password_salt', 'created_on', 'last_login')


class MyUserAdmin(BaseUserAdmin):
    add_form = MyUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
