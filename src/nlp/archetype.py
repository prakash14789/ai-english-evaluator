import os
import json

def determine_archetype(all_responses):
    """
    Analyze multiple responses to determine a user's English speaking archetype.
    """
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

    default_data = {
        "archetype": "The Communicator",
        "description": "A speaker who focuses on getting the message across effectively.",
        "strengths": ["Clear communication", "Practical usage"],
        "growth_area": "Expand vocabulary variety"
    }

    if not api_key:
        return default_data

    combined_text = "\n\n".join([f"Answer {i+1}: {text}" for i, text in enumerate(all_responses)])

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        
        prompt = f"""
        Analyze these spoken English responses and categorize the speaker into a creative 'English Archetype'.
        
        Responses:
        {combined_text}

        Determine:
        - "archetype": A creative title.
        - "description": A 2-sentence explanation.
        - "strengths": A JSON list of 2 key strengths.
        - "growth_area": One specific area for improvement.

        Output ONLY the JSON.
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Robust JSON cleaning
        if "```json" in response_text:
            response_text = response_text.split("```json")[-1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[-1].split("```")[0].strip()
            
        data = json.loads(response_text)
        
        return {
            "archetype": data.get("archetype", default_data["archetype"]),
            "description": data.get("description", default_data["description"]),
            "strengths": data.get("strengths", default_data["strengths"]),
            "growth_area": data.get("growth_area", default_data["growth_area"])
        }
        
    except Exception as e:
        print(f"Error determining archetype: {e}")
        return default_data
