FROM python:3.12-slim

# Устанавливаем рабочий каталог
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=online_store.settings

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt /app/

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . /app/

# Выполняем миграции и сбор статики (на этапе сборки)
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]