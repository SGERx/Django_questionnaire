from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Participant
from .forms import LoginForm, RegistrationForm
import bcrypt
from django.contrib.auth import authenticate, login, logout


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


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            user = Participant(username=username, password=hashed_password.decode('utf-8'), email=email)
            user.save()

            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = Participant.objects.filter(username=username).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password'})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
