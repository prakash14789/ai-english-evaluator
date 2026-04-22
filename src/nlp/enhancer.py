import os
import re
import google.generativeai as genai
from .local_evaluator import LocalEnglishEvaluator

# Initialize local evaluator lazily
_local_eval_instance = None

def get_local_evaluator():
    global _local_eval_instance
    if _local_eval_instance is None:
        _local_eval_instance = LocalEnglishEvaluator()
    return _local_eval_instance



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

    # Decide whether to use local model or API
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    
    if not api_key or use_local:
        if not use_local:
            print("GEMINI_API_KEY not found. Using local AI model for evaluation...")
        else:
            print("USE_LOCAL_MODEL is set. Using local AI model...")
            
        try:
            local_eval = get_local_evaluator()
            return local_eval.evaluate(text, question)
        except Exception as e:
            print(f"Local model error: {e}")
            if not api_key:
                return fallback
            # If local fails but API key exists, continue to API below

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        prompt = f"""
        You are an English grammar evaluator.
        
        Given a sentence (converted from speech), do the following:
        1. Correct the grammar.
        2. List the mistakes and their corrections.
        3. Give a grammar score out of 10 based on correctness and fluency.
        
        Input text: "{text}"
        {"Question asked: " + question if question else ""}
        
        Keep the response short and structured in JSON format:
        {{
          "corrected": "...",
          "mistakes": [
            {{"original": "...", "correction": "..."}}
          ],
          "relevancy": "...",
          "score": ...
        }}
        
        Note: The 'relevancy' field should evaluate if the response matches the question (if provided).
        Only return JSON. Do not add explanations outside the JSON.
        """

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

        import json
        try:
            data = json.loads(response.text.strip())
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            fallback["mistakes"] = ["Failed to parse AI response."]
            return fallback

        # Map JSON keys to the internal app keys
        mistakes_list = []
        for m in data.get("mistakes", []):
            if isinstance(m, dict):
                mistakes_list.append(f"You said: \"{m.get('original', '')}\" -> Correction: \"{m.get('correction', '')}\"")
            else:
                mistakes_list.append(str(m))

        return {
            "original": text,
            "mistakes": mistakes_list if mistakes_list else ["No specific mistakes identified."],
            "improved": data.get("corrected", text),
            "relevancy": data.get("relevancy", "Excellent, you answered the topic."),
            "score": str(data.get("score", "N/A"))
        }

    except Exception as e:
        print(f"Error in Enhancer: {e}")
        fallback["mistakes"] = [f"Error: {e}"]
        return fallback