import json
import urllib.parse as urlparse
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import InMemoryChannelLayer
from channels.exceptions import AcceptConnection, DenyConnection

from utils.utils_jwt import check_jwt_token

class CapyBackConsumer(AsyncWebsocketConsumer):
    # 当客户端尝试建立 WebSocket 连接时调用
    async def connect(self) -> None:
        jwt_token = urlparse.parse_qs(self.scope['query_string'].decode('utf-8')).get("jwt")
        if jwt_token is None:
            raise DenyConnection("No JWT token provided")
        jwt_token = jwt_token[0]
        jwt_token_payload = check_jwt_token(jwt_token)
        if jwt_token_payload is None:
            raise DenyConnection("Invalid or expired JWT")

        from chat.models import UserInfo
        # user = UserInfo.objects.filter(username=jwt_token_payload['username']).first()
        # The above usage needs os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true" in asgi file
        user = await UserInfo.objects.filter(username=jwt_token_payload['username']).afirst()
        if user is None:
            raise DenyConnection("Invalid username")

        self.username = user.username
        self.channel_layer: InMemoryChannelLayer

        # 将当前 WebSocket 连接添加到一个全体用户组中
        # 这样可以确保发给这个组的所有消息都会被转发给目前连接的所有客户端
        await self.channel_layer.group_add(self.username, self.channel_name)

        # 接受 WebSocket 连接
        await self.accept()

    # 当 WebSocket 连接关闭时调用
    async def disconnect(self, close_code: int) -> None:
        # 将当前 WebSocket 从其所在的组中移除
        if hasattr(self, 'username'):
            await self.channel_layer.group_discard(self.username, self.channel_name)

    # 向指定用户组发送 notification
    async def notify(self, event) -> None:
        await self.send(text_data=event['message'])
