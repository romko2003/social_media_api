Social API (Django + DRF + JWT)
Setup & Run
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt   # or `pip install .` if you use pyproject.toml
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Media files

MEDIA_URL = /media/

MEDIA_ROOT = ./media

Documentation

OpenAPI JSON: /api/schema/

Swagger UI: /api/docs/

Authentication (JWT)

Register: POST /api/auth/register/

{ "username": "romko", "email": "r@example.com", "password": "StrongPass123!" }


Obtain tokens: POST /api/auth/jwt/create/

{ "username": "romko", "password": "StrongPass123!" }


Refresh: POST /api/auth/jwt/refresh/

{ "refresh": "<refresh>" }


Verify: POST /api/auth/jwt/verify/

{ "token": "<access>" }


Logout (blacklist): POST /api/auth/logout/

{ "refresh": "<refresh>" }

Profiles

My profile: GET /api/auth/profiles/me/

Update my profile: PATCH /api/auth/profiles/me/ (use multipart/form-data for avatar)

Browse/search profiles: GET /api/auth/profiles/?search=<text>

Profile by ID: GET /api/auth/profiles/{id}/

Follow: POST /api/auth/profiles/{id}/follow/

Unfollow: POST /api/auth/profiles/{id}/unfollow/

Followers/following lists:

GET /api/auth/profiles/{id}/followers/

GET /api/auth/profiles/{id}/following/

Posts

Create: POST /api/posts/ (JSON or multipart: text, optional image)

List:

All posts: GET /api/posts/

Feed (only followed users + own): GET /api/posts/?feed=1

By author: GET /api/posts/?author=romko

By hashtag: GET /api/posts/?hashtag=python

Search in text: GET /api/posts/?search=data

Retrieve/update/delete: GET|PATCH|DELETE /api/posts/{id}/ (only the author can edit/delete)

Like: POST /api/posts/{id}/like/

Unlike: POST /api/posts/{id}/unlike/

Posts I liked: GET /api/posts/liked/

Comments

List/add comments to a post: GET|POST /api/posts/{id}/comments/

CRUD comment (only your own): GET|PATCH|DELETE /api/comments/{id}/

Scheduled Posts (Celery, optional)

Create scheduled post:
POST /api/scheduled-posts/

{ "text": "Hello future!", "publish_at": "2025-10-01T18:00:00Z" }


List my scheduled posts: GET /api/scheduled-posts/

Delete scheduled post: DELETE /api/scheduled-posts/{id}/

Celery setup

You need Redis and Celery workers running:

# start redis
redis-server

# start celery worker & beat
celery -A socialapi worker -l info
celery -A socialapi beat -l info


Configure a periodic task (e.g., every 60 sec) for posts.tasks.publish_scheduled_posts using Celery Beat or crontab.

Security & Best Practices

Only owners can edit/delete their posts, comments, and profiles.

Passwords validated with Django’s standard validators.

Hashtags automatically extracted from post text.

API fully documented via /api/docs/ (Swagger).

For production: disable DEBUG, configure ALLOWED_HOSTS, move secrets to .env, set up HTTPS, and use S3/cloud storage for media.
