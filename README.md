# Autosalon Shop

A web application for an auto details store.

## Tech Stack

- Python 3.12
- Django 6.0
- SQLite (development) / PostgreSQL (production)
- Docker
- Matplotlib (data visualization)
- OpenWeatherMap API
- National Bank of Belarus API (currency rates)

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

