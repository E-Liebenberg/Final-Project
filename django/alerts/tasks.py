# # alerts/tasks.py

# from celery import shared_task
# import threading
# import time
# import paho.mqtt.client as mqtt
# import os
# from dotenv import load_dotenv
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from alerts.models import Alert
# from remotes.models import Remote

# load_dotenv()

# MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
# MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
# MQTT_USERNAME = os.getenv('MQTT_USERNAME')
# MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# TOPIC_SUBS = [
#     'nursecall/+/button/+',
#     'nursecall/+/led/+/state',
# ]

# def start_mqtt_listener():
#     channel_layer = get_channel_layer()

#     def safe_group_send(group, message):
#         try:
#             async_to_sync(channel_layer.group_send)(group, message)
#         except Exception as e:
#             print(f"[WEBSOCKET] Safe send error: {e}")

#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("[MQTT] Connected")
#             for topic in TOPIC_SUBS:
#                 client.subscribe(topic)
#                 print(f"[MQTT] Subscribed: {topic}")
#         else:
#             print(f"[MQTT] Failed to connect: {rc}")

#     def on_message(client, userdata, msg):
#         print(f"[MQTT] {msg.topic} → {msg.payload.decode()}")
#         topic_parts = msg.topic.split('/')
#         remote_id = topic_parts[1]
#         payload = msg.payload.decode()

#         if "led" in topic_parts and topic_parts[-1] == "state":
#             led_name = topic_parts[-2]
#             led_state = payload.upper()
#             safe_group_send(
#                 f"remote_{remote_id}",
#                 {
#                     "type": "send_alert",
#                     "data": {
#                         "type": "led_state_update",
#                         "led_name": led_name,
#                         "led_state": led_state
#                     }
#                 }
#             )
#             return

#         try:
#             button_id = topic_parts[3]
#         except IndexError:
#             print("[MQTT] Incomplete topic for alert")
#             return

#         alert_map = {
#             "1": "nurse_call",
#             "2": "light",
#             "3": "code_blue",
#             "4": "sound",
#             "5": "motion",
#             "nurse": "nurse_call",
#             "light": "light",
#             "volume_up": "sound",
#             "volume_down": "sound",
#             "channel_up": "motion",
#             "channel_down": "motion",
#             "tv_power": "code_blue",
#         }

#         alert_type = alert_map.get(button_id, "nurse_call")
#         remote, _ = Remote.objects.get_or_create(remote_id=remote_id)
#         alert = Alert.objects.create(remote=remote, alert_type=alert_type)
#         safe_group_send(
#             f"remote_{remote_id}",
#             {
#                 "type": "send_alert",
#                 "data": {
#                     "alert_type": alert_type,
#                     "timestamp": str(alert.timestamp.timestamp()),
#                     "source": "mqtt"
#                 }
#             }
#         )

#     client = mqtt.Client()
#     if MQTT_USERNAME and MQTT_PASSWORD:
#         client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(MQTT_BROKER, MQTT_PORT, 60)
#     client.loop_forever()


# @shared_task
# def mqtt_listener_task():
#     print("[CELERY] Starting MQTT Listener")
#     thread = threading.Thread(target=start_mqtt_listener, daemon=True)
#     thread.start()

#     # Keep the task alive to avoid Celery stopping it
#     while True:
#         time.sleep(10)

# from celery import shared_task
# import threading
# import time
# import paho.mqtt.client as mqtt
# import os
# from dotenv import load_dotenv
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from alerts.models import Alert
# from remotes.models import Remote

# load_dotenv()

# MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
# MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
# MQTT_USERNAME = os.getenv('MQTT_USERNAME')
# MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# TOPIC_SUBS = [
#     'nursecall/+/button/+',
#     'nursecall/+/led/+/state',
# ]

# def start_mqtt_listener():
#     channel_layer = get_channel_layer()

#     def safe_group_send(group, message):
#         try:
#             async_to_sync(channel_layer.group_send)(group, message)
#         except Exception as e:
#             print(f"[WEBSOCKET] Safe send error: {e}")

#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("[MQTT] Connected")
#             for topic in TOPIC_SUBS:
#                 client.subscribe(topic)
#                 print(f"[MQTT] Subscribed: {topic}")
#         else:
#             print(f"[MQTT] Failed to connect: {rc}")

#     def on_message(client, userdata, msg):
#         print(f"[MQTT] {msg.topic} → {msg.payload.decode()}")
#         topic_parts = msg.topic.split('/')
#         remote_id = topic_parts[1]
#         payload = msg.payload.decode()

#         if "led" in topic_parts and topic_parts[-1] == "state":
#             led_name = topic_parts[-2]
#             led_state = payload.upper()
#             safe_group_send(
#                 f"remote_{remote_id}",
#                 {
#                     "type": "send_alert",
#                     "data": {
#                         "type": "led_state_update",
#                         "led_name": led_name,
#                         "led_state": led_state
#                     }
#                 }
#             )
#             return

