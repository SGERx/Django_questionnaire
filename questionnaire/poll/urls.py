from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_page'),
    path('home/', views.index, name='main_page'),
    path('index/', views.index, name='main_page'),
    path('polls/', views.poll_list, name='polls_page'),
    path('polls/<int:pk>/', views.poll_detail, name='poll_details'),
    # path('questions/', views.poll_list, name='questions_page'),
    path('questions/<int:pk>/', views.poll_detail, name='question_details'),
]
