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
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST

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


@login_required
def survey_detail(request, pk, question_number=None):
    if request.method == 'GET':
        print("START - ПЕРЕХОДИМ НА МЕТОД GET")
        return survey_detail_get(request, pk, question_number)
    elif request.method == 'POST':
        print("START - ПЕРЕХОДИМ НА МЕТОД POST")
        return survey_detail_post(request, pk, question_number)
    else:
        return HttpResponseServerError("Invalid HTTP method")


@login_required
@require_GET
def survey_detail_get(request, pk, question_number=None):
    print(f"НАЧАЛО ФУНКЦИИ GET - вопрос {question_number}")
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    print("МЕТОД ЗАПРОСА GET - НАЧАЛО ФУНКЦИИ")
    if question_number is None:
        print("ПЕРВОЕ РАЗДЕЛЕНИЕ - GET - НОМЕРА ОТКРЫВАЮЩЕГО ВОПРОСА НЕТ")
        opening_question = get_opening_question(cursor, pk, user_id)

        if opening_question:
            print('GET - ПОДОБРАН ОТКРЫВАЮЩИЙ ВОПРОС')
            opening_question_length = len(opening_question)
            print('GET - СОЗДАНИЕ ПЕРВОЙ ФОРМЫ GET')
            options = []

            for i in range(11, 8, -1):
                if len(opening_question[i]) != 0:
                    print(f'opening_question[{i}] - {opening_question[i]}')
                    options.extend([
                        (str(j + 1), answer) for j, answer in enumerate(opening_question[8:i+1])
                    ])
                    print('Options:', options)
                    break

            print('GET - Options outside the loop:', options)

            form = QuestionResponseForm(options=options)

            print(f'GET - ДЛИНА ОТКРЫВАЮЩЕГО ВОПРОСА - {opening_question_length}')
            context = {
                'question_data': {
                    'survey_id': opening_question[1],
                    'question_id': opening_question[0],
                    'title': opening_question[2],
                    'answered_quantity': opening_question[3],
                    'answered_rating': opening_question[4],
                    'question_text': opening_question[5],
                    'created_on': opening_question[6],
                    'redacted': opening_question[7],
                    'answer_option_1': opening_question[8],
                    'answer_option_2': opening_question[9] if opening_question_length >= 10 else None,
                    'answer_option_3': opening_question[10] if opening_question_length >= 11 else None,
                    'answer_option_4': opening_question[11] if opening_question_length >= 12 else None,
                },
                'form': form,
            }

            return render(request, 'survey/survey_detail.html', context)
        else:
            print('GET - ДОСТУПНЫХ ВОПРОСОВ НЕТ')
            was_there_any_question = check_empty_survey(cursor, pk)

            if was_there_any_question > 0:
                print('GET - В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                return redirect('statistics_page', pk=pk)
            elif was_there_any_question == 0:
                print('GET - В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                return redirect('empty_survey')
            else:
                error_message = "ошибка проверки опроса"
                return HttpResponseServerError(error_message)
    else:

        print('ПЕРВОЕ РАЗДЕЛЕНИЕ - GET - XXX - В МЕТОД GET БЫЛ ПЕРЕДАН НОМЕР ВОПРОСА - НЕПРОВЕРЕННЫЙ ФУНКЦИОНАЛ! XXX')
        passed_question = get_passed_question(cursor, pk, user_id, question_number)
        # if passed_question:
        print(f'LATEST ANOMALY - {passed_question}')
        print(f'LATEST ANOMALY TYPE - {type(passed_question)}')
        passed_question_length = len(passed_question)
        print('XXX - СОЗДАНИЕ ПЕРЕДАННОЙ ФОРМЫ GET')
        options = []

        if len(passed_question[9]) > 0:
            for i in range(11, 8, -1):
                if len(passed_question[i]) != 0:
                    print(f'opening_question[{i}] - {passed_question[i]}')
                    options.extend([
                        (str(j + 1), answer) for j, answer in enumerate(passed_question[8:i+1])
                    ])
                    print('Options:', options)
                    break
        else:
            options = [('1', passed_question[8])]

        print('XXX - Options outside the loop:', options)

        form = QuestionResponseForm(options=options)

        print(f'XXX - ДЛИНА ПЕРЕДАННОГО ВОПРОСА - {passed_question_length}')
        context = {
            'question_data': {
                'survey_id': passed_question[1],
                'question_id': passed_question[0],
                'title': passed_question[2],
                'answered_quantity': passed_question[3],
                'answered_rating': passed_question[4],
                'question_text': passed_question[5],
                'created_on': passed_question[6],
                'redacted': passed_question[7],
                'answer_option_1': passed_question[8],
                'answer_option_2': passed_question[9] if passed_question_length >= 10 else None,
                'answer_option_3': passed_question[10] if passed_question_length >= 11 else None,
                'answer_option_4': passed_question[11] if passed_question_length >= 12 else None,
            },
            'form': form,
        }

        return render(request, 'survey/survey_detail.html', context)


@login_required
@require_POST
def survey_detail_post(request, pk, question_number=None):
    print(f"НАЧАЛО ФУНКЦИИ POST - вопрос {question_number}")
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    print('МЕТОД ЗАПРОСА POST - НАЧАЛО ФУНКЦИИ')
    if question_number is None:
        print("POST - НОМЕР СЛЕДУЮЩЕГО ВОПРОСА НЕ ПЕРЕДАН В VIEW-ФУНКЦИЮ")
        opening_question = get_opening_question(cursor, pk, user_id)
        next_question_length = len(opening_question)

        print('POST - СОЗДАНИЕ ПЕРВОЙ ФОРМЫ POST')

        options = []

        for i in range(11, 8, -1):
            if len(opening_question[i]) != 0:
                print(f'opening_question[{i}] - {opening_question[i]}')
                options.extend([
                    (str(j + 1), answer) for j, answer in enumerate(opening_question[8:i+1])
                ])
                print('Options:', options)
                break

        print('POST - Options outside the loop:', options)

        form = QuestionResponseForm(request.POST, options=options)
        if form.is_valid():
            print("POST - ФОРМА ВАЛИДНА")
            print(f'ooo POST ЗАФИКСИРОВАН ОТВЕТ, form.cleaned_data - {form.cleaned_data}')
            print(f"POST selected_option - {form.cleaned_data['selected_option']}")
            print(f"POST тип возвращаемого значения - {type(form.cleaned_data['selected_option'])}")
            selected_option = form.cleaned_data['selected_option']
            cursor.execute('''
                INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                VALUES (%s, %s, %s, %s)
            ''', [request.user.id, opening_question[0], int(selected_option), datetime.now()])

            connection.commit()
            current_question_number = opening_question[0]
            next_question_exists = check_next_question_existance(cursor, pk, user_id, current_question_number)
            print(f'POST СЛЕДУЮЩИЙ ВОПРОС ПРОВЕРЕН - {next_question_exists}')
            if next_question_exists is not None:
                print(f'NEW ANOMALY - {next_question_exists}')
                print(f'NEW ANOMALY TYPE - {type(next_question_exists)}')
                print('POST СЛЕДУЮЩИЙ ВОПРОС ЕСТЬ')
                next_question = get_next_question_data(cursor, pk, user_id, current_question_number, answer_option=selected_option)
                if next_question is None:
                    print('POST - СЛЕДУЮЩЕГО ВОПРОСА НЕТ')
                    was_there_any_question = check_empty_survey(cursor, pk)
                    if was_there_any_question > 0:
                        print('POST - В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                        return redirect('statistics_page', pk=pk)
                        # url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
                    elif was_there_any_question == 0:
                        print('POST - В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                        return redirect('empty_survey')
                    else:
                        error_message = "ошибка проверки опроса"
                        return HttpResponseServerError(error_message)

                print(f"POST СЛЕДУЮЩИЙ ВОПРОС ИЗ ОПРОСА {pk}, ВОПРОС НОМЕР {next_question[0]}, ДАННЫЕ: {next_question}")
                print('POST - СОЗДАНИЕ ВТОРОЙ ФОРМЫ POST')

                options = []

                for i in range(11, 8, -1):
                    if len(next_question[i]) != 0:
                        print(f'opening_question[{i}] - {next_question[i]}')
                        options.extend([
                            (str(j + 1), answer) for j, answer in enumerate(next_question[8:i+1])
                        ])
                        print('Options:', options)
                        break

                print('POST - Options outside the loop:', options)

                form = QuestionResponseForm(request.POST, options=options)
                next_question_length = len(next_question)

                print(f'POST -Длина следующего вопроса - {next_question_length}')
                next_question_number = next_question[0]
                context = {
                    'question_data': {
                        'survey_id': next_question[1],
                        'question_id': next_question[0],
                        'title': next_question[2],
                        'answered_quantity': next_question[3],
                        'answered_rating': next_question[4],
                        'question_text': next_question[5],
                        'created_on': next_question[6],
                        'redacted': next_question[7],
                        'answer_option_1': next_question[8],
                        'answer_option_2': next_question[9] if next_question_length >= 10 else None,
                        'answer_option_3': next_question[10] if next_question_length >= 11 else None,
                        'answer_option_4': next_question[11] if next_question_length >= 12 else None,
                    },
                    'form': form,
                    'survey_id': pk,
                    'question_number': next_question_number,
                }
                print(f"***POST - КОНТЕКСТ ПЕРЕХОДА НА СЛЕДУЮЩИЙ ВОПРОС - |||{context} ||| КОНЕЦ КОНТЕКСТА")
                # return render(request, 'survey/survey_detail.html', context)
                (print(f'! POST - ПЕРЕДАВАЕМЫЙ СЛЕДУЮЩИЙ ВОПРОС - {next_question_number}'))
                url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
                return HttpResponseRedirect(url)
            else:
                print('POST - СЛЕДУЮЩЕГО ВОПРОСА НЕТ')
                was_there_any_question = check_empty_survey(cursor, pk)
                if was_there_any_question > 0:
                    print('POST - В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                    return redirect('statistics_page', pk=pk)
                    # url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
                elif was_there_any_question == 0:
                    print('POST - В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                    return redirect('empty_survey')
                else:
                    error_message = "ошибка проверки опроса"
                    return HttpResponseServerError(error_message)
        else:
            error_message = "POST - 111 POST - ФОРМА НЕВАЛИДНА"
            print(form.errors)
            return HttpResponseServerError(error_message)
            return render(request, 'survey/survey_detail.html', context)
    else:
        print('VVV POST - В МЕТОД POST БЫЛ ПЕРЕДАН НОМЕР ВОПРОСА - НЕПРОВЕРЕННЫЙ ФУНКЦИОНАЛ! VVV')
        passed_question = get_passed_question(cursor, pk, user_id, question_number)
        passed_question_length = len(passed_question)
        print('VVV POST - СОЗДАНИЕ ПЕРЕДАННОЙ ФОРМЫ POST')
        options = []

        for i in range(11, 8, -1):
            if len(passed_question[i]) != 0:
                print(f'VVV POST - opening_question[{i}] - {passed_question[i]}')
                options.extend([
                    (str(j + 1), answer) for j, answer in enumerate(passed_question[8:i+1])
                ])
                print('VVV POST - Options:', options)
                break

        print('VVV POST - Options outside the loop:', options)

        form = QuestionResponseForm(request.POST, options=options)

        print(f'VVV POST - ДЛИНА ПЕРЕДАННОГО ВОПРОСА - {passed_question_length}')
        context = {
            'question_data': {
                'survey_id': passed_question[1],
                'question_id': passed_question[0],
                'title': passed_question[2],
                'answered_quantity': passed_question[3],
                'answered_rating': passed_question[4],
                'question_text': passed_question[5],
                'created_on': passed_question[6],
                'redacted': passed_question[7],
                'answer_option_1': passed_question[8],
                'answer_option_2': passed_question[9] if passed_question_length >= 10 else None,
                'answer_option_3': passed_question[10] if passed_question_length >= 11 else None,
                'answer_option_4': passed_question[11] if passed_question_length >= 12 else None,
            },
            'form': form,
        }

        if form.is_valid():
            print(f'VVV POST ЗАФИКСИРОВАН ОТВЕТ, form.cleaned_data - {form.cleaned_data}')
            print(f"VVVPOST - КОНТЕКСТ ПЕРЕХОДА НА СЛЕДУЮЩИЙ ВОПРОС - |||{context} ||| КОНЕЦ КОНТЕКСТА")
            if 'selected_option' in form.cleaned_data:
                selected_option = form.cleaned_data['selected_option']
            else:
                error_message = "VVV POST - 222 POST - ФОРМА НЕВАЛИДНА"
                print(form.errors)
                return HttpResponseServerError(error_message)
            cursor.execute('''
                INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                VALUES (%s, %s, %s, %s)
            ''', [request.user.id, passed_question[0], int(selected_option), datetime.now()])

            connection.commit()
        next_question = get_next_question_data(cursor, pk, user_id, current_question_number=question_number, answer_option=selected_option)
        if next_question:
            next_question_number = next_question[0]
            (print(f'!VVV POST -  - ПЕРЕДАВАЕМЫЙ СЛЕДУЮЩИЙ ВОПРОС - {next_question_number}'))
            url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
            return HttpResponseRedirect(url)
        else:
            print('VVV POST -  - СЛЕДУЮЩЕГО ВОПРОСА НЕТ')
            was_there_any_question = check_empty_survey(cursor, pk)
            if was_there_any_question > 0:
                print('VVV POST -  - В ОПРОСЕ ВОПРОСЫ БЫЛИ')
                return redirect('statistics_page', pk=pk)
            elif was_there_any_question == 0:
                print('VVV POST -  - В ОПРОСЕ ВОПРОСОВ НЕ БЫЛО')
                return redirect('empty_survey')
            else:
                error_message = "VVV POST -  - ошибка проверки опроса"
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
    SELECT q.*
    FROM questions q
    WHERE q.survey_id = {pk}
    AND q.id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id = {user_id})
    AND (
    q.id NOT IN (SELECT child_question_id FROM question_relations WHERE parent_question_id IS NOT NULL)
    OR
    q.id IN (
    SELECT qr.child_question_id
    FROM question_relations qr
    JOIN user_answers ua ON qr.parent_question_id = ua.question_id
    WHERE ua.auth_user_id = {user_id}
    AND (
    qr.response_condition = ua.selected_option::VARCHAR
    OR
    qr.response_condition::INTEGER = ua.selected_option
    )
    )
    );
    '''
    cursor.execute(get_opening_question_query)
    opening_question = cursor.fetchone()
    print(f'???ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ - {opening_question}')
    simple_next_question_result_type = type(opening_question)
    print(f'???ТИП ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ = {simple_next_question_result_type}')
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
        print("check_next_question_existance - NONE")
        return False
    else:
        print("check_next_question_existance - PASSED")
        print(simple_check_answer[0])
        return True


def get_next_question_data(cursor, pk, user_id, current_question_number, answer_option):
    print('!!!ПРОВЕРКА НАЛИЧИЯ ДОЧЕРНЕГО ВОПРОСА')
    check_child_question_existence = f'''SELECT * FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}' '''
    cursor.execute(check_child_question_existence)
    check_child_question_existence_result = cursor.fetchone()
    if check_child_question_existence_result is None:
        print('!!!ДОЧЕРНЕГО ВОПРОСА НЕТ')
        simple_next_question_query = f'''SELECT * FROM questions WHERE survey_id='{pk}' AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id='{user_id}') AND id NOT IN (SELECT child_question_id FROM question_relations) '''
        cursor.execute(simple_next_question_query)
        simple_next_question_result = cursor.fetchone()
        print(f'!!!ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ - {simple_next_question_result}')
        simple_next_question_result_type = type(simple_next_question_result)
        print(f'!!!ТИП ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ = {simple_next_question_result_type}')
        return simple_next_question_result
    else:
        print('!!!ДОЧЕРНИЙ ВОПРОС ЕСТЬ')
        check_child_question_was_not_answered = f'''SELECT * FROM user_answers WHERE auth_user_id={user_id} AND question_id IN (SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}') '''
        cursor.execute(check_child_question_was_not_answered)
        check_child_question_was_not_answered_result = cursor.fetchone()

        if check_child_question_was_not_answered_result is None:
            print('!!!ДОЧЕРНИЙ ВОПРОС БЕЗ ОТВЕТА, ПЕРЕХОДИМ К НЕМУ')
            child_question = f'''SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition='{answer_option}' '''
            cursor.execute(child_question)
            child_question_result = cursor.fetchone()
            print(f'!!!ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ - {child_question_result}')
            child_question_result_type = type(child_question_result)
            print(f'!!!ТИП ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ = {child_question_result_type}')
            child_question_id = child_question_result[0]
            next_child_question_query = f'''SELECT * FROM questions WHERE id='{child_question_id}' '''
            cursor.execute(next_child_question_query)
            child_question_result = cursor.fetchone()
            return child_question_result
        else:
            print('!!!ДОЧЕРНИЙ ВОПРОС БЫЛ ОТВЕЧЕН, БЕРЕМ СЛЕДУЮЩИЙ ОБЫЧНЫЙ')
            simple_next_question = f'''SELECT id FROM questions WHERE survey_id='{pk}' AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id='{user_id}') AND id NOT IN (SELECT child_question_id FROM question_relations)'''
            cursor.execute(simple_next_question)
            simple_next_question_result = cursor.fetchone()
            return simple_next_question_result


def get_passed_question(cursor, pk, user_id, passed_question_number):
    get_passed_question_query = f'''
        SELECT * FROM questions
        WHERE survey_id={pk} AND id={passed_question_number}
    '''
    cursor.execute(get_passed_question_query)
    passed_question = cursor.fetchone()
    print(f'XXX ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ - {passed_question}')
    passed_question_result_type = type(passed_question)
    print(f'XXX ТИП ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ = {passed_question_result_type}')
    return passed_question


def statistics_detail(request, pk):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    context = {'pk': pk, 'user_id': user_id}
    return render(request, 'survey/statistics.html', context=context)
    # url = reverse('statistics_page', kwargs={'pk': pk, 'user_id': user_id})
    # return HttpResponseRedirect(url)


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
