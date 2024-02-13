from django.http import HttpResponse
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from psycopg2 import sql
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


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

    print("surveys")
    try:
        create_surveys_query = '''CREATE TABLE IF NOT EXISTS surveys(
        id serial PRIMARY KEY,
        title VARCHAR (50) UNIQUE NOT NULL,
        description TEXT,
        participants INT DEFAULT 0 NOT NULL,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP
        );'''
        cursor.execute(create_surveys_query)
        print("surveys - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    print("questions")
    try:
        create_questions_query = '''CREATE TABLE IF NOT EXISTS questions(
        id serial PRIMARY KEY,
        survey_id INT NOT NULL,
        title VARCHAR (50) NOT NULL,
        answered_quantity INT DEFAULT 0 NOT NULL,
        answered_rating DECIMAL(5, 2) DEFAULT 0 NOT NULL,
        question_text TEXT,
        created_on TIMESTAMP NOT NULL,
        redacted TIMESTAMP,
        answer_option_1 TEXT,
        answer_option_2 TEXT,
        answer_option_3 TEXT,
        answer_option_4 TEXT,

        CONSTRAINT fk_surveys FOREIGN KEY(survey_id) REFERENCES surveys(id)
        );'''
        cursor.execute(create_questions_query)
        print("questions - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("question_relations")
    try:
        create_questions_query = '''CREATE TABLE IF NOT EXISTS question_relations (
        id serial PRIMARY KEY,
        parent_question_id INT NOT NULL,
        child_question_id INT NOT NULL,
        response_condition VARCHAR(255),
        FOREIGN KEY (parent_question_id) REFERENCES questions(id),
        FOREIGN KEY (child_question_id) REFERENCES questions(id)
        );'''
        cursor.execute(create_questions_query)
        print("question_relations - created")
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")

    print("user_answers")
    try:
        create_user_answers_query = '''CREATE TABLE IF NOT EXISTS user_answers(
        id serial PRIMARY KEY,
        auth_user_id INT NOT NULL,
        question_id INT NOT NULL,
        selected_option INT NOT NULL,
        response_date TIMESTAMP NOT NULL,
        CONSTRAINT fk_auth_user FOREIGN KEY (auth_user_id) REFERENCES auth_user (id),
        CONSTRAINT fk_questions FOREIGN KEY (question_id) REFERENCES questions (id),
        CONSTRAINT unique_user_question_answer UNIQUE (auth_user_id, question_id)
        );'''
        cursor.execute(create_user_answers_query)
        print("user_answers - created")
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

        create_users_index_username = '''CREATE INDEX IF NOT EXISTS idx_auth_user_username ON auth_user(username);'''
        cursor.execute(create_users_index_username)
        create_users_index_email = '''CREATE INDEX IF NOT EXISTS idx_auth_user_email ON auth_user(email);'''
        cursor.execute(create_users_index_email)
        create_users_index_last_login = '''CREATE INDEX IF NOT EXISTS idx_auth_user_last_login ON auth_user(last_login);'''
        cursor.execute(create_users_index_last_login)

        create_surveys_index_title = '''CREATE INDEX IF NOT EXISTS idx_surveys_title ON surveys(title);'''
        cursor.execute(create_surveys_index_title)

        create_question_index_question_surveys_id = '''CREATE INDEX IF NOT EXISTS idx_questions_survey_id ON questions(survey_id);'''
        cursor.execute(create_question_index_question_surveys_id)

        create_user_answers_index_users_id = '''CREATE INDEX IF NOT EXISTS idx_user_answers_auth_user_id ON user_answers(auth_user_id);'''
        cursor.execute(create_user_answers_index_users_id)
        create_user_answers_index_question_id = '''CREATE INDEX IF NOT EXISTS idx_user_answers_question_id ON user_answers(question_id);'''
        cursor.execute(create_user_answers_index_question_id)

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


if __name__ == "__main__":
    load_environment_variables()
    connection_parameters = get_connection_params_from_env()
    creation_params = get_connection_params_from_env()
    database_name = creation_params['dbname']
    execute_db_creation(creation_params, database_name)
    execute_built_in_django_tables_creation(connection_parameters)
    execute_custom_tables_creation(connection_parameters)
    execute_index_creation(connection_parameters)
