# Autosalon Shop

A web application for an auto details store.

## Tech Stack

| Component | Version / Description |
|---|---|
| Python | 3.12 |
| Django | 6.0 |
| Database | SQLite (development) / PostgreSQL (production) |
| Containerization | Docker, Docker Compose |
| Visualization | Matplotlib |
| External APIs | OpenWeatherMap, NBRB (currency rates) |
| Utilities | `pytz`, `python-dateutil`, `requests` |

---

## Features

- Product catalog with filtering and search
- Shopping cart and order checkout
- User authentication and registration
- Personal account with order history
- Reviews with CRUD operations
- Promo codes
- News articles
- FAQ
- Job vacancies
- Statistics (mean, median, mode of sales)
- Data visualization (charts)
- Text-based calendar
- Timezone support
- Phone number and age validation (18+)
- External APIs (currency rates, weather)

## Architecture

The project is built on **Django (MVT pattern)** and is divided into independent applications (`apps`), each responsible for its own domain area. Interaction between applications is organized through models and Python-level imports, without circular dependencies.

### Main Components

```text
+-----------------------------------------------------------------+
|                         CLIENT (Browser)                        |
+--------------------------------+--------------------------------+
                                 | HTTP / HTTPS
                                 v
+-----------------------------------------------------------------+
|                    DJANGO (autosalon/settings.py)               |
|  +-----------------------------------------------------------+  |
|  |                    URL Routing (urls.py)                  |  |
|  +-----------------------------------------------------------+  |
|         |              |              |              |          |
|         v              v              v              v          |
|   +----------+   +----------+   +----------+   +----------+     | 
|   |   core   |   | products |   |   news   |   |  promo   |     |
|   |  (views) |   | (models) |   | (models) |   | (models) |     |
|   +----+-----+   +----+-----+   +----+-----+   +----+-----+     |
|        |              |              |              |           |
|        +--------------+--------------+--------------+           |
|                              |                                  |
|                              v                                  |
|                    +------------------+                         |
|                    |   Django ORM     |                         |
|                    +--------+---------+                         |
+-----------------------------+-----------------------------------+
                              |
              +---------------+---------------+
              v               v               v
        +----------+   +-----------+   +--------------+
        |  SQLite  |   | PostgreSQL|   |  File System |
        |  (dev)   |   |  (prod)       |   (media)    |
        +----------+   +-----------+   +--------------+
                                              |
                                              v
                                       +-------------+
                                       |   media/    |
                                       |  (images,   |
                                       |   charts)   |
                                       +-------------+
```

### External services

```text
+------------------+         +-------------------------+
|  OpenWeatherMap  |<--------|  core/services/         |
|      API         |         |  api_services.py        |
+------------------+         |  get_weather()          |
                             +------------+------------+
                                          |
+------------------+                      |
|    NBRB API     |<---------------------+
|    (currency)   |         get_currency_rates()
+------------------+
```

### Main model relations

```text
User (Django auth) --1:1--> Customer --1:N--> Sale --1:N--> SaleItem
                              |                |                |
                              |                |                v
                              |                |            Product
                              |                v                |
                              |           PromoCode             |
                              |                                 |
                              v                                 v
                          Review <--------------------------- Product
                                                              |
                              +-------------------------------+
                              v                               v
                        Manufacturer                    ProductType
                              ^                               ^
                              |                               |
                        Supply <-- Product --M:N--> Supplier --+
                              |                               |
                              v                               v
                          Employee                       Employee
                                                              |
                                                              v
                                                     PickupPoint (core)
```


## Modules Overview

### `core` - Application Core

| File | Responsibility |
|---|---|
| `views/home.py` | Home page, "About Company", privacy policy |
| `views/catalog.py` | Product catalog with filtering, search, sorting; product detail page |
| `views/cart.py` | Cart: view, add, remove, update quantity |
| `views/checkout.py` | Order checkout, creation of `Sale` and `SaleItem`, promo code application |
| `views/auth.py` | Registration, login, logout; extended `RegisterForm` with 18+ validation |
| `views/profile.py` | Personal account, order history, profile editing |
| `views/contacts.py` | Contacts page (employees, pickup points) |
| `views/calendar.py` | Date/time demo, timezone switching, currency rates and weather output |
| `views/statistics.py` | Statistics (mean, median, mode), chart generation via Matplotlib |
| `models.py` | `CompanyInfo`, `Employee`, `PickupPoint` |
| `services/api_services.py` | Integration with external APIs: NBRB (currency rates), OpenWeatherMap (weather) |

### `products` - Products and Sales

