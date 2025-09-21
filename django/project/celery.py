# # project/celery.py
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # Set the default Django settings module
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# app = Celery("project")

# # Load task modules from all registered Django app configs.
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")

# project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module for 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# Create Celery application
app = Celery("project")

# Load task settings from Django's settings.py using the 'CELERY_' namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all registered Django app configs
app.autodiscover_tasks()
