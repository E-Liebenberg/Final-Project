from django.shortcuts import render
from django.http import JsonResponse
import paho.mqtt.publish as publish
import os
from dotenv import load_dotenv
from .models import Theatre
import paho.mqtt.client as mqtt
from theatre.models import TheatreLog
import csv
from django.http import HttpResponse

# Load environment variables (MQTT settings)
load_dotenv()

# Dashboard page
# def dashboard_view(request):
#     theatres = Theatre.objects.values_list('theatre_id', flat=True).distinct()
#     print("Theatres in DB:", list(theatres))  # ✅ Debug output
#     return render(request, 'theatre/dashboard.html', {'theatres': theatres})
# theatre/views.py (snippet)
# theatre/views.py
def dashboard_view(request):
    theatres = list(Theatre.objects.values_list('theatre_id', flat=True).distinct())
    default_theatre = theatres[0] if theatres else "theatre"
    return render(request, 'theatre/dashboard.html', {
        'theatres': theatres,
        'default_theatre': default_theatre,
    })

# Toggle LED endpoint
def toggle_led(request):
    led = request.GET.get("led")
    theatre = request.GET.get("theatre", "theatre1")

    if not led:
        return JsonResponse({"status": "error", "message": "Missing LED parameter"}, status=400)

    topic = f"{theatre}/led/{led}"
    payload = "toggle"

    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", None)
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None)

    client = mqtt.Client()

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        client.publish(topic, payload=payload)
        client.loop_stop()
        client.disconnect()
        return JsonResponse({"status": "ok", "topic": topic})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
def theatre_history(request):
    theatre_id = request.GET.get('theatre')
    if not theatre_id:
        return JsonResponse({"error": "Missing theatre"}, status=400)

    logs = (
        TheatreLog.objects
        .filter(theatre_id=theatre_id, topic__in=[
            f"{theatre_id}/temperature",
            f"{theatre_id}/humidity"
        ])
        .order_by('-timestamp')[:50]
    )
    data = {'temperature': [], 'humidity': []}
    for log in logs:
        raw = log.value.replace('°C','').replace('%','').strip()
        try:
            val = float(raw)
        except ValueError:
            continue
        if 'temperature' in log.topic:
            data['temperature'].append({'timestamp': log.timestamp.isoformat(), 'value': val})
        else:
            data['humidity'].append({'timestamp': log.timestamp.isoformat(), 'value': val})
    return JsonResponse(data)

def code_blue_history(request):
    theatre_id = request.GET.get('theatre')
    logs = (
        TheatreLog.objects
        .filter(theatre_id=theatre_id, topic=f"{theatre_id}/led/code_blue")
        .order_by('-timestamp')[:20]
    )
    return JsonResponse([{
        'value': log.value,
        'timestamp': log.timestamp.isoformat()
    } for log in logs], safe=False)


# tablet
def download_csv(request):
    theatre = request.GET.get('theatre')
    logs = TheatreLog.objects.filter(topic__startswith=theatre).order_by('-timestamp')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=\"{theatre}_history.csv\"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Topic', 'Value'])

    for log in logs:
        writer.writerow([log.timestamp.strftime('%Y-%m-%d %H:%M:%S'), log.topic, log.value])

    return response