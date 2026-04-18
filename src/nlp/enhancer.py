import os
import re
import google.generativeai as genai



def enhance_speech(text, question=None):
    """
    Analyzes spoken English and returns a structured dict with:
    - original: the raw transcript
    - mistakes: list of identified errors
    - improved: the corrected, professional version
    - relevancy: feedback on whether the answer matched the question
    - score: a realistic score out of 10
    """
    # Read API key fresh every call to avoid stale module-level None
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

    fallback = {
        "original": text,
        "mistakes": ["Could not analyze. GEMINI_API_KEY is not set in your environment."],
        "improved": text,
        "relevancy": "Analysis skipped.",
        "score": "0"
    }

    if not api_key:
        return fallback

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        context_prompt = ""
        if question:
            context_prompt = f"The user was asked this specific question: \"{question}\"\n\n"

        prompt = f"""You are a strict English speaking evaluator and coach.

{context_prompt}A user spoke the following sentence (converted from speech to text):

"{text}"

Your job:
1. Identify ALL grammar, vocabulary, and fluency mistakes. 
2. For each mistake, explicitly quote what they said, and provide the ENTIRE sentence corrected. Do not just return the corrected word or phrase in isolation.
3. RELEVANCY CHECK: If a question was provided above, determine if this answer is relevant. If it is NOT relevant or off-topic, explain why and suggest what they should have talked about instead.
4. Rewrite the entire response as a native English speaker would say it at a professional level (this goes in the IMPROVED section). If the answer was irrelevant, the IMPROVED version should be a sample of a PERFECT, relevant answer to the question.
5. Give a realistic score — most spoken sentences score between 3–7.

Return output EXACTLY in this format (no extra text):

MISTAKES:
- [You said: "part of sentence"] -> [Full Corrected Sentence: "the entire sentence corrected"]

RELEVANCY:
<Brief feedback on relevancy. If relevant, say "Excellent, you answered the question." If not, explain why and give a tip.>

IMPROVED:
<the fully corrected and professional version of the whole text (or a perfect sample answer if original was off-topic)>

SCORE:
<A single number from 1 to 10. Do NOT write "N/A". Even if the answer is short, give a score based on what was said.>
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500
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
        relevancy = "No question was provided for relevancy check."
        score = "N/A"

        # Extract MISTAKES block
        mistakes_match = re.search(r"MISTAKES:\s*((?:- .+\n?)+)", raw, re.IGNORECASE)
        if mistakes_match:
            mistakes_block = mistakes_match.group(1).strip()
            mistakes = [line.lstrip("- ").strip() for line in mistakes_block.split("\n") if line.strip().startswith("-")]

        # Extract RELEVANCY block
        relevancy_match = re.search(r"RELEVANCY:\s*(.+?)(?=IMPROVED:|$)", raw, re.IGNORECASE | re.DOTALL)
        if relevancy_match:
            relevancy = relevancy_match.group(1).strip()

        # Extract IMPROVED block
        improved_match = re.search(r"IMPROVED:\s*(.+?)(?=SCORE:|$)", raw, re.IGNORECASE | re.DOTALL)
        if improved_match:
            improved = improved_match.group(1).strip()

        # Extract SCORE block - handles "SCORE: 7", "Score: 7/10", "SCORE: 7.5" etc.
        score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", raw, re.IGNORECASE)
        if score_match:
            score = score_match.group(1)
        else:
            # Secondary check for just "Score: 7"
            score_match = re.search(r"Score:\s*(\d+(?:\.\d+)?)", raw, re.IGNORECASE)
            if score_match:
                score = score_match.group(1)

        # Final Cleanup: If score is still not a number, default to 5 to avoid display issues
        if not str(score).replace('.', '', 1).isdigit():
            score = "5"
            mistakes.append("Note: Speech score calculation was approximate due to formatting.")

        return {
            "original": text,
            "mistakes": mistakes if mistakes else ["No specific mistakes identified."],
            "improved": improved,
            "relevancy": relevancy,
            "score": score
        }

    except Exception as e:
        print(f"Error in Enhancer: {e}")
        fallback["mistakes"] = [f"Error: {e}"]
        return fallback