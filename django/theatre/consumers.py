# theatre/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TheatreDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("theatre_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("theatre_updates", self.channel_name)

    async def send_theatre_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
