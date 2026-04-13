import re

def calculate_fluency(transcription_result):
    """
    Calculate Words Per Minute (WPM) and detect filler words.
    """
    text = transcription_result.get("text", "")
    segments = transcription_result.get("segments", [])
    
    if not text or not segments:
        return {
            "wpm": 0,
            "filler_count": 0,
            "filler_list": [],
            "duration_sec": 0
        }

    # 1. Calculate Duration
    start_time = segments[0]["start"]
    end_time = segments[-1]["end"]
    duration_sec = end_time - start_time
    
    # Avoid division by zero
    if duration_sec <= 0:
        duration_sec = 1 

    # 2. Count Words
    words = text.split()
    word_count = len(words)
    
    # 3. Calculate WPM
    wpm = int((word_count / duration_sec) * 60)

    # 4. Detect Filler Words
    # Common English fillers
    fillers = ["um", "uh", "ah", "er", "like", "you know", "actually", "basically", "literally"]
    detected_fillers = []
    
    # Case insensitive search
    text_lower = text.lower()
    for filler in fillers:
        # Use regex to find word boundaries
        matches = re.findall(rf"\b{re.escape(filler)}\b", text_lower)
        if matches:
            for _ in range(len(matches)):
                detected_fillers.append(filler)

    return {
        "wpm": wpm,
        "filler_count": len(detected_fillers),
        "filler_list": list(set(detected_fillers)), # Unique list for display
        "duration_sec": round(duration_sec, 2),
        "word_count": word_count
    }

if __name__ == "__main__":
    # Mock result
    mock = {
        "text": "Well, I think, like, coding is quite fun actually.",
        "segments": [{"start": 0.0, "end": 5.0}]
    }
    print(calculate_fluency(mock))
