# import os
# import google.generativeai as genai

# # Configure the Gemini API
# api_key = os.getenv("GEMINI_API_KEY")
# if api_key:
#     genai.configure(api_key=api_key)
# else:
#     # Fallback or warning if key is missing
#     print("Warning: GEMINI_API_KEY not found in environment variables.")

# import random

# def generate_questions(count=3, level="intermediate"):
#     """
#     Generate multiple unique spoken English questions using Gemini with a random seed.
#     """
#     if not api_key:
#         return ["Can you tell me a little bit about yourself?"] * count

#     # Add a random seed for variety
#     seed = random.randint(1, 1000)

#     try:
#         model = genai.GenerativeModel("gemini-flash-latest")
#         prompt = f"""
#         Seed: {seed}
#         Generate {count} unique, conversational English interview questions for an {level} learner.
#         Each question MUST focus on a completely different theme (e.g., Question 1: Space, Question 2: Cooking, Question 3: Technology).
#         Do NOT use common questions like 'Tell me about yourself'.
#         Output ONLY the questions as a simple list, one per line, without numbers.
#         """

#         response = model.generate_content(prompt)
#         questions = [q.strip() for q in response.text.strip().split("\n") if q.strip()]
        
#         # Unique Fallback Pool
#         fallbacks = [
#             "If you could travel anywhere in time, where would you go?",
#             "What is a piece of technology you can't live without?",
#             "How do you think AI will change our jobs in 5 years?",
#             "Describe a meal that always makes you happy.",
#             "What is a hobby you've always wanted to try but haven't yet?"
#         ]
#         random.shuffle(fallbacks)

#         while len(questions) < count:
#             questions.append(fallbacks.pop())
            
#         return questions[:count]
#     except Exception as e:
#         print(f"Error generating questions: {e}")
#         return ["Describe a significant challenge you overcame.", "What motivates you to learn English?", "Where do you see yourself in 5 years?"]

# def generate_question(level="beginner"):
#     """Legacy wrapper for single question."""
#     return generate_questions(count=1, level=level)[0]

# if __name__ == "__main__":
#     # Test the generator if run directly
#     print(f"Generated Question: {generate_question('beginner')}")


import os
import random
import google.generativeai as genai


# -------------------------------
# Configure the Gemini API
# -------------------------------
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ Warning: GEMINI_API_KEY not found. Using fallback questions.")


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


# -------------------------------
# Clean & Parse Model Output
# -------------------------------
def clean_questions(raw_text):
    lines = raw_text.strip().split("\n")
    questions = []

    for line in lines:
        q = line.strip()

        # Remove bullets, numbers, etc.
        q = q.lstrip("-•1234567890. ").strip()

        if q:
            questions.append(q)

    # Remove duplicates while preserving order
    unique_questions = list(dict.fromkeys(questions))

    return unique_questions


# -------------------------------
# Main Generator Function
# -------------------------------
def generate_questions(count=3, level="intermediate"):
    """
    Generate unique spoken English questions using Gemini.
    """

    # If API key missing → return fallback directly
    if not api_key:
        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]

    seed = random.randint(1, 10000)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Seed: {seed}

        Generate {count} UNIQUE, DIFFERENT conversational English interview questions for a {level} learner.

        STRICT RULES:
        - Each question must be about a completely different topic
        - No repeated questions
        - Avoid common questions like "Tell me about yourself"
        - Output exactly {count} questions
        - One question per line
        - No numbering or bullet points
        """

        response = model.generate_content(prompt)

        if not response.text:
            raise ValueError("Empty response from model")

        questions = clean_questions(response.text)

        # If still less → fill with fallback
        if len(questions) < count:
            remaining = count - len(questions)

            random.shuffle(FALLBACK_QUESTIONS)
            for q in FALLBACK_QUESTIONS:
                if q not in questions:
                    questions.append(q)
                if len(questions) == count:
                    break

        return questions[:count]

    except Exception as e:
        print(f"❌ Error generating questions: {e}")

        random.shuffle(FALLBACK_QUESTIONS)
        return FALLBACK_QUESTIONS[:count]


# -------------------------------
# Single Question Wrapper
# -------------------------------
def generate_question(level="beginner"):
    return generate_questions(count=1, level=level)[0]


# -------------------------------
# Testing
# -------------------------------
if __name__ == "__main__":
    print("\nGenerated Questions:\n")

    questions = generate_questions(count=3, level="beginner")

    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")