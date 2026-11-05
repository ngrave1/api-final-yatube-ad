# API для Yatube

REST API социальной сети Yatube: публикации с изображениями, комментарии,
сообщества и подписки на авторов. API позволяет подключать к проекту веб-клиенты
и мобильные приложения. Контракт API находится в `yatube_api/static/redoc.yaml`.

Анонимным пользователям доступны публикации, комментарии и сообщества для чтения.
Для создания контента и работы с подписками нужна JWT-аутентификация. Редактировать
и удалять публикации и комментарии может только их автор. Сообщества и учётные
записи создаются через административную панель.


## Установка и запуск

В терминале перейдите в корень клонированного репозитория `api-final-yatube-ad`.
Создайте виртуальное окружение и установите зависимости:

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Примените миграции, создайте администратора и запустите сервер:

```bash
cd yatube_api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API: <http://127.0.0.1:8000/api/v1/>.
Документация Redoc: <http://127.0.0.1:8000/redoc/>.
Административная панель: <http://127.0.0.1:8000/admin/>.

Изображения сохраняются в `yatube_api/media/` и доступны локально при `DEBUG=True`.
Настройки проекта предназначены для локальной разработки.

## Эндпоинты

| Адрес относительно `/api/v1/` | Методы | Назначение |
| --- | --- | --- |
| `posts/` | GET, POST | Список публикаций, создание публикации |
| `posts/{id}/` | GET, PUT, PATCH, DELETE | Работа с публикацией |
| `posts/{post_id}/comments/` | GET, POST | Комментарии публикации |
| `posts/{post_id}/comments/{id}/` | GET, PUT, PATCH, DELETE | Работа с комментарием |
| `groups/` | GET | Список сообществ |
| `groups/{id}/` | GET | Информация о сообществе |
| `follow/` | GET, POST | Собственные подписки, подписка на автора |
| `jwt/create/` | POST | Получение access- и refresh-токенов |
| `jwt/refresh/` | POST | Обновление access-токена |
| `jwt/verify/` | POST | Проверка токена |

## Примеры запросов

Получение токенов для существующего пользователя:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jwt/create/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "leo", "password": "your-password"}'
```

Ответ содержит `access` и `refresh`. Заголовок имеет формат `Bearer <токен>`.

Создание публикации:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Моя первая публикация", "group": 1}'
```

Обязательно только поле `text`. Поля `group` и `image` необязательны.
Для загрузки изображения отправьте multipart/form-data:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -F 'text=Публикация с фотографией' -F 'image=@photo.jpg'
```

Получение публикаций с пагинацией:

```bash
curl 'http://127.0.0.1:8000/api/v1/posts/?limit=10&offset=0'
```

Ответ содержит `count`, `next`, `previous` и `results`.
Без параметра `limit` возвращается обычный список публикаций.
`offset` — количество пропускаемых публикаций.

Добавление комментария к публикации с id=1:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/1/comments/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Отличная публикация!"}'
```

Подписка на существующего автора и поиск по собственным подпискам:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/follow/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"following": "another_author"}'

curl 'http://127.0.0.1:8000/api/v1/follow/?search=another' \
  -H 'Authorization: Bearer ACCESS_TOKEN'
```

Подписка на себя и повторная подписка возвращают `400` с описанием ошибки.
Анонимный запрос к подпискам или изменение контента без токена возвращает `401`;
попытка изменить чужой контент — `403`; отсутствующий объект — `404`.

Обновление access-токена:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jwt/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh": "REFRESH_TOKEN"}'
```

## Проверки

Из корня репозитория при активном виртуальном окружении:

```bash
python -m pytest
python -m pip install flake8
python -m flake8
python yatube_api/manage.py check
python yatube_api/manage.py makemigrations --check --dry-run
```

В каталоге `postman_collection/` находится коллекция запросов и инструкция
по её использованию для дополнительной проверки API.
