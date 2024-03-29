from django.contrib import admin
from django.urls import path, include
from django.urls import re_path

from . import views

urlpatterns = [
    path('', views.index, name='main_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register_view, name='register'),
    path('home/', views.index, name='home'),
    path('index/', views.index, name='main_page'),
    path('surveys/admin/', admin.site.urls),
    re_path(r'^.*admin/', admin.site.urls),
    path('surveys/', views.survey_list, name='surveys_page'),
    path('surveys/<int:pk>/', views.survey_detail, name='survey_detail'),
    path('surveys/<int:pk>/<int:question_number>/', views.survey_detail, name='survey_detail'),
    path('questions/<int:pk>/', views.survey_detail, name='question_details'),
    path('statistics/<int:pk>/', views.statistics_detail, name='statistics_page'),
    path('empty_survey/', views.empty_survey, name='empty_survey'),
]

handler404 = "questionnaire.views.page_not_found_view"
handler403 = "questionnaire.views.access_denied_view"
handler500 = "questionnaire.views.internal_error_view"