#         try:
#             button_id = topic_parts[3]
#         except IndexError:
#             print("[MQTT] Incomplete topic for alert")
#             return

#         alert_map = {
#             "1": "nurse_call",
#             "2": "light",
#             "3": "code_blue",
#             "4": "sound",
#             "5": "motion",
#             "nurse": "nurse_call",
#             "light": "light",
#             "volume_up": "sound",
#             "volume_down": "sound",
#             "channel_up": "motion",
#             "channel_down": "motion",
#             "tv_power": "code_blue",
#         }

#         alert_type = alert_map.get(button_id, "nurse_call")
#         remote, _ = Remote.objects.get_or_create(remote_id=remote_id)
#         alert = Alert.objects.create(remote=remote, alert_type=alert_type)
#         safe_group_send(
#             f"remote_{remote_id}",
#             {
#                 "type": "send_alert",
#                 "data": {
#                     "alert_type": alert_type,
#                     "timestamp": str(alert.timestamp.timestamp()),
#                     "source": "mqtt"
#                 }
#             }
#         )

#     client = mqtt.Client()
#     if MQTT_USERNAME and MQTT_PASSWORD:
#         client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(MQTT_BROKER, MQTT_PORT, 60)
#     client.loop_forever()


# @shared_task
# def mqtt_listener_task():
#     print("[CELERY] Starting MQTT Listener")
#     threading.Thread(target=start_mqtt_listener, daemon=True).start()

#     while True:
#         time.sleep(10)

# alerts/tasks.py
import os, asyncio, paho.mqtt.client as mqtt
from dotenv import load_dotenv
from celery import shared_task
from channels.layers import get_channel_layer
from alerts.models import Alert
from remotes.models import Remote

load_dotenv()

def main():
    """Blocking MQTT loop → runs inside the mqtt‑queue worker."""
    MQTT_BROKER   = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT     = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

    TOPIC_SUBS = [
        "nursecall/+/button/+",
        "nursecall/+/led/+/state",
    ]

    channel_layer = get_channel_layer()

    # ── helper that works even if there is no running event‑loop ──────────
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
            print(f"[WS] send error → {e}")

    # ── MQTT callbacks ───────────────────────────────────────────────────
    def on_connect(client, userdata, flags, rc):
        print(f"[Alerts MQTT] Connected ({rc})")
        if rc == 0:
            for t in TOPIC_SUBS:
                client.subscribe(t)
                print(f"[MQTT] Subscribed → {t}")

    def on_message(client, userdata, msg):
        topic   = msg.topic
        payload = msg.payload.decode()
        print(f"[MQTT] {topic} → {payload}")

        parts = topic.split("/")
        remote_id = parts[1]

        # LED state updates
        if "led" in parts and parts[-1] == "state":
            led_name  = parts[-2]
            led_state = payload.upper()
            safe_group_send(
                f"remote_{remote_id}",
                {
                    "type": "send_alert",
                    "data": {
                        "type": "led_state_update",
                        "led_name": led_name,
                        "led_state": led_state,
                    },
                },
            )
            return

        # Button alerts
        try:
            button_id = parts[3]
        except IndexError:
            print("[MQTT] Incomplete topic for alert")
            return

        alert_map = {
            "1": "nurse_call",
            "2": "light",
            "3": "code_blue",
            "4": "sound",
            "5": "motion",
            # mnemonic names (if ESP publishes these)
            "nurse": "nurse_call",
            "light": "light",
            "volume_up": "sound",
            "volume_down": "sound",
            "channel_up": "motion",
            "channel_down": "motion",
            "tv_power": "code_blue",
        }
        alert_type = alert_map.get(button_id, "nurse_call")

        remote, _ = Remote.objects.get_or_create(remote_id=remote_id)
        alert = Alert.objects.create(remote=remote, alert_type=alert_type)

        safe_group_send(
            f"remote_{remote_id}",
            {
                "type": "send_alert",
                "data": {
                    "alert_type": alert_type,
                    "timestamp": str(alert.timestamp.timestamp()),
                    "source": "mqtt",
                },
            },
        )

    # ── Client bootstrapping ─────────────────────────────────────────────
    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[MQTT] Connecting → {MQTT_BROKER}:{MQTT_PORT}")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()                       # <— blocks forever


# Celery wrapper: 1 task → mqtt queue → blocks forever
@shared_task(
    bind=True,
    queue="mqtt",                               # ➊ route to mqtt worker
    name="alerts.tasks.mqtt_listener_task",
    ignore_result=True,
)
def mqtt_listener_task(self):
    main()
