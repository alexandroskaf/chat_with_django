# Build stage: Use an Alpine-based image with pandas installed
FROM nickgryg/alpine-pandas AS builder

# Set working directory for the build stage
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    postgresql-dev

RUN pip install --no-binary :all: PyNaCl

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    libpq-dev \
    && pip install --upgrade pip

# Copy the requirements.txt and install dependencies to generate wheels
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Main stage: Use Python 3.10 Alpine image (instead of slim)
FROM python:3.10-alpine

# Set the working directory
WORKDIR /usr/src/app

# Set environment variables for the app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the Python path explicitly
ENV PYTHONPATH=/home/app/web

# Install required system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    libpq-dev \
    libffi-dev

# Create necessary directories and app user
RUN mkdir -p /home/app/web /home/app/web/static /home/app/web/user_files
RUN addgroup --system app && adduser --system --ingroup app app

# Set environment variables for the app home
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# Copy wheels from the builder stage
COPY --from=builder /usr/src/app/wheels /wheels

# Install dependencies from the wheels directory
RUN pip install --no-cache /wheels/*

# Copy the project files into the container
COPY ./entrypoint.sh $APP_HOME
COPY . $APP_HOME
WORKDIR $APP_HOME
# Set ownership of all files to the app user
RUN chown -R app:app $APP_HOME

# Switch to the app user
USER app
RUN python manage.py collectstatic --noinput

# Expose the necessary port
EXPOSE 8081

# Start the server with Gunicorn
CMD ["daphne", "djangochat.asgi:application", "-b", "0.0.0.0", "-p", "8081"]
