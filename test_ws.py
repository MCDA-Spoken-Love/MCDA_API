import asyncio
import os

import websockets

token = os.getenv('USER_TOKEN')
uri = f"ws://localhost:8000/ws/relationship-requests/?token={token}"


async def listen():
    async with websockets.connect(
        uri,
        origin="http://localhost:8000"
    ) as websocket:
        print("Connected to WebSocket.")
        while True:
            msg = await websocket.recv()
            print("Received:", msg)

asyncio.run(listen())
