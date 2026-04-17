import os
import sys

# Add src to path just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.whisper_stt import load_whisper_model, transcribe_audio
from nlp.grammar import evaluate_grammar, correct_grammar
from utils.question_generator import generate_question
from nlp.enhancer import enhance_speech

def run_evaluation(audio_path):
    print("--- AI English Evaluator ---")
    
    # 0. Generate dynamic question
    question = generate_question("beginner")
    print(f"\n[AI] Question: {question}")
    
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

    # 3. AI Evaluation & Enhancement
    print("\n[NLP] Analyzing and Enhancing Speech...")
    enhancement = enhance_speech(original_text, question=question)
    grammar_result = evaluate_grammar(original_text)

    # 4. Final Report
    print("\n" + "="*30)
    print("      FINAL EVALUATION")
    print("="*30)
    print(f"Original Text:  {original_text}")
    print(f"Grammar Score:  {grammar_result['score']}/10")
    
    print("\n[Topic Relevancy]")
    print(enhancement.get("relevancy", "N/A"))

    if enhancement.get("mistakes"):
        print("\n[Key Corrections]")
        for m in enhancement["mistakes"]:
            print(f"- {m}")

    print("\n[Improved Version]")
    print(enhancement.get("improved", "N/A"))
    
    if grammar_result["errors"]:
        print("\n[Detailed Grammar Notes]")
        for i, error in enumerate(grammar_result["errors"], 1):
            print(f"{i}. {error}")
    
    print("="*30)

if __name__ == "__main__":
    # Check if sample.wav exists in root
    sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample.wav")
    
    if os.path.exists(sample_file):
        run_evaluation(sample_file)
    else:
        print(f"Error: Could not find {sample_file}")
