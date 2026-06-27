# Blog API

A full-featured blog REST API built with Django REST Framework and JWT authentication.

## Features

- Post management (CRUD) with slug and status workflow
- Nested comments with reply support (django-mptt)
- Like/Dislike system for posts and comments
- JWT Authentication
- Category filtering and search
- Interactive API documentation (Swagger)

## Tech Stack

- Python / Django
- Django REST Framework
- SimpleJWT
- django-mptt
- drf-spectacular (Swagger)

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/posts/` | GET | No | List published posts |
| `/api/posts/` | POST | Yes | Create post |
| `/api/posts/<slug>/` | GET | No | Post detail |
| `/api/posts/<slug>/` | PUT/DELETE | Yes | Edit/Delete post |
| `/api/posts/<slug>/comments/` | GET/POST | No/Yes | Comments |
| `/api/posts/<slug>/reaction/` | POST | Yes | Like/Dislike |
| `/api/comments/<id>/like/` | POST | Yes | Like comment |
| `/api/categories/` | GET | No | Categories |
| `/api/token/` | POST | No | Get JWT token |
| `/api/token/refresh/` | POST | No | Refresh token |
| `/api/docs/` | GET | No | Swagger UI |

## Setup

```bash
git clone <repo>
cd blog-api
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Docs

After running, visit: `http://127.0.0.1:8000/api/docs/`
