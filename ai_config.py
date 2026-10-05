import os
from dotenv import load_dotenv
import google.generativeai as genai
from database import get_db_setting

# Clean up any malformed system proxy variables that cause GRPC errors
for proxy_var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    val = os.getenv(proxy_var, "")
    if val and (" " in val or "composer" in val or "your-proxy-url" in val):
        os.environ.pop(proxy_var, None)

# Load environment variables from .env
load_dotenv()

# Supported models in priority order for high availability and separate quota pools
CANDIDATE_MODELS = [
    "models/gemini-3.1-flash-lite",
    "models/gemini-3.8-flash",
    "models/gemini-3.7-flash",
    "models/gemini-3.5-flash",
    "models/gemini-flash-latest",
    "models/gemini-pro-latest",
    "models/gemini-2.5-pro"
]

def get_api_key() -> str:
    """Retrieves the Gemini API key from database setting, environment, or .env."""
    db_key = get_db_setting("GEMINI_API_KEY")
    if db_key and db_key.strip():
        return db_key.strip()
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    return env_key.strip()

def is_api_configured() -> bool:
    """Returns True if a valid Gemini API key is configured."""
    key = get_api_key()
    return bool(key) and key != "your_gemini_api_key_here"

def get_gemini_model(model_name: str = None) -> genai.GenerativeModel:
    """Initializes and returns a Gemini GenerativeModel instance."""
    api_key = get_api_key()
    if api_key and api_key != "your_gemini_api_key_here":
        genai.configure(api_key=api_key)
    
    preferred_model = model_name or os.getenv("GEMINI_MODEL", "models/gemini-3.1-flash-lite")
    if not preferred_model.startswith("models/"):
        preferred_model = f"models/{preferred_model}"
        
    return genai.GenerativeModel(model_name=preferred_model)

def generate_ai_text(prompt: str, preferred_model: str = None) -> str:
    """
    Robust generator that queries Gemini with automatic model fallback
    if a specific model hits quota limits (429) or is retired (404).
    """
    api_key = get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key is not configured.")
        
    genai.configure(api_key=api_key)
    
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model if preferred_model.startswith("models/") else f"models/{preferred_model}")
    env_model = os.getenv("GEMINI_MODEL")
    if env_model:
        norm = env_model if env_model.startswith("models/") else f"models/{env_model}"
        if norm not in models_to_try:
            models_to_try.append(norm)
    for m in CANDIDATE_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)
            
    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            elif hasattr(response, "parts") and response.parts:
                return response.parts[0].text.strip()
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            # If 404 (not found), 429 (quota exceeded), or deprecated, seamlessly try next model
            if any(code in err_str for code in ["404", "429", "quota", "resourceexhausted", "not found", "no longer available"]):
                continue
            else:
                raise e

    if last_error:
        raise last_error
    raise RuntimeError("Failed to generate content with any Gemini model.")
