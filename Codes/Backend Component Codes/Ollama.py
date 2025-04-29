import requests
import json


def generate_response(input_file, output_file):
    # Ollama API endpoint
    url = "http://localhost:11434/api/generate"

    # Read the transcription file
    try:
        with open(input_file, "r") as file:
            prompt = file.read().strip()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # Prepare the API request payload
    payload = {
        "model": "llama3",
        "prompt": f"Please respond in the tone of a museum curator, with a maximum of 60 words: {prompt}",
        "stream": False,
        "max_tokens": 60  # Limit the response length
    }


    try:
        # Send POST request to the Ollama API
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        
        # Check response status
        if response.status_code == 200:
            response_data = response.json()
            generated_text = response_data.get("response", "No response generated.")
            
            # Write the generated response to a file
            with open(output_file, "w") as output:
                output.write(generated_text)
            
            print(f"Response saved to {output_file}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    generate_response("transcription.txt", "response.txt")
