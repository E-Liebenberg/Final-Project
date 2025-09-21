from django.conf import settings
import paho.mqtt.publish as publish
import json
import traceback
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from remotes.models import Remote
from patients.models import Patient
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


LED_MAP = {
    "1": "nurse",
    "2": "light",
    "3": "volume_up",
    "4": "volume_down",
    "5": "channel_up",
    "6": "channel_down",
    "7": "tv_power"
}

IR_ENABLED = {"volume_up", "volume_down", "channel_up", "channel_down", "tv_power"}

@csrf_exempt
def publish_command(request):
    if request.method != "POST":
        return JsonResponse({"status": "failed", "reason": "POST only"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        remote_id = data.get("remote_id") or data.get("mac")
        led_id = str(data.get("led_id"))
        state = data.get("state")

        if not remote_id:
            return JsonResponse({"status": "error", "message": "Missing remote_id"}, status=400)

        # Handle sync request
        if led_id == "sync":
            topic = f"nursecall/{remote_id}/get_led_states"
            payload = "sync"
        else:
            if led_id not in LED_MAP:
                return JsonResponse({"status": "error", "message": "Invalid led_id"}, status=400)

            led_name = LED_MAP[led_id]
            topic = f"nursecall/{remote_id}/led/{led_name}/set"
            payload = "ON" if state else "OFF"

        print(f"[MQTT PUBLISH] Topic: {topic} | Payload: {payload}")

        # Optionally also send an IR command if applicable
        if state and led_name in IR_ENABLED:
            ir_topic = f"nursecall/{remote_id}/ir/{led_name}"
            publish.single(
                ir_topic,
                payload="send",
                hostname=settings.MQTT_HOST,
                port=int(settings.MQTT_PORT),
                auth={
                    "username": settings.MQTT_USERNAME,
                    "password": settings.MQTT_PASSWORD
                }
            )
            print(f"[IR] Sent IR command → {ir_topic}")
        
        # Publish the LED toggle
        publish.single(
            topic,
            payload=payload,
            hostname=settings.MQTT_HOST,
            port=int(settings.MQTT_PORT),
            auth={
                "username": settings.MQTT_USERNAME,
                "password": settings.MQTT_PASSWORD
            }
        )
        print(f"[MQTT] Published to {topic} → {payload}")

        # Send LED state update via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"remote_{remote_id}",
            {
                "type": "led_state_update",  # Frontend listens for this type
                "led_name": led_name,
                "led_state": payload,
            }
        )

        return JsonResponse({
            "status": "success",
            "topic": topic,
            "payload": payload
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # <-- Add this line
        print(f"[ERROR] MQTT Publish failed: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def remote_dashboard(request, remote_id):
    try:
        remote = Remote.objects.get(remote_id=remote_id)
    except Remote.DoesNotExist:
        return render(request, "dashboard/remote_not_found.html", {"remote_id": remote_id})

    # Request sync on page load
    try:
        publish.single(
            topic=f"nursecall/{remote.remote_id}/get_led_states",
            payload="sync",
            hostname=settings.MQTT_HOST,
            port=int(settings.MQTT_PORT),
            auth={
                "username": settings.MQTT_USERNAME,
                "password": settings.MQTT_PASSWORD,
            }
        )
        print(f"[SYNC] Requested LED state sync for {remote.remote_id}")
    except Exception as e:
        print(f"[SYNC ERROR] Failed to sync state: {e}")

    button_labels = [
        "Nurse Call",
        "Light Toggle",
        "Volume +",
        "Volume -",
        "Channel +",
        "Channel -",
        "TV Power"
    ]

    LED_MAP = {
        "1": "nurse",
        "2": "light",
        "3": "volume_up",
        "4": "volume_down",
        "5": "channel_up",
        "6": "channel_down",
        "7": "tv_power"
    }

    return render(request, "dashboard/remote_dashboard.html", {
        "remote": remote,
        "button_labels": button_labels,
        "led_map": json.dumps(LED_MAP)
    })