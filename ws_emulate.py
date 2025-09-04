import asyncio
import os

import websockets
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')
token = os.getenv('USER_TOKEN')
chat_uri = f"ws://localhost:8000/ws/chat/?token={token}"
relationship_uri = f"ws://localhost:8000/ws/relationship-requests/?token={token}"


async def listen():
    async with websockets.connect(
        chat_uri,
        origin="http://localhost:8000"
    ) as websocket:
        print("Connected to WebSocket.")
        while True:
            msg = await websocket.recv()
            print("Received:", msg)

asyncio.run(listen())
