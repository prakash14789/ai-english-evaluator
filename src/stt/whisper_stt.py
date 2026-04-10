import whisper

# Load model (first time it will download)
model = whisper.load_model("base")

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

if __name__ == "__main__":
    audio_file = "sample.wav"  # your test file
    text = transcribe_audio(audio_file)
    print("Transcription:", text)