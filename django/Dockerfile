# Dockerfile (in the django/ directory)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file from the correct path
COPY project/requirements.txt /app/requirements.txt

# Install Django, Celery, Redis, and other dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the entire project directory
COPY . .

# Expose the Django port
EXPOSE 8000

# Default command (Django runserver)
# CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

CMD ["bash", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 project.asgi:application"]
