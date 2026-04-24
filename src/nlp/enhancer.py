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
    Analyzes spoken English and returns a comprehensive structured dict.
    Consolidates Grammar, Vocabulary, and Relevancy into one call for speed.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

    # Decide whether to use local model or API
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    
    if not api_key or use_local:
        try:
            local_eval = get_local_evaluator()
            return local_eval.evaluate(text, question)
        except Exception as e:
            print(f"Local model error: {e}")
            if not api_key:
                return {"original": text, "mistakes": ["Key missing"], "improved": text, "score": "0"}

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        prompt = f"""
        Analyze this spoken English text: "{text}"
        {"Target Topic: " + question if question else ""}

        Perform a deep analysis and return ONLY a JSON object with:
        1. "corrected": A 10/10 professional version of the text.
        2. "mistakes": List of specific grammar/style mistakes found.
        3. "vocab_level": CEFR Level (A1-C2).
        4. "vocab_suggestions": List of 2-3 word upgrades ({{ "original": "...", "improved": "...", "improved_sentence": "..." }}).
        5. "relevancy": 1-sentence feedback on topic matching.
        6. "score": A numeric score out of 10.
        7. "lesson": A 'Micro-Lesson' (2 sentences max) explaining the main grammar rule violated + 3 short practice exercises (questions) for the user.

        Response format:
        {{
          "corrected": "...",
          "mistakes": ["..."],
          "vocab_level": "...",
          "vocab_suggestions": [{{...}}],
          "relevancy": "...",
          "score": 8.5,
          "lesson": {{ "explanation": "...", "exercises": ["...", "...", "..."] }}
        }}
        """

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )

        import json
        data = json.loads(response.text.strip())
        
        return {
            "original": text,
            "mistakes": data.get("mistakes", []),
            "improved": data.get("corrected", text),
            "relevancy": data.get("relevancy", "Relevant."),
            "score": str(data.get("score", "N/A")),
            "vocab": {
                "level": data.get("vocab_level", "B1"),
                "suggestions": data.get("vocab_suggestions", [])
            },
            "lesson": data.get("lesson", {"explanation": "Keep practicing!", "exercises": []})
        }

    except Exception as e:
        print(f"Error in Consolidated Enhancer: {e}")
        return {"original": text, "mistakes": [f"Error: {e}"], "improved": text, "score": "0", "vocab": {"level": "B1", "suggestions": []}}

    except Exception as e:
        print(f"Error in Enhancer: {e}")
        fallback["mistakes"] = [f"Error: {e}"]
        return fallback