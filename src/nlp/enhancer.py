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
        Raw Transcript (Potentially broken or incorrect): "{text}"

        Task: Transform this into a "Perfect 10/10 Spoken Response".
        - FIX ALL GRAMMAR ERRORS.
        - If the transcript is a fragment (e.g., missing a verb or subject), RECONSTRUCT it into a complete, sophisticated sentence.
        - Use "IELTS Band 9" vocabulary and natural flow.
        - Keep the original intention but make it sound intelligent and professional.
        
        Example: 
        Raw: "I working data science because like code." 
        10/10: "I am currently employed in the field of data science, a career I pursued primarily due to my profound passion for programming and problem-solving."

        Output ONLY the perfected text. No explanations.
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
