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

def generate_questions(count=3, level="intermediate"):
    """
    Generate unique spoken English questions using Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Warning: GEMINI_API_KEY not found. Using fallback questions.")
        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]

    # Deferred import for speed
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    seed = random.randint(1, 10000)

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        prompt = f"""
        Seed: {seed}
        Generate {count} UNIQUE conversational English interview questions for a {level} learner.
        One question per line. No numbering.
        """
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Empty response")

        questions = clean_questions(response.text)
        if len(questions) < count:
            random.shuffle(FALLBACK_QUESTIONS)
            for q in FALLBACK_QUESTIONS:
                if q not in questions:
                    questions.append(q)
                if len(questions) >= count: break
        return questions[:count]
    except Exception as e:
        print(f"Error: {e}")
        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]

def generate_question(level="beginner"):
    return generate_questions(count=1, level=level)[0]

if __name__ == "__main__":
    print("\nGenerated Questions:\n")
    questions = generate_questions(count=3, level="beginner")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")