| File | Responsibility |
|---|---|
| `models/products.py` | `Product` - product, stock calculation `calculate_stock()` |
| `models/categories.py` | `ProductType` - product type/category |
| `models/manufacturers.py` | `Manufacturer` - manufacturer |
| `models/suppliers.py` | `Supplier` - supplier with phone validation |
| `models/supplies.py` | `Supply` - product supply (Product <-> Supplier link) |
| `models/sales.py` | `Sale`, `SaleItem` - sale and sold items |
| `models/customers.py` | `Customer` - customer profile (linked to `User`) |
| `models/validator.py` | `UserValidatorMixin` - shared phone and age validation |

### `news` - News

| File | Responsibility |
|---|---|
| `models.py` | `Article` - articles/news with slug, image, dates |

### `promo` - Promo Codes

| File | Responsibility |
|---|---|
| `models.py` | `PromoCode` - discount coupon, `is_valid()` check, date validation |

### `reviews` - Reviews

| File | Responsibility |
|---|---|
| `models.py` | `Review` - review with rating 1-5, linked to `User` and `Product` |

### `faq` - Questions and Answers

| File | Responsibility |
|---|---|
| `models.py` | `FAQItem` - question-answer with sorting and publication flag |

### `vacancies` - Job Vacancies

| File | Responsibility |
|---|---|
| `models.py` | `Vacancy` - vacancy with requirements, conditions, salary |

### Root Files

| File | Responsibility |
|---|---|
| `manage.py` | Entry point for Django management commands |
| `autosalon/settings.py` | Project settings (DB, apps, API keys, media/static) |
| `autosalon/urls.py` | Root URL routing |

---

## Integration Points

### 1. Database

| Environment | DBMS | Location |
|---|---|---|
| Development | SQLite | `db.sqlite3` in project root |
| Production | PostgreSQL | Configured via environment variables / `settings.py` |

**Notes:**

- Django ORM is the only data access layer.
- Migrations: `python manage.py migrate`.
- Transactions: `transaction.atomic()` in `checkout.py` and `SaleItem.save()` to ensure order and stock integrity.

### 2. External Services (HTTP APIs)

| Service| Purpose |
|---|---|
| **NBRB** | Currency rates USD, EUR, RUB, PLN | 
| **OpenWeatherMap** | Weather in Minsk |

**Requirements:**

- OpenWeatherMap API key is set in `settings.OPENWEATHER_API_KEY` (or via environment variables).
- Request timeout - 10 seconds.
- On error or missing key, returns `None`; templates handle missing data gracefully.

### 3. File System

| Directory | Purpose |
|---|---|
| `media/company/` | Company logo (`CompanyInfo.logo`) |
| `media/employees/` | Employee photos (`Employee.photo`) |
| `media/news/` | Article images (`Article.image`) |
| `media/charts/` | Generated charts (`popularity.png` from `statistics.py`) |
| `static/` | CSS, JS, static images |

**Settings:**

- `MEDIA_ROOT`, `MEDIA_URL` - in `settings.py`.
- `os.makedirs(..., exist_ok=True)` in `statistics.py` to create `media/charts/`.

### 4. Authentication and Sessions

| Component | Responsibility |
|---|---|
| `django.contrib.auth` | Users, groups, permissions |
| `User` <-> `Customer` | 1:1 link via `OneToOneField` |
| `LoginRequiredMixin` | Protects `CheckoutView`, `ProfileView`, `OrderHistoryView` |
| `UserPassesTestMixin` | Restricts `StatisticsView` to `is_superuser` only |
| Django sessions | Store cart (`request.session['cart']`) and timezone (`user_timezone`) |

### 5. Data Visualization

| Tool | Purpose | File |
|---|---|---|
| **Matplotlib** (`Agg`) | Bar chart of product type popularity | `core/views/statistics.py::generate_chart()` |
| **dateutil.relativedelta** | Age calculation (18+) | `validator.py`, `customers.py`, `auth.py` |
| **pytz** | Timezone handling | `core/views/calendar.py` |

### 6. Containerization

| File | Purpose |
|---|---|
| `Dockerfile` | Application image build |
| `docker-compose.yml` | Orchestration (web + DB) |
| Port | `8000` (mapped with `-p 8000:8000`) |

---


## Installation and Setup

### Local Development

```bash
git clone https://github.com/KATTSS/Autosalon_shop.git
cd Autosalon_shop/autosalon
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Docker

```bash
docker build -t autosalon .
docker run -p 8000:8000 autosalon
```

### Docker Compose

```bash
docker-compose up --build
```

## Hosting

The project is deployed at:

[Hosting link](https://ekatss.pythonanywhere.com/)

## Admin Panel

```
/admin/
```


