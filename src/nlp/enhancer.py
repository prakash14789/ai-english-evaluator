import os
import google.generativeai as genai

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def enhance_speech(text):
    """
    Takes a raw transcript and transforms it into a polished, professional, 
    and impactful version while preserving the original meaning.
    """
    if not api_key:
        return text # Fallback

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Original Spoken Text: "{text}"

        Task: Rewrite this spoken response to be "Great Speech". 
        - Use sophisticated vocabulary and professional idioms.
        - Improve sentence structure and flow.
        - Keep the original meaning and core message.
        - Make it sound natural for a high-level English speaker.
        
        Output ONLY the enhanced text. Do not add explanations or quotes.
        """

        response = model.generate_content(prompt)
        enhanced_text = response.text.strip()
        
        return enhanced_text
    except Exception as e:
        print(f"Error enhancing speech: {e}")
        return text

if __name__ == "__main__":
    test_text = "I like coding because it is fun and I can make things that help people."
    print("Original:", test_text)
    print("Enhanced:", enhance_speech(test_text))
