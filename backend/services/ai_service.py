import os
from google import genai


def generate_ai_response(prompt):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key is not configured")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text
