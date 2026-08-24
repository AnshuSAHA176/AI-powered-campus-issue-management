from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONNECT CALLED")
        await self.accept()
        print("ACCEPTED")

    async def disconnect(self, close_code):
        print("DISCONNECTED", close_code)
    async def receive(self, text_data = None, bytes_data = None):
        self.send(text_data)