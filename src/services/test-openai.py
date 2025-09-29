from openai import OpenAI
from dotenv import load_dotenv
import os

# load the .env file
load_dotenv()

# get key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# simple test request
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ]
)

print(response.choices[0].message.content)