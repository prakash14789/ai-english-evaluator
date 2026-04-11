import os
import sys

# Add src to path just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.whisper_stt import load_whisper_model, transcribe_audio
from nlp.grammar import evaluate_grammar, correct_grammar

def run_evaluation(audio_path):
    print("--- AI English Evaluator ---")
    
    # 1. Load Whisper Model
    model = load_whisper_model("base")
    if not model:
        print("Failed to load Whisper model.")
        return

    # 2. Transcribe Audio
    print(f"\n[STT] Processing audio: {audio_path}")
    transcription = transcribe_audio(model, audio_path)
    
    if not transcription or not transcription["text"].strip():
        print("Failed to transcribe audio or audio is silent.")
        return
    
    original_text = transcription["text"].strip()
    print(f"[STT] Transcribed Text: \"{original_text}\"")

    # 3. Grammar Evaluation
    print("\n[NLP] Evaluating Grammar...")
    grammar_result = evaluate_grammar(original_text)
    corrected_text = correct_grammar(original_text)

    # 4. Final Report
    print("\n" + "="*30)
    print("      FINAL EVALUATION")
    print("="*30)
    print(f"Original Text:  {original_text}")
    print(f"Corrected Text: {corrected_text}")
    print(f"Grammar Score:  {grammar_result['score']}/10")
    
    if grammar_result["errors"]:
        print("\nSuggestions to improve:")
        for i, error in enumerate(grammar_result["errors"], 1):
            print(f"{i}. {error}")
    else:
        print("\nGreat job! No grammar issues detected.")
    
    print("="*30)

if __name__ == "__main__":
    # Check if sample.wav exists in root
    sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample.wav")
    
    if os.path.exists(sample_file):
        run_evaluation(sample_file)
    else:
        print(f"Error: Could not find {sample_file}")
