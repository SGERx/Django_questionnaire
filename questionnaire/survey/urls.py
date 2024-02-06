from django.urls import path, include
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='main_page'),
    # path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register_view, name='register'),
    path('home/', views.index, name='home'),
    path('index/', views.index, name='main_page'),
    path('surveys/admin/', admin.site.urls),
    path('surveys/', views.survey_list, name='surveys_page'),
    path('surveys/<int:pk>/', views.survey_detail, name='survey_details'),
    path('questions/<int:pk>/', views.survey_detail, name='question_details'),
]
