from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm, QuestionResponseForm
import bcrypt
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, User
from django.contrib.auth import authenticate, login, logout
from psycopg2 import sql
import psycopg2
from django.db import connection
from datetime import datetime


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

    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()
    query = 'SELECT * FROM questions WHERE id IN (SELECT MIN(id) from questions WHERE id NOT IN (SELECT id FROM user_answers))'
    cursor.execute(query)
    question_data = cursor.fetchone()
    cursor.close()
    conn.close()

    options = [
        (str(i + 1), question_data[6 + i]) for i in range(4)
    ]

    form = QuestionResponseForm(request.POST if request.method == 'POST' else None, options=options)
    context = {
        'question_data': {
            'survey_id': question_data[1],
            'question_id': question_data[0],
            'title': question_data[2],
            'answered_quantity': question_data[3],
            'answered_rating': question_data[4],
            'question_text': question_data[5],
            'answer_option_1': question_data[6],
            'answer_option_2': question_data[7],
            'answer_option_3': question_data[8],
            'answer_option_4': question_data[9],
            'created_on': question_data[10],
            'redacted': question_data[11],
        },
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            selected_option = form.cleaned_data['selected_option']

            with psycopg2.connect(**connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                        VALUES (%s, %s, %s, %s)
                    ''', [request.user.id, question_data[0], selected_option, datetime.now()])

            with psycopg2.connect(**connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        SELECT * FROM questions
                        WHERE id IN (
                            SELECT MIN(id) FROM questions
                            WHERE id NOT IN (SELECT id FROM user_answers WHERE auth_user_id = %s)
                        )
                    ''', [request.user.id])
                    next_question_data = cursor.fetchone()

            return redirect('survey_detail', pk=pk)

    return render(request, 'survey/survey_detail.html', context)


def statistics_detail(request):
    return render('statistics.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print('form is valid')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            hashed_password = make_password(password)
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
