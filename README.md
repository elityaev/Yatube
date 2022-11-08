[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
<h1 align="center">Yatube</h1>

## Описание

**Yatube** - это социальная сеть для публикации личных дневников, где 
можно создавать свою страницу, на которой можно посмотреть все записи 
автора. Пользователи могу заходить на чужие страницы, подписываться на 
авторов и комментировать их записи. Записи можно группировать в 
сообщества, на странице которого размещены записи разных авторов. 

### Основные технологии и библиотеки

* [Python](https://www.python.org/)
* [Django](https://docs.djangoproject.com/en/4.1/)
* [Unitest](https://docs.python.org/3/library/unittest.html)
* [Pytest](https://docs.pytest.org/en/7.1.x/contents.html)

### Реализованная функциональность

* с помощью Django ORM реализованы основные CRUD-операции, 
фильтрация объектов, агрегирующие функции;  
* аутентификация пользователей, изменение пароля, 
реализованные с помощью модуля django.contrib.auth, но с 
переопределенными кастомными шаблонами;
  * сценарий восстановления пароля реализован путем эмуляции почтового 
  сервера с сохранением писем в отдельную директорию `/sent_emails`;
  * для проверки авторизации использован декоратор @login_required;
* применен контекст-процессор для формирования отображения текущего
года в шаблоне футера;
* реализована пагинация постов

## Запуска проекта

- Создать виртуальное окружение и подключить его.
```
python -m venv venv
source venv/Scripts/activate
```
- Обновить pip
```
python -m pip install --upgrade pip
```
- Установить все зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Создать и применить миграции 
```
python manage.py makemigrations
python manage.py migrate
```
- Перейти в папку ```/yatube```
```
cd yatube/
```
- Запустите проект
```
python manage.py runserver
```
фы 
Если вы это сделали на локальной машине. Сайт будет доступен по адресу http://localhost/ / http://127.0.0.1:8000/
