import os
import random
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"), override=True)

# -------------------------------
# Fallback Questions Pool
# -------------------------------
FALLBACK_QUESTIONS = [
    "If you could travel anywhere in time, where would you go?",
    "What is a piece of technology you can't live without?",
    "How do you think AI will change jobs in the future?",
    "Describe a meal that always makes you happy.",
    "What is a hobby you've always wanted to try but haven't yet?",
    "What kind of environment helps you learn best?",
    "If you could master one skill instantly, what would it be?",
    "What does your perfect day look like?",
]

def clean_questions(raw_text):
    lines = raw_text.strip().split("\n")
    questions = []
    for line in lines:
        q = line.strip().lstrip("-•1234567890. ").strip()
        if q:
            questions.append(q)
    return list(dict.fromkeys(questions))

import google.generativeai as genai

def generate_questions(count=3, level="intermediate", track="General"):
    """
    Generate unique spoken English questions using Gemini based on a specific track.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Warning: GEMINI_API_KEY not found. Using fallback questions.")
        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]

    genai.configure(api_key=api_key)
    seed = random.randint(1, 10000)

    track_prompts = {
        "Software Engineer": "focused on technical interviews, SDLC, system design, and coding collaboration",
        "IELTS Speaking": "strictly following the IELTS Speaking Part 1 and Part 3 format",
        "Visa Interview": "focused on common questions asked by consulate officers for student or work visas",
        "General": "conversational and general interest topics"
    }

    track_desc = track_prompts.get(track, track_prompts["General"])

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        prompt = f"Seed: {seed}. List {count} unique conversational English questions for a {level} learner {track_desc}. One per line."
        
        response = model.generate_content(prompt)
        questions = clean_questions(response.text)
        
        if len(questions) < count:
            random.shuffle(FALLBACK_QUESTIONS)
            questions.extend(FALLBACK_QUESTIONS[:count-len(questions)])
            
        return questions[:count]
    except Exception as e:
        print(f"Error: {e}")
        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]

def generate_question(level="beginner", track="General"):
    return generate_questions(count=1, level=level, track=track)[0]

if __name__ == "__main__":
    print("\nGenerated Questions:\n")
    questions = generate_questions(count=3, level="beginner")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")