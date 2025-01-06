# DRF Library Service

A library management system built using Django Rest Framework (DRF) to manage book borrowing, payments, and user accounts.

## Features

- User authentication using JSON Web Tokens (JWT).
- Manage books, borrowing records, and payments.
- Integration with Stripe for payment processing.
- Background task management using Celery and Redis.
- API auto-documentation using DRF Spectacular.

---

## Technologies Used

1. **Backend Framework**: [Django](https://www.djangoproject.com/) 5.1
   - [Django Rest Framework](https://www.django-rest-framework.org/) for building APIs.
   - [Django Filter](https://django-filter.readthedocs.io/) to filter query results.
   - [DRF Spectacular](https://drf-spectacular.readthedocs.io/) for API schema and documentation.
   - [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) for auth tokens.

2. **Task Queue**:
   - [Celery](https://docs.celeryproject.org/) for asynchronous job processing.
   - [Redis](https://redis.io/) as a message broker for Celery.

3. **Database**:
   - [PostgreSQL](https://www.postgresql.org/) as the database.

4. **Payment**:
   - [Stripe](https://stripe.com/) for handling payments.

5. **Containerization**:
   - [Docker](https://www.docker.com/) for easy deployment.
   - [Docker Compose](https://docs.docker.com/compose/) for managing multi-container applications.

6. **Other Tools**:
   - [django-celery-beat](https://django-celery-beat.readthedocs.io/) for scheduling periodic tasks.
   - [dotenv](https://pypi.org/project/python-dotenv/) for environment variable configuration.

---

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites
1. Install **Docker** and **Docker Compose**.
2. Install **Python 3.12** if you don't want to use Docker.
3. Create a `.env` file based on `.env.sample` and fill in the required environment variables.

### Installation and Setup

Clone the repository:
```bash
git clone https://github.com/YaroslavBordovoy/drf-library-service.git
cd drf-library-service
```

#### Running with Docker (Recommended)
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Create a superuser for admin access (inside the container):
   ```bash
   docker-compose exec library python manage.py createsuperuser
   ```
   
3. Access the application:
   - API: [http://localhost:8000/](http://localhost:8000/)
   - API Documentation: [http://localhost:8000/schema/](http://localhost:8000/schema/)

---

#### Running Without Docker

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

2. Install project dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
   
4. Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the application at [http://localhost:8000/](http://localhost:8000/).

---

### Environment Variables

Example configuration is included in the `.env.sample` file. Copy it to `.env` and set your specific values.

#### Required Variables:
- `SECRET_KEY`: Django's secret key.
- `PGDATA`: Path where PostgreSQL stores its data (e.g., `/var/lib/postgresql/data`).
- `REDIS_URL`: Redis URL for caching.
- `CELERY_REDIS_URL`: Redis URL specifically for Celery.
- `STRIPE_SECRET_KEY`: Stripe secret key.
- `STRIPE_PUBLISHABLE_KEY`: Stripe public key.
- `POSTGRES_DB`: Name of the PostgreSQL database.
- `POSTGRES_USER`: PostgreSQL username.
- `POSTGRES_PASSWORD`: PostgreSQL user password.
- `POSTGRES_HOST`: PostgreSQL host (e.g., `localhost` or `db` for Docker).
- `POSTGRES_PORT`: PostgreSQL port (default is `5432`).
---

## Celery Task Queue

The project includes Celery for background task processing. Ensure the `celery` and `redis` services are running in Docker:

```bash
docker-compose up -d celery redis
```

To manually start Celery without Docker:
```bash
celery -A core worker --loglevel=info
celery -A core beat --loglevel=info
```
