from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_socket_message(channel_name: str, type: str, message: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        channel_name,
        {
            'type': type,
            'content': message
        }
    )
