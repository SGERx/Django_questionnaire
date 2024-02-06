from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='main_page'),
    path('home/', views.index, name='main_page'),
    path('index/', views.index, name='main_page'),
    path('surveys/admin/', admin.site.urls),
    path('surveys/', views.survey_list, name='surveys_page'),
    path('surveys/<int:pk>/', views.survey_detail, name='survey_details'),
    path('questions/<int:pk>/', views.survey_detail, name='question_details'),
]
