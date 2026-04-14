# Интернет-магазин на Django

Проект интернет-магазина, разработанный в рамках курса "Python разработчик".

## О проекте

Веб-приложение интернет-магазина с функционалом:
- Каталог товаров с фильтрацией по категориям
- Корзина покупок
- Оформление заказов
- Личный кабинет покупателя
- Административная панель для управления товарами, заказами и клиентами
- Учёт движения товаров на складе

## Технологии

- **Backend:** Python 3.12, Django 6.0
- **База данных:** PostgreSQL, SQLite (для тестов)
- **Контейнеризация:** Docker, Docker Compose
- **Управление зависимостями:** Poetry
- **Фронтенд:** HTML, CSS (встроенные стили)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Clavker/OnlineStore-.git
cd OnlineStore-
git checkout online-store-part2
```

### 2. Настройка окружения

Создайте файл .env в корне проекта:
```env
SECRET_KEY=ваш-секретный-ключ
DB_NAME=online_store_db
DB_USER=django_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
```

### 3. Установка зависимостей

```bash
poetry install
```

### 4. Выполнение миграций

```bash
poetry run python manage.py migrate
```

### 5. Запуск сервера

```bash
poetry run python manage.py runserver
```

## Запуск через Docker

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000
Для обеспечения корректной работы при старте контейнера, команда `collectstatic` вынесена из Dockerfile в `docker-compose.yml`:

```yaml
command: >
  sh -c "
  python manage.py migrate &&
  python manage.py collectstatic --noinput &&
  python manage.py runserver 0.0.0.0:8000
```

Это гарантирует, что:
- миграции применятся до сбора статистики
- статистика будет собираться после доступности БД
- при первом запуске не возникнет ошибок подключения к БД

## Структура проекта
```
OnlineStore-/
├── main/                   # Основное приложение (модели, представления, шаблоны)
├── users/                  # Приложение для кастомной модели пользователя
├── online_store/           # Настройки проекта
├── static/                 # Статические файлы (генерируются при сборке)
├── media/                  # Загруженные пользователями файлы
├── .env                    # Переменные окружения (не в репозитории)
├── docker-compose.yml      # Конфигурация Docker
├── Dockerfile              # Инструкция для сборки Docker-образа
├── pyproject.toml          # Зависимости Poetry
└── manage.py               # Управляющий скрипт Django
```

## Основные возможности
### Для покупателей
- Просмотр каталога товаров с фильтрацией по категориям
- Добавление товаров в корзину
- Оформление заказов
- Просмотр истории заказов и статусов

### Для администраторов
- Управление товарами (CRUD) 
- Управление категориями
- Управление заказами (изменение статуса)
- Управление клиентами
- Просмотр движения товаров на складе

## Тестирование
```bash
# Запуск всех тестов
poetry run python manage.py test

# Запуск тестов с подробным выводом
poetry run python manage.py test -v 2
```

## Команды управления
```bash
# Экспорт остатков товаров в CSV
poetry run python manage.py export_product_residue

# Загрузка товаров из CSV
poetry run python manage.py load_goods goods.csv

# Загрузка фикстур
poetry run python manage.py loaddata data.json
```

## Лицензия

Проект создан в образовательных целях

## Автор

- GitHub: Clavker
- Email: slavker.belakov@yandex.ru
