import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Your name is QUORRA and you are a helpful assistant that manages data. You are a custom chatbot for Asera."
}


def generate_gpt_reply(conversation_history: list[dict]) -> str:
    """
    Takes a list of {"role": ..., "content": ...} messages and returns GPT-4 reply.
    """
    full_history = [SYSTEM_PROMPT] + conversation_history

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=full_history,
        temperature=0.7
    )

    return response.choices[0].message.content
