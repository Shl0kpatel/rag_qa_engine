from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()  # loads .env from the project root/current working dir

from typing import Optional

from groq import Groq

_client: Optional[Groq] = None


def _get_client() -> Groq:
    """Create the Groq client only when needed (prevents import-time crash)."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Set it as an environment variable and re-run.\n"
            "PowerShell (current session):  $env:GROQ_API_KEY='YOUR_KEY'\n"
            "PowerShell (persistent):       setx GROQ_API_KEY \"YOUR_KEY\"\n"
            "cmd (current session):         set GROQ_API_KEY=YOUR_KEY"
        )

    _client = Groq(api_key=api_key)
    return _client


def generate_answer(prompt: str) -> str:
    client = _get_client()

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
    )

    return chat_completion.choices[0].message.content.strip()
