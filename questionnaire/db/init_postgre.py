from django.http import HttpResponse
import psycopg2
from psycopg2 import sql
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

file_path_tables = os.path.join(os.path.dirname(__file__),
                                'create_tables.sql')
database_name = 'questionnaire_postgres'


def execute_db_creation(connection_parameters, database_name):
    try:
        connection_parameters.pop('dbname', None)
        connection = psycopg2.connect(**connection_parameters)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()
        cursor.execute("ROLLBACK;")

        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(database_name)))

        connection.commit()
    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")

    finally:
        if connection:
            connection.close()


def execute_tables_creation(connection_parameters):

    connection = psycopg2.connect(**connection_parameters)
    cursor = connection.cursor()

    try:
        create_users_query = '''CREATE TABLE IF NOT EXISTS questionnaire_users(
        id serial PRIMARY KEY,
        username VARCHAR (30) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        password_salt VARCHAR(255) NOT NULL,
        email VARCHAR (30) UNIQUE NOT NULL,
        created_on TIMESTAMP NOT NULL,
        last_login TIMESTAMP
        ); '''
        cursor.execute(create_users_query)

        create_poll_query = '''CREATE TABLE IF NOT EXISTS poll(
        id serial PRIMARY KEY,
        title VARCHAR (50) UNIQUE NOT NULL,
        description TEXT,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP
        );'''
        cursor.execute(create_poll_query)

        create_question_query = '''CREATE TABLE IF NOT EXISTS question(
        id serial PRIMARY KEY,
        poll_id INT NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP,
        CONSTRAINT fk_poll FOREIGN KEY(poll_id) REFERENCES poll(id)
        );'''
        cursor.execute(create_question_query)

        create_answer_query = '''CREATE TABLE IF NOT EXISTS answer (
        id serial PRIMARY KEY,
        questionnaire_users_id INT NOT NULL,
        question_id INT NOT NULL,
        response_text TEXT,
        response_date TIMESTAMP NOT NULL,
        CONSTRAINT fk_questionnaire_users FOREIGN KEY (questionnaire_users_id) REFERENCES questionnaire_users (id),
        CONSTRAINT fk_question FOREIGN KEY (question_id) REFERENCES question (id)
        );'''
        cursor.execute(create_answer_query)

        connection.commit()

    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    finally:
        connection.close()


def execute_index_creation(connection_parameters):

    connection = psycopg2.connect(**connection_parameters)
    cursor = connection.cursor()

    try:

        create_users_index_username = '''CREATE INDEX IF NOT EXISTS idx_questionnaire_users_username ON questionnaire_users(username);'''
        cursor.execute(create_users_index_username)
        create_users_index_email = '''CREATE INDEX IF NOT EXISTS idx_questionnaire_users_email ON questionnaire_users(email);'''
        cursor.execute(create_users_index_email)
        create_users_index_last_login = '''CREATE INDEX IF NOT EXISTS idx_questionnaire_users_last_login ON questionnaire_users(last_login);'''
        cursor.execute(create_users_index_last_login)

        create_poll_index_title = '''CREATE INDEX IF NOT EXISTS idx_poll_title ON poll(title);'''
        cursor.execute(create_poll_index_title)

        create_question_index_question_poll_id = '''CREATE INDEX IF NOT EXISTS idx_question_poll_id ON question(poll_id);'''
        cursor.execute(create_question_index_question_poll_id)

        create_answer_index_users_id = '''CREATE INDEX IF NOT EXISTS idx_answer_questionnaire_users_id ON answer(questionnaire_users_id);'''
        cursor.execute(create_answer_index_users_id)
        create_answer_index_question_id = '''CREATE INDEX IF NOT EXISTS idx_answer_question_id ON answer(question_id);'''
        cursor.execute(create_answer_index_question_id)
        connection.commit()

    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    finally:
        connection.close()


connection_parameters = {
        'dbname': 'questionnaire_postgres',
        'user': 'postgres',
        'password': 'root',
        'host': '127.0.0.1',
        'port': '5433'
}


execute_db_creation(connection_parameters, database_name)
execute_tables_creation(connection_parameters)
execute_index_creation(connection_parameters)
