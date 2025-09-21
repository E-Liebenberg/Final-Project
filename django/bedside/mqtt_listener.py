# """
# Blocking MQTT loop for the bedside unit.

# A Celery task (bedside.tasks.mqtt_listener_task) calls `main()`
# once at worker start‑up; this file must NOT start the MQTT loop
# when it is merely imported.
# """

# import os
# import paho.mqtt.client as mqtt
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# from bedside.models import BedsideUnit, Alert, SensorReading, RFIDTagLog

# # ───────────────────────────────────────────────────────────────────────────
# BED_ID = "bedsidev3"
# PREFIX = f"{BED_ID}/"
# channel_layer = get_channel_layer()


# def _broadcast(event_type: str, data: dict):
#     """Send a payload to the WebSocket group `bedsidev3_updates`."""
#     async_to_sync(channel_layer.group_send)(
#         f"{BED_ID}_updates",
#         {"type": "bedside.update", "event": event_type, "data": data},
#     )


# # ───────────────────────────────────────────────────────────────────────────
# def main():
#     """Connect to the MQTT broker and run `loop_forever()` (never returns)."""
#     mqtt_host = os.getenv("MQTT_HOST", "mqtt")
#     mqtt_port = int(os.getenv("MQTT_PORT", 1883))
#     mqtt_user = os.getenv("MQTT_USERNAME") or os.getenv("MQTT_USER")
#     mqtt_pass = os.getenv("MQTT_PASSWORD") or os.getenv("MQTT_PASS")

#     client = mqtt.Client()
#     if mqtt_user and mqtt_pass:
#         client.username_pw_set(mqtt_user, mqtt_pass)

#     # ── MQTT Callbacks ───────────────────────────────────────────────────
#     def on_connect(clt, userdata, flags, rc):
#         print(f"[Bedside MQTT] Connected (rc={rc})")
#         if rc == 0:
#             clt.subscribe(f"{PREFIX}#")
#             print(f"[MQTT] Subscribed → {PREFIX}#")

#     def on_message(clt, userdata, msg):
#         topic_rel = msg.topic[len(PREFIX):]  # strip "bedsidev3/"
#         payload   = msg.payload.decode()

#         unit, _ = BedsideUnit.objects.get_or_create(bed_id=BED_ID)

#         match topic_rel.split("/"):
#             # ── Alert buttons ──────────────────────────────────────────
#             case ["nursecall", "code_blue"]:
#                 Alert.objects.create(unit=unit, alert_type=Alert.Type.CODE_BLUE)
#                 _broadcast("code_blue", {"active": True})

#             case ["nursecall", "nurse_call"]:
#                 Alert.objects.create(unit=unit, alert_type=Alert.Type.NURSE_CALL)
#                 _broadcast("nurse_call", {"active": True})

#             case ["nursecall", "no_movement"]:
#                 Alert.objects.create(unit=unit, alert_type=Alert.Type.NO_MOVEMENT)
#                 _broadcast("no_movement", {"active": True})

#             # ── Environment (DHT22) ────────────────────────────────────
#             case ["nursecall", "temperature"]:
#                 SensorReading.objects.create(
#                     unit=unit, temperature=float(payload), humidity=None
#                 )
#                 _broadcast("temperature", {"value": payload})

#             case ["nursecall", "humidity"]:
#                 latest = SensorReading.objects.filter(unit=unit).latest("recorded_at")
#                 latest.humidity = float(payload)
#                 latest.save(update_fields=["humidity"])
#                 _broadcast("humidity", {"value": payload})

#             # ── RFID tag scans ─────────────────────────────────────────
#             case ["rfid", "tag"]:
#                 RFIDTagLog.objects.create(unit=unit, tag_uid=payload)
#                 _broadcast("rfid_tag", {"uid": payload})

#             # ── Room‑light status (GPIO 26) ───────────────────────────
#             case ["room", "light", "status"]:          # payload = "on"/"off"
#                 _broadcast("room_light", {"state": payload})
            
#             # ── Environment readings ────────────────────────────────────────────────
#             case ["temperature"] | ["nursecall", "temperature"]:
#                 t = float(payload)
#                 SensorReading.objects.create(unit=unit, temperature=t, humidity=None)
#                 _broadcast("temperature", {"value": t})

#             case ["humidity"] | ["nursecall", "humidity"]:
#                 h = float(payload)
#                 # update latest row or create if none
#                 latest = SensorReading.objects.filter(unit=unit).order_by("-recorded_at").first()
#                 if latest and latest.temperature is not None and latest.humidity is None:
#                     latest.humidity = h
#                     latest.save(update_fields=["humidity"])
#                 else:
#                     SensorReading.objects.create(unit=unit, temperature=None, humidity=h)
#                 _broadcast("humidity", {"value": h})

