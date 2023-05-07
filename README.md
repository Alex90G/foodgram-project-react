# Продуктовый помощник Foodgram

# Адрес для подключения к проекту:
## http://84.201.177.90

## Учётные данные администратора:
> логин: admin

> пароль: QazThm1!$

> электронная почта: admin@test.ru

# Общее описание проекта:
Онлайн-сервис «Продуктовый помощник Foodgram» позволяе пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


# Техническое описание проекта Foodgram:

Ресурсы API Foodgram:

    Ресурс users: пользователи.
    Ресурс tags: теги (пример: завтрак, обед, ужин)
    Ресурс recipes: рецепты, добавляемые пользователями.
    Ресурс favorite: добавление рецепта в избранное.
    Ресурс subscriptions: подписки на автора рецептов.
    Ресурс ingredients: доступные ингредиенты, которые можно использовать при создании рецепта.

Пользовательские роли и права доступа:

    Аноним — может просматривать описания произведений, читать отзывы и комментарии.
    Аутентифицированный пользователь (user) — может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
    Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
    Суперюзер Django должен всегда обладать правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.

# Установка:

## Как запустить проект:

- Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/Alex90G/foodgram-project-react.git
```

#### Обновить индекс пакетов APT
>sudo apt update 

#### Обновить установленные в системе пакеты и установите обновления безопасности
>sudo apt upgrade -y

#### Установить менеджер пакетов pip, утилиту для создания виртуального окружения venv, систему контроля версий git, чтобы клонировать ваш проект.
>sudo apt install python3-pip python3-venv git -y

#### Установить на свой сервер Docker
>sudo apt install docker.io

#### Установить docker-compose
>sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

>sudo chmod +x /usr/local/bin/docker-compose

#### Загрузить файлы docker-compose.yaml и nginx.conf на удалённый сервер.
>scp /mnt/c/<Путь к проекту>/infra/nginx.conf  <login>@<IP>:/home/<Имя>

>scp /mnt/c/<Путь к проекту>/infra/docker-compose.yaml  <login>@<IP>:/home/<Имя>

#### Добавить в Secrets GitHub переменные окружения:

>DB_ENGINE = "django.db.backends.postgresql"

>DB_NAME = "имя базы данных postgres"

>DB_USER = "пользователь базы данных"

>DB_PASSWORD = "пароль"

>DB_HOST = "db"

>DB_PORT = "5432"

>DOCKER_PASSWORD=<пароль от DockerHub>

>DOCKER_USERNAME=<имя пользователя>

>DJANGO_SK=<секретный ключ проекта django>

>USER=<username для подключения к серверу>

>HOST=<IP сервера>

>PASSPHRASE=<пароль для сервера, если он установлен>

>SSH_KEY=<SSH ключ (cat ~/.ssh/id_rsa)>

#### Для отслеживания статуса работы workflow через Telegram можно также добавить в Secrets GitHub следующие переменные:

>TELEGRAM_TO = "ID Вашего телеграм-аккаунта"

>TELEGRAM_TOKEN = "Токен вашего бота. Получить этот токен можно у бота @BotFather"

## Workflow состоит из следующих шагов:
##### Тестирование проекта PEP8.
##### Сборка и публикация образа.
##### Автоматический деплой на сервер.

#### Сборка контейнеров на удалённом сервере
>sudo docker-compose up -d --build

#### Выполнение миграций, сбор статики, создание суперпользователя:
>sudo docker-compose exec web python manage.py migrate

>sudo docker-compose exec web python manage.py collectstatic

>sudo docker-compose exec web python manage.py createsuperuser

#### Загрузить ингредиенты в базу данных можно с помощью команды
>sudo docker-compose exec web python manage.py upload_ingredients ingredients.json

# Документация API и примеры:

```json
/redoc/
```

# Статус бэйджа (настройки приватности репозитория - "Public")
![main workflow](https://github.com/Alex90G/foodgram-project-react/actions/workflows/foodgram_workflows.yml/badge.svg)
