import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from notion_api import build_clients_payload

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- tool definition ---
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "list_clients",
            "description": "Return all client names from the Notion database. Optionally filter by a keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional substring to filter client names"
                    }
                },
                "required": []
            }
        }
    }
]

# --- in-memory message history ---
chat_history = [
    {"role": "system", "content": "Your name is QUORRA and you are a helpful assistant that manages client data. You get data from Notion. And you are a custom chatbot for Asera."},
]

# --- looped chat interaction ---
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        break

    # Add user message to chat
    chat_history.append({"role": "user", "content": user_input})

    # Call GPT-4 with tool definitions
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=chat_history,
        tools=tool_definitions,
        tool_choice="auto"
    )

    assistant_msg = response.choices[0].message
    chat_history.append(assistant_msg)

    # If GPT wants to call a function
    if assistant_msg.tool_calls:
        tool_call = assistant_msg.tool_calls[0]
        fn_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"\n💡 GPT wants to call: {fn_name}({args})")

        if fn_name == "list_clients":
            tool_response = build_clients_payload(**args)
        else:
            tool_response = {"error": f"Unknown tool: {fn_name}"}

        # Add tool response to chat history
        chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": fn_name,
            "content": json.dumps(tool_response)
        })

        # Final GPT response after seeing the tool output
        followup = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=chat_history
        )
        final_msg = followup.choices[0].message
        chat_history.append(final_msg)
        print(f"\n🤖 GPT: {final_msg.content}\n")

    else:
        print(f"\n🤖 GPT: {assistant_msg.content}\n")
