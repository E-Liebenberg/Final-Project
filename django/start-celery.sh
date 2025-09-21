#!/bin/bash

echo "[BOOT] Starting Celery worker..."
celery -A project worker --loglevel=info &

# Wait for Celery worker to initialize
sleep 5

echo "[BOOT] Triggering MQTT listener..."
celery -A project call alerts.tasks.mqtt_listener_task
celery -A project call theatre.tasks.mqtt_listener_task

# Keep the container running
wait
