import asyncio
import websockets
import json

connected_users = {}

async def handler(websocket):
    username = None
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "message":
                target = data.get("to")
                sender = data.get("from")
                text = data.get("text")

                if username is None:
                    username = sender
                    connected_users[username] = websocket
                    print(f"User connected: {username}")

                target_ws = connected_users.get(target)
                if target_ws:
                    await target_ws.send(json.dumps({
                        "type": "message",
                        "from": sender,
                        "text": text
                    }))
                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"User '{target}' not found or offline."
                    }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if username:
            connected_users.pop(username, None)
            print(f"User disconnected: {username}")

async def main():
    async with websockets.serve(handler, "localhost", 8080):
        print("WebSocket server started on ws://localhost:8080")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
