import asyncio
import websockets
import json
import os
import requests
import whisper  # Make sure you have the whisper package installed

# Constants and file names
SIGNALING_SERVER = "ws://35.211.45.54:5000"
PC_ID = "HyderabadPC"
PARTNER_ID = "BangalorePC"

RECEIVED_FILE = "received.wav"
TRANSCRIPTION_FILE = "transcription.txt"
RESPONSE_FILE = "response.txt"
OUTPUT_FILE = "output.wav"

async def receive_file(ws, output_file):
    """Receive a file from the partner PC and save it as output_file."""
    print(f"📥 Waiting for file from {PARTNER_ID}...")
    received_chunks = []
    while True:
        message = await ws.recv()
        data = json.loads(message)
        if data.get("type") == "file_chunk":
            received_chunks.append(data["data"])
        elif data.get("type") == "file_end":
            # Save the complete file
            with open(output_file, "wb") as f:
                # Convert each chunk (sent as latin-1 encoded string) back to bytes
                f.write(b"".join(chunk.encode("latin-1") for chunk in received_chunks))
            print(f"✅ File saved as {output_file}")
            break

async def send_file(ws, file_path):
    """Send a file to the partner PC in chunks."""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found.")
        return

    print(f"📤 Sending file {file_path} to {PARTNER_ID}...")
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            await ws.send(json.dumps({
                "type": "file_chunk",
                "data": chunk.decode("latin-1"),
                "target": PARTNER_ID
            }))
            await asyncio.sleep(0.01)
    await ws.send(json.dumps({
        "type": "file_end",
        "target": PARTNER_ID
    }))
    print("✅ File transfer complete! Switching back to listening mode...")

def transcribe_audio(input_file, output_file):
    """Transcribe the input audio file using Whisper and save the transcription."""
    print(f"🎤 Transcribing {input_file} (English only)...")
    model = whisper.load_model("base")
    result = model.transcribe(input_file, language='en')
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result['text'])
    print(f"✅ Transcription saved to {output_file}")

def generate_response(input_file, output_file):
    """Generate a text response using the Ollama API based on the transcription."""
    url = "http://localhost:11434/api/generate"
    try:
        with open(input_file, "r") as file:
            prompt = file.read().strip()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    payload = {
        "model": "llama3",
        "prompt": f"Please respond in the tone of a museum curator, with a maximum of 60 words: {prompt}",
        "stream": False,
        "max_tokens": 60
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        if response.status_code == 200:
            response_data = response.json()
            generated_text = response_data.get("response", "No response generated.")
            with open(output_file, "w") as out_file:
                out_file.write(generated_text)
            print(f"✅ Response saved to {output_file}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def text_to_speech(input_file, output_file):
    """Convert the text response to speech using the TTS API."""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read().strip()
        if not text:
            print("Error: The input file is empty.")
            return
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    url = "http://localhost:8000/v1/audio/speech"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "sk-111111111"  # Replace with your actual API key if required
    }
    data = {
        "input": text,
        "model": "tts-1"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio saved as {output_file}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

async def main():
    async with websockets.connect(SIGNALING_SERVER, ping_interval=30, ping_timeout=60) as ws:
        # Register with the signaling server
        await ws.send(json.dumps({"type": "register", "id": PC_ID}))
        print(f"🔗 Connected to signaling server as {PC_ID}")

        while True:
            # 1. Wait for the incoming "received.wav" file
            await receive_file(ws, RECEIVED_FILE)
            # 2. Send an acknowledgment of receipt
            await ws.send(json.dumps({"type": "received_ack", "sender": PC_ID, "target": PARTNER_ID}))
            print(f"✅ File received; acknowledgment sent to {PARTNER_ID}")

            # 3. Process the file through the pipeline:
            # a) Transcribe the audio using Whisper
            transcribe_audio(RECEIVED_FILE, TRANSCRIPTION_FILE)
            # b) Generate a response via the Ollama API
            generate_response(TRANSCRIPTION_FILE, RESPONSE_FILE)
            # c) Convert the response text to speech using the TTS API
            text_to_speech(RESPONSE_FILE, OUTPUT_FILE)

            # 4. Wait for the "ready_to_receive" signal before sending the output audio file
            while True:
                message = await ws.recv()
                data = json.loads(message)
                if data.get("type") == "ready_to_receive":
                    print(f"🔔 Received 'ready_to_receive' signal from {data.get('sender')}. Sending output file...")
                    await send_file(ws, OUTPUT_FILE)
                    break

            print("🔄 Processing complete. Returning to listening mode...")

if __name__ == "__main__":
    asyncio.run(main())
