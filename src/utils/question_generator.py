import os
import google.generativeai as genai

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    # Fallback or warning if key is missing
    print("Warning: GEMINI_API_KEY not found in environment variables.")

def generate_question(level="beginner"):
    """
    Generate one spoken English question for a specific level learner using Gemini.
    """
    if not api_key:
        return "Can you tell me a little bit about yourself?" # Fallback static question

    try:
        model = genai.GenerativeModel("gemini-flash-latest") # Optimized for 2026 standards
        prompt = f"""
        Generate one spoken English interview-style question for a {level} level learner.
        Keep it simple, conversational, and open-ended.
        Output ONLY the question text.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating question: {e}")
        return "Describe your favorite hobby and why you enjoy it."

if __name__ == "__main__":
    # Test the generator if run directly
    print(f"Generated Question: {generate_question('beginner')}")
