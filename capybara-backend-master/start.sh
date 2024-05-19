#!/bin/sh
# python3 manage.py makemigrations board
python3 manage.py migrate

# Run with uWSGI
# uwsgi --module=CapyBack.wsgi:application \
#     --env DJANGO_SETTINGS_MODULE=CapyBack.settings \
#     --master \
#     --http=0.0.0.0:80 \
#     --processes=5 \
#     --harakiri=20 \
#     --max-requests=5000 \
#     --vacuum

# Run with Daphne using ASGI
daphne -p 80 -b 0.0.0.0 CapyBack.asgi:application

# gunicorn 'CapyBack.wsgi' -b 0.0.0.0:8000 --access-logfile - --log-level info