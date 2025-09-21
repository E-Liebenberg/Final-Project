# bedside/apps.py
import sys
from django.apps import AppConfig

class BedsideConfig(AppConfig):
    name = "bedside"

    def ready(self):
        """
        Queue the MQTT listener exactly once per Django boot.
        We skip when this code is imported inside Celery workers,
        because they have their own copy of the listener loop.
        """
        if "celery" in sys.argv[0]:          # running under `celery worker` or `celery beat`
            return

        from bedside.tasks import mqtt_listener_task
        mqtt_listener_task.apply_async()     # one job → mqtt queue
