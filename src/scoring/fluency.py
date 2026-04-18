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

    # 4. Timeline Analysis (for Graphing)
    timeline_data = []
    blank_spots = 0
    
    for i, seg in enumerate(segments):
        seg_text = seg.get("text", "").strip()
        seg_words = len(seg_text.split())
        seg_duration = seg["end"] - seg["start"]
        
        # Calculate WPM for this segment
        seg_wpm = int((seg_words / max(0.1, seg_duration)) * 60)
        timeline_data.append({"time": seg["start"], "wpm": seg_wpm})
        
        # Detect Blanks (pauses between segments)
        if i > 0:
            pause = seg["start"] - segments[i-1]["end"]
            if pause > 1.5: # 1.5 seconds is a significant blank
                blank_spots += 1

    # 5. Detect Filler Words
    fillers = ["um", "uh", "ah", "er", "like", "you know", "actually", "basically", "literally"]
    detected_fillers = []
    text_lower = text.lower()
    for filler in fillers:
        matches = re.findall(rf"\b{re.escape(filler)}\b", text_lower)
        if matches:
            for _ in range(len(matches)):
                detected_fillers.append(filler)

    return {
        "wpm": wpm,
        "filler_count": len(detected_fillers),
        "filler_list": list(set(detected_fillers)),
        "duration_sec": round(duration_sec, 2),
        "word_count": word_count,
        "timeline": timeline_data,
        "blank_spots": blank_spots
    }

if __name__ == "__main__":
    # Mock result
    mock = {
        "text": "Well, I think, like, coding is quite fun actually.",
        "segments": [{"start": 0.0, "end": 5.0}]
    }
    print(calculate_fluency(mock))
