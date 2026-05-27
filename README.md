# 📦 Warehouse — Система учёта товаров на складе

Веб-приложение на **Django 5 + SQLAlchemy 2 + SQLite** для управления складским учётом.  
Реализованы полный CRUD, поиск, сортировка (через SQLAlchemy), Django Admin и система движения товаров.

---

## 🗂️ Структура базы данных

```
Category          Supplier
    │                 │
    └──── Product ────┘
               │
         StockMovement
```

| Таблица         | Назначение                                          |
|-----------------|-----------------------------------------------------|
| `Category`      | Категории товаров                                   |
| `Supplier`      | Поставщики (название, контакты, статус)             |
| `Product`       | Товары (SKU, цена, остаток, мин. остаток, FK)       |
| `StockMovement` | История движений: приход / расход / корректировка   |

---

## ⚡ Ключевые возможности

| Функция            | Реализация                                    |
|--------------------|-----------------------------------------------|
| CRUD товаров       | Django ORM + CBV-style функции                |
| CRUD категорий     | Django ORM                                    |
| CRUD поставщиков   | Django ORM                                    |
| Движение товаров   | Автоматически обновляет `quantity` в Product  |
| **Поиск**          | **SQLAlchemy** — по name, sku, description    |
| **Сортировка**     | **SQLAlchemy** — любое поле, ASC / DESC       |
| Фильтр по категории| SQLAlchemy ForeignKey join                    |
| Фильтр «мало»      | SQLAlchemy — `quantity <= min_quantity`       |
| Агрегации          | SQLAlchemy `func.sum`, `func.count`           |
| Дашборд            | Статистика склада в реальном времени          |
| **Админка**        | **Django Admin** с расширенной конфигурацией  |
| JSON API           | `/api/stats/` — статистика в JSON             |
| Авторизация        | Django Auth — все страницы требуют логин      |

---

## 🛠️ Деплой локально в PyCharm (Python 3.12)

### Шаг 1. Клонировать / скопировать проект

Разместите папку `warehouse_project` в удобном месте, например:

```
C:\Projects\warehouse_project\   (Windows)
~/projects/warehouse_project/   (macOS / Linux)
```

---

### Шаг 2. Открыть проект в PyCharm

1. Запустите **PyCharm** → **File → Open…**
2. Выберите папку `warehouse_project` → **OK**
3. Дождитесь индексации проекта.

---

### Шаг 3. Создать виртуальное окружение (venv) под Python 3.12

#### Вариант A — через интерфейс PyCharm (рекомендуется)

1. **File → Settings** (Windows/Linux) или **PyCharm → Settings** (macOS)
2. **Project: warehouse_project → Python Interpreter**
3. Нажмите шестерёнку ⚙️ → **Add Interpreter → Add Local Interpreter**
4. Выберите **Virtualenv Environment → New**
5. В поле **Base interpreter** выберите **Python 3.12**
6. Путь к venv установится автоматически (`.venv` внутри проекта)
7. Нажмите **OK** → **Apply**

#### Вариант B — через терминал

```bash
# Windows (в PowerShell внутри PyCharm)
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3.12 -m venv .venv
source .venv/bin/activate
```

---

### Шаг 4. Установить зависимости

Откройте **Terminal** внутри PyCharm (вкладка снизу) и выполните:

```bash
pip install -r requirements.txt
```

Содержимое `requirements.txt`:
```
Django==5.0.6
SQLAlchemy==2.0.30
```

Убедитесь, что установка прошла успешно:
```bash
python -c "import django, sqlalchemy; print(django.__version__, sqlalchemy.__version__)"
# Ожидаемый вывод: 5.0.6  2.0.30
```

---

### Шаг 5. Применить миграции (создать БД)

```bash
python manage.py migrate
```

Django создаст файл `db.sqlite3` в корне проекта со всеми таблицами.

---

### Шаг 6. Создать суперпользователя (для входа в систему и Admin)

```bash
python manage.py createsuperuser
```

Введите:
- **Username** — например, `admin`
- **Email** — можно оставить пустым
- **Password** — минимум 8 символов

---

### Шаг 7. Загрузить демонстрационные данные (опционально)

```bash
python manage.py seed_data
```

Команда добавит:
- 5 категорий (Электроника, Офисные принадлежности, Мебель и др.)
- 4 поставщика
- 15 товаров с реалистичными данными
- Начальные приходы для каждого товара

---

### Шаг 8. Настроить Run Configuration в PyCharm

1. В правом верхнем углу нажмите **"Add Configuration…"** (или **Edit Configurations…**)
2. Нажмите **+** → **Django Server**
3. Настройки:
   - **Name:** `Warehouse Dev Server`
   - **Host:** `127.0.0.1`
   - **Port:** `8000`
   - **Environment variables:** *(можно оставить пустым)*
4. PyCharm должен автоматически определить `manage.py` и `Settings`
5. Нажмите **OK**

