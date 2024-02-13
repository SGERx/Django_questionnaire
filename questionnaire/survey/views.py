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
from dotenv import load_dotenv
from pathlib import Path
import os


def load_environment_variables():
    env_path = Path(__file__).resolve().parent.parent / '.env'
    print(f"Путь к файлу .env: {env_path}")
    print(f"Содержимое .env: {open(env_path).read()}")
    load_dotenv(dotenv_path=env_path)


def get_connection_params_from_env():
    return {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }


connection_params = get_connection_params_from_env()


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
        return survey_detail_get(request, pk, question_number)
    elif request.method == 'POST':
        return survey_detail_post(request, pk, question_number)
    else:
        return HttpResponseServerError("Invalid HTTP method")


@login_required
@require_GET
def survey_detail_get(request, pk, question_number=None):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    if question_number is None:
        opening_question = get_opening_question(cursor, pk, user_id)
        if opening_question:
            opening_question_length = len(opening_question)
            options = []

            for i in range(11, 8, -1):
                if len(opening_question[i]) != 0:
                    options.extend([
                        (str(j + 1), answer) for j, answer in enumerate(opening_question[8:i+1])
                    ])
                    break

            form = QuestionResponseForm(options=options)

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
            was_there_any_question = check_empty_survey(cursor, pk)

            if was_there_any_question > 0:
                return redirect('statistics_page', pk=pk)
            elif was_there_any_question == 0:
                return redirect('empty_survey')
            else:
                error_message = "ошибка проверки опроса"
                return HttpResponseServerError(error_message)
    else:
        passed_question = get_passed_question(cursor, pk, user_id, question_number)
        passed_question_length = len(passed_question)
        options = []

        if len(passed_question[9]) > 0:
            for i in range(11, 8, -1):
                if len(passed_question[i]) != 0:
                    options.extend([
                        (str(j + 1), answer) for j, answer in enumerate(passed_question[8:i+1])
                    ])
                    break
        else:
            options = [('1', passed_question[8])]

        form = QuestionResponseForm(options=options)

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
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    if question_number is None:
        opening_question = get_opening_question(cursor, pk, user_id)
        next_question_length = len(opening_question)
        options = []

        for i in range(11, 8, -1):
            if len(opening_question[i]) != 0:
                options.extend([
                    (str(j + 1), answer) for j, answer in enumerate(opening_question[8:i+1])
                ])
                break

        form = QuestionResponseForm(request.POST, options=options)
        if form.is_valid():

            selected_option = form.cleaned_data['selected_option']
            cursor.execute('''
                INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                VALUES (%s, %s, %s, %s)
            ''', [request.user.id, opening_question[0], int(selected_option), datetime.now()])

            connection.commit()
            current_question_number = opening_question[0]
            next_question_exists = check_next_question_existance(cursor, pk, user_id, current_question_number)
            if next_question_exists is not None:
                next_question = get_next_question_data(cursor, pk, user_id, current_question_number, answer_option=selected_option)
                if next_question is None:
                    was_there_any_question = check_empty_survey(cursor, pk)
                    if was_there_any_question > 0:
                        return redirect('statistics_page', pk=pk)
                    elif was_there_any_question == 0:
                        return redirect('empty_survey')
                    else:
                        error_message = "ошибка проверки опроса"
                        return HttpResponseServerError(error_message)

                options = []

                for i in range(11, 8, -1):
                    if len(next_question[i]) != 0:
                        options.extend([
                            (str(j + 1), answer) for j, answer in enumerate(next_question[8:i+1])
                        ])
                        break

                form = QuestionResponseForm(request.POST, options=options)
                next_question_length = len(next_question)

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

                url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
                return HttpResponseRedirect(url)
            else:
                was_there_any_question = check_empty_survey(cursor, pk)
                if was_there_any_question > 0:
                    return redirect('statistics_page', pk=pk)
                elif was_there_any_question == 0:
                    return redirect('empty_survey')
                else:
                    error_message = "ошибка проверки опроса"
                    return HttpResponseServerError(error_message)
        else:
            error_message = "ФОРМА НЕВАЛИДНА"
            return HttpResponseServerError(error_message)
    else:
        passed_question = get_passed_question(cursor, pk, user_id, question_number)
        passed_question_length = len(passed_question)
        options = []

        for i in range(11, 8, -1):
            if len(passed_question[i]) != 0:
                options.extend([
                    (str(j + 1), answer) for j, answer in enumerate(passed_question[8:i+1])
                ])
                break

        form = QuestionResponseForm(request.POST, options=options)

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
            if 'selected_option' in form.cleaned_data:
                selected_option = form.cleaned_data['selected_option']
            else:
                error_message = "ФОРМА НЕВАЛИДНА"
                return HttpResponseServerError(error_message)
            cursor.execute('''
                INSERT INTO user_answers (auth_user_id, question_id, selected_option, response_date)
                VALUES (%s, %s, %s, %s)
            ''', [request.user.id, passed_question[0], int(selected_option), datetime.now()])

            connection.commit()
        next_question = get_next_question_data(cursor, pk, user_id, current_question_number=question_number, answer_option=selected_option)
        if next_question:
            next_question_number = next_question[0]
            url = reverse('survey_detail', kwargs={'pk': pk, 'question_number': next_question_number})
            return HttpResponseRedirect(url)
        else:
            was_there_any_question = check_empty_survey(cursor, pk)
            if was_there_any_question > 0:
                return redirect('statistics_page', pk=pk)
            elif was_there_any_question == 0:
                return redirect('empty_survey')
            else:
                error_message = "ошибка проверки опроса"
                return HttpResponseServerError(error_message)


