#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# collect static files before gunicorn starts
echo "Collecting static files..."
python3 /home/app/web/manage.py collectstatic --noinput




exec "$@"