import asyncio
import websockets
import json

SIGNALING_SERVER = "ws://35.211.45.54:5000"  # Change to your signaling server's IP
RECEIVER_ID = "HyderabadPC"
SENDER_ID = "BangalorePC"

received_chunks = []

async def signaling():
    async with websockets.connect(SIGNALING_SERVER) as ws:
        # Register as receiver
        await ws.send(json.dumps({"type": "receiver", "id": RECEIVER_ID}))

        # Request the file
        await ws.send(json.dumps({"type": "request_file", "target": SENDER_ID}))
        print("File request sent to sender...")

        while True:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "file_chunk":
                received_chunks.append(data["data"])
            elif data["type"] == "file_end":
                save_file()
                break

def save_file():
    with open("Received.wav", "wb") as file:
        file.write(b"".join(chunk.encode("latin-1") for chunk in received_chunks))
    print("File Received & Saved!")

# Run signaling loop
asyncio.run(signaling())