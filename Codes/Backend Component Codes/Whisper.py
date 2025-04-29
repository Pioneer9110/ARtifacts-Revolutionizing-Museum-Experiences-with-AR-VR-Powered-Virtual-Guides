import whisper
import os


def transcribe_audio(input_file, output_file):
    try:
        # Load the Whisper model
        model = whisper.load_model("base")
        
        # Check if the input file exists
        if not os.path.isfile(input_file):
            print(f"Error: File '{input_file}' not found.")
            return
        
        # Transcribe the audio file
        print(f"Transcribing '{input_file}'... This may take a while.")
        result = model.transcribe(input_file)
        
        # Save the transcription to a file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        print(f"Transcription saved as '{output_file}'.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    input_audio = "Received.wav"
    output_text = "transcription.txt"
    transcribe_audio(input_audio, output_text)

# You can run this directly with:
# python Whisper.py

# Let me know if you want me to add automatic environment activation or anything else! 🚀