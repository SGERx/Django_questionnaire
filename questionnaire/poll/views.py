from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader


# Главная страница
def index(request):
    template = loader.get_template('poll/index.html')
    return HttpResponse(template.render({}, request))


# Список опросов
def poll_list(request):
    template = loader.get_template('poll/polls.html')
    return HttpResponse(template.render({}, request))


# Детали опроса
def poll_detail(request, pk):
    template = loader.get_template('poll/poll_detail.html')
    return HttpResponse(template.render({}, request))


# Админка
def admin(request):
    return HttpResponse("Заглушка под переход в админку")
