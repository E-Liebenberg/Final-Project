# bedside/tasks.py
from celery import shared_task
from bedside.mqtt_listener import main           # ← now valid path!

@shared_task(bind=True, queue="mqtt",
             name="bedside.tasks.mqtt_listener_task",
             ignore_result=True)
def mqtt_listener_task(self):
    main()  # never returns
