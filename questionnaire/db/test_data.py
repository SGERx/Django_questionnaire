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

create_surveys_query = sql.SQL('''
INSERT INTO surveys (title,description,participants,created_on,redacted) VALUES
	('Опрос первый - для проверки дерева вопросов','Описание первого опроса, созданного для проверки дерева вопросов',0,'2024-02-08 08:58:41.95191','2024-02-08 08:58:41.95191'),
	('Опрос второй - для проверки вопросов без дерева','Описание второго опроса, созданного для проверки вопросов без дерева',0,'2024-02-08 08:59:07.80819','2024-02-08 08:59:07.80819'),
	('Опрос третий - для проверки одного вопроса','Описание третьего опроса, созданного для проверки опроса с одним вопросом',0,'2024-02-08 08:59:40.098066','2024-02-08 08:59:40.098066'),
	('Опрос четвертый - без вопросов','Описание четвертого опроса, созданного для проверки опроса без вопросов',0,'2024-02-08 08:59:49.344866','2024-02-08 08:59:49.344866');
''')

create_questions_query_one = sql.SQL('''
INSERT INTO questions (survey_id,title,answered_quantity,answered_rating,question_text,answer_option_1,answer_option_2,answer_option_3,answer_option_4,created_on,redacted) VALUES
	 (1,'Первый вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','Ко второму','К третьему','К четвертому','К пятому','2024-02-08 09:02:54.82681',NULL),
	 (1,'Второй вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К шестому','К седьмому','','','2024-02-08 09:03:35.275116',NULL),
	 (1,'Третий вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К шестому','К седьмому','','','2024-02-08 09:04:07.247292',NULL),
	 (1,'Четвертый вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К восьмому','К девятому','','','2024-02-08 09:05:17.787445',NULL),
	 (1,'Пятый вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К восьмому','К девятому','','','2024-02-08 09:05:43.686526',NULL),
	 (1,'Шестой вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К десятому','','','','2024-02-08 09:06:07.066675',NULL),
	 (1,'Седьмой вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К десятому','','','','2024-02-08 09:06:29.419019',NULL),
	 (1,'Восьмой вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К десятому','','','','2024-02-08 09:07:33.616468',NULL),
	 (1,'Девятый вопрос первого опроса',0,0.00,'К какому вопросу Вы хотели бы перейти?','К десятому','','','','2024-02-08 09:08:03.756847',NULL),
	 (1,'Десятый вопрос первого опроса',0,0.00,'Хотели бы посмотреть статистику?','Конечно','','','','2024-02-08 09:08:34.139517',NULL);
''')

create_questions_query_two = sql.SQL('''
INSERT INTO questions (survey_id,title,answered_quantity,answered_rating,question_text,answer_option_1,answer_option_2,answer_option_3,answer_option_4,created_on,redacted) VALUES
	 (2,'Первый вопрос второго опроса',0,0.00,'Какой вариант ответа выбираете?','Первый','Второй','Третий','Четвертый','2024-02-08 09:09:52.888839',NULL),
	 (2,'Второй вопрос второго опроса',0,0.00,'А теперь какой вариант ответа выбираете?','Конечно же, первый','Разумеется, второй','Определенно, третий','Абсолютно уверен, четвертый','2024-02-08 09:34:19.13053',NULL),
	 (2,'Третий вопрос второго опроса',0,0.00,'Пришло время просмотра статистики?','Да','Да, конечно','Да, разумеется','Да, определенно','2024-02-08 09:35:27.02271',NULL),
	 (3,'Единственный вопрос третьего опроса',0,0.00,'Сразу к статистике?','Да','Да','Да','Да','2024-02-08 09:36:10.022097',NULL);
''')

create_question_relations_one = sql.SQL('''
INSERT INTO question_relations (parent_question_id,child_question_id,response_condition) VALUES
	 (1,2,'1'),
	 (1,3,'2'),
	 (1,4,'3'),
	 (1,5,'4'),
	 (2,6,'1'),
	 (2,7,'2'),
	 (3,6,'1'),
	 (3,7,'2'),
	 (4,8,'1'),
	 (4,9,'2');
''')

create_question_relations_two = sql.SQL('''
INSERT INTO question_relations (parent_question_id,child_question_id,response_condition) VALUES
	 (5,8,'1'),
	 (5,9,'2'),
	 (6,10,'1'),
	 (7,10,'1'),
	 (8,10,'1'),
	 (9,10,'1');
''')

try:
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    cursor.execute(create_surveys_query)
    cursor.execute(create_questions_query_one)
    cursor.execute(create_questions_query_two)
    cursor.execute(create_question_relations_one)
    cursor.execute(create_question_relations_two)
    connection.commit()
    print("Тестовые даннные успешно внесены в базу данных")
except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
