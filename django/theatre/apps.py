import sys
from django.apps import AppConfig

class TheatreConfig(AppConfig):
    name = "theatre"       # folder name

    def ready(self):
        # Skip when this code runs inside a Celery worker or beat process
        if "celery" in sys.argv[0]:
            return

        # Queue the long‑running MQTT listener exactly once
        from theatre.tasks import mqtt_listener_task
        mqtt_listener_task.apply_async()       # → mqtt queue
