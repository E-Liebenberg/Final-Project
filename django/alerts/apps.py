# from django.apps import AppConfig


# class AlertsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'alerts'
import sys
from django.apps import AppConfig

class AlertsConfig(AppConfig):
    name = "alerts"

    def ready(self):
        if "celery" in sys.argv[0]:
            return

        from alerts.tasks import mqtt_listener_task
        mqtt_listener_task.apply_async()       # → mqtt queue