> **Если конфигурация Django Server недоступна:**  
> File → Settings → Languages & Frameworks → Django → Enable Django Support  
> Django project root: выберите папку `warehouse_project`  
> Settings: `warehouse/settings.py`

---

### Шаг 9. Запустить сервер

Нажмите зелёную кнопку ▶️ **Run** или используйте терминал:

```bash
python manage.py runserver
```

---

### Шаг 10. Открыть приложение в браузере

| URL                              | Описание                    |
|----------------------------------|-----------------------------|
| http://127.0.0.1:8000/           | Главная (Дашборд)           |
| http://127.0.0.1:8000/products/  | Список товаров              |
| http://127.0.0.1:8000/admin/     | Django Admin панель         |
| http://127.0.0.1:8000/api/stats/ | JSON статистика             |
| http://127.0.0.1:8000/login/     | Страница входа              |

---

## 📁 Структура проекта

```
warehouse_project/
├── manage.py                      # Точка входа Django CLI
├── requirements.txt               # Зависимости
├── db.sqlite3                     # БД SQLite (создаётся при migrate)
├── static/                        # Статические файлы
│
├── warehouse/                     # Конфигурация проекта
│   ├── __init__.py
│   ├── settings.py                # Настройки (DB, INSTALLED_APPS и др.)
│   ├── urls.py                    # Корневые URL маршруты
│   └── wsgi.py
│
└── inventory/                     # Основное приложение
    ├── __init__.py
    ├── models.py                  # Django ORM модели (4 таблицы)
    ├── views.py                   # Представления (CRUD, поиск, API)
    ├── urls.py                    # URL маршруты приложения
    ├── forms.py                   # Django формы
    ├── admin.py                   # Конфигурация Django Admin
    ├── db_sa.py                   # SQLAlchemy engine, сессии, запросы
    │
    ├── management/
    │   └── commands/
    │       └── seed_data.py       # Команда загрузки демо-данных
    │
    └── templates/
        └── inventory/
            ├── base.html          # Базовый шаблон с навигацией
            ├── login.html         # Страница входа
            ├── dashboard.html     # Дашборд со статистикой
            ├── product_list.html  # Список товаров + поиск/фильтр
            ├── product_detail.html# Карточка товара + история движений
            ├── product_form.html  # Форма создания/редактирования
            ├── category_list.html # Список категорий
            ├── supplier_list.html # Список поставщиков
            ├── movement_list.html # История движений
            └── confirm_delete.html# Подтверждение удаления
```

---

## 🔍 Как работает интеграция SQLAlchemy + Django

Оба ORM работают с **одной и той же** базой данных `db.sqlite3`.

- **Django ORM** управляет схемой через `migrate`, выполняет CRUD.
- **SQLAlchemy** используется для **поиска, сортировки и агрегации** — подключается к той же БД через `SQLALCHEMY_DATABASE_URL` из `settings.py`.

```python
# db_sa.py — пример SQLAlchemy запроса с поиском и сортировкой
def sa_search_products(query, sort_by, sort_dir, category_id, low_stock):
    db = SessionLocal()
    q = db.query(SAProduct)
    if query:
        q = q.filter(
            SAProduct.name.ilike(f"%{query}%") |
            SAProduct.sku.ilike(f"%{query}%")
        )
    if low_stock:
        q = q.filter(SAProduct.quantity <= SAProduct.min_quantity)
    sort_col = getattr(SAProduct, sort_by, SAProduct.name)
    return q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc()).all()
```

---

## 🛡️ Команды для разработки

```bash
# Создать новые миграции (если изменили models.py)
python manage.py makemigrations inventory
python manage.py migrate

# Запустить тесты
python manage.py test inventory

# Открыть Django shell
python manage.py shell

# Пример в shell — запрос через SQLAlchemy
from inventory.db_sa import sa_warehouse_stats, sa_search_products
print(sa_warehouse_stats())
results = sa_search_products(query="Ноутбук", sort_by="price", sort_dir="desc")
for p in results: print(p.name, p.price)
```

---

## 🚨 Возможные проблемы и решения

| Проблема | Решение |
|---|---|
| `ModuleNotFoundError: No module named 'django'` | Убедитесь, что активировано venv: в PyCharm проверьте интерпретатор в правом нижнем углу |
| `OperationalError: no such table` | Выполните `python manage.py migrate` |
| Страница входа не редиректит на главную | Убедитесь, что `LOGIN_REDIRECT_URL = '/'` в settings.py |
| PyCharm не видит конфигурацию Django | File → Settings → Languages & Frameworks → Django → Enable Django Support |
| `STATICFILES_DIRS` warning | Создайте пустую папку `static/` в корне проекта |
| Порт 8000 занят | `python manage.py runserver 8001` |

---

## 📝 Лицензия

MIT — свободное использование в учебных и коммерческих целях.
