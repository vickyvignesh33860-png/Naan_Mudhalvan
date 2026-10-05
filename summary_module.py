import google.generativeai as genai
from ai_config import generate_ai_text, is_api_configured
from database import log_interaction

def summarize_text(text: str) -> str:
    """Summarizes long paragraphs or educational passages into concise, clear versions."""
    model_name = "Gemini AI"
    
    if not is_api_configured():
        summary = (
            "⚠️ Google Gemini API Key is not configured yet. "
            "Please add your GEMINI_API_KEY in the .env file or update it in the Admin Dashboard to enable live AI summarization."
        )
        log_interaction(module="summarize", input_text=text[:150], output_text=summary, model_used="System Notice")
        return summary

    try:
        prompt = f"Summarize the following text in simple language, highlighting the main points clearly:\n\n{text}"
        summary = generate_ai_text(prompt)
            
        log_interaction(
            module="summarize",
            input_text=text[:200] + ("..." if len(text) > 200 else ""),
            output_text=summary,
            model_used=model_name
        )
        return summary
    except Exception as e:
        error_msg = f"⚠️ Error in Summary: {e}"
        log_interaction(module="summarize", input_text=text[:150], output_text=error_msg, model_used="Error")
        return error_msg
