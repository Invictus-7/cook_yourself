# Foodgram

Проект помогает хранить рецепты, обмениваться ими, а также создавать и скачивать список 
покупок для них.

---

[![foodgram workflow](https://github.com/Invictus-7/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)](https://github.com/Invictus-7/foodgram-project-react/actions/workflows/foodgram-workflow.yml)

---


### [Cсылка на сайт](http://158.160.9.218)

#### Данные для проверяющего:
(вход с правами суперпользователя)

**логин**: review@mail.ru \
**пароль**: recipe_777


[Панель администратора](http://158.160.9.218/admin/)

[Redoc](http://158.160.9.218/api/docs/redoc.html)

---
#### Учебный проект Яндекс.Практикума.
##### Когорта Python 10 +

###Автор - Кирилл Резник


---

## Технологии
- Python `v3.7`
- Django `v2.2.16`
- DRF (Django REST framework) `v3.13.1`
- Djoser `v.2.0.5`


## Описание проекта

Cайт Foodgram, «Продуктовый помощник» - онлайн-сервис и API для него. 
Пользователи этого сервиса могут публиковать рецепты, подписываться 
на других пользователей, добавлять понравившиеся рецепты 
в «Избранное», а также скачивать итоговый список 
продуктов, необходимых для приготовления выбранных блюд.

## Установка и запуск backend-проекта на локальном компьютере

1. Клонируйте проект на свой компьютер и перейдите в его корневую папку:
```
git clone https://github.com/Invictus-7/foodgram-project-react.git
cd foodgram-project-react
```
2. Создайте и активируйте виртуальное окружение:

```
python -m venv venv
активация - /venv/scripts/activate
```


3. Обновите pip и установите зависимости в виртуальное окружение:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Выполните миграции:
```
python manage.py migrate
```

5. Наполните базу данных стартовыми данными (при необходимости):
```
python manage.py imp_ingr
```

6. Создайте суперпользователя Django (при необходимости):
```
python manage.py createsuperuser
```

7. Запустите проект:
```
python manage.py runserver
```

## Уровни доступа к сайту
- **Анонимный пользователь** — может просматривать и фильтровать по ярлыкам все рецепты 
и рецепты отдельных пользователей.
- **Аутентифицированный пользователь (`user`)** — имеет доступы, как и у Анонима, а также 
может публиковать новые рецепты, редактировать свои рецепты, подписываться
на обновления рецептов других пользователей, добавлять рецепты в избранное и 
формировать список покупок.
- **Администратор (`admin`)** — обладает полными правми на управление всем контентом проекта, в
том числе с правами на создание и удаление рецептов, тегов и ингредиентов. Также может управлять пользователями.
Весь функционал доступен в стандартной админ-панели Django.
- **Суперпользователь Django** должен всегда обладать правами администратора, 
пользователя с правами admin. Даже если изменить пользовательскую роль 
суперпользователя — это не лишит его прав администратора. 
Суперпользователь — всегда администратор, но администратор — не обязательно 
суперпользователь.

## API-ресурсы проекта
- Ресурс **auth**: аутентификация - получение и отзыв токена.
- Ресурс **users**: пользователи и подписки.
- Ресурс **tags**: ярлыки ('тэги'), создаются администраторами
- Ресурс **recepies**: рецепты, в том числе добавление в списки
избранных и списки покупок.
- Ресурс **ingredients**: ингредиенты.

Описание каждого ресурса дано в документации: указаны эндпоинты (адреса, по которым можно 
сделать запрос), разрешённые типы запросов, права доступа и дополнительные параметры, 
если это необходимо.

Для доступа к документации проекта запустите проект согласно инструкции ниже
и пройдите [по ссылке](http://localhost/api/docs/redoc.html).
