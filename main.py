"""
Chatbot with a GUI (tkinter) whose AI answers come from CrewAI agents.

- The chat reply is produced by a CrewAI agent (crew_agent.py). No API key
  is stored in the project: Groq is used when GROQ_API_KEY is set, and a
  local Ollama server otherwise (fully key-less).
- GUI is built with Python's built-in tkinter.
- The chat request runs in a background thread so the UI never freezes.

Usage:
    python main.py            # launch the GUI
    python main.py --selftest # print one reply to the console (no GUI)
"""

import os
import sys
import threading
import tkinter as tk

from crew_agent import crew_chat

# ---------------------------------------------------------------------------
# Console self-test (no GUI) -- validates the CrewAI connection.
# ---------------------------------------------------------------------------
def run_selftest():
    print("[selftest] sending: 'Hello, who is Dr. Shamima Jahan?'")
    try:
        reply = crew_chat(
            [{"role": "user", "content": "Hello, who is Dr. Shamima Jahan?"}]
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
        self.history = []  # list of {"role": ..., "content": ...}

        root.title("Crew AI Chatbot")
        root.geometry("680x580")
        root.configure(bg="#f5f5f5")

        self._build_ui()

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
            reply = crew_chat(messages)
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