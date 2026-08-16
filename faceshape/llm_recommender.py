# """
# LLM-powered hairstyle recommendations
# """

import json
from django.conf import settings
from openai import OpenAI

def get_llm_client():
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


def build_prompt(face_shape: str, gender: str = "unisex", extra: dict = None) -> str:
    """
    Build a strong prompt for consistent, useful recommendations.
    """
    extra = extra or {}
    hair_length = extra.get("hair_length", "any")
    hair_texture = extra.get("hair_texture", "any")
    lifestyle = extra.get("lifestyle", "everyday")
    preferences = extra.get("preferences", "")

    prompt = f"""
You are an expert barber and hairstylist working at a modern barbershop called Barbro.
Your job is to recommend the best haircuts and hairstyles for a client based on face shape and gender presentation.

Client details:
- Face shape: {face_shape}
- Gender presentation: {gender}
- Preferred hair length: {hair_length}
- Hair texture: {hair_texture}

# Please respond in the following JSON format only (no extra text):

# {{
#   "face_shape": "{face_shape}",
#   "summary": "One short friendly sentence about this face shape",
#   "best_haircuts": [
#     {{"name": "Haircut name", "why": "Why it suits this face shape"}},
#     {{"name": "Haircut name", "why": "Why it suits this face shape"}},
#     {{"name": "Haircut name", "why": "Why it suits this face shape"}}
#     {{"name": "Haircut name", "why": "Why it suits this face shape"}}
#   ],
#   "best_styles": [
#     {{"name": "Style / finish name", "why": "Short reason"}},
#     {{"name": "Style / finish name", "why": "Short reason"}}
#   ],
#   "what_to_avoid": [
#     "Thing to avoid 1",
#     "Thing to avoid 2"
#   ],
#   "pro_tip": "One practical tip the barber can tell the client"
# }}

# Rules:
# - Give practical, modern recommendations suitable for a real barbershop.
# - Prefer styles that are popular in 2025-2026.
# - Keep language friendly and professional.
# - Return ONLY valid JSON.
# """
    return prompt.strip()


def get_llm_recommendations(
    face_shape: str,
    gender: str = "unisex",
    extra: dict = None,
) -> dict:
    """
    Returns hairstyle recommendations using Groq's llama-3.1-8b-instant model.
    """
    client = get_llm_client()

    prompt = build_prompt(face_shape, gender, extra)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional hairstylist. Always reply with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,# 0.7
            max_completion_tokens=300,# 800
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        data["source"] = "llm"
        return data

    except Exception as e:
        return {
    "face_shape": face_shape,
    "summary": f"Classic recommendations for a {face_shape} face.",

    "best_haircuts": [
        {"name": "Classic side part", "why": "A timeless haircut that suits most face shapes."},
        {"name": "Textured crop", "why": "Adds texture and enhances facial features."},
        {"name": "Pompadour", "why": "Creates volume and balances proportions."},
        {"name": "Quiff", "why": "Provides height and a modern look."},
        {"name": "Medium length with soft layers", "why": "Adds movement and versatility."}
    ],

    "best_styles": [
        {"name": "Long layers", "why": "Adds softness and natural movement."},
        {"name": "Blunt bob", "why": "Creates a clean and elegant appearance."},
        {"name": "Curtain bangs", "why": "Frames the face beautifully."},
        {"name": "Soft waves", "why": "Enhances facial balance with texture."},
        {"name": "Pixie cut", "why": "Highlights facial features with confidence."}
    ],

    "what_to_avoid": [
        "Avoid hairstyles that exaggerate your face shape.",
        "Avoid styles that create unnecessary width or length.",
        "Avoid extremely blunt heavy cuts."
    ],

    "pro_tip": "Choose hairstyles that complement your face shape and hair texture.",
    "source": "fallback",
    "error": str(e)
}

# ------------------------------------------------------------------

