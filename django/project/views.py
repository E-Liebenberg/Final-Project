from django.shortcuts import render
# core/views.py
import json, os, paho.mqtt.publish as mqtt_publish
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def home(request):
    return render(request, 'home.html')

@csrf_exempt
@require_POST
def mqtt_publish_view(request):
    """
    POST  {"topic": "...", "payload": "..."}
    Publishes a single MQTT message and returns {"status": "ok"}.
    """
    data = json.loads(request.body)
    mqtt_publish.single(
        topic   = data["topic"],
        payload = data.get("payload", ""),
        qos     = 0,
        hostname= settings.MQTT_HOST,
        port    = settings.MQTT_PORT,
        auth    = {
            "username": os.getenv("MQTT_USERNAME") or os.getenv("MQTT_USER"),
            "password": os.getenv("MQTT_PASSWORD") or os.getenv("MQTT_PASS"),
        },
    )
    return JsonResponse({"status": "ok"})