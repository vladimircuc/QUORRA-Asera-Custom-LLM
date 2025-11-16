# services/gpt_tool_service.py
"""
Tool-calling runner for QUORRA.

- Exposes `generate_gpt_reply_with_tools(messages, tool_context=None)`
- Gives the model ONE tool for now: `rag_search_tool` (defined in services/tools/rag_search_tool.py)
- Enforces server guardrails (max tool calls, no source leakage, etc.)
- Prints an audit trail of tool calls (category, query, counts, best similarity…)
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

# Register tools
from services.tools.rag_search_tool import (
    TOOL_NAME as RAG_TOOL_NAME,
    get_tool_definition as rag_tool_def,
    run as rag_tool_run,
)

# -----------------------------
# Config knobs (easy to tweak)
# -----------------------------
MAX_TOOL_CALLS_PER_TURN = int(os.getenv("MAX_TOOL_CALLS_PER_TURN", "3"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # any tool-capable model
PRINT_MODEL_DECISION = True  # print what the model *planned* each time
# -----------------------------

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool registry (name → handler)
_TOOL_REGISTRY = {
    RAG_TOOL_NAME: {
        "def": rag_tool_def(),  # function schema for OpenAI
        "run": rag_tool_run,    # python executor
    },
}

def _tool_definitions_for_openai() -> List[Dict[str, Any]]:
    """OpenAI expects a list of tool specs."""
    return [entry["def"] for entry in _TOOLS_IN_USE]

# For now we only enable the RAG tool. If you add more, include them here.
_TOOLS_IN_USE = [
    _TOOL_REGISTRY[RAG_TOOL_NAME],
]


def generate_gpt_reply_with_tools(
    messages: List[Dict[str, str]],
    *,
    tool_context: Optional[Dict[str, Any]] = None,
    max_calls: int = MAX_TOOL_CALLS_PER_TURN,
    model: str = OPENAI_MODEL,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Main tool-calling loop.
    - `messages` must already include your system + client context + summary + history.
    - We append tool results back into this running `messages` list as the model calls tools.
    - Returns (assistant_text, audit_list).

    audit_list contains dicts like:
      {
        "idx": 1,
        "tool": "rag_search_tool",
        "args": {"query": "...", "category": "...", ...},
        "ok": True,
        "error": None,
        "result_meta": {...}  # kept, total, best_similarity, titles…
      }
    """
    tool_context = tool_context or {}
    audit: List[Dict[str, Any]] = []

    # Small internal rule to the model: you *may* call tools, but only if needed.
    # Messages coming in from api/messages.py already instruct this, but we add a gentle nudge.
    preface_rule = {
        "role": "system",
        "content": (
            "Tool policy: You may call tools to retrieve evidence. "
            "Use them only if you need more context to answer reliably. "
            f"You can call at most {max_calls} tool times this turn."
        ),
    }
    messages = [preface_rule, *messages]

    calls_remaining = max_calls

    while True:
        # 1) Ask the model what to do next (answer or tool-call)
        resp = _client.chat.completions.create(
            model=model,
            messages=messages,
            tools=_tool_definitions_for_openai(),
            tool_choice="auto",  # let the model decide
            temperature=0.2,
        )
        choice = resp.choices[0]
        msg = choice.message

        # 2) If the model returned a normal answer (no tool calls), we're done
        if not msg.tool_calls:
            # edge-case: sometimes content is None; normalize to empty string
            final_text = msg.content or ""
            return final_text, audit

        # 3) Otherwise, the model wants to call one or more tools
        tool_calls = msg.tool_calls
        if PRINT_MODEL_DECISION:
            print(f"🛠  Model requested {len(tool_calls)} tool call(s). "
                  f"Budget left: {calls_remaining}")

        # We append the model's tool-call message to history first
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
            tc.model_dump() if hasattr(tc, "model_dump") else tc for tc in tool_calls
        ]})

        # Execute each tool call in order
        for tc in tool_calls:
            tool_name = tc.function.name
            raw_args = tc.function.arguments or "{}"

            # Resolve and run
            registry_entry = next((t for t in _TOOLS_IN_USE if t["def"]["function"]["name"] == tool_name), None)
            if not registry_entry:
                # Unknown tool: tell the model it failed and let it decide a new step.
                err_note = f"Unknown tool '{tool_name}'."
                print(f"⚠️  {err_note}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": f'{{"ok": false, "error": "{err_note}"}}',
                })
                audit.append({
                    "idx": len(audit) + 1,
                    "tool": tool_name,
                    "args": raw_args,
                    "ok": False,
                    "error": err_note,
                })
                continue

            # Execute Python function
            try:
                result_payload = registry_entry["run"](raw_args, tool_context=tool_context)
                # tool result must be stringified JSON for OpenAI
                result_json = result_payload["json"]
                result_meta = result_payload.get("meta", {})
                print(f"✅ Tool '{tool_name}' executed.")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": result_json,  # JSON string
                })
                audit.append({
                    "idx": len(audit) + 1,
                    "tool": tool_name,
                    "args": result_payload.get("effective_args", raw_args),
                    "ok": True,
                    "error": None,
                    "result_meta": result_meta,
                })
            except Exception as e:
                err = f"Tool '{tool_name}' error: {e}"
                print(f"❌ {err}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": f'{{"ok": false, "error": "{str(e)}"}}',
                })
                audit.append({
                    "idx": len(audit) + 1,
                    "tool": tool_name,
                    "args": raw_args,
                    "ok": False,
                    "error": str(e),
                })

            # Decrease the budget after each executed tool
            calls_remaining -= 1
            if calls_remaining <= 0:
                print("⏳ Tool budget reached. Asking model to finish with available info.")
                messages.append({
                    "role": "system",
                    "content": "Tool budget reached. Finish your answer with the information you have.",
                })
                # Ask once more for final answer
                final = _client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                )
                return final.choices[0].message.content or "", audit

        # Loop again: the newly appended tool results are now in `messages`;
        # the model may either make another tool call (if budget left) or answer.
