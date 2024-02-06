from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


# Главная страница
@login_required
def index(request):
    template = loader.get_template('survey/index.html')
    return HttpResponse(template.render({}, request))


# Список опросов
@login_required
def survey_list(request):
    template = loader.get_template('survey/surveys.html')
    return HttpResponse(template.render({}, request))


# Детали опроса
@login_required
def survey_detail(request, pk):
    template = loader.get_template('survey/survey_detail.html')
    return HttpResponse(template.render({}, request))


# @login_required
# def login_page(request):
#     template = loader.get_template('survey/login_page.html')
#     return HttpResponse(template.render({}, request))
