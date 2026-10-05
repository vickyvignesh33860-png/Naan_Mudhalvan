import google.generativeai as genai
from ai_config import generate_ai_text, is_api_configured
from database import log_interaction

def answer_question_with_gemini(question: str) -> str:
    """Answers general knowledge and academic questions using Google Gemini."""
    model_name = "Gemini AI"
    
    if not is_api_configured():
        answer = (
            "⚠️ Google Gemini API Key is not configured yet. "
            "Please add your GEMINI_API_KEY in the .env file or update it in the Admin Dashboard to enable live Q&A."
        )
        log_interaction(module="qna", input_text=question, output_text=answer, model_used="System Notice")
        return answer

    try:
        answer = generate_ai_text(question)
        log_interaction(module="qna", input_text=question, output_text=answer, model_used=model_name)
        return answer
    except Exception as e:
        error_msg = f"⚠️ Error in QnA: {e}"
        log_interaction(module="qna", input_text=question, output_text=error_msg, model_used="Error")
        return error_msg
