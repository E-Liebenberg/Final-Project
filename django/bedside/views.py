from django.shortcuts import render

# Create your views here.
# bedside/views.py
from django.views.generic import TemplateView
class BedsideDashboardView(TemplateView):
    template_name = "bedside/dashboard.html"

# core/views.py
import json, os, paho.mqtt.publish as mqtt_publish
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import csv, zoneinfo
from django.http import HttpResponse
from django.views.generic import TemplateView
from bedside.models import SensorReading

class BedsideDashboardView(TemplateView):
    template_name = "bedside/dashboard.html"

def download_csv(request):
    """Return all SensorReading rows as CSV (UTC timestamps)."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="bedsidev3_history.csv"'
    writer = csv.writer(response)
    writer.writerow(["timestamp_utc", "temperature_c", "humidity_pct"])
    for row in SensorReading.objects.order_by("-recorded_at"):
        writer.writerow([row.recorded_at.replace(tzinfo=zoneinfo.ZoneInfo("UTC")),
                         row.temperature, row.humidity])
    return response

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
