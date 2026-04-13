import os
import google.generativeai as genai
import json

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_vocabulary(text):
    """
    Analyze the vocabulary complexity and provide suggestions using Gemini.
    """
    if not api_key:
        return {
            "level": "Unknown",
            "suggestions": [],
            "message": "GEMINI_API_KEY not found."
        }

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        
        prompt = f"""
        Analyze the following spoken English text for vocabulary quality:
        "{text}"

        Provide the analysis in JSON format with the following keys:
        - "level": The estimated CEFR level (A1, A2, B1, B2, C1, or C2).
        - "suggestions": A list of objects, each with "original" (the simple word used) and "improved" (a more sophisticated synonym). Focus on 2-3 key improvements.
        - "feedback": A brief 1-sentence observation about the word choice.

        Output ONLY the JSON.
        """

        response = model.generate_content(prompt)
        # Clean response text in case of markdown formatting
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Error analyzing vocabulary: {e}")
        return {
            "level": "B1",
            "suggestions": [],
            "feedback": "Could not perform deep analysis at this time."
        }

if __name__ == "__main__":
    test_text = "I think it is very good because I can do it easily."
    print(analyze_vocabulary(test_text))
