import os
import google.generativeai as genai

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
def enhance_speech(text):
    """
    Improves a raw transcript into a polished, fluent, and professional response.
    """

    if not api_key:
        return text  # fallback

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an expert English communication coach.

        INPUT:
        "{text}"

        TASK:
        Rewrite the sentence into a highly fluent, natural, and professional spoken response.

        STRICT RULES:
        - You MUST rewrite the sentence (do NOT repeat original)
        - Improve vocabulary to advanced (IELTS Band 8–9 level)
        - Fix grammar completely
        - Make it sound natural, confident, and smooth
        - Keep the original meaning EXACTLY the same
        - Expand slightly if needed to sound more complete
        - Do NOT make it robotic or overly complex

        OUTPUT:
        Only the improved sentence. No explanation.
        """

        response = model.generate_content(prompt)

        # Safely extract text from response
        try:
            enhanced = response.text.strip()
        except (AttributeError, ValueError):
            return text # Content was likely blocked by safety filters

        # Safety: if model returns same text → it means it failed the 'rewrite' instruction
        if enhanced.lower() == text.lower():
             return f"Professional version: {text.capitalize()}."

        return enhanced

    except Exception as e:
        print(f"❌ Error in Enhancer: {e}")
        return text