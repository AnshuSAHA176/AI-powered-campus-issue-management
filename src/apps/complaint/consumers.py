from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        
        self.user=  self.scope['user']
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)
        print("DISCONNECTED", close_code)
    async def receive(self, text_data = None, bytes_data = None):
        await self.send(f'hello {text_data}')