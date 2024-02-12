import os
from pathlib import Path
from django.contrib.auth.hashers import make_password
import psycopg2
from django.conf import settings
from psycopg2 import sql


current_directory = Path(__file__).resolve().parent

project_directory = current_directory.parent.parent

settings_file = project_directory / 'questionnaire' / 'questionnaire' / 'settings.py'

os.environ["DJANGO_SETTINGS_MODULE"] = "questionnaire.questionnaire.settings"

settings.configure()

if settings_file.is_file():
    print(f"Файл settings.py найден: {settings_file}")
else:
    print("Файл settings.py не найден. Убедитесь, что путь к файлу верен.")


connection_params = {
    'dbname': 'questionnaire_postgres',
    'user': 'postgres',
    'password': 'root',
    'host': '127.0.0.1',
    'port': '5433'
}

test_user_one_name = 'test_user_one'
test_user_one_password = 'testone1111'
test_user_one_email = 'test_user_one@mail.ru'
test_user_one_first_name = 'test_user_one'
test_user_one_last_name = 'test_user_one'
test_user_one_hashed_password = make_password(test_user_one_password)

params_one = (test_user_one_name, test_user_one_hashed_password, test_user_one_email, test_user_one_first_name, test_user_one_last_name)

test_user_two_name = 'test_user_two'
test_user_two_password = 'testtwo2222'
test_user_two_email = 'test_user_two@mail.ru'
test_user_two_first_name = 'test_user_two'
test_user_two_last_name = 'test_user_two'
test_user_two_hashed_password = make_password(test_user_two_password)

create_test_user_two_query = sql.SQL('''
    INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
''')
params_two = (test_user_two_name, test_user_two_hashed_password, test_user_two_email, test_user_two_first_name, test_user_two_last_name)

test_user_three_name = 'test_user_three'
test_user_three_password = 'testthree3333'
test_user_three_email = 'test_user_three@mail.ru'
test_user_three_first_name = 'test_user_three'
test_user_three_last_name = 'test_user_three'
test_user_three_hashed_password = make_password(test_user_three_password)

create_test_user_three_query = sql.SQL('''
    INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
''')
params_three = (test_user_three_name, test_user_three_hashed_password, test_user_three_email, test_user_three_first_name, test_user_three_last_name)

test_user_four_name = 'test_user_four'
test_user_four_password = 'testfour4444'
test_user_four_email = 'test_user_four@mail.ru'
test_user_four_first_name = 'test_user_four'
test_user_four_last_name = 'test_user_four'
test_user_four_hashed_password = make_password(test_user_four_password)

create_test_user_four_query = sql.SQL('''
    INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
''')
params_four = (test_user_four_name, test_user_four_hashed_password, test_user_four_email, test_user_four_first_name, test_user_four_last_name)

create_test_user_query = sql.SQL('''
    INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
''')

add_test_data_query_one = sql.SQL('''
INSERT INTO user_answers (auth_user_id,question_id,selected_option,response_date) VALUES
	 (2,14,2,'2024-02-11 17:54:16.360246'),
	 (2,11,2,'2024-02-11 17:54:20.214055'),
	 (2,12,3,'2024-02-11 17:54:22.141947'),
	 (2,13,4,'2024-02-11 17:54:23.334487'),
	 (2,1,2,'2024-02-11 17:54:26.393694'),
	 (2,3,2,'2024-02-11 17:54:27.567077'),
	 (2,7,1,'2024-02-11 17:54:28.666396'),
	 (2,10,1,'2024-02-11 17:54:30.018367'),
	 (3,1,4,'2024-02-11 17:55:42.216104'),
	 (3,5,1,'2024-02-11 17:55:45.083313');
''')

add_test_data_query_two = sql.SQL('''
INSERT INTO user_answers (auth_user_id,question_id,selected_option,response_date) VALUES
	 (3,8,2,'2024-02-11 17:55:47.191726'),
	 (3,11,1,'2024-02-11 17:55:51.637001'),
	 (3,12,4,'2024-02-11 17:55:53.00419'),
	 (3,13,2,'2024-02-11 17:55:54.082258'),
	 (3,14,2,'2024-02-11 17:55:57.729615'),
	 (4,1,1,'2024-02-11 17:56:53.522346'),
	 (4,2,1,'2024-02-11 17:56:55.083828'),
	 (4,6,1,'2024-02-11 17:56:56.899722'),
	 (4,11,2,'2024-02-11 17:57:00.419385'),
	 (4,12,1,'2024-02-11 17:57:02.723296');
''')

add_test_data_query_three = sql.SQL('''
INSERT INTO user_answers (auth_user_id,question_id,selected_option,response_date) VALUES
	 (4,13,4,'2024-02-11 17:57:03.726452'),
	 (4,14,1,'2024-02-11 17:57:06.131054'),
	 (5,11,1,'2024-02-11 17:57:33.343342'),
	 (5,1,1,'2024-02-11 17:57:42.799943'),
	 (5,2,1,'2024-02-11 17:58:56.570219');
''')

try:
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    print("создание тестовых пользователей...")
    cursor.execute(create_test_user_query, params_one)
    print(f"Пользователь '{test_user_one_name}' успешно создан в таблице auth_user.")
    cursor.execute(create_test_user_query, params_two)
    print(f"Пользователь '{test_user_two_name}' успешно создан в таблице auth_user.")
    cursor.execute(create_test_user_query, params_three)
    print(f"Пользователь '{test_user_three_name}' успешно создан в таблице auth_user.")
    cursor.execute(create_test_user_query, params_four)
    print(f"Пользователь '{test_user_four_name}' успешно создан в таблице auth_user.")
    cursor.execute(add_test_data_query_one)
    print("Первая часть тестовых ответов добавлена")
    cursor.execute(add_test_data_query_two)
    print("Вторая часть тестовых ответов добавлена")
    cursor.execute(add_test_data_query_three)
    print("Третья часть тестовых ответов добавлена")
    connection.commit()

except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
