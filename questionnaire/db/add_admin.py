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


default_values = input("Использовать значения по умолчанию для создания администратора Django? [y/n] ")
if default_values.upper() == 'Y':
    print("логин - admin, пароль - admin")
    admin_name = 'admin'
    password = 'admin'
    email = 'admin@admin.com'
    first_name = 'admin'
    last_name = 'admin'
elif default_values.upper() == 'N':
    admin_name = input("Введите юзернейм для администратора Django: ")
    password = input("Введите пароль для администратора Django: ")
    email = input("Введите email администратора Django: ")
    first_name = input("Введите имя администратора Django: ")
    last_name = input("Введите фамилию администратора Django: ")

hashed_password = make_password(password)

connection_params = {
    'dbname': 'questionnaire_postgres',
    'user': 'postgres',
    'password': 'root',
    'host': '127.0.0.1',
    'port': '5433'
}

create_admin_query = sql.SQL('''
    INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, TRUE, NOW());
''')

params = (admin_name, hashed_password, email, first_name, last_name)


try:
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    cursor.execute(create_admin_query, params)
    connection.commit()
    print("Пользователь 'admin' успешно создан в таблице auth_user.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
