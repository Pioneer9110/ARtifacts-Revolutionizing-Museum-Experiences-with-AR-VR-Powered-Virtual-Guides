import asyncio
import websockets
import json
import os
import sys

SIGNALING_SERVER = "ws://35.211.45.54:5000"  # Change to your signaling server's IP
SENDER_ID = "HyderabadPC"
RECEIVER_ID = "BangalorePC"

async def signaling():
    async with websockets.connect(SIGNALING_SERVER) as ws:
        # Register as sender
        await ws.send(json.dumps({"type": "sender", "id": SENDER_ID}))

        while True:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "request_file":
                print("Sending file request received")
                await send_file(ws)  # Ensure full file transfer before breaking
                break  # Exit loop only after sending the full file

    print("File sent successfully. Exiting...")
    sys.exit(0)  # Exit script after sending the file

async def send_file(ws):
    file_path = "output.wav"
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as file:
        while chunk := file.read(1024):
            await ws.send(json.dumps({
                "type": "file_chunk",
                "data": chunk.decode("latin-1"),
                "target": RECEIVER_ID
            }))
            await asyncio.sleep(0.01)  # Ensure chunks are sent properly

    await ws.send(json.dumps({"type": "file_end", "target": RECEIVER_ID}))
    print("File transfer complete!")

# Run signaling loop
asyncio.run(signaling())
