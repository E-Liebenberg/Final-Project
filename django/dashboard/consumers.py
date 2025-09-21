from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.remote_id = self.scope['url_route']['kwargs']['remote_id']
        self.group_name = f"remote_{self.remote_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        await self.send(text_data=json.dumps({
            "status": "connected",
            "remote_id": self.remote_id
        }))

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages from the frontend
        data = json.loads(text_data)
        print(f"[WS RECEIVE] {data}")

    async def send_alert(self, event):
        # Forward alert to frontend with expected structure
        await self.send(text_data=json.dumps({
            "type": "send_alert",
            "data": event["data"]
        }))

    async def led_state_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "led_state_update",
            "led_name": event["led_name"],
            "led_state": event["led_state"],
        }))
