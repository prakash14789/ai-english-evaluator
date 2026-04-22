import re

class LocalEnglishEvaluator:
    def __init__(self, model_name="vennify/t5-base-grammar-correction"):
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        print(f"Loading local English evaluation model: {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Optimize memory and speed: use float16 on GPU, int8 on CPU if supported
        if self.device == "cuda":
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, torch_dtype=torch.float16).to(self.device)
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
            
        print("Model loaded successfully.")

    def evaluate(self, text, question=None):
        """
        Analyzes the text locally and returns structured feedback.
        """
        # 1. Grammar Correction
        input_text = "gec: " + text
        inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_length=512, 
                num_beams=1, # Greedy search is much faster than beam search
                early_stopping=True
            )
        
        improved_text = self.tokenizer.decode(outputs[0], skip_special_code=True, skip_special_tokens=True)
        
        # 2. Identify Mistakes (Simplified comparison)
        mistakes = self._extract_mistakes(text, improved_text)
        
        # 3. Scoring (Heuristic based on diff and length)
        score = self._calculate_score(text, improved_text)
        
        # 4. Relevancy (Simple keyword matching or semantic similarity if library available)
        relevancy = "Excellent, you answered the topic." if not question else self._check_relevancy(text, question)

        return {
            "original": text,
            "mistakes": mistakes if mistakes else ["No major grammar mistakes detected."],
            "improved": improved_text,
            "relevancy": relevancy,
            "score": str(score)
        }

    def _extract_mistakes(self, original, corrected):
        if original.strip().lower() == corrected.strip().lower():
            return []
        
        import difflib
        
        orig_words = original.split()
        corr_words = corrected.split()
        
        matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
        mistakes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                orig_part = " ".join(orig_words[i1:i2])
                corr_part = " ".join(corr_words[j1:j2])
                mistakes.append(f"You said: \"{orig_part}\" -> Correction: \"{corr_part}\"")
            elif tag == 'delete':
                orig_part = " ".join(orig_words[i1:i2])
                mistakes.append(f"Consider removing: \"{orig_part}\"")
            elif tag == 'insert':
                corr_part = " ".join(corr_words[j1:j2])
                mistakes.append(f"Consider adding: \"{corr_part}\"")
        
        if not mistakes:
            # Fallback if opcodes didn't catch it
            mistakes.append(f"Full rewrite suggested: \"{corrected}\"")
            
        return mistakes

    def _calculate_score(self, original, corrected):
        if not original.strip():
            return 0
            
        # Basic scoring logic
        import difflib
        s = difflib.SequenceMatcher(None, original.lower(), corrected.lower())
        ratio = s.ratio() # 1.0 means identical
        
        score = ratio * 10
        
        # Length penalty
        words = original.split()
        if len(words) < 5:
            score -= 1.5
            
        return round(max(1, min(10, score)), 1)

    def _check_relevancy(self, text, question):
        # Placeholder for relevancy check
        text_words = set(text.lower().split())
        question_words = set(question.lower().split())
        
        # Common non-informative words to ignore
        stopwords = {"what", "is", "your", "how", "do", "you", "the", "a", "an", "i", "my"}
        q_keywords = question_words - stopwords
        
        if not q_keywords:
            return "Relevant."
            
        overlap = text_words.intersection(q_keywords)
        if len(overlap) > 0:
            return "Good relevance to the question."
        else:
            return "The answer seems slightly off-topic. Try to use more keywords from the question."

if __name__ == "__main__":
    evaluator = LocalEnglishEvaluator()
    result = evaluator.evaluate("i goes to school yesterday", "What did you do yesterday?")
    print(result)
