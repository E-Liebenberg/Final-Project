import os
import asyncio
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from theatre.models import Theatre, TheatreLog  # ✅ Import both models

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

TOPIC_SUBS = [
    "+/temperature",
    "+/humidity",
    "+/rfid/tag",
    "+/led/+/state",
    "+/led/clean",
    "+/led/code_blue",
    "+/led/in_use",
    "+/led/lights"
]

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
                    print(f"[MQTT] Subscribed to topic: {topic}")
            else:
                print(f"[MQTT] Connection failed with code {rc}")

        def on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode()
            print(f"[MQTT] {topic} → {payload}")

            try:
                theatre_id = topic.split("/")[0]

                # ✅ Auto-create Theatre if not exists
                theatre, created = Theatre.objects.get_or_create(theatre_id=theatre_id)
                if created:
                    print(f"[DB] New Theatre created: {theatre_id}")

                # Log the reading
                TheatreLog.objects.create(
                    theatre_id=theatre_id,
                    topic=topic,
                    value=payload
                )
                print(f"[DB] Logged: {topic} → {payload}")
            except Exception as e:
                print(f"[DB] Logging failed: {e}")

            safe_group_send(
                "theatre_updates",
                {
                    "type": "send.theatre.update",
                    "data": {
                        "topic": topic,
                        "value": payload
                    }
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
