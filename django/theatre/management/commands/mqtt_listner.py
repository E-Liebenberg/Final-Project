# theatre/management/commands/theatre_mqtt_listener.py
import os, re, asyncio
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from theatre.models import Theatre, TheatreLog

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Subscribe to ESPHome's real topics
TOPIC_SUBS = [
    "+/sensor/+/state",     # e.g. theatre/sensor/theatre_temperature/state
    "+/switch/+/state",     # e.g. theatre/switch/theatre_led_-_clean/state
    "+/rfid/tag",           # e.g. theatre/rfid/tag
    "+/led/+",              # e.g. theatre/led/code_blue (message triggers from your config)
]

# Map ESPHome switch entity id suffixes to your canonical LED names
_LED_SWITCH_MAP = {
    "theatre_led_-_clean": "clean",
    "theatre_led_-_code_blue": "code_blue",
    "theatre_led_-_in_use": "in_use",
    "theatre_led_-_lights": "lights",
}

_temp_sensor_re = re.compile(r"^([^/]+)/sensor/theatre_temperature/state$")
_hum_sensor_re  = re.compile(r"^([^/]+)/sensor/theatre_humidity/state$")
_switch_re      = re.compile(r"^([^/]+)/switch/([^/]+)/state$")
_led_trigger_re = re.compile(r"^([^/]+)/led/([^/]+)$")
_rfid_re        = re.compile(r"^([^/]+)/rfid/tag$")

def normalize_topic(topic: str) -> str | None:
    """
    Convert ESPHome-flavored topics to your canonical ones so the
    dashboard JS keeps working unchanged.
    """
    # theatre/sensor/theatre_temperature/state -> theatre/temperature
    m = _temp_sensor_re.match(topic)
    if m:
        theatre_id = m.group(1)
        return f"{theatre_id}/temperature"

    # theatre/sensor/theatre_humidity/state -> theatre/humidity
    m = _hum_sensor_re.match(topic)
    if m:
        theatre_id = m.group(1)
        return f"{theatre_id}/humidity"

    # theatre/switch/theatre_led_-_clean/state -> theatre/led/clean
    m = _switch_re.match(topic)
    if m:
        theatre_id, switch_entity = m.groups()
        led_name = _LED_SWITCH_MAP.get(switch_entity)
        if led_name:
            return f"{theatre_id}/led/{led_name}"
        # Unknown switch entity? Keep raw so you can see it in logs.
        return f"{theatre_id}/switch/{switch_entity}"

    # theatre/led/code_blue (already canonical shape for triggers)
    m = _led_trigger_re.match(topic)
    if m:
        theatre_id, led = m.groups()
        return f"{theatre_id}/led/{led}"

    # theatre/rfid/tag -> theatre/rfid/tag (already fine)
    m = _rfid_re.match(topic)
    if m:
        theatre_id = m.group(1)
        return f"{theatre_id}/rfid/tag"

    # Fallback: return original so you can still inspect it in DB
    return topic

class Command(BaseCommand):
    help = "Starts the MQTT listener for theatre modules"

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()

        def safe_group_send(group, message):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                if loop.is_running():
                    asyncio.ensure_future(channel_layer.group_send(group, message))
                else:
                    loop.run_until_complete(channel_layer.group_send(group, message))
            except Exception as e:
                print(f"[WEBSOCKET] Safe send error: {e}")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("[MQTT] Connected successfully")
                for topic in TOPIC_SUBS:
                    client.subscribe(topic)
                    print(f"[MQTT] Subscribed: {topic}")
            else:
                print(f"[MQTT] Connection failed with code {rc}")

        def on_message(client, userdata, msg):
            raw_topic = msg.topic
            payload = msg.payload.decode(errors="ignore").strip()
            norm_topic = normalize_topic(raw_topic)

            print(f"[MQTT] {raw_topic} → {payload} | normalized → {norm_topic}")

            try:
                theatre_id = norm_topic.split("/")[0] if "/" in norm_topic else raw_topic.split("/")[0]
                # Auto-create Theatre
                Theatre.objects.get_or_create(theatre_id=theatre_id)

                # Store normalized topic so your history endpoints & JS match
                TheatreLog.objects.create(
                    theatre_id=theatre_id,
                    topic=norm_topic,
                    value=payload
                )
            except Exception as e:
                print(f"[DB] Logging failed: {e}")

            # Push normalized topic/value to the WS group the dashboard listens to
            safe_group_send(
                "theatre_updates",
                {
                    "type": "send.theatre.update",
                    "data": {"topic": norm_topic, "value": payload}
                }
            )

        client = mqtt.Client()
        if MQTT_USERNAME and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        client.on_connect = on_connect
        client.on_message = on_message

        print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
