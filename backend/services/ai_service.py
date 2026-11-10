
import os
from anthropic import Anthropic


def generate_ai_response(prompt):

    # Read Anthropic API key securely
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "Anthropic API key is not configured. "
            "Please configure ANTHROPIC_API_KEY."
        )

    # Select model from environment configuration
    model = os.getenv(
        "ANTHROPIC_MODEL",
        "claude-sonnet-4-5"
    )

    # Create Anthropic client
    client = Anthropic(
        api_key=api_key,
        timeout=120.0,
        max_retries=2
    )

    # Send prompt to Claude
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract text response
    response_text = "".join(
        block.text
        for block in response.content
        if block.type == "text"
    )

    if not response_text:
        raise ValueError("Claude returned an empty response.")

    return response_text
