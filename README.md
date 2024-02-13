# Questionnare
### Описание
Проект для проведения опросов с учетом пользователя и динамическим отображением вопросов, созданный с помощью Django и PostgreSQL. Доступно создание дерева вопросов, что предоставляет возможность динамического отображения вопросов в зависимости от ответов пользователя.

С целью изучения PostgreSQL и системных таблиц Django проект написан без использования Django ORM.

### Технологии
- Python 3.9
- Django 4.2.9
- psycopg2 2.9.9
- PostgreSQL

### Возможности проекта:

- Создание и редактирование опросов и вопросов через админку;
- Веб-интерфейс, позволяющий пользователям проходить опросы и отвечать на вопросы;
- Сохранение ответов пользователей в связке с соответствующими опросами;
- Логика, позволяющую определить, какие вопросы показывать или скрывать в зависимости от предыдущих ответов пользователя (т.е. дерево);
- Вывод результатов опросов, включая статистику ответов на каждый вопрос, после завершения опроса;

После завершения опроса пользователю показывается статистика опроса:
-- Общее кол-во участников опроса (например, 100)
- На каждый вопрос:
    - Количество ответивших и их доля от общего количества участников опроса (например, 95 / 95%)
    - Порядковый номер вопроса по количеству ответивших. Если количество совпадает, то и номер должен совпадать (например, для трех вопросов с 95, 95, 75 ответивших получаются соответствующие им номера 1, 1, 2)
    - Количество ответивших на каждый из вариантов ответа и их доля от общего количества ответивших на этот вопрос после завершения опроса.




### Установка проекта

1) Скачать проект:
```
git@github.com:SGERx/Django_questionnaire.git
```
2) Установить и активировать виртуальное окружение

3) Установить зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 

4) Установить PostgreSQL

5) В файле .env прописать параметры подключения по образцу из .env-example

6) Для создания базы данных, тестового администратора и пользователей можно использовать скрипты из папки:
```
questionnaire/db
```

- Для создания базы данных:

```
questionnaire/db/init_postgre.py
```

- Для создания пользователя-администратора (скрипт предложит внести свои данные или использовать существующие):

```
questionnaire/db/add_admin.py
```

- Для внесения тестовых данных (опросы, вопросы и связи между вопросами):

```
questionnaire/db/test_survey_data.py
```

- Для внесения тестовых данных (4 пользователя и их ответы на вопросы):

```
questionnaire/db/test_users_and_answers.py
```

# Запуск проекта

В папке с файлом manage.py выполнить команду:
```
python3 manage.py runserver
```

В настройках проекта отключен режим дебага, разрешены подключения '127.0.0.1' и 'localhost'

### Автор
SGERx
