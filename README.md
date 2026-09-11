# Shop API (Geeks Project)

RESTful API для интернет-магазина, построенное на стеке **Django / Django REST Framework**. Проект предоставляет функционал аутентификации пользователей (включая Google OAuth), управления каталогом товаров, разграничения прав доступа, фоновых задач (Celery) и автоматического сбора аналитики/отчетов.

---

## 🛠 Технологический стек

* **Язык программирования:** Python 3.x
* **Фреймворк:** Django, Django REST Framework (DRF)
* **Асинхронные задачи / Очереди:** Celery, Celery Beat
* **Брокер сообщений / Кэш:** Redis
* **База данных:** PostgreSQL
* **Веб-сервер / Прокси:** Nginx
* **Контейнеризация:** Docker, Docker Compose
* **Документация API:** Swagger / ReDoc (`drf-yasg`)

---

## ✨ Основной функционал

### 1. Пользователи и Аутентификация (`users`)
* Регистрация и аутентификация пользователей.
* Авторизация через **Google OAuth**.
* Использование кастомной модели пользователя (`Custom User Model`).
* Фоновая отправка уведомлений и email-сообщений через Celery.

### 2. Управление товарами (`product`)
* CRUD-операции для категорий, товаров и связанных сущностей.
* Гибкое разграничение прав доступа (Permissions) для пользователей и администраторов.
* Кастомная валидация данных (цены, артикулы, характеристики).
* Автоматическая сгенерированная отчетность по товарам (генерация JSON-отчетов по расписанию в `reports/`).

### 3. Документация API
* Интерактивная документация Swagger UI и ReDoc.

---

## 📁 Структура проекта

```text
shop_api/
├── shop_api/         # Основные настройки Django, URLs, Celery, Swagger
├── product/          # Приложение товаров (Модели, Сериализаторы, Views, Задачи Celery)
├── users/            # Приложение пользователей (OAuth, Менеджеры, Модели, Сервисы)
├── common/           # Общие валидаторы и вспомогательные функции
├── reports/          # Автоматически сгенерированные отчеты (JSON)
├── static/           # Статические файлы (Admin UI, DRF-YASG)
├── Dockerfile        # Конфигурация Docker-образа
├── docker-compose.yaml # Оркестрация контейнеров (Web, DB, Celery, Redis, Nginx)
├── entrypoint.sh     # Скрипт автоматического запуска и применения миграций
├── nginx.conf        # Конфигурация Nginx
└── requirements.txt  # Зависимости Python
```

---

## 🚀 Установка и запуск

### Вариант 1. Запуск через Docker Compose (Рекомендуемый)

> Убедитесь, что у вас установлены **Docker** и **Docker Compose**.

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
   cd shop_api-main
   ```

2. **Создайте файл окружения `.env`:**
   ```bash
   cp .env.example .env
   ```
   *Заполните необходимые переменные в созданном файле `.env`.*

3. **Соберите и запустите контейнеры:**
   ```bash
   docker-compose up --build -d
   ```

Приложение будет доступно по адресу: `http://localhost` (или `http://127.0.0.1`).

---

### Вариант 2. Локальный запуск (Без Docker)

1. **Перейдите в директорию проекта:**
   ```bash
   cd shop_api-main/shop_api
   ```

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv venv
   
   # Для Linux/macOS:
   source venv/bin/activate
   
   # Для Windows:
   venv\Scripts\activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   Создайте файл `.env` в корне проекта по аналогии с `.env.example`.

5. **Примените миграции:**
   ```bash
   python manage.py migrate
   ```

6. **Создайте суперпользователя (Администратора):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
   ```

---

## ⚡ Фоновые задачи (Celery & Redis)

Для обработки фоновых задач (отправка писем, генерация отчетов по расписанию) при локальном запуске запустите вордкер и планировщик Celery в отдельных терминалах:

* **Запуск Celery Worker:**
  ```bash
  celery -A shop_api worker --loglevel=info
  ```

* **Запуск Celery Beat (Планировщик задач):**
  ```bash
  celery -A shop_api beat --loglevel=info
  ```

---

## 📖 Документация API

После запуска проекта интерактивная документация доступна по следующим адресам:

* **Swagger UI:** [http://localhost/swagger/](http://localhost/swagger/) *(или http://127.0.0.1:8000/swagger/)*
* **ReDoc:** [http://localhost/redoc/](http://localhost/redoc/) *(или http://127.0.0.1:8000/redoc/)*

---

## 🧪 Тестирование

Для запуска модульных тестов выполните команду:

* **Локально:**
  ```bash
  python manage.py test
  ```

* **При использовании Docker:**
  ```bash
  docker-compose exec web python manage.py test
  ```

