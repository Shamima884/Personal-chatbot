"""
Crew AI agent engine — replaces the old Groq API-key call.

The "Groq AI" chat tab (and the tkinter chatbot in main.py) now gets its
answers from a small CrewAI crew (one Agent + one Task) instead of calling
the Groq HTTP endpoint directly with a hardcoded API key.

No API key is stored in this project:
  - If the GROQ_API_KEY environment variable is set (Render injects it for
    you), the agent uses Groq through CrewAI.
  - Otherwise the agent tries a local Ollama server
    (http://localhost:11434) so the app can run completely key-less.

Usage:
    from crew_agent import crew_chat
    reply = crew_chat(history)   # history = [{"role": ..., "content": ...}]
"""

import os
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
DEFAULT_OLLAMA_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

BACKSTORY = (
    "You are the helpful AI assistant for Dr. Shamima Jahan's personal "
    "chatbot. You follow the user's conversation and answer their last "
    "question clearly, accurately and in plain text. You do not invent "
    "facts; when you are unsure you say so."
)


# ---------------------------------------------------------------------------
# .env handling (no python-dotenv dependency)
# ---------------------------------------------------------------------------
def load_env(path=ENV_PATH):
    """Return a dict of KEY=VALUE pairs parsed from a simple .env file."""
    values = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    values[k.strip()] = v.strip()
        except OSError:
            pass
    return values


def _env(key):
    """Read a config value from the environment or the project .env file."""
    value = os.environ.get(key, "").strip()
    if value:
        return value
    return load_env().get(key, "").strip()


# ---------------------------------------------------------------------------
# LLM selection — Groq when a key is provided, local Ollama otherwise.
# ---------------------------------------------------------------------------
def _has_ollama():
    """True if a local Ollama server answers on the default port."""
    probe = OLLAMA_URL.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(probe, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def make_llm():
    """Build the CrewAI LLM without storing any key in the project.

    Prefers GROQ_API_KEY (set → uses Groq cloud). Without a key it falls
    back to a local Ollama server. Raises RuntimeError with friendly
    instructions when no LLM is reachable.
    """
    groq_key = _env("GROQ_API_KEY")
    if groq_key:
        try:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=_env("GROQ_MODEL") or DEFAULT_GROQ_MODEL,
                groq_api_key=groq_key,
                temperature=0.7,
            )
        except TypeError:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model_name=_env("GROQ_MODEL") or DEFAULT_GROQ_MODEL,
                groq_api_key=groq_key,
                temperature=0.7,
            )

    if not _has_ollama():
        raise RuntimeError(
            "No AI engine is configured for the Crew AI agent. Either:\n"
            "  1) set GROQ_API_KEY (the Render env var), or\n"
            "  2) install and start Ollama from https://ollama.com so the "
            "chatbot can run without any key."
        )
    try:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=_env("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL,
            base_url=_env("OLLAMA_URL") or OLLAMA_URL,
            temperature=0.7,
        )
    except TypeError:
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=_env("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL,
            base_url=_env("OLLAMA_URL") or OLLAMA_URL,
        )
def _make_agent(llm):
    """Create the CrewAI agent (tolerant to small API differences)."""
    from crewai import Agent

    kwargs = dict(
        role="Dr. Shamima Jahan's chatbot assistant",
        goal=(
            "Answer the user's last question helpfully, accurately and "
            "concisely, using the conversation so far as context."
        ),
        backstory=BACKSTORY,
        llm=llm,
    )
    try:
        return Agent(**kwargs, verbose=False, max_iter=2)
    except TypeError:
        return Agent(**kwargs)


def crew_chat(messages):
    """Answer the last user message with a CrewAI agent.

    messages: list of {"role": "user"|"assistant", "content": str}
    Returns the reply text.
    """
    # Resolve the LLM first: raises the friendly configuration error before
    # importing the heavy crewai package.
    llm = make_llm()

    from crewai import Crew, Process, Task

    agent = _make_agent(llm)

    transcript = "\n".join(
        "{0}: {1}".format(
            "User" if m.get("role") == "user" else "Assistant",
            m.get("content", ""),
        )
        for m in messages
        if m.get("content")
    )
    if not transcript:
        transcript = "(no prior conversation)"

    task = Task(
        description=(
            "Continue the conversation below as the assistant. Reply only "
            "to the last user message, using the earlier messages as "
            "context. Keep the reply short and plain.\n\n"
            "--- conversation ---\n" + transcript
        ),
        expected_output=(
            "A short, helpful, plain-text reply to the user's last message."
        ),
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff(inputs={})
    return getattr(result, "raw", None) or str(result)


if __name__ == "__main__":
    # Quick console self-test.
    try:
        reply = crew_chat(
            [{"role": "user", "content": "Hello, who is Dr. Shamima Jahan?"}]
        )
        print("[crew_agent] reply:", reply)
    except Exception as exc:
        print("[crew_agent] ERROR:", exc)