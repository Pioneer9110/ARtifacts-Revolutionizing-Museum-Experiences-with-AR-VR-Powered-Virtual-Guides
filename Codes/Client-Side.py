import asyncio
import websockets
import json
import os
from pydub import AudioSegment
from pydub.utils import mediainfo

SIGNALING_SERVER = "ws://35.211.45.54:5000"
PC_ID = "BangalorePC"
PARTNER_ID = "HyderabadPC"
FILE_TO_SEND = "Meows.wav"
RECEIVED_FILE = "Received_Back.wav"
CONVERTED_FILE = "Converted.wav"

async def main():
    async with websockets.connect(SIGNALING_SERVER, ping_interval=30, ping_timeout=60) as ws:
        await ws.send(json.dumps({"type": "register", "id": PC_ID}))
        print(f"Connected to signaling server as {PC_ID}")

        # Step 1: Send the file first
        await send_file(ws, FILE_TO_SEND)

        # Step 2: Wait for acknowledgment from HyderabadPC
        while True:
            message = await ws.recv()
            data = json.loads(message)

            if data.get("type") == "received_ack":
                print(f"Received acknowledgment from {PARTNER_ID}, sending 'ready_to_receive' ping...")
                await ws.send(json.dumps({"type": "ready_to_receive", "sender": PC_ID, "target": PARTNER_ID}))
                break  # Exit loop after sending ping

        # Step 3: Start receiving the file from Hyderabad PC
        print(f"Now listening for a file from {PARTNER_ID}...")
        await receive_file(ws, RECEIVED_FILE)

        # Step 4: Convert if necessary
        if not validate_wav(RECEIVED_FILE):
            print("File is invalid, attempting to fix...")
            if convert_to_wav(RECEIVED_FILE, CONVERTED_FILE):
                print(f"File successfully converted and saved as {CONVERTED_FILE}.")
            else:
                print("Error: Unable to fix the WAV file.")
                return

        # Step 5: Send a final ping after receiving
        await ws.send(json.dumps({"type": "ping", "sender": PC_ID, "target": PARTNER_ID}))
        print("File received, fixed if necessary, and sent ping notification to HyderabadPC.")
        print("File transfer complete. Exiting program.")

async def send_file(ws, file_path):
    """ Send a file to the partner PC """
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print(f"Sending file {file_path} to {PARTNER_ID}...")
    with open(file_path, "rb") as file:
        while chunk := file.read(1024):
            await ws.send(json.dumps({"type": "file_chunk", "data": chunk.decode('latin-1'), "target": PARTNER_ID}))
            await asyncio.sleep(0.01)

    await ws.send(json.dumps({"type": "file_end", "target": PARTNER_ID}))
    print("File transfer complete! Waiting for confirmation...")

async def receive_file(ws, output_file):
    """ Receive a file from the partner PC """
    print(f"Waiting for file from {PARTNER_ID}...")
    received_chunks = []

    while True:
        message = await ws.recv()
        data = json.loads(message)

        if data.get("type") == "file_chunk":
            received_chunks.append(data["data"])
        elif data.get("type") == "file_end":
            with open(output_file, "wb") as file:
                file.write(b"".join(chunk.encode("latin-1") for chunk in received_chunks))
            print(f"File saved as {output_file}")
            break

def validate_wav(file_path):
    """ Check if a WAV file is valid. """
    try:
        info = mediainfo(file_path)
        return info.get("codec_name") == "pcm_s16le"
    except Exception:
        return False

def convert_to_wav(input_file, output_file):
    """ Convert an incorrect WAV file to a proper format """
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav", parameters=["-ac", "2", "-ar", "44100"])
        print(f"Converted file saved as {output_file}")
        return True
    except Exception as e:
        print(f"Conversion error: {e}")
        return False

asyncio.run(main())
