# Portfolio Backend — Setup Guide

Complete setup guide for the Django REST API backend powering the developer
portfolio sites. Follow these steps to get the project running locally.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Install uv (Package Manager)](#3-install-uv-package-manager)
4. [Create Virtual Environment & Install Dependencies](#4-create-virtual-environment--install-dependencies)
5. [PostgreSQL Setup](#5-postgresql-setup)
6. [Environment Variables](#6-environment-variables)
7. [Run Migrations](#7-run-migrations)
8. [Create Superuser](#8-create-superuser)
9. [Seed the Database](#9-seed-the-database)
10. [Run the Development Server](#10-run-the-development-server)
11. [Verify the Setup](#11-verify-the-setup)
12. [Project Structure](#12-project-structure)
13. [Apps Overview](#13-apps-overview)
14. [API Endpoints](#14-api-endpoints)
15. [Common Commands](#15-common-commands)

---

## 1. Prerequisites

| Tool       | Version  | Notes                                   |
| ---------- | -------- | --------------------------------------- |
| Python     | ≥ 3.12   | Required by Django 6.x                  |
| PostgreSQL | ≥ 14     | Any recent version works                |
| uv         | ≥ 0.9    | Fast Python package manager (see below) |
| Git        | any      | For cloning the repo                    |

> **Windows users**: Run everything inside **WSL 2** (Ubuntu recommended).
> The project is developed and tested on WSL.

---

## 2. Clone the Repository

```bash
git clone git@github.com:<your-org>/portfolio_backend.git
cd portfolio_backend
```

---

## 3. Install uv (Package Manager)

This project uses [uv](https://docs.astral.sh/uv/) instead of pip for
dependency management. It's significantly faster and handles virtual
environments automatically.

**Linux / macOS / WSL:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
# Expected: uv 0.9.x or newer
```

---

## 4. Create Virtual Environment & Install Dependencies

```bash
# From the project root (portfolio_backend/)
uv sync
```

This single command:
- Creates a `.venv/` virtual environment (Python 3.12)
- Installs all production + dev dependencies from `pyproject.toml`
- Locks versions in `uv.lock`

Activate the venv (needed for running `manage.py` directly):

```bash
source .venv/bin/activate
```

> **Tip**: You can also run commands without activating:
> `uv run python manage.py runserver`

---

## 5. PostgreSQL Setup

### 5a. Install PostgreSQL

**Ubuntu / WSL:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (Homebrew):**

```bash
brew install postgresql@16
brew services start postgresql@16
```

### 5b. Start the Service

```bash
sudo service postgresql start    # Ubuntu / WSL
# or
brew services start postgresql   # macOS
```

### 5c. Create Database & User

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
CREATE USER pf_user WITH PASSWORD 'portfolio_backend';
CREATE DATABASE portfolio_db OWNER pf_user;
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO pf_user;
\q
```

### 5d. Verify Connection

```bash
psql -U pf_user -d portfolio_db -h localhost
# Enter password: portfolio_backend
# If you get a prompt, the connection works. Type \q to exit.
```

> **Note**: If `psql` asks for a password and rejects it, edit
> `/etc/postgresql/<version>/main/pg_hba.conf` and change the local
> auth method from `peer` to `md5` for the `pf_user`, then restart
> PostgreSQL: `sudo service postgresql restart`.

---

## 6. Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env   # if .env.example exists, otherwise create manually
```

**Required `.env` contents:**

```dotenv
# Django
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=django-insecure-replace-this-with-a-real-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS — add your Next.js frontend URL
CORS_ALLOWED_ORIGINS=http://localhost:3000

# PostgreSQL
DB_NAME=portfolio_db
DB_USER=pf_user
DB_PASSWORD=portfolio_backend
DB_HOST=localhost
DB_PORT=5432
```

> **Important**: Never commit `.env` to git. It's already in `.gitignore`.

---

## 7. Run Migrations

```bash
python manage.py migrate
```

Expected output — all migrations applied:

```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying core.0001_initial... OK
  Applying core.0002_alter_profile_bio... OK
  Applying core.0003_alter_sociallink_platform... OK
  Applying bijay_dev.0001_initial... OK
  ...
```

This creates all required tables:

| App        | Tables                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------ |
| `core`     | `core_profile`, `core_sociallink`, `core_contactsubmission`                                |
| `bijay_dev`| `bijay_skillcategory`, `bijay_techstack`, `bijay_project`, `bijay_experience`,              |
|            | `bijay_education`, `bijay_certification`, `bijay_blogcategory`, `bijay_blogtag`,            |
|            | `bijay_blogpost`, `bijay_readinglist`, `bijay_thought`, `bijay_book` + junction tables     |

---

## 8. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.
This account is used to log into Django Admin at `/admin/`.

---

## 9. Seed the Database

The project includes management commands to populate the database with
realistic sample data. Run them in order:

```bash
# Seed core app (Profile, SocialLinks, ContactSubmissions)
python manage.py seed_core

# Seed bijay_dev app (Skills, Projects, Experience, Blog, etc.)
python manage.py seed_bijay
```

**What gets seeded:**

| Command       | Data Created                                                                     |
| ------------- | -------------------------------------------------------------------------------- |
| `seed_core`   | 1 Profile (with placeholder avatar), 5 Social Links, 3 Contact Submissions      |
| `seed_bijay`  | 5 Skill Categories, 23 Tech Stack entries, 5 Projects, 3 Experience entries,     |
|               | 2 Education entries, 3 Certifications, 4 Blog Categories, 8 Blog Tags,          |
|               | 4 Blog Posts, 4 Reading List items, 5 Thoughts, 4 Books                         |

**Options:**

```bash
# Reset and re-seed (flushes existing data first)
python manage.py seed_core --flush
python manage.py seed_bijay --flush
```

Both commands are idempotent — running them again without `--flush` skips
existing records (uses `get_or_create`).

---

## 10. Run the Development Server

```bash
python manage.py runserver
```

The server starts at `http://localhost:8000/`.

---

## 11. Verify the Setup

Open these URLs in your browser to confirm everything is working:

| URL                                          | What it shows                        |
| -------------------------------------------- | ------------------------------------ |
| `http://localhost:8000/admin/`               | Django Admin (login with superuser)  |
| `http://localhost:8000/api/docs/`            | Swagger UI (interactive API docs)    |
| `http://localhost:8000/api/redoc/`           | ReDoc (alternative API docs)         |
| `http://localhost:8000/api/v1/core/profile/` | Portfolio profile JSON               |
| `http://localhost:8000/api/v1/bijay/skills/` | Skill categories JSON                |
| `http://localhost:8000/api/v1/bijay/blog/posts/` | Published blog posts JSON        |

All API responses follow this envelope format:

```json
{
  "status": "success",
  "data": { ... },
  "message": null,
  "meta": { "count": 10, "limit": 10, "offset": 0, "next": "...", "previous": null }
}
```

---

## 12. Project Structure

```
portfolio_backend/
├── manage.py                  # Django management entry point
├── pyproject.toml             # Dependencies & tool config (uv, ruff, pytest)
├── .env                       # Environment variables (not committed)
│
├── config/                    # Project configuration
│   ├── settings/
│   │   ├── base.py            # Shared settings (DRF, CORS, CKEditor, logging)
│   │   ├── dev.py             # Development overrides
│   │   └── prod.py            # Production overrides (SSL, HSTS)
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI entry point
│   └── asgi.py                # ASGI entry point
│
├── common/                    # Shared utilities (no models, no migrations)
│   ├── base_model.py          # TimeStampedModel (UUID pk, created_at, updated_at)
│   ├── constants.py           # Shared constants (pagination, response status, logger names)
│   ├── exceptions.py          # Application-level exceptions (NotFoundError, etc.)
│   ├── exception_handler.py   # Custom DRF exception handler → consistent JSON envelope
│   ├── pagination.py          # LimitOffsetPagination + get_paginated_response()
│   ├── renderers.py           # EnvelopeRenderer — wraps all responses in standard envelope
│   └── responses.py           # success_response() helper
│
├── core/                      # Shared across all portfolio deployments
│   ├── models.py              # Profile (singleton), SocialLink, ContactSubmission
│   ├── serializers.py         # Input/Output serializer pattern
│   ├── views.py               # ProfileViewSet, SocialLinkViewSet, ContactSubmissionViewSet
│   ├── admin.py               # Admin with inline social links, read-only contact list
│   ├── urls.py                # Router → /api/v1/core/
│   └── management/commands/
│       └── seed_core.py       # Seed command for core data
│
├── bijay_dev/                 # Bijay's personal portfolio data
│   ├── models.py              # 12 models (skills, projects, blog, etc.)
│   ├── serializers.py         # 13 output serializers (all read-only)
│   ├── views.py               # 11 ViewSets (all read-only)
│   ├── admin.py               # 12 admin classes with rich previews
│   ├── urls.py                # Router → /api/v1/bijay/
│   └── management/commands/
│       └── seed_bijay.py      # Seed command for bijay_dev data
│
├── media/                     # User-uploaded files (avatars, thumbnails, etc.)
├── staticfiles/               # Collected static files (admin CSS/JS, CKEditor)
├── diagrams/                  # ERD diagrams (Mermaid format)
├── prompts/                   # AI assistant instructions
└── docs/                      # Documentation (you are here)
```

---

## 13. Apps Overview

### `common/` — Shared Utilities

Not a Django app (no models or migrations). Provides reusable building blocks:

- **`TimeStampedModel`** — Abstract base model with UUID primary key, `created_at`, `updated_at`. All models inherit from this.
- **`success_response()`** — Builds the standard `{"status": "success", "data": ..., "message": ...}` envelope.
- **`get_paginated_response()`** — Paginates any queryset using `LimitOffsetPagination` and wraps in the success envelope with `meta` block.
- **`EnvelopeRenderer`** — Global DRF renderer ensuring every response matches the envelope contract.
- **`custom_exception_handler`** — Converts all exceptions (Django, DRF, application-level) into consistent error envelopes.
- **`NotFoundError`, `ApplicationError`** — Domain exceptions that map to HTTP 404/400.

### `core/` — Shared Portfolio Data

Models shared by all portfolio deployments:

| Model               | Purpose                                      | API Endpoints                           |
| ------------------- | -------------------------------------------- | --------------------------------------- |
| `Profile`           | Singleton portfolio owner info (name, bio, avatar) | `GET /api/v1/core/profile/`       |
| `SocialLink`        | Social media links (GitHub, LinkedIn, etc.)  | `GET /api/v1/core/social-links/`        |
| `ContactSubmission` | Visitor contact form messages                | `POST /api/v1/core/contact/`            |

- Profile is a **singleton** — only one row per deployment, enforced at model and admin level.
- Contact form is **rate-limited** to 5 submissions per hour per IP.
- Social links are filtered to only return active links.

### `bijay_dev/` — Bijay's Portfolio

All data specific to Bijay's developer portfolio:

| Model            | Purpose                           | API Endpoint                               |
| ---------------- | --------------------------------- | ------------------------------------------ |
| `SkillCategory`  | Skill groupings (Backend, DevOps) | `GET /api/v1/bijay/skills/`                |
| `TechStack`      | Individual tools/skills           | `GET /api/v1/bijay/tech-stack/`            |
| `Project`        | Portfolio projects                | `GET /api/v1/bijay/projects/`              |
| `Experience`     | Work history                      | `GET /api/v1/bijay/experience/`            |
| `Education`      | Academic history                  | `GET /api/v1/bijay/education/`             |
| `Certification`  | Certificates & achievements       | `GET /api/v1/bijay/certifications/`        |
| `BlogCategory`   | Blog post categories              | `GET /api/v1/bijay/blog/categories/`       |
| `BlogTag`        | Blog post tags                    | `GET /api/v1/bijay/blog/tags/`             |
| `BlogPost`       | Full blog posts with SEO          | `GET /api/v1/bijay/blog/posts/`            |
| `ReadingList`    | Bookmarked articles               | `GET /api/v1/bijay/reading-list/`          |
| `Thought`        | Short personal thoughts           | `GET /api/v1/bijay/thoughts/`              |
| `Book`           | Books with reading progress       | `GET /api/v1/bijay/books/`                 |

All bijay_dev endpoints are **read-only**. Data is managed through Django Admin.

---

## 14. API Endpoints

### Core Endpoints (`/api/v1/core/`)

| Method | Endpoint                          | Description                          |
| ------ | --------------------------------- | ------------------------------------ |
| GET    | `/api/v1/core/profile/`           | Retrieve singleton portfolio profile |
| GET    | `/api/v1/core/social-links/`      | List active social links             |
| GET    | `/api/v1/core/social-links/{id}/` | Retrieve single social link          |
| POST   | `/api/v1/core/contact/`           | Submit contact form (rate limited)   |

### Bijay Endpoints (`/api/v1/bijay/`)

| Method | Endpoint                              | Description                              |
| ------ | ------------------------------------- | ---------------------------------------- |
| GET    | `/api/v1/bijay/skills/`               | List skill categories (nested skills)    |
| GET    | `/api/v1/bijay/skills/{id}/`          | Retrieve single skill category           |
| GET    | `/api/v1/bijay/tech-stack/`           | List all tech stack entries              |
| GET    | `/api/v1/bijay/tech-stack/{id}/`      | Retrieve single tech stack entry         |
| GET    | `/api/v1/bijay/projects/`             | List active projects                     |
| GET    | `/api/v1/bijay/projects/{id}/`        | Retrieve single project                  |
| GET    | `/api/v1/bijay/experience/`           | List work history entries                |
| GET    | `/api/v1/bijay/experience/{id}/`      | Retrieve single experience entry         |
| GET    | `/api/v1/bijay/education/`            | List education entries                   |
| GET    | `/api/v1/bijay/education/{id}/`       | Retrieve single education entry          |
| GET    | `/api/v1/bijay/certifications/`       | List certifications                      |
| GET    | `/api/v1/bijay/certifications/{id}/`  | Retrieve single certification            |
| GET    | `/api/v1/bijay/blog/categories/`      | List blog categories                     |
| GET    | `/api/v1/bijay/blog/categories/{id}/` | Retrieve single blog category            |
| GET    | `/api/v1/bijay/blog/tags/`            | List blog tags                           |
| GET    | `/api/v1/bijay/blog/tags/{id}/`       | Retrieve single blog tag                 |
| GET    | `/api/v1/bijay/blog/posts/`           | List published blog posts                |
| GET    | `/api/v1/bijay/blog/posts/{slug}/`    | Retrieve single blog post (by slug)      |
| GET    | `/api/v1/bijay/reading-list/`         | List reading list items                  |
| GET    | `/api/v1/bijay/reading-list/{id}/`    | Retrieve single reading list item        |
| GET    | `/api/v1/bijay/thoughts/`             | List thoughts                            |
| GET    | `/api/v1/bijay/thoughts/{id}/`        | Retrieve single thought                  |
| GET    | `/api/v1/bijay/books/`                | List books                               |
| GET    | `/api/v1/bijay/books/{id}/`           | Retrieve single book                     |

### Query Parameters

Several list endpoints support filtering:

| Endpoint               | Parameter        | Example                                    |
| ---------------------- | ---------------- | ------------------------------------------ |
| `/bijay/tech-stack/`   | `?is_featured=true` | Only featured skills                     |
| `/bijay/projects/`     | `?is_featured=true` | Only featured projects                   |
| `/bijay/blog/posts/`   | `?category=<slug>`  | Filter by category slug                  |
| `/bijay/blog/posts/`   | `?tag=<slug>`       | Filter by tag slug                       |
| `/bijay/blog/posts/`   | `?is_featured=true` | Only the featured post                   |

All list endpoints support pagination:

| Parameter | Default | Max | Description              |
| --------- | ------- | --- | ------------------------ |
| `limit`   | 10      | 100 | Number of items to return|
| `offset`  | 0       | —   | Starting position        |

### Documentation Endpoints

| URL                | Description                    |
| ------------------ | ------------------------------ |
| `/api/docs/`       | Swagger UI (interactive)       |
| `/api/redoc/`      | ReDoc (clean read-only docs)   |
| `/api/schema/`     | Raw OpenAPI 3.0 schema (JSON)  |

---

## 15. Common Commands

```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Seed database
python manage.py seed_core
python manage.py seed_bijay

# Reset and re-seed
python manage.py seed_core --flush
python manage.py seed_bijay --flush

# Create superuser for Django Admin
python manage.py createsuperuser

# Collect static files (needed before production deployment)
python manage.py collectstatic --noinput

# Run system checks
python manage.py check

# Open Django shell
python manage.py shell

# Run linter
uv run ruff check .

# Run linter with auto-fix
uv run ruff check . --fix

# Run tests
uv run pytest
```

---

## Troubleshooting

### `psycopg2` installation fails

If `psycopg2-binary` fails to install, ensure PostgreSQL dev headers are present:

```bash
sudo apt install libpq-dev python3-dev   # Ubuntu / WSL
```

### Port 8000 already in use

```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### `DJANGO_SETTINGS_MODULE` not set

Ensure `.env` exists in the project root with `DJANGO_SETTINGS_MODULE=config.settings.dev`.
Django reads this automatically via `django-environ`.

### CKEditor 5 static files missing

```bash
python manage.py collectstatic --noinput
```

### Media files not showing in development

Ensure `DEBUG=True` in `.env`. Media files are served by Django's dev server
only when `DEBUG=True` (configured in `config/urls.py`).