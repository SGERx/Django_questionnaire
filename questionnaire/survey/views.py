from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Participant
from .forms import LoginForm, RegistrationForm
import bcrypt
from django.contrib.auth import authenticate, login, logout
from psycopg2 import sql
import psycopg2

connection_params = {
    'dbname': 'questionnaire_postgres',
    'user': 'postgres',
    'password': 'root',
    'host': '127.0.0.1',
    'port': '5433'
}


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
            print('form is valid')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password = make_password(password)
            # user = Participant(username=username, password=hashed_password.decode('utf-8'), email=email)
            user = Participant(username=username, password=hashed_password, email=email)
            user.save()
            first_name = 'default'
            last_name = 'default'
            create_auth_user_query = sql.SQL('''
            INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
            VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
            ''')
            params = (username, hashed_password, email, first_name, last_name)
            connection = psycopg2.connect(**connection_params)
            cursor = connection.cursor()
            cursor.execute(create_auth_user_query, params)
            connection.commit()
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
            # if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            if user and check_password(password, user.password):
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
