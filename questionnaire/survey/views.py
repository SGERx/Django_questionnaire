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
from django.shortcuts import render, redirect
from django.db import connection
from django.utils import timezone
from .forms import QuestionResponseForm
from django.http import HttpResponseServerError

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
def survey_detail(request, pk, question_number=None):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    if request.method == 'GET':
        print("МЕТОД ЗАПРОСА GET")
        if question_number is None:
            print("GET - НОМЕРА ОТКРЫВАЮЩЕГО ВОПРОСА НЕТ")
            opening_question = get_opening_question(cursor, pk, user_id)
            if opening_question:
                print('ПОДОБРАН ОТКРЫВАЮЩИЙ ВОПРОС')
                options = [
                    (str(i + 1), opening_question[6 + i]) for i in range(4) if opening_question[6 + i]
                ]
                form = QuestionResponseForm(request.POST if request.method == 'POST' else None, options=options)
                context = {
                    'question_data': {
                        'survey_id': opening_question[1],
                        'question_id': opening_question[0],
                        'title': opening_question[2],
                        'answered_quantity': opening_question[3],
                        'answered_rating': opening_question[4],
                        'question_text': opening_question[5],
                        'answer_option_1': opening_question[6],
                        'answer_option_2': opening_question[7],
                        'answer_option_3': opening_question[8],
                        'answer_option_4': opening_question[9],
                        'created_on': opening_question[10],
                        'redacted': opening_question[11],
                    },
                    'form': form,
                }

                return render(request, 'survey/survey_detail.html', context)
            else:
                print('ДОСТУПНЫХ ВОПРОСОВ НЕТ')
                was_there_any_question = check_empty_survey(cursor, pk)
                if was_there_any_question > 0:
                    print('В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                    return redirect('statistics_page', pk=pk)
                elif was_there_any_question == 0:
                    print('В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                    return redirect('empty_survey')
                else:
                    error_message = "ошибка проверки опроса"
                    return HttpResponseServerError(error_message)
        else:
            error_message = "в методе GET не предусмотрена передача номера вопроса"
            return HttpResponseServerError(error_message)

    if request.method == 'POST':
        print('МЕТОД ЗАПРОСА POST')
        if question_number is None:
            print("POST - ОТКРЫВАЮЩЕГО ВОПРОСА НЕТ")
            opening_question = get_opening_question(cursor, pk, user_id)
            options = [
                    (str(i + 1), opening_question[6 + i]) for i in range(4) if opening_question[6 + i]
                ]
            form = QuestionResponseForm(request.POST, options=options)
            if form.is_valid():
                print("ФОРМА ВАЛИДНА")
                selected_option = form.cleaned_data['selected_option']
                cursor.execute('''
                    INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                    VALUES (%s, %s, %s, %s)
                ''', [request.user.id, opening_question[0], selected_option, datetime.now()])

                connection.commit()
                current_question_number = opening_question[0]
                next_question_exists = check_next_question_existance(cursor, pk, user_id, current_question_number)
                print(f'СЛЕДУЮЩИЙ ВОПРОС ПРОВЕРЕН - {next_question_exists}')
                if next_question_exists:
                    print('СЛЕДУЮЩИЙ ВОПРОС ЕСТЬ')
                    next_question = get_next_question_data(cursor, pk, user_id, current_question_number, answer_option=selected_option)
                    print(f"СЛЕДУЮЩИЙ ВОПРОС ИЗ ОПРОСА {pk}, ВОПРОС НОМЕР {next_question[0]}, ДАННЫЕ: {next_question}")
                    options = [
                        (str(i + 1), next_question[6 + i]) for i in range(4) if next_question[6 + i]
                    ]
                    form = QuestionResponseForm(request.POST, options=options)
                    context = {
                        'question_data': {
                            'survey_id': next_question[1],
                            'question_id': next_question[0],
                            'title': next_question[2],
                            'answered_quantity': next_question[3],
                            'answered_rating': next_question[4],
                            'question_text': next_question[5],
                            'answer_option_1': next_question[6],
                            'answer_option_2': next_question[7],
                            'answer_option_3': next_question[8],
                            'answer_option_4': next_question[9],
                            'created_on': next_question[10],
                            'redacted': next_question[11],
                        },
                        'form': form,
                        'survey_id': pk,
                        'question_number': next_question,
                    }
                    return render(request, 'survey/survey_detail.html', context)
                else:
                    print('СЛЕДУЮЩЕГО ВОПРОСА НЕТ')
                    was_there_any_question = check_empty_survey(cursor, pk)
                    if was_there_any_question > 0:
                        print('В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                        return redirect('statistics_page', pk=pk)
                    elif was_there_any_question == 0:
                        print('В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                        return redirect('empty_survey')
                    else:
                        error_message = "ошибка проверки опроса"
                        return HttpResponseServerError(error_message)
            else:
                error_message = "POST - ФОРМА НЕВАЛИДНА"
                return render(request, 'survey/survey_detail.html', context)
        else:
            error_message = "в методе POST не предусмотрена передача номера вопроса"
            return HttpResponseServerError(error_message)


def check_empty_survey(cursor, pk):
    check_empty_survey_query = f'''SELECT COUNT(*) FROM questions WHERE survey_id={pk}'''
    cursor.execute(check_empty_survey_query)
    survey_check = cursor.fetchone()
    survey_check_result = survey_check[0]
    print(survey_check_result)
    return survey_check_result


def get_opening_question(cursor, pk, user_id):
    get_opening_question_query = f'''
        SELECT * FROM questions
        WHERE survey_id={pk} AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id={user_id})
        AND id NOT IN (SELECT child_question_id FROM question_relations WHERE parent_question_id IN (SELECT question_id FROM user_answers WHERE auth_user_id={user_id}))
    '''
    cursor.execute(get_opening_question_query)
    opening_question = cursor.fetchone()
    return opening_question


def check_next_question_existance(cursor, pk, user_id, current_question_number=None):
    simple_check = f'''
        SELECT * FROM questions
        WHERE survey_id={pk} AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id={user_id})
        AND id NOT IN (SELECT child_question_id FROM question_relations WHERE parent_question_id IN (SELECT question_id FROM user_answers WHERE auth_user_id={user_id}))
    '''
    cursor.execute(simple_check)
    simple_check_answer = cursor.fetchone()
    if simple_check_answer is None:
        print("get_next_question - NONE")
        return False
    else:
        print("get_next_question - PASSED")
        print(simple_check_answer[0])
        return True


def get_next_question_data(cursor, pk, user_id, current_question_number, answer_option):
    check_child_question_existence = f'''SELECT * FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}' '''
    cursor.execute(check_child_question_existence)
    check_child_question_existence_result = cursor.fetchone()
    if check_child_question_existence_result is None:
        simple_next_question = f'''SELECT * FROM questions WHERE survey_id='{pk}' AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id='{user_id}') AND id NOT IN (SELECT child_question_id FROM question_relations)'''
        cursor.execute(simple_next_question)
        simple_next_question_result = cursor.fetchone()
        return simple_next_question_result
    else:
        check_child_question_was_not_answered = f'''SELECT * FROM user_answers WHERE question_id IN (SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}') '''
        cursor.execute(check_child_question_was_not_answered)
        check_child_question_was_not_answered_result = cursor.fetchone()
        if check_child_question_was_not_answered_result is None:
            child_question = f'''SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' '''
            cursor.execute(child_question)
            child_question_result = cursor.fetchone()
            return child_question_result
        else:
            simple_next_question = f'''SELECT id FROM questions WHERE survey_id='{pk}' AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id='{user_id}') AND id NOT IN (SELECT child_question_id FROM question_relations)'''
            cursor.execute(simple_next_question)
            simple_next_question_result = cursor.fetchone()
            return simple_next_question_result


def statistics_detail(request, pk):
    context = {'pk': pk}
    return render(request, 'survey/statistics.html', context=context)


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


# Страница пустого опроса (нет вопросов)
@login_required
def empty_survey(request):
    template = loader.get_template('survey/empty_survey.html')
    return HttpResponse(template.render({}, request))
