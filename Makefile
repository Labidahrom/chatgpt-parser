PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) chatgpt_parser.wsgi:application & \
	poetry run celery -A chatgpt_parser worker --loglevel=info

app_start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) --timeout 1600 chatgpt_parser.wsgi:application

celery_start:
	poetry run celery -A chatgpt_parser worker --loglevel=debug

makemigrations:
	poetry run python manage.py makemigrations chatgpt_parser

migrate:
	poetry run python manage.py migrate

lint:
	poetry run flake8 chatgpt_parser

test:
	poetry run python3 manage.py test