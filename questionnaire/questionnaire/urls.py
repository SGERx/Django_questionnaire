from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('home/admin/', admin.site.urls),
    path('surveys/admin/', admin.site.urls),
]
