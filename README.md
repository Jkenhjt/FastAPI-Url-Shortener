# 🚀 FastAPI Monitoring & Dashboard Project

A production-ready **FastAPI** application with Docker support, Prometheus monitoring, Grafana dashboards, and Nginx reverse proxy. This project follows a modular structure with Alembic migrations, database models, routers, schemas, security utilities, and unit tests.

This repository is designed to provide a scalable and maintainable backend service with monitoring and visualization capabilities out-of-the-box. It's suitable for learning, prototyping, or deploying small to medium production projects.

---

## ✨ Features

- 🐍 FastAPI backend with modular routers  
  - Organized by resource type for clarity and maintainability.  
- 🗄️ PostgreSQL database integration using SQLAlchemy  
  - Includes models and schemas for database interactions.  
- 🔄 Alembic for database migrations  
  - Allows version-controlled database schema changes.  
- 🐳 Dockerized services for FastAPI, Nginx, Prometheus, and Grafana  
  - Each service has its own Dockerfile for modularity.  
- 📊 Prometheus monitoring and Grafana dashboards  
  - Metrics collection and visualization ready for production.  
- 🌐 Nginx reverse proxy configuration  
  - Provides routing, caching, and security improvements.  
- ⏱️ Rate limiting and logging utilities  
  - Includes configurable rate limiting and structured logging.  
- 🧪 Unit tests for routes and services  
  - Ensures reliability and correctness of the codebase.

---

## 📂 Directory Structure
```
fastapi_url_shortener
├── LICENSE
├── README.md
├── compose.yml # Docker Compose configuration for all services
├── fastapi.Dockerfile # Dockerfile for the FastAPI application
├── requirements.txt # Python dependencies
├── grafana
│ ├── dashboard.json # Preconfigured dashboard for Grafana
│ ├── dashboards.yml # Dashboard configurations
│ ├── datasource.yml # Grafana data source configuration
│ └── grafana.dockerfile # Dockerfile for Grafana
├── nginx
│ ├── nginx.Dockerfile # Dockerfile for Nginx reverse proxy
│ └── nginx.conf # Nginx configuration
├── prometheus
│ ├── prometheus.Dockerfile # Dockerfile for Prometheus
│ └── prometheus.yml # Prometheus configuration
└── src
├── __init__.py
├── main.py # FastAPI application entrypoint
├── alembic # Alembic migrations
│ ├── README
│ ├── env.py
│ ├── script.py.mako
│ └── versions
├── alembic.ini # Alembic configuration
├── database
│ ├── __init__.py
│ └── db.py # Database connection/session management
├── models # SQLAlchemy models
│ ├── __init__.py
│ ├── url.py
│ └── user.py
├── routers # FastAPI route definitions
│ ├── __init__.py
│ ├── admin.py
│ ├── url.py
│ └── user.py
├── schemas # Pydantic schemas
│ ├── __init__.py
│ ├── admin.py
│ └── user.py
├── security # Authentication and security utilities
│ ├── init.py
│ └── security.py
├── utils # Helper functions (logging, rate limiting, etc.)
│ ├── __init__.py
│ ├── limiter.py
│ ├── logger.py
│ └── utils.py
└── tests # Unit tests
├── __init__.py
├── test_admin.py
└── test_users.py
```

---

## 🏁 Getting Started

### Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### Install Python dependencies

```
pip install -r requirements.txt
```

### Run FastAPI locally

```
uvicorn src.main:app --reload
```
Open your browser at http://127.0.0.1:8000
You can also explore the interactive API documentation at `/docs` (Swagger UI)

## 🐳 Docker Setup

The project includes Dockerfiles for each service and a `docker-compose.yml` for orchestration.

### Start services
```
docker compose up --build
```

### Services

* 🚀 **FastAPI**: port `8000` — Serves the backend API
* 🌐 **Nginx**: port `80` — Acts as a reverse proxy and load balancer
* 📈 **Prometheus**: port `9090` — Collects application and system metrics
* 📊 **Grafana**: port `3000` — Visualizes metrics with preconfigured dashboards

### Stop services
```
docker compose down
```

> Tip: Use `docker compose logs -f <service>` to follow real-time logs for any service.

## 📊 Monitoring

* ⏱️ **Prometheus** collects metrics from FastAPI, including request counts, response times, and custom application metrics.
* 📈 **Grafana** visualizes metrics using preconfigured dashboards for easy monitoring of application performance.
* ➕ Add custom dashboards in `grafana/dashboards.yml` or create new ones in the Grafana UI.

> Note: Metrics are automatically exposed at `/metrics` endpoint in FastAPI.

## 🧪 Testing

Unit tests are located in `src/tests`. Run tests using:
```
pytest src/tests
```

> Tip: Use `pytest -v` for verbose output and `pytest --cov=src` to check test coverage.

## 📄 License
This project is licensed under the terms of the LICENSE file.
