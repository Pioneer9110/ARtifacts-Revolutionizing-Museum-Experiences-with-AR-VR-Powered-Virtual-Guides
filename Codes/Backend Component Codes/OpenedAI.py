import requests

def text_to_speech(input_file, output_file):
    # Read the text from the input file
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read().strip()
        
        if not text:
            print("Error: The input file is empty.")
            return
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # API request details
    url = "http://localhost:8000/v1/audio/speech"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "sk-111111111"  # Replace with your API key if required
    }
    data = {
        "input": text,
        "model": "tts-1"  # Specify the TTS model
    }

    # Make the request
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Audio saved as {output_file}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    input_file = "response.txt"
    output_file = "output.wav"
    text_to_speech(input_file, output_file)
