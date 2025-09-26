# Makefile for Django + Docker project

# Variables
PYTHON=python
PIP=pip
DJANGO_MANAGE=$(PYTHON) manage.py
WEB=web
DB=db

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make run            - Run Django development server (local)"
	@echo "  make migrate        - Apply database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser- Create Django superuser"
	@echo "  make shell          - Open Django shell"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run flake8 linter"
	@echo "  make freeze         - Export dependencies to requirements.txt"
	@echo "  make clean          - Remove pycache and migration files"
	@echo "  make up             - Start Docker containers"
	@echo "  make down           - Stop Docker containers"
	@echo "  make clean-docker   - Remove containers + volumes"

# --------------------
# Django commands
# --------------------
install:
	$(PIP) install -r requirements.txt

run:
	$(DJANGO_MANAGE) runserver

migrate:
	$(DJANGO_MANAGE) migrate

makemigrations:
	$(DJANGO_MANAGE) makemigrations

createsuperuser:
	$(DJANGO_MANAGE) createsuperuser

shell:
	$(DJANGO_MANAGE) shell

test:
	$(DJANGO_MANAGE) test

lint:
	flake8 .

freeze:
	$(PIP) freeze > requirements.txt

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -path "*/migrations/*.py" ! -name "__init__.py" -delete

# --------------------
# Docker commands
# --------------------
up:
	docker compose up --build

down:
	docker compose down

clean-docker:
	docker compose down -v

migrate-docker:
	docker compose run --rm $(WEB) python manage.py migrate

makemigrations-docker:
	docker compose run --rm $(WEB) python manage.py makemigrations

collectstatic:
	docker compose run --rm $(WEB) python manage.py collectstatic --noinput

shell-docker:
	docker compose run --rm $(WEB) python manage.py shell

test-docker:
	docker compose run --rm $(WEB) pytest
