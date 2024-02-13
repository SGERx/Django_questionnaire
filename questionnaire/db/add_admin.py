import os
from dotenv import load_dotenv
from pathlib import Path
import psycopg2
from django.contrib.auth.hashers import make_password
from django.conf import settings
from psycopg2 import sql


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


def configure_django_settings():
    current_directory = Path(__file__).resolve().parent
    project_directory = current_directory.parent.parent
    settings_file = project_directory / 'questionnaire' / 'questionnaire' / 'settings.py'

    os.environ["DJANGO_SETTINGS_MODULE"] = "questionnaire.questionnaire.settings"
    settings.configure()

    if settings_file.is_file():
        print(f"Файл settings.py найден: {settings_file}")
    else:
        print("Файл settings.py не найден. Убедитесь, что путь к файлу верен.")


def get_admin_credentials():
    default_values = input("Использовать значения по умолчанию для создания администратора Django? [y/n] ")
    if default_values.upper() == 'Y':
        return 'admin', 'admin', 'admin@admin.com', 'admin', 'admin'
    elif default_values.upper() == 'N':
        admin_name = input("Введите юзернейм для администратора Django: ")
        password = input("Введите пароль для администратора Django: ")
        email = input("Введите email администратора Django: ")
        first_name = input("Введите имя администратора Django: ")
        last_name = input("Введите фамилию администратора Django: ")
        return admin_name, password, email, first_name, last_name


def create_admin_in_database(admin_name, password, email, first_name, last_name):
    hashed_password = make_password(password)

    connection_params = get_connection_params_from_env()

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


if __name__ == "__main__":
    load_environment_variables()
    configure_django_settings()
    admin_name, password, email, first_name, last_name = get_admin_credentials()
    create_admin_in_database(admin_name, password, email, first_name, last_name)