def check_empty_survey(cursor, pk):
    check_empty_survey_query = f'''SELECT COUNT(*) FROM questions WHERE survey_id={pk}'''
    cursor.execute(check_empty_survey_query)
    survey_check = cursor.fetchone()
    survey_check_result = survey_check[0]
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
        return False
    else:
        return True


def get_next_question_data(cursor, pk, user_id, current_question_number, answer_option):
    check_child_question_existence = f'''SELECT * FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}' '''
    cursor.execute(check_child_question_existence)
    check_child_question_existence_result = cursor.fetchone()
    if check_child_question_existence_result is None:
        simple_next_question_query = f'''SELECT * FROM questions WHERE survey_id='{pk}' AND id NOT IN (SELECT question_id FROM user_answers WHERE auth_user_id='{user_id}') AND id NOT IN (SELECT child_question_id FROM question_relations) '''
        cursor.execute(simple_next_question_query)
        simple_next_question_result = cursor.fetchone()
        simple_next_question_result_type = type(simple_next_question_result)
        return simple_next_question_result
    else:
        check_child_question_was_not_answered = f'''SELECT * FROM user_answers WHERE auth_user_id={user_id} AND question_id IN (SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition = '{answer_option}') '''
        cursor.execute(check_child_question_was_not_answered)
        check_child_question_was_not_answered_result = cursor.fetchone()

        if check_child_question_was_not_answered_result is None:
            child_question = f'''SELECT child_question_id FROM question_relations WHERE parent_question_id='{current_question_number}' AND response_condition='{answer_option}' '''
            cursor.execute(child_question)
            child_question_result = cursor.fetchone()
            child_question_result_type = type(child_question_result)
            child_question_id = child_question_result[0]
            next_child_question_query = f'''SELECT * FROM questions WHERE id='{child_question_id}' '''
            cursor.execute(next_child_question_query)
            child_question_result = cursor.fetchone()
            return child_question_result
        else:
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
    passed_question_result_type = type(passed_question)
    return passed_question


