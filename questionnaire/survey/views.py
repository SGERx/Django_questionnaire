from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm, QuestionForm
import bcrypt
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, User
from django.contrib.auth import authenticate, login, logout
from psycopg2 import sql
import psycopg2
from django.db import connection


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
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    query = 'SELECT * FROM surveys ORDER BY participants DESC;'
    cursor.execute(query)
    surveys_data = cursor.fetchall()
    cursor.close()
    conn.close()
    print(surveys_data)
    for survey in surveys_data:
        print(survey)
    context = {
        'surveys_data': [
            {'id': survey[0], 'title': survey[1], 'description': survey[2],
             'participants': survey[3], 'created_on': survey[4], 'redacted': survey[5]}
            for survey in surveys_data
        ],
    }
    return render(request, 'survey/surveys.html', context)


# Детали опроса
@login_required
def survey_detail(request, pk):
    form = QuestionForm()
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    query = f'SELECT * FROM questions WHERE survey_id={pk}'
    cursor.execute(query)
    question_data = cursor.fetchall()
    cursor.close()
    conn.close()
    print(question_data)
    for question in question_data:
        print(question)
    context = {
        'question_data': [
            {'survey_id': question[1], 'question_id': question[0], 'title': question[2],
             'answered_quantity': question[3], 'answered_rating': question[4],
             'question_text': question[5], 'created_on': question[6], 'redacted': question[7]}
            for question in question_data
        ],
    }
    # return render(request, 'survey/survey_detail.html', context, {'form': form})
    return render(request, 'survey/survey_detail.html', context)
    
    
    
    # template = loader.get_template('survey/survey_detail.html')
    # return HttpResponse(template.render({}, request))


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
            # user = Participant(username=username, password=hashed_password, email=email)
            # user.save()
            first_name = 'default'
            last_name = 'default'
            create_auth_user_query = sql.SQL('''
            INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
            VALUES (%s, %s, %s, %s, %s, False, False, TRUE, NOW());
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


# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = Participant.objects.filter(username=username).first()
#             # if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
#             if user and check_password(password, user.password):
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password'})
#     else:
#         form = LoginForm()

#     return render(request, 'login.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM auth_user WHERE username = %s",
                    [username]
                )
                user_row = cursor.fetchone()

            if user_row and check_password(password, user_row[1]):
                user_id = user_row[0]
                user = User(id=user_id, username=username)
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
