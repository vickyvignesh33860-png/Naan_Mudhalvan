import traceback
import google.generativeai as genai
from ai_config import generate_ai_text, is_api_configured
from database import log_interaction

def get_learning_recommendations(topic: str) -> str:
    """
    Generates a personalized, structured learning path for any given topic,
    covering beginner, intermediate, and advanced concepts with suggested resources.
    """
    model_name = "Gemini 1.5 Pro"
    
    if not is_api_configured():
        fallback_path = f"""## Learning Recommendations for "{topic}":

### I. Beginner Level: Building a Foundation
*(Estimated Time: 1-2 weeks)*
- **Key Concepts:** Core definitions, introductory principles, syntax and vocabulary.
- **Hands-on practice:** Basic hello-world exercises and foundational drills.
- **Recommended Free Resources:**
  - Official documentation & beginner tutorials
  - Khan Academy / FreeCodeCamp overview video

### II. Intermediate Level: Core Applications & Tools
*(Estimated Time: 2-3 weeks)*
- **Key Concepts:** Practical problem solving, working with tools, libraries, and frameworks.
- **Projects:** Build 2 end-to-end guided mini-projects.
- **Recommended Resources:**
  - Interactive tutorials, documentation guides, and community forums.

### III. Advanced Level: Mastery & Optimization
*(Estimated Time: 3-4 weeks)*
- **Key Concepts:** Performance tuning, system architecture, edge cases, and best practices.
- **Projects:** Portfolio-ready capstone project solving a real-world problem.

*(Tip: Add your Google Gemini API Key in the .env file or Admin Dashboard for dynamically tailored AI recommendations.)*"""
        log_interaction(
            module="learning_path",
            input_text=topic,
            output_text=fallback_path,
            model_used="Curriculum Template"
        )
        return fallback_path

    prompt = f"""
You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of learning, and resources (books, tutorials, video courses).
Include beginner, intermediate, and advanced levels with estimated timelines and practical tips.
Format with clean Markdown with bold headers and bullet points.
"""
    try:
        result = generate_ai_text(prompt)


        log_interaction(
            module="learning_path",
            input_text=topic,
            output_text=result,
            model_used=model_name
        )
        return result
    except Exception as e:
        traceback.print_exc()
        error_msg = f"Error occurred: {str(e)}"
        log_interaction(
            module="learning_path",
            input_text=topic,
            output_text=error_msg,
            model_used="Error"
        )
        return error_msg
