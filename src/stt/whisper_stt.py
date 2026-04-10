import whisper
import os

# Load model (GPU if available, else CPU)
def load_whisper_model(model_size="base"):
    try:
        model = whisper.load_model(model_size)
        print(f"Model '{model_size}' loaded successfully.")
        return model
    except Exception as e:
        print("Error loading model:", e)
        return None


# Transcribe audio function
def transcribe_audio(model, file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print("Transcribing audio...")

        result = model.transcribe(file_path)

        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", [])
        }

    except Exception as e:
        print("Error during transcription:", e)
        return None


# Main execution
if __name__ == "__main__":
    audio_file = "sample.wav"  # change path if needed

    model = load_whisper_model("base")

    if model:
        output = transcribe_audio(model, audio_file)

        if output:
            print("\n=== Transcription Result ===")
            print("Language:", output["language"])
            print("Text:", output["text"])

            # Optional: print timestamps
            print("\n--- Segments ---")
            for seg in output["segments"]:
                print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")