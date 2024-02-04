from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('home', views.index),
    path('index', views.index),
    path('poll/', views.poll_list),
    path('poll/<int:pk>/', views.poll_detail),
]
