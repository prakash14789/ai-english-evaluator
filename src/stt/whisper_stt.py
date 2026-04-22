try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    import whisper
    HAS_FASTER_WHISPER = False

import os
import torch

# Load model (GPU if available, else CPU)
def load_whisper_model(model_size="base"):
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if HAS_FASTER_WHISPER:
            # Use int8 for CPU to be fast, float16 for GPU
            compute_type = "float16" if device == "cuda" else "int8"
            print(f"Loading [Faster-Whisper] model '{model_size}' on {device} ({compute_type})...")
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
        else:
            print(f"Loading [OpenAI-Whisper] model '{model_size}' on {device}...")
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

        if HAS_FASTER_WHISPER and isinstance(model, WhisperModel):
            # faster-whisper returns a generator of segments
            segments, info = model.transcribe(file_path, beam_size=5)
            
            segments_list = []
            full_text = ""
            for segment in segments:
                full_text += segment.text
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })

            return {
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": segments_list
            }
        else:
            # standard openai-whisper
            result = model.transcribe(file_path)
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "language_probability": 1.0, # Placeholder
                "duration": 0.0, # Placeholder
                "segments": result.get("segments", [])
            }

    except Exception as e:
        print("Error during transcription:", e)
        return None


# Main execution
if __name__ == "__main__":
    audio_file = "sample.wav"
    
    # Robust path check
    if not os.path.exists(audio_file):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        audio_file = os.path.join(root_dir, "sample.wav")

    model = load_whisper_model("base")

    if model:
        output = transcribe_audio(model, audio_file)

        if output:
            print("\n=== Transcription Result ===")
            print(f"Language: {output['language']}")
            print("Text:", output["text"])

            # Optional: print timestamps
            print("\n--- Segments ---")
            for seg in output["segments"][:3]: # Show first 3 for brevity
                print(f"[{seg['start']:.2f}s] {seg['text']}")