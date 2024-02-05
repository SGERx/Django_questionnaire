from django.http import HttpResponse
import psycopg2
from psycopg2 import sql
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

file_path_tables = os.path.join(os.path.dirname(__file__),
                                'create_tables.sql')
database_name = 'questionnaire_postgres'


def execute_db_creation(connection_parameters, database_name):
    print("STARTING DATABASE CREATION")
    try:
        connection_parameters.pop('dbname', None)
        connection = psycopg2.connect(**connection_parameters)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()
        cursor.execute("ROLLBACK;")

        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(database_name)))

        connection.commit()
        print("DATABASE CREATION COMPLETE")
    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")

    finally:
        if connection:
            connection.close()


def execute_custom_tables_creation(connection_parameters):
    print("STARTING CUSTOM TABLES CREATION")
    connection = psycopg2.connect(**connection_parameters)
    cursor = connection.cursor()
    print("participants")
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
        print("participants - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("polls")
    try:
        create_polls_query = '''CREATE TABLE IF NOT EXISTS polls(
        id serial PRIMARY KEY,
        title VARCHAR (50) UNIQUE NOT NULL,
        description TEXT,
        participants INT DEFAULT 0 NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP
        );'''
        cursor.execute(create_polls_query)
        print("polls - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("questions")
    try:
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
        print("questions - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("answer_options")
    try:
        create_answer_options_query = '''CREATE TABLE IF NOT EXISTS answer_options(
        id serial PRIMARY KEY,
        question_id INT NOT NULL,
        option_text TEXT NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP,
        CONSTRAINT fk_question FOREIGN KEY (question_id) REFERENCES questions (id)
        );'''
        cursor.execute(create_answer_options_query)
        print("answer_options - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("answers")
    try:
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
        print("answers - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    finally:
        connection.commit()
        connection.close()
        print("CUSTOM TABLES CREATION COMPLETE")


def execute_index_creation(connection_parameters):
    print("STARTING INDEX CREATION")
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
        print("INDEX CREATION COMPLETE")


def execute_built_in_django_tables_creation(connection_parameters):
    connection = psycopg2.connect(**connection_parameters)
    cursor = connection.cursor()
    print("auth_user")
    try:
        create_auth_users_query = '''CREATE TABLE auth_user (
        id serial PRIMARY KEY,
        username VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(128) NOT NULL,
        first_name VARCHAR(30) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        email VARCHAR(254) UNIQUE NOT NULL,
        is_staff BOOLEAN NOT NULL,
        is_active BOOLEAN NOT NULL,
        is_superuser BOOLEAN NOT NULL,
        last_login TIMESTAMP,
        date_joined TIMESTAMP NOT NULL
        ); '''
        cursor.execute(create_auth_users_query)
        print("auth_user - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("django_session")
    try:
        create_session_table_query = '''CREATE TABLE django_session (
        session_key varchar(40) NOT NULL PRIMARY KEY,
        session_data text NOT NULL,
        expire_date timestamp with time zone NOT NULL
        ); '''
        cursor.execute(create_session_table_query)
        print("django_session - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("django_content_type")
    try:
        create_django_content_type_query = '''CREATE TABLE django_content_type (
        id serial NOT NULL PRIMARY KEY,
        app_label varchar(100) NOT NULL,
        model varchar(100) NOT NULL,
        UNIQUE (app_label, model)
        ); '''
        cursor.execute(create_django_content_type_query)
        print("django_content_type - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("django_admin_log")
    try:
        create_admin_log_table_query = '''CREATE TABLE IF NOT EXISTS django_admin_log (
        id serial NOT NULL PRIMARY KEY,
        action_time timestamp with time zone NOT NULL,
        user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED,
        content_type_id integer,
        object_id text NULL,
        object_repr varchar(200) NOT NULL,
        action_flag smallint NOT NULL,
        change_message text NOT NULL,
        CONSTRAINT fk_django_admin_log_content_type
            FOREIGN KEY (content_type_id)
            REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED
        );
        '''

        cursor.execute(create_admin_log_table_query)
        print("django_admin_log - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("auth_group")
    try:
        create_auth_group_query = '''CREATE TABLE IF NOT EXISTS auth_group (
                id serial NOT NULL PRIMARY KEY,
                name varchar(150) NOT NULL UNIQUE
        );
        '''
        cursor.execute(create_auth_group_query)
        print("auth_group - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("auth_permission")
    try:
        create_auth_group_query = '''CREATE TABLE auth_permission (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        codename VARCHAR(100) NOT NULL,
        content_type_id INTEGER,
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id),
        CONSTRAINT unique_permission_code UNIQUE (content_type_id, codename)
        );
        '''
        cursor.execute(create_auth_group_query)
        print("auth_permission - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("django_migrations")
    try:
        create_auth_group_query = '''CREATE TABLE django_migrations (
        id SERIAL PRIMARY KEY,
        app VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        applied TIMESTAMP NOT NULL
        );

        '''
        cursor.execute(create_auth_group_query)
        print("django_migrations - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("auth_group_permissions")
    try:
        create_auth_group_query = '''CREATE TABLE auth_group_permissions (
        id SERIAL PRIMARY KEY,
        group_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        FOREIGN KEY (group_id) REFERENCES auth_group (id),
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id),
        CONSTRAINT unique_group_permission UNIQUE (group_id, permission_id)
        );
        '''
        cursor.execute(create_auth_group_query)
        print("auth_group_permissions - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("auth_user_groups")
    try:
        create_auth_group_query = '''CREATE TABLE auth_user_groups (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
        FOREIGN KEY (group_id) REFERENCES auth_group (id),
        CONSTRAINT unique_user_group UNIQUE (user_id, group_id)
        );
        '''
        cursor.execute(create_auth_group_query)
        print("auth_user_groups - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("auth_user_user_permissions")
    try:
        create_auth_group_query = '''CREATE TABLE auth_user_user_permissions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id),
        CONSTRAINT unique_user_permission UNIQUE (user_id, permission_id)
        );
        '''
        cursor.execute(create_auth_group_query)
        print("auth_user_user_permissions - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        connection.commit()
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
execute_custom_tables_creation(connection_parameters)
execute_index_creation(connection_parameters)
execute_built_in_django_tables_creation(connection_parameters)