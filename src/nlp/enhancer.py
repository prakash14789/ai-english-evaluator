import os
import re
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def enhance_speech(text):
    """
    Analyzes spoken English and returns a structured dict with:
    - original: the raw transcript
    - mistakes: list of identified errors
    - improved: the corrected, professional version
    - score: a realistic score out of 10
    """
    fallback = {
        "original": text,
        "mistakes": ["Could not analyze. API key missing or unavailable."],
        "improved": text,
        "score": "N/A"
    }

    if not api_key:
        return fallback

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a strict English speaking evaluator and coach.

A user spoke the following sentence (converted from speech to text):

"{text}"

Your job:
1. Identify ALL grammar, vocabulary, and fluency mistakes
2. Rewrite it as a native English speaker would say it at a professional level
3. Give a realistic score — most spoken sentences score between 3–7

Return output EXACTLY in this format (no extra text):

MISTAKES:
- <mistake 1>
- <mistake 2>
- <mistake 3>

IMPROVED:
<the fully corrected and professional version>

SCORE:
<number only, out of 10>
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 400
            }
        )

        try:
            raw = response.text.strip()
        except (AttributeError, ValueError):
            fallback["mistakes"] = ["Safety filter blocked the response."]
            return fallback

        # --- Parse the structured response ---
        mistakes = []
        improved = text
        score = "N/A"

        # Extract MISTAKES block
        mistakes_match = re.search(r"MISTAKES:\s*((?:- .+\n?)+)", raw, re.IGNORECASE)
        if mistakes_match:
            mistakes_block = mistakes_match.group(1).strip()
            mistakes = [line.lstrip("- ").strip() for line in mistakes_block.split("\n") if line.strip().startswith("-")]

        # Extract IMPROVED block
        improved_match = re.search(r"IMPROVED:\s*(.+?)(?=SCORE:|$)", raw, re.IGNORECASE | re.DOTALL)
        if improved_match:
            improved = improved_match.group(1).strip()

        # Extract SCORE block
        score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", raw, re.IGNORECASE)
        if score_match:
            score = score_match.group(1)

        return {
            "original": text,
            "mistakes": mistakes if mistakes else ["No specific mistakes identified."],
            "improved": improved,
            "score": score
        }

    except Exception as e:
        print(f"❌ Error in Enhancer: {e}")
        fallback["mistakes"] = [f"Error: {e}"]
        return fallback