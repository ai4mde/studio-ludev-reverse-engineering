import os
from typing import Dict, Any

# Try to import groq, but provide fallback if not available
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Warning: groq module not found, using OpenAI as fallback")
    GROQ_AVAILABLE = False

from openai import OpenAI
from llm.prompts.diagram import DIAGRAM_GENERATE_ATTRIBUTE, DIAGRAM_GENERATE_METHOD

def remove_reply_markdown(reply: str) -> str:
    lines = reply.splitlines()
    if len(lines) > 2:
        return '\n'.join(lines[1:-1])
    return ""


def call_openai(model: str, prompt: str) -> str:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    try:
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model = model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise Exception("Failed to call LLM, error " + str(e))


def call_groq(model: str, prompt: str) -> str:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    try:
        chat_completion = client.chat.completions.create(
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ],
            model = model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise Exception("Failed to call LLM, error " + str(e))


def llm_handler(prompt_name: str, model: str = "mixtral-8x7b-32768", input_data: Dict[str, Any] = {}) -> str:

    if not input_data:
        raise Exception("No input data given")

    if prompt_name == "DIAGRAM_GENERATE_ATTRIBUTE":
        prompt = DIAGRAM_GENERATE_ATTRIBUTE.format(data=input_data)
    elif prompt_name == "DIAGRAM_GENERATE_METHOD":
        prompt = DIAGRAM_GENERATE_METHOD.format(data=input_data)
    else:
        raise Exception("Invalid prompt name")

    if model == 'gpt-4o':
        return call_openai(model = model, prompt = prompt)
    else:
        return call_groq(model = model, prompt = prompt)
