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
"""
Blocking MQTT loop for the bedside unit.

A Celery task (bedside.tasks.mqtt_listener_task) calls `main()`
once at worker start-up; this file must NOT start the MQTT loop
when it is merely imported.
"""
import os
import re
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from bedside.models import BedsideUnit, Alert, SensorReading  # add RFIDTagLog if you have it

# ───────────────────────────────────────────────────────────────────────────
BED_ID = "bedsidev3"
PREFIX        = f"{BED_ID}/"         # message triggers / custom topics
UNIT_PREFIX   = f"{BED_ID}_unit/"    # ESPHome entity topics (sensor/switch/binary_sensor/...)
channel_layer = get_channel_layer()

# Precompiled matchers for ESPHome topics we care about
RE_TEMP   = re.compile(rf"^{re.escape(UNIT_PREFIX)}sensor/bedsidev3_room_temperature/state$")
RE_HUM    = re.compile(rf"^{re.escape(UNIT_PREFIX)}sensor/bedsidev3_room_humidity/state$")
RE_RFID   = re.compile(rf"^{re.escape(UNIT_PREFIX)}sensor/bedsidev3_last_rfid_tag/state$")
RE_CB_BTN = re.compile(rf"^{re.escape(UNIT_PREFIX)}binary_sensor/bedsidev3_code_blue_button/state$")
RE_NC_BTN = re.compile(rf"^{re.escape(UNIT_PREFIX)}binary_sensor/bedsidev3_nurse_call_button/state$")
RE_LIGHT_STATE = re.compile(rf"^{re.escape(UNIT_PREFIX)}switch/bedsidev3_room_light/state$")
RE_MOTION = re.compile(rf"^{re.escape(UNIT_PREFIX)}binary_sensor/bedsidev3_pir_motion_sensor/state$")  # optional

def _broadcast(event_type: str, data: dict):
    """Send a payload to the WebSocket group `bedsidev3_updates`."""
    async_to_sync(channel_layer.group_send)(
        f"{BED_ID}_updates",
        {"type": "bedside.update", "event": event_type, "data": data},
    )

def _parse_number(payload: str) -> float | None:
    """Extract a float from payloads like '19.3' or '19.3 °C'."""
    try:
        return float(payload.strip().split()[0])
    except Exception:
        return None

def _on_esphome_topic(unit: BedsideUnit, topic: str, payload: str):
    """Handle ESPHome topics under bedsidev3_unit/... and broadcast normalized events."""
    # Temperature
    if RE_TEMP.match(topic):
        value = _parse_number(payload)
        if value is None:
            print(f"[MQTT] Bad temperature payload: {payload}")
            return
        SensorReading.objects.create(unit=unit, temperature=value, humidity=None)
        _broadcast("temperature", {"value": value})
        return

    # Humidity
    if RE_HUM.match(topic):
        value = _parse_number(payload)
        if value is None:
            print(f"[MQTT] Bad humidity payload: {payload}")
            return
        # Try to attach humidity to the latest temp row if it's missing humidity
        latest = SensorReading.objects.filter(unit=unit).order_by("-recorded_at").first()
        if latest and latest.humidity is None:
            latest.humidity = value
            latest.save(update_fields=["humidity"])
        else:
            SensorReading.objects.create(unit=unit, temperature=None, humidity=value)
        _broadcast("humidity", {"value": value})
        return

    # RFID last tag (text sensor)
    if RE_RFID.match(topic):
        tag = payload.strip()
        # If you have RFIDTagLog, store it here
        # RFIDTagLog.objects.create(unit=unit, tag=tag)
        _broadcast("rfid_tag", {"value": tag})
        return

    # Code Blue button (binary sensor ON/OFF)
    if RE_CB_BTN.match(topic):
        on = payload.strip().upper() == "ON"
        if on:
            Alert.objects.create(unit=unit, alert_type=Alert.Type.CODE_BLUE)
        _broadcast("code_blue", {"active": on})
        return

    # Nurse Call button (binary sensor ON/OFF)
    if RE_NC_BTN.match(topic):
        on = payload.strip().upper() == "ON"
        if on:
            Alert.objects.create(unit=unit, alert_type=Alert.Type.NURSE_CALL)
        _broadcast("nurse_call", {"active": on})
        return

    # Room Light switch state
    if RE_LIGHT_STATE.match(topic):
        state = payload.strip().lower()  # 'on' / 'off'
        _broadcast("room_light", {"state": state})
        return

    # Optional: motion → you might map to your own semantics if needed
    if RE_MOTION.match(topic):
        on = payload.strip().upper() == "ON"
        # If you want a dedicated event, broadcast here; not mapped to 'no_movement' by default
        return

    # Unknown ESPHome topic: ignore
    # print("[MQTT] Ignored ESPHome topic:", topic, payload)

def _on_custom_topic(unit: BedsideUnit, topic_rel: str, payload: str):
    """
    Handle your custom topics under bedsidev3/... (eg message triggers/acks).
    These are the ones you already use for acks and manual control.
    """
    parts = topic_rel.split("/")

    # bedsidev3/nursecall/code_blue → mark active
    if parts == ["nursecall", "code_blue"]:
        Alert.objects.create(unit=unit, alert_type=Alert.Type.CODE_BLUE)
        _broadcast("code_blue", {"active": True})
        return

    if parts == ["nursecall", "nurse_call"]:
        Alert.objects.create(unit=unit, alert_type=Alert.Type.NURSE_CALL)
        _broadcast("nurse_call", {"active": True})
        return

    if parts == ["nursecall", "no_movement"]:
        Alert.objects.create(unit=unit, alert_type=Alert.Type.NO_MOVEMENT)
        _broadcast("no_movement", {"active": True})
        return

    # room light set command is handled by the device; we only mirror its STATE from ESPHome topics
    # Unknown custom topic: ignore

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

    def on_connect(clt, userdata, flags, rc):
        print(f"[Bedside MQTT] Connected (rc={rc})")
        if rc == 0:
            # Subscribe to BOTH prefixes
            clt.subscribe(f"{PREFIX}#")
            clt.subscribe(f"{UNIT_PREFIX}#")
            print(f"[MQTT] Subscribed → {PREFIX}# and {UNIT_PREFIX}#")

    def on_message(clt, userdata, msg):
        topic   = msg.topic
        payload = msg.payload.decode(errors="ignore")

        unit, _ = BedsideUnit.objects.get_or_create(bed_id=BED_ID)

        if topic.startswith(UNIT_PREFIX):
            _on_esphome_topic(unit, topic, payload)
        elif topic.startswith(PREFIX):
            # strip "bedsidev3/" for compatibility with your previous code path
            topic_rel = topic[len(PREFIX):]
            _on_custom_topic(unit, topic_rel, payload)
        else:
            # Not our device
            pass

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[MQTT] Connecting → {mqtt_host}:{mqtt_port}")
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
