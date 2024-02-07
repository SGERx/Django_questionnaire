from django.contrib import admin
from .models import Question, QuestionRelation, Survey, UserAnswer
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
    list_display = (
        'id', 'survey_id', 'title', 'answered_quantity',
        'answered_rating', 'question_text', 'answer_option_1',
        'answer_option_2', 'answer_option_3', 'answer_option_4',
        'created_on', 'redacted')
    search_fields = ('question_text',)
    fields = ('survey', 'title', 'question_text', 'answer_option_1',
              'answer_option_2', 'answer_option_3', 'answer_option_4')


@admin.register(QuestionRelation)
class QuestionRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_question', 'child_question', 'response_condition')
    search_fields = ('parent_question__question_text', 'child_question__question_text')
    fields = ('parent_question', 'child_question', 'response_condition')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'auth_user_id', 'question_id', 'selected_option', 'response_date')
    search_fields = ('selected_option',)


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
