# 🛒 ProDev E-Commerce Backend

## 📌 Overview
The **ProDev E-Commerce Backend** is a backend API built with **Django** and **Django REST Framework (DRF)**.  
It powers an e-commerce platform with authentication, product catalog, and API documentation.  

### ✨ Features
- 🔑 JWT Authentication (secure login & token refresh)
- 📦 Products & Categories (CRUD operations)
- 🔍 Filtering (by category, price range)
- ↕️ Sorting & Pagination
- 📑 API Documentation with Swagger (via drf-spectacular)
- 🐳 Docker support
- 🧪 Unit tests for core features

---

## ⚡ Quick Start (Local Development)

### 1️⃣ Clone the repo
```bash
git clone https://github.com/Wege0921/prodev-be-ecommerce.git
cd prodev-be-ecommerce


## Quick start (local)
1. Create virtualenv:
   python -m venv .venv
   source .venv/bin/activate

2. Install deps:
   pip install -r requirements.txt

3. Create `.env` from `.env.example` and set DB credentials

4. Run migrations and create superuser:
   python manage.py migrate
   python manage.py createsuperuser

5. Run dev server:
   python manage.py runserver

## Docker
docker compose up --build

## API Docs
- Schema: /api/schema/
- Swagger UI: /api/docs/swagger/
