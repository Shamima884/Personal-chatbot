"""
Chatbot with a GUI (tkinter) that talks to Groq's API.

- Reads API_KEY from .env (no external packages required).
- GUI is built with Python's built-in tkinter.
- The chat request runs in a background thread so the UI never freezes.

Usage:
    python main.py            # launch the GUI
    python main.py --selftest # print one reply to the console (no GUI)
"""

import json
import os
import sys
import threading
import time
import tkinter as tk
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
API_BASE = "https://api.groq.com/openai/v1/chat/completions"

# A model that is currently available on Groq. Change to any model you like.
DEFAULT_MODEL = "qwen/qwen3.8-27b"
MAX_RETRIES = 4
RETRY_DELAY = 2.0

# A browser-style User-Agent is required -- Groq / its WAF rejects the
# default "Python-urllib" User-Agent with a 403 error.
BROWSER_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
}

# ---------------------------------------------------------------------------
# .env handling (no python-dotenv dependency)
# ---------------------------------------------------------------------------
def load_env(path=ENV_PATH):
    """Return a dict of KEY=VALUE pairs parsed from a simple .env file."""
    values = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                values[k.strip()] = v.strip()
    return values


def get_api_key():
    try:
        return load_env().get("API_KEY", "").strip()
    except Exception:
        return ""
# ---------------------------------------------------------------------------
# Groq API call (the request is retried because connections sometimes drop).
# ---------------------------------------------------------------------------
def chat_completion(messages, model=DEFAULT_MODEL, api_key=None):
    """Send one request to Groq and return the assistant's reply text.

    Raises RuntimeError if the request ultimately fails.
    """
    api_key = api_key if api_key is not None else get_api_key()
    if not api_key:
        raise RuntimeError(
            "API_KEY not found. Add it to the .env file in the project folder."
        )

    headers = dict(BROWSER_HEADERS)
    headers["Authorization"] = "Bearer " + api_key

    body = json.dumps(
        {"model": model, "messages": messages, "max_tokens": 800}
    ).encode("utf-8")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            request = urllib.request.Request(API_BASE, data=body, headers=headers)
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as exc:
            # A real API problem: bad key, bad model, or rate limiting.
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")
            except Exception:
                pass
            raise RuntimeError(
                f"Groq API error {exc.code} {exc.reason}. "
                f"Detail: {detail or '(none)'}"
            ) from exc
        except (urllib.error.URLError, ConnectionError, OSError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"Could not reach the Groq API after {MAX_RETRIES} tries: {last_error}"
    )
# ---------------------------------------------------------------------------
# Console self-test (no GUI) -- validates the API connection.
# ---------------------------------------------------------------------------
def run_selftest():
    api_key = get_api_key()
    if not api_key:
        print("[selftest] ERROR: API_KEY not found in .env")
        return 1
    print(f"[selftest] model = {DEFAULT_MODEL}")
    print("[selftest] sending: 'Hello, who are you?'")
    try:
        reply = chat_completion(
            [{"role": "user", "content": "Hello, who are you?"}]
        )
        print("[selftest] reply: " + reply)
        return 0
    except Exception as exc:
        print(f"[selftest] FAILED: {exc}")
        return 1


# ---------------------------------------------------------------------------
# GUI application (tkinter)
# ---------------------------------------------------------------------------
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.api_key = get_api_key()
        self.history = []  # list of {"role": ..., "content": ...}

        root.title("Groq Chatbot")
        root.geometry("680x580")
        root.configure(bg="#f5f5f5")

        self._build_ui()

        if not self.api_key:
            self._add_line("Warning: API_KEY missing in .env. Add it & restart.",
                           "system")

    # -- UI construction ------------------------------------------------
    def _build_ui(self):
        frame = tk.Frame(self.root, bg="#f5f5f5", padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        chat_frame = tk.Frame(frame, bg="#f5f5f5")
        chat_frame.pack(fill="both", expand=True)

        self.chat = tk.Text(
            chat_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#1a1a1a",
            padx=10,
            pady=10,
            state="disabled",
            relief="flat",
        )
        self.chat.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat.configure(yscrollcommand=scrollbar.set)

        self.chat.tag_configure("usr", foreground="#0b5cad",
                                font=("Consolas", 10, "bold"))
        self.chat.tag_configure("bot", foreground="#0a7d34",
                                font=("Consolas", 10))
        self.chat.tag_configure("system", foreground="#c0392b")
        self.chat.tag_configure("status", foreground="#888888")

        input_frame = tk.Frame(frame, bg="#f5f5f5")
        input_frame.pack(fill="x", pady=(10, 0))

        self.entry = tk.Entry(input_frame, font=("Consolas", 11),
                              relief="solid", bd=1)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self._on_send())

        self.send_btn = tk.Button(
            input_frame, text="Send", command=self._on_send,
            bg="#0b57d0", fg="white", activebackground="#0a4ab0",
            activeforeground="white", relief="flat", padx=18,
            font=("Segoe UI", 10, "bold"),
        )
        self.send_btn.pack(side="left", padx=(8, 0))

        clear_btn = tk.Button(input_frame, text="Clear", command=self._on_clear,
                              bg="#e0e0e0", relief="flat", padx=12,
                              font=("Segoe UI", 10))
        clear_btn.pack(side="left", padx=(6, 0))

        self.entry.focus_set()

    # -- helpers --------------------------------------------------------
    def _on_clear(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.history = []

    def _on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")

        self._add_line("You: " + text, "usr")
        self.history.append({"role": "user", "content": text})
        messages = list(self.history)

        self.send_btn.configure(state="disabled")
        self._add_line("… thinking …", "status")

        threading.Thread(target=self._worker,
                         args=(messages,), daemon=True).start()

    def _worker(self, messages):
        try:
            reply = chat_completion(messages, api_key=self.api_key)
            self.root.after(0, self._finish, reply, None)
        except Exception as exc:
            self.root.after(0, self._finish, None, str(exc))

    def _finish(self, reply, error):
        self._remove_last_line()
        if error:
            self._add_line("Error: " + error, "system")
        else:
            self._add_line("Bot: " + reply, "bot")
            self.history.append({"role": "assistant", "content": reply})
        self.send_btn.configure(state="normal")
        self.entry.focus_set()

    # -- low-level text helpers ---------------------------------------
    def _add_line(self, text, tag=None):
        self.chat.configure(state="normal")
        self.chat.insert("end", text + "\n", tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _remove_last_line(self):
        self.chat.configure(state="normal")
        end = self.chat.index("end-1c")
        line = int(end.split(".")[0])
        if line > 1:
            self.chat.delete(f"{line - 1}.0", "end")
        else:
            self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return run_selftest()

    root = tk.Tk()
    ChatApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())