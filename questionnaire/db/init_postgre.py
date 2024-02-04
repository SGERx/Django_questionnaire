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
        create_users_query = '''CREATE TABLE IF NOT EXISTS participants(
        id serial PRIMARY KEY,
        username VARCHAR (30) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        password_salt VARCHAR(255) NOT NULL,
        email VARCHAR (30) UNIQUE NOT NULL,
        created_on TIMESTAMP NOT NULL,
        last_login TIMESTAMP
        ); '''
        cursor.execute(create_users_query)

        create_polls_query = '''CREATE TABLE IF NOT EXISTS polls(
        id serial PRIMARY KEY,
        title VARCHAR (50) UNIQUE NOT NULL,
        description TEXT,
        participants INT DEFAULT 0 NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP
        );'''
        cursor.execute(create_polls_query)

        create_questions_query = '''CREATE TABLE IF NOT EXISTS questions(
        id serial PRIMARY KEY,
        poll_id INT NOT NULL,
        participants INT DEFAULT 0 NOT NULL,
        answered_rating INT DEFAULT 0 NOT NULL,
        question_text TEXT,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP,
        CONSTRAINT fk_polls FOREIGN KEY(poll_id) REFERENCES polls(id)
        );'''
        cursor.execute(create_questions_query)


        create_answer_options_query = '''CREATE TABLE IF NOT EXISTS answer_options(
        id serial PRIMARY KEY,
        question_id INT NOT NULL,
        option_text TEXT NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP,
        CONSTRAINT fk_question FOREIGN KEY (question_id) REFERENCES questions (id)
        );'''
        cursor.execute(create_answer_options_query)


        create_answers_query = '''CREATE TABLE IF NOT EXISTS answers(
        id serial PRIMARY KEY,
        participants_id INT NOT NULL,
        question_id INT NOT NULL,
        response_text TEXT ,
        response_date TIMESTAMP NOT NULL,
        CONSTRAINT fk_participants FOREIGN KEY (participants_id) REFERENCES participants (id),
        CONSTRAINT fk_questions FOREIGN KEY (question_id) REFERENCES questions (id)
        );'''
        cursor.execute(create_answers_query)

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

        create_users_index_username = '''CREATE INDEX IF NOT EXISTS idx_participants_username ON participants(username);'''
        cursor.execute(create_users_index_username)
        create_users_index_email = '''CREATE INDEX IF NOT EXISTS idx_participants_email ON participants(email);'''
        cursor.execute(create_users_index_email)
        create_users_index_last_login = '''CREATE INDEX IF NOT EXISTS idx_participants_last_login ON participants(last_login);'''
        cursor.execute(create_users_index_last_login)

        create_polls_index_title = '''CREATE INDEX IF NOT EXISTS idx_polls_title ON polls(title);'''
        cursor.execute(create_polls_index_title)

        create_question_index_question_polls_id = '''CREATE INDEX IF NOT EXISTS idx_questions_poll_id ON questions(poll_id);'''
        cursor.execute(create_question_index_question_polls_id)

        create_answers_index_users_id = '''CREATE INDEX IF NOT EXISTS idx_answers_participants_id ON answers(participants_id);'''
        cursor.execute(create_answers_index_users_id)
        create_answers_index_question_id = '''CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);'''
        cursor.execute(create_answers_index_question_id)
        create_answers_options_index_question_id = '''CREATE INDEX IF NOT EXISTS idx_answer_options_question_id ON answer_options(question_id);'''
        cursor.execute(create_answers_options_index_question_id)

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

creation_params = {
        'dbname': 'questionnaire_postgres',
        'user': 'postgres',
        'password': 'root',
        'host': '127.0.0.1',
        'port': '5433'
}


execute_db_creation(creation_params, database_name)
execute_tables_creation(connection_parameters)
execute_index_creation(connection_parameters)






