import os
import threading
from typing import Optional
from database import log_interaction
from ai_config import is_api_configured, get_gemini_model

# Local Model State
_explain_tokenizer = None
_explain_model = None
_model_loading = False
_model_load_lock = threading.Lock()
_model_load_error = None

def _get_local_model():
    """Lazily loads the LaMini-Flan-T5-783M model and tokenizer."""
    global _explain_tokenizer, _explain_model, _model_loading, _model_load_error
    
    if _explain_tokenizer is not None and _explain_model is not None:
        return _explain_tokenizer, _explain_model
        
    with _model_load_lock:
        if _explain_tokenizer is not None and _explain_model is not None:
            return _explain_tokenizer, _explain_model
            
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            # Check if local model weights are already cached locally
            try:
                tokenizer = AutoTokenizer.from_pretrained("MBZUAI/LaMini-Flan-T5-783M", local_files_only=True)
                model = AutoModelForSeq2SeqLM.from_pretrained("MBZUAI/LaMini-Flan-T5-783M", local_files_only=True)
            except Exception:
                # If not cached locally, use Gemini unless DOWNLOAD_LAMINI=true
                if os.getenv("DOWNLOAD_LAMINI", "").lower() == "true":
                    print("[EduGenie] Downloading local model: MBZUAI/LaMini-Flan-T5-783M...")
                    tokenizer = AutoTokenizer.from_pretrained("MBZUAI/LaMini-Flan-T5-783M")
                    model = AutoModelForSeq2SeqLM.from_pretrained("MBZUAI/LaMini-Flan-T5-783M")
                else:
                    return None, None
            
            # Place on GPU if CUDA is available, else CPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            
            _explain_tokenizer = tokenizer
            _explain_model = model
            print("[EduGenie] Local LaMini-Flan-T5-783M loaded successfully.")
            return _explain_tokenizer, _explain_model
        except Exception as e:
            _model_load_error = str(e)
            return None, None

def explain_topic(topic: str) -> str:
    """
    Explains the concept in a simple and clear way for a school student.
    Uses LaMini-Flan-T5-783M locally as specified in EduGenie documentation,
    with automatic fallback to Gemini 1.5 if local model is unavailable.
    """
    model_used = "LaMini-Flan-T5-783M"
    explanation = None
    
    # Try local LaMini-Flan-T5 model first
    tokenizer, model = _get_local_model()
    if tokenizer and model:
        try:
            import torch
            input_text = f"Explain the concept of '{topic}' in a simple and clear way for a school student."
            device = next(model.parameters()).device
            inputs = tokenizer(input_text, return_tensors="pt").to(device)

            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                do_sample=True
            )

            explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"[Local Explanation Error]: {e}")
            explanation = None

    # Fallback to Gemini if local model unavailable or failed
    if not explanation:
        if is_api_configured():
            try:
                prompt = f"Explain the concept of '{topic}' in a simple and clear way for a school student. Keep it concise, engaging, and easy to grasp in 2-3 short paragraphs."
                explanation = generate_ai_text(prompt)
                model_used = "Gemini AI (Cloud)"
            except Exception as e:
                explanation = f"Error generating explanation via Gemini: {e}"
                model_used = "Error"
        else:
            # Informative fallback if neither local model nor API key is active
            explanation = (
                f"{topic.capitalize()} is an important concept! In simple terms, it refers to the core principles "
                f"governing how this system works. (To activate live AI generation, connect your Google Gemini API key "
                f"or download the local LaMini-Flan-T5 model weights)."
            )
            model_used = "Offline Educational Demo"

    # Log interaction to SQLite database
    log_interaction(
        module="explain",
        input_text=topic,
        output_text=explanation,
        model_used=model_used
    )
    
    return explanation
