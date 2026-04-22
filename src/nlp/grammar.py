import os
import language_tool_python
from .local_evaluator import LocalEnglishEvaluator

# Initialize rule-based tool as secondary/fallback
tool = language_tool_python.LanguageTool('en-US')

# Lazy initialize local evaluator
_local_evaluator = None

def get_local_evaluator():
    global _local_evaluator
    if _local_evaluator is None:
        _local_evaluator = LocalEnglishEvaluator()
    return _local_evaluator

def evaluate_grammar(text):
    """
    Evaluates grammar using either rule-based LanguageTool or Local AI Model.
    """
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    
    if use_local:
        print("Using local AI model for grammar evaluation...")
        try:
            evaluator = get_local_evaluator()
            result = evaluator.evaluate(text)
            
            # Convert LocalEnglishEvaluator format to expected evaluate_grammar format
            num_errors = len(result.get("mistakes", []))
            if result.get("mistakes") == ["No major grammar mistakes detected."]:
                num_errors = 0
                
            return {
                "score": float(result.get("score", 0)),
                "errors": result.get("mistakes", []),
                "corrected_text": result.get("improved", text),
                "num_errors": num_errors
            }
        except Exception as e:
            print(f"Local AI evaluation failed: {e}. Falling back to Rule-based.")

    # Rule-based Fallback (LanguageTool)
    print("Evaluating with rule-based LanguageTool...")
    matches = tool.check(text)
    num_errors = len(matches)
    score = 10 - (num_errors * 1.5)
    
    words = text.split()
    if len(words) < 5:
        score -= 2
    if text.lower().strip().startswith("because"):
        score -= 1.5
        
    score = max(0, min(10, round(score, 1)))
    corrected_text = tool.correct(text)
    
    return {
        "score": score,
        "errors": [f"Issue: '{match.message}' (Suggestion: {match.replacements[0] if match.replacements else 'N/A'})" for match in matches],
        "corrected_text": corrected_text,
        "num_errors": num_errors
    }

def correct_grammar(text):
    result = evaluate_grammar(text)
    return result["corrected_text"]

if __name__ == "__main__":
    sentence = "She go to school yesterday"
    result = evaluate_grammar(sentence)
    print("\n=== Grammar Result ===")
    print("Original:", sentence)
    print("Score:", result["score"], "/10")
    print("Corrected:", result["corrected_text"])