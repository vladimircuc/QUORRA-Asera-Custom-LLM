# backend/services/title_generator.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_conversation_title(message_text: str) -> str:
    """
    Generate a short, descriptive title for a conversation based on the first user message.
    Example: "Fixing Asera Email Automation Issue"
    """
    prompt = f"""
    Create a short, clear title (max 8 words) for a chat conversation.
    The conversation starts with this message:
    "{message_text}"

    The title should summarize the main intent or topic.
    Do not use quotes or punctuation at the end.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise summarizer that creates short conversation titles."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    title = response.choices[0].message.content.strip()
    return title
