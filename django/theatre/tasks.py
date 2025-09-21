# theatre/tasks.py
import os, asyncio
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from dotenv import load_dotenv
from celery import shared_task
from .models import TheatreLog
from .models import TheatreLog, Theatre

load_dotenv()

# ── 1.  Put the loop in its own callable ────────────────────────────────
def main():
    MQTT_BROKER   = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT     = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

    # 1️⃣  add a constant (or read from .env)
    THEATRE_ID = os.getenv("THEATRE_ID", "theatre")

    # 2️⃣  subscribe only to *this* theatre’s topics
    TOPIC_SUBS = [
        f"{THEATRE_ID}/temperature",
        f"{THEATRE_ID}/humidity",
        f"{THEATRE_ID}/rfid/tag",
        f"{THEATRE_ID}/led/+/state",
        f"{THEATRE_ID}/led/clean",
        f"{THEATRE_ID}/led/code_blue",
        f"{THEATRE_ID}/led/in_use",
        f"{THEATRE_ID}/led/lights",
    ]


    channel_layer = get_channel_layer()

    def safe_group_send(group, message):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():          # happens on hot‑reload
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                asyncio.ensure_future(channel_layer.group_send(group, message))
            else:
                loop.run_until_complete(channel_layer.group_send(group, message))
        except Exception as e:
            print(f"[WS] Safe group send failed: {e}")

    def on_connect(client, userdata, flags, rc):
        print(f"[Theatre MQTT] Connected ({rc})")
        if rc == 0:
            for topic in TOPIC_SUBS:
                client.subscribe(topic)
                print(f"[MQTT] Subscribed → {topic}")

    # def on_message(client, userdata, msg):
    #     topic   = msg.topic
    #     payload = msg.payload.decode()
    #     print(f"[MQTT] {topic} → {payload}")

    #     # DB log
    #     try:
    #         theatre_id = topic.split("/")[0]
    #         TheatreLog.objects.create(
    #             theatre_id=theatre_id,
    #             topic=topic,
    #             value=payload,
    #         )
    #     except Exception as e:
    #         print(f"[DB] Log failed: {e}")

    #     # WebSocket broadcast
    #     safe_group_send(
    #         "theatre_updates",
    #         {
    #             "type": "send.theatre.update",
    #             "data": {"topic": topic, "value": payload},
    #         },
    #     )

def on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode()
    print(f"[MQTT] {topic} → {payload}")

    # Extract theatre_id from "theatre1/temperature" etc.
    theatre_id = topic.split("/")[0]

    # Ensure Theatre exists
    try:
        Theatre.objects.get_or_create(theatre_id=theatre_id)
    except Exception as e:
        print(f"[DB] Theatre ensure failed: {e}")

    # Log
    try:
        TheatreLog.objects.create(
            theatre_id=theatre_id,
            topic=topic,
            value=payload,
        )
    except Exception as e:
        print(f"[DB] Log failed: {e}")

    # WebSocket broadcast (unchanged)
    safe_group_send(
        "theatre_updates",
        {
            "type": "send.theatre.update",
            "data": {"topic": topic, "value": payload},
        },
    )

    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()     # ← blocks forever


# ── 2.  Celery task wrapper (runs main(), never returns) ────────────────
@shared_task(
    bind=True,
    queue="mqtt",                         # ➊ target the mqtt queue
    name="theatre.tasks.mqtt_listener_task",
    ignore_result=True,                   # no result backend churn
)
def mqtt_listener_task(self):
    main()                                # blocks forever
