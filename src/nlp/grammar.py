import language_tool_python

print("Starting grammar module...")

# Initialize the language tool (downloads about 100-200MB on first run, much smaller)
print("Loading LanguageTool...")
tool = language_tool_python.LanguageTool('en-US')
print("Model loaded.")

def correct_grammar(text):
    print("Correcting grammar...")
    corrected = tool.correct(text)
    return corrected


def evaluate_grammar(text):
    print("Evaluating grammar...")
    matches = tool.check(text)
    
    # Base score
    num_errors = len(matches)
    score = 10 - (num_errors * 1.5) # More strict penalty
    
    # Penalty for fragments (very short text with no main verb or bad structure)
    words = text.split()
    if len(words) < 5:
        score -= 2
    
    # Check for basic structure issues not caught by Tool (like starting with "because")
    if text.lower().strip().startswith("because"):
        score -= 1.5
        
    score = max(0, min(10, round(score, 1)))
    
    return {
        "score": score,
        "errors": [match.message for match in matches],
        "num_errors": num_errors
    }


if __name__ == "__main__":
    print("Running main...")

    sentence = "She go to school yesterday"

    corrected = correct_grammar(sentence)
    result = evaluate_grammar(sentence)

    print("\n=== Grammar Result ===")
    print("Original:", sentence)
    print("Corrected:", corrected)
    print("Score:", result["score"], "/10")
    if result["errors"]:
        print("Suggestions:", result["errors"])