#             # ── Anything else: ignore ─────────────────────────────────
#             case _:
#                 pass

#     # ── Boot the client and block forever ───────────────────────────────
#     client.on_connect = on_connect
#     client.on_message = on_message

#     print(f"[MQTT] Connecting → {mqtt_host}:{mqtt_port}")
#     client.connect(mqtt_host, mqtt_port, 60)
#     client.loop_forever()

"""
Blocking MQTT loop for the bedside unit.

A Celery task (bedside.tasks.mqtt_listener_task) calls `main()`
once at worker start‑up; this file must NOT start the MQTT loop
when it is merely imported.
"""

import os
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from bedside.models import BedsideUnit, Alert, SensorReading, RFIDTagLog

# ───────────────────────────────────────────────────────────────────────────
BED_ID = "bedsidev3"
PREFIX = f"{BED_ID}/"
channel_layer = get_channel_layer()


def _broadcast(event_type: str, data: dict):
    """Send a payload to the WebSocket group `bedsidev3_updates`."""
    async_to_sync(channel_layer.group_send)(
        f"{BED_ID}_updates",
        {"type": "bedside.update", "event": event_type, "data": data},
    )


# ───────────────────────────────────────────────────────────────────────────
def main():
    """Connect to the MQTT broker and run `loop_forever()` (never returns)."""
    mqtt_host = os.getenv("MQTT_HOST", "mqtt")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    mqtt_user = os.getenv("MQTT_USERNAME") or os.getenv("MQTT_USER")
    mqtt_pass = os.getenv("MQTT_PASSWORD") or os.getenv("MQTT_PASS")

    client = mqtt.Client()
    if mqtt_user and mqtt_pass:
        client.username_pw_set(mqtt_user, mqtt_pass)

    # ── MQTT Callbacks ───────────────────────────────────────────────────
    def on_connect(clt, userdata, flags, rc):
        print(f"[Bedside MQTT] Connected (rc={rc})")
        if rc == 0:
            clt.subscribe(f"{PREFIX}#")
            print(f"[MQTT] Subscribed → {PREFIX}#")

    def on_message(clt, userdata, msg):
        topic_rel = msg.topic[len(PREFIX):]  # strip "bedsidev3/"
        payload   = msg.payload.decode()

        unit, _ = BedsideUnit.objects.get_or_create(bed_id=BED_ID)

        match topic_rel.split("/"):
            # ── Alert buttons ──────────────────────────────────────────
            case ["nursecall", "code_blue"]:
                Alert.objects.create(unit=unit, alert_type=Alert.Type.CODE_BLUE)
                _broadcast("code_blue", {"active": True})

            case ["nursecall", "nurse_call"]:
                Alert.objects.create(unit=unit, alert_type=Alert.Type.NURSE_CALL)
                _broadcast("nurse_call", {"active": True})

            case ["nursecall", "no_movement"]:
                Alert.objects.create(unit=unit, alert_type=Alert.Type.NO_MOVEMENT)
                _broadcast("no_movement", {"active": True})

            # ── Environment: temperature & humidity (accept both topic styles) ──
            case ["temperature"] | ["nursecall", "temperature"]:
                try:
                    value = float(payload.split()[0])  # handles "19.3" or "19.3 °C"
                except ValueError:
                    print(f"[MQTT] Bad temperature payload: {payload}")
                    return
                SensorReading.objects.create(unit=unit, temperature=value, humidity=None)
                _broadcast("temperature", {"value": value})

            case ["humidity"] | ["nursecall", "humidity"]:
                try:
                    value = float(payload.split()[0])  # handles "46.5" or "46.5 %"
                except ValueError:
                    print(f"[MQTT] Bad humidity payload: {payload}")
                    return

                latest = (
                    SensorReading.objects.filter(unit=unit)
                    .order_by("-recorded_at")
                    .first()
                )
                if latest and latest.humidity is None:
                    latest.humidity = value
                    latest.save(update_fields=["humidity"])
                else:
                    SensorReading.objects.create(unit=unit, temperature=None, humidity=value)

                _broadcast("humidity", {"value": value})


            # ── Anything else: ignore ─────────────────────────────────
            case _:
                pass

    # ── Boot the client and block forever ───────────────────────────────
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[MQTT] Connecting → {mqtt_host}:{mqtt_port}")
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
