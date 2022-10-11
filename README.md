# Yatube

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
## Описание
Yatube - это социальная сеть для публикации личных дневников, где можно создавать свою страницу, на которой можно посмотреть все записи автора. Пользователи могу заходить на чужие страницы, подписываться на авторов и комментировать их записи. Записи можно группировать в сообщества, на странице которого размещены записи разных авторов. 
## Для запуска проекта
Нужно:  
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
Если вы это сделали на локальной машине. Сайт будет доступен по адресу http://localhost/ / http://127.0.0.1:8000/
