import os
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from alerts.models import Alert
from remotes.models import Remote
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio

# Load environment variables
load_dotenv()

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

TOPIC_SUBS = [
    'nursecall/+/button/+',
    'nursecall/+/led/+/state',
]

class Command(BaseCommand):
    help = "Starts the MQTT listener to receive messages from ESP devices"

    def handle(self, *args, **kwargs):
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
            print(f"[MQTT] {msg.topic} → {msg.payload.decode()}")

            try:
                topic_parts = msg.topic.split('/')
                remote_id = topic_parts[1]
                payload = msg.payload.decode()
            except Exception as e:
                print(f"[MQTT] Failed to parse topic: {e}")
                return

            # Handle LED state updates
            if "led" in topic_parts and topic_parts[-1] == "state":
                led_name = topic_parts[-2]
                led_state = payload.upper()

                safe_group_send(
                    f"remote_{remote_id}",
                    {
                        "type": "led_state_update",
                        "led_name": led_name,
                        "led_state": led_state
                    }
                )
                print(f"[WEBSOCKET] Sent LED state update: {led_name} = {led_state}")
                return

            # Handle button/alert topics
            try:
                button_id = topic_parts[3]
            except IndexError:
                print("[MQTT] Incomplete topic format for alert")
                return

            alert_type_map = {
                "1": "nurse_call",
                "2": "light",
                "3": "code_blue",
                "4": "sound",
                "5": "motion",
                "nurse": "nurse_call",
                "light": "light",
                "volume_up": "sound",
                "volume_down": "sound",
                "channel_up": "motion",
                "channel_down": "motion",
                "tv_power": "code_blue",
            }

            alert_type = alert_type_map.get(button_id, "nurse_call")

            remote, created = Remote.objects.get_or_create(
                remote_id=remote_id,
                defaults={
                    "ward": "unassigned",
                    "bed": "unassigned",
                    "mac_address": None,
                    "ip_address": None,
                    "assigned_to": None,
                }
            )

            if created:
                print(f"[MQTT] 🚀 Auto-registered new remote: {remote_id}")
            else:
                print(f"[MQTT] ✅ Found registered remote: {remote_id}")

            alert = Alert.objects.create(
                remote=remote,
                alert_type=alert_type
            )
            print(f"[ALERT] Saved alert for {remote} → {alert_type}")

            safe_group_send(
                f"remote_{remote_id}",
                {
                    "type": "alert_received",
                    "alert_type": alert_type
                }
            )
            print(f"[WEBSOCKET] Sent alert to group remote_{remote.remote_id}")

        # MQTT setup
        client = mqtt.Client()
        if MQTT_USERNAME and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        client.on_connect = on_connect
        client.on_message = on_message

        print(f"[MQTT] Connecting to broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()