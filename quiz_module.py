import re
import json
from typing import List, Dict, Any
from ai_config import generate_ai_text, is_api_configured
from database import log_interaction

def clean_json_block(text: str) -> str:
    """Removes Markdown ```json code fences if present and extracts json array."""
    # Find JSON array [...] inside text if surrounded by markdown or explanations
    match = re.search(r"(\[.*\])", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()

def generate_quiz(text: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    Generates multiple-choice questions (MCQs) from a given passage or topic.
    The number of questions generated is determined by the `count` parameter.
    Each contains a question, 4 options, and a matching correct answer.
    """
    try:
        count = max(1, min(int(count), 10))
    except (ValueError, TypeError):
        count = 3

    if not is_api_configured():
        # Fallback sample quiz for testing when Gemini API key is not set
        mock_quiz = []
        for i in range(1, count + 1):
            mock_quiz.append({
                "question": f"Question {i}: What is a fundamental aspect of '{text.strip()}'?",
                "options": [
                    f"Core foundational concept of {text.strip()}",
                    "Unrelated historical fiction",
                    "A hardware device discontinued in 1995",
                    "None of the above"
                ],
                "answer": f"Core foundational concept of {text.strip()}"
            })
        log_interaction(
            module="quiz",
            input_text=f"{text} (count: {count})",
            output_text=json.dumps(mock_quiz),
            model_used="Demo Quiz Generator"
        )
        return mock_quiz

    prompt = f"""
You are an expert educational quiz generator.

From the following topic or passage, generate exactly {count} multiple-choice questions (MCQs).
Each question must include:
1. "question": A clear, educational question testing knowledge of the topic.
2. "options": A list of exactly 4 plausible options [A, B, C, D].
3. "answer": The correct answer string which MUST EXACTLY match one of the items in "options".

Return ONLY a valid JSON array format, with NO Markdown wrapping and NO extra text:
[
  {{
    "question": "What is ...?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "answer": "Option 1"
  }}
]

Topic / Passage:
{text}
"""
    try:
        quiz_text = generate_ai_text(prompt)
        cleaned_text = clean_json_block(quiz_text)
        parsed_quiz = json.loads(cleaned_text)
        
        # Verify format
        if isinstance(parsed_quiz, list) and len(parsed_quiz) > 0:
            log_interaction(
                module="quiz",
                input_text=f"{text} (count: {count})",
                output_text=json.dumps(parsed_quiz),
                model_used="Gemini AI"
            )
            return parsed_quiz
        else:
            raise ValueError("Parsed quiz is not a valid list of questions")
            
    except Exception as e:
        print(f"[Quiz Module Error]: {e}")
        # Build graceful fallback MCQs matching the requested count
        fallback = []
        for i in range(1, count + 1):
            fallback.append({
                "question": f"Question {i}: In relation to '{text}', which principle is central to its study?",
                "options": [
                    f"Understanding key fundamentals and applications of {text}.",
                    "Disregarding all evidence and theory.",
                    "Memorizing isolated terminology without context.",
                    "None of the above."
                ],
                "answer": f"Understanding key fundamentals and applications of {text}."
            })
        log_interaction(
            module="quiz",
            input_text=f"{text} (count: {count})",
            output_text=f"Quiz Error Fallback: {e}",
            model_used="Error"
        )
        return fallback