def statistics_detail(request, pk):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    user_id = request.user.id
    participants_quantity_query = f'''SELECT COUNT(DISTINCT auth_user_id) from user_answers WHERE question_id IN (SELECT id FROM questions WHERE survey_id={pk});'''
    cursor.execute(participants_quantity_query)
    participants_quantity = cursor.fetchone()
    participants_quantity_transmission = participants_quantity[0]

    survey_questions_quantity_query = f'''SELECT DISTINCT(id) FROM questions WHERE survey_id={pk}'''
    cursor.execute(survey_questions_quantity_query)
    questions_ids = cursor.fetchall()
    answered_question_transmission = []
    answered_question_storage = []
    for i in range(0, len(questions_ids)):
        answered_questions_query = f'''SELECT COUNT(DISTINCT auth_user_id) from user_answers WHERE question_id={questions_ids[i][0]};'''
        cursor.execute(answered_questions_query)
        answered_questions_quantity = cursor.fetchone()
        answered_question_storage.append(answered_questions_quantity[0])
        answered_questions_data = f'Количество ответивших на вопрос {i+1} - {answered_questions_quantity[0]}'
        answered_question_transmission.append(answered_questions_data)

    answered_ratings_transmission = []
    for i in range(0, len(questions_ids)):
        if answered_question_storage[i] > 0:
            answered_ratings_data = f'Доля ответивших на вопрос {i+1} - {float(answered_question_storage[i]/participants_quantity[0])*100}%'
        else:
            answered_ratings_data = f'Доля ответивших на вопрос {i+1} - 0%'
        answered_ratings_transmission.append(answered_ratings_data)

    questions_by_ratings_query = f'''SELECT question_id, COUNT(DISTINCT auth_user_id) AS respondents_count
    FROM user_answers
    WHERE question_id IN (SELECT id FROM questions WHERE survey_id = {pk})
    GROUP BY question_id
    ORDER BY respondents_count DESC'''
    cursor.execute(questions_by_ratings_query)
    questions_by_ratings_quantity = cursor.fetchall()
    questions_by_ratings = []

    place_counter = 0
    for i in range(0, len(questions_by_ratings_quantity)):
        if len(questions_by_ratings) == 0:
            rating_record = f'Место 1 - вопрос с ID {questions_by_ratings_quantity[i][0]}, количество ответивших - {questions_by_ratings_quantity[i][1]}'
            questions_by_ratings.append(rating_record)
            place_counter = place_counter+1
        else:
            if questions_by_ratings_quantity[i][1] == questions_by_ratings_quantity[i-1][1]:
                rating_record = f'Место {place_counter} - вопрос с ID {questions_by_ratings_quantity[i][0]}, количество ответивших - {questions_by_ratings_quantity[i][1]}'
                questions_by_ratings.append(rating_record)
            elif questions_by_ratings_quantity[i][1] < questions_by_ratings_quantity[i-1][1]:
                place_counter = place_counter+1
                rating_record = f'Место {place_counter} - вопрос с ID {questions_by_ratings_quantity[i][0]}, количество ответивших - {questions_by_ratings_quantity[i][1]}'
                questions_by_ratings.append(rating_record)

    questions_by_ratings_transmission = questions_by_ratings

    questions_answers_and_answer_quantity_query = f'''SELECT question_id, selected_option, COUNT(auth_user_id) AS response_count
    FROM user_answers
    WHERE question_id IN (SELECT id FROM questions WHERE survey_id = {pk})
    GROUP BY question_id, selected_option;'''
    cursor.execute(questions_answers_and_answer_quantity_query)
    answers_data = cursor.fetchall()
    question_quantity_in_survey_query = f'''SELECT id, answer_option_1, answer_option_2, answer_option_3, answer_option_4 FROM questions WHERE survey_id = {pk};'''
    cursor.execute(question_quantity_in_survey_query)
    questions_data = cursor.fetchall()
    gathered_answered_question_id = []

    for k in range(0, len(answers_data)):
        if answers_data[k][0] not in gathered_answered_question_id: 
            gathered_answered_question_id.append(answers_data[k][0])

    total_answers_for_question_dict_counter = {}
    for g in range(0, len(questions_data)):
        total_answers_for_question_dict_counter[questions_data[g][0]] = 0
    for g in range(0, len(questions_data)):
        if questions_data[g][0] in gathered_answered_question_id:
            for h in range(0, len(answers_data)):
                if answers_data[h][0] == questions_data[g][0]:
                    total_answers_for_question_dict_counter[questions_data[g][0]] = total_answers_for_question_dict_counter[questions_data[g][0]] + answers_data[h][2]

    transmission_data = []
    for i in range(0, len(questions_data)):
        question_options_counter = [0, 0, 0, 0]
        if questions_data[i][4]:
            if questions_data[i][0] in gathered_answered_question_id:
                for b in range(0, len(answers_data)):
                    if answers_data[b][0] != questions_data[i][0]:
                        continue
                    else:
                        if answers_data[b][1] == 1:
                            question_options_counter[0] = question_options_counter[0] + answers_data[b][2]
                        if answers_data[b][1] == 2:
                            question_options_counter[1] = question_options_counter[1] + answers_data[b][2]
                        if answers_data[b][1] == 3:
                            question_options_counter[2] = question_options_counter[2] + answers_data[b][2]
                        if answers_data[b][1] == 4:
                            question_options_counter[3] = question_options_counter[3] + answers_data[b][2]
            stats_data_one = f"Вопрос {i+1} - ответ 1 - вариант '{questions_data[i][1]}' - количество выборов - {question_options_counter[0]}, доля от общих ответов на вопрос - {int(question_options_counter[0]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            stats_data_two = f"Вопрос {i+1} - ответ 2 - вариант '{questions_data[i][2]}' - количество выборов - {question_options_counter[1]}, доля от общих ответов на вопрос - {int(question_options_counter[1]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            stats_data_three = f"Вопрос {i+1} - ответ 3 - вариант '{questions_data[i][3]}' - количество выборов - {question_options_counter[2]}, доля от общих ответов на вопрос - {int(question_options_counter[2]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            stats_data_four = f"Вопрос {i+1} - ответ 4 - вариант '{questions_data[i][4]}' - количество выборов - {question_options_counter[3]}, доля от общих ответов на вопрос - {int(question_options_counter[3]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            transmission_data.append(stats_data_one)
            transmission_data.append(stats_data_two)
            transmission_data.append(stats_data_three)
            transmission_data.append(stats_data_four)
        elif questions_data[i][3]:
            if questions_data[i][0] in gathered_answered_question_id:
                for b in range(0, len(answers_data)):
                    if answers_data[b][0] != questions_data[i][0]:
                        continue
                    else:
                        if answers_data[b][1] == 1:
                            question_options_counter[0] = question_options_counter[0] + answers_data[b][2]
                        if answers_data[b][1] == 2:
                            question_options_counter[1] = question_options_counter[1] + answers_data[b][2]
                        if answers_data[b][1] == 3:
                            question_options_counter[2] = question_options_counter[2] + answers_data[b][2]
                        if answers_data[b][1] == 4:
                            question_options_counter[3] = question_options_counter[3] + answers_data[b][2]
            stats_data_one = f"Вопрос {i+1} - ответ 1 - вариант '{questions_data[i][1]}' - количество выборов - {question_options_counter[0]}, доля от общих ответов на вопрос - {int(question_options_counter[0]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            stats_data_two = f"Вопрос {i+1} - ответ 2 - вариант '{questions_data[i][2]}' - количество выборов - {question_options_counter[1]}, доля от общих ответов на вопрос - {int(question_options_counter[1]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            stats_data_three = f"Вопрос {i+1} - ответ 3 - вариант '{questions_data[i][3]}' - количество выборов - {question_options_counter[2]}, доля от общих ответов на вопрос - {int(question_options_counter[2]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
            transmission_data.append(stats_data_one)
            transmission_data.append(stats_data_two)
            transmission_data.append(stats_data_three)
        else:
            if questions_data[i][0] in gathered_answered_question_id:
                for b in range(0, len(answers_data)):
                    if answers_data[b][0] != questions_data[i][0]:
                        continue
                    else:
                        if answers_data[b][1] == 1:
                            question_options_counter[0] = question_options_counter[0] + answers_data[b][2]
                        if answers_data[b][1] == 2:
                            question_options_counter[1] = question_options_counter[1] + answers_data[b][2]
                        if answers_data[b][1] == 3:
                            question_options_counter[2] = question_options_counter[2] + answers_data[b][2]
                        if answers_data[b][1] == 4:
                            question_options_counter[3] = question_options_counter[3] + answers_data[b][2]
                stats_data_one = f"Вопрос {i+1} - ответ 1 - вариант '{questions_data[i][1]}' - количество выборов - {question_options_counter[0]}, доля от общих ответов на вопрос - {int(question_options_counter[0]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
                stats_data_two = f"Вопрос {i+1} - ответ 2 - вариант '{questions_data[i][2]}' - количество выборов - {question_options_counter[1]}, доля от общих ответов на вопрос - {int(question_options_counter[1]/total_answers_for_question_dict_counter[questions_data[i][0]]*100)}%"
                transmission_data.append(stats_data_one)
                transmission_data.append(stats_data_two)
            else:
                stats_data_one = f"Вопрос {i+1} - ответ 1 - вариант '{questions_data[i][1]}' - количество выборов - 0, доля от общих ответов на вопрос - 0%"
                stats_data_two = f"Вопрос {i+1} - ответ 2 - вариант '{questions_data[i][2]}' - количество выборов - 0, доля от общих ответов на вопрос - 0%"
                transmission_data.append(stats_data_one)
                transmission_data.append(stats_data_two)
    questions_answers_and_answer_quantity_transmission  = transmission_data
    context = {
        'pk': pk,
        'user_id': user_id,
        'participants_quantity': participants_quantity_transmission,
        'answered_question': answered_question_transmission,
        'answered_ratings': answered_ratings_transmission,
        'questions_by_ratings': questions_by_ratings_transmission,
        'questions_answers_and_answer_percentage': questions_answers_and_answer_quantity_transmission
        }
    return render(request, 'survey/statistics.html', context=context)


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
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
