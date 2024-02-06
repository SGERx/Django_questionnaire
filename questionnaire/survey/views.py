from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader


# Главная страница
def index(request):
    template = loader.get_template('survey/index.html')
    return HttpResponse(template.render({}, request))


# Список опросов
def survey_list(request):
    template = loader.get_template('survey/surveys.html')
    return HttpResponse(template.render({}, request))


# Детали опроса
def survey_detail(request, pk):
    template = loader.get_template('survey/survey_detail.html')
    return HttpResponse(template.render({}, request))


# Админка
def admin(request):
    return HttpResponse("Заглушка под переход в админку")
