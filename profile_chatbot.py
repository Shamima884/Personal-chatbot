"""
Custom Chatbot based on the profile of Dr. Shamima Jahan.

Answers ONLY questions that are based on the profile information provided.
If a question is outside that profile, it politely explains it cannot answer.

Profile facts:
  - Name: Dr. Shamima Jahan
  - Age: 44
  - Educational Qualification: M.B.B.S, M.Phil (Physiology)
  - Occupation: Medical teaching
  - Responsibility: Take the lecture class of first year medical students
  - Job station: Tairunnessa Medical College, Gazipur

Built with Python's built-in tkinter (no external packages required).

Usage:
    python profile_chatbot.py            # launch the GUI
    python profile_chatbot.py --selftest # test several questions in console
"""

import sys
import tkinter as tk

# ---------------------------------------------------------------------------
# Knowledge base -------------------------------------------------------------
# Each topic has a label, matching keywords, and the answer to give.
# ---------------------------------------------------------------------------
KNOWLEDGE = [
    {
        "label": "name",
        "keywords": ["name", "who", "called", "your name", "introduce"],
        "answer": "Her name is Dr. Shamima Jahan.",
    },
    {
        "label": "qualification",
        "keywords": ["qualification", "degree", "education", "educated",
                     "mbbs", "mphil", "m.phil", "physiology", "study", "studied",
                     "academic", "graduated", "doctor degree", "certificate",
                     "ai", "artificial intelligence"],
        "answer": (
            "Her educational qualifications are M.B.B.S, M.Phil in "
            "Physiology, and AI training from the AI Academy of Bangladesh."
        ),
    },
    {
        "label": "ai",
        "keywords": ["ai", "artificial intelligence", "a i", "ai training",
                     "aiab", "academy of bangladesh", "ai academy",
                     "mastermind", "founder", "dr jahan", "dr jahans",
                     "ai trainer", "first ai trainer", "physiologist",
                     "training"],
        "answer": (
            "She has completed her AI training under the AI Academy of "
            "Bangladesh (AIAB). She is one of the masterminds of AIAB, the "
            "founder of Dr. Jahan's AI Academy, and the first AI trainer "
            "among the Physiologists of Bangladesh."
        ),
    },
    {
        "label": "occupation",
        "keywords": ["occupation", "job", "profession", "work", "do you do",
                     "what does she do", "does she do", "professionally",
                     "career", "employment", "role", "earning",
                     "teaching", "teacher", "lecture"],
        "answer": "Her occupation is medical teaching.",
    },
    {
        "label": "responsibility",
        "keywords": ["responsibility", "duties", "duty", "work do", "do in",
                     "teach", "lecture", "class", "students", "take", "classes",
                     "responsibilities", "day"],
        "answer": (
            "Her responsibility is to take the lecture class to the first year "
            "medical students."
        ),
    },
    {
        "label": "jobstation",
        "keywords": ["job station", "jobstation", "workplace", "college",
                     "institution", "where do you work", "where does she work",
                     "where do she work", "does she work", "university",
                     "gazipur", "tairunnessa", "hospital", "organization",
                     "employer"],
        "answer": (
            "Her job station is Tairunnessa Medical College, Gazipur."
        ),
    },
]
PRIORITY = ["name", "qualification", "ai", "jobstation", "occupation",
            "responsibility"]

FALLBACK = (
    "Sorry, I can only answer questions that are based on Dr. Shamima Jahan's "
    "profile. I have no information about that. You can ask about her name, "
    "educational qualification, AI training, occupation, responsibility, "
    "or job station."
)


# ---------------------------------------------------------------------------
# Matching / answering logic -------------------------------------------------
# ---------------------------------------------------------------------------
def normalize(text):
    cleaned = text.lower().strip()
    for ch in ".,;:!?()'\"":
        cleaned = cleaned.replace(ch, "")
    return " " + cleaned + " "


def score_topic(topic, question):
    q = normalize(question)
    score = 0
    for keyword in topic["keywords"]:
        kw = keyword.lower()
        if kw in q:
            score += 1
            if len(kw) > 7:
                score += 0.5
    return score


def get_answer(question):
    q = question.strip()
    if not q:
        return "Please type a question."

    best = None
    best_score = 0
    for topic in KNOWLEDGE:
        s = score_topic(topic, q)
        if s > best_score or (s == best_score and s > 0 and best is not None
                              and PRIORITY.index(topic["label"])
                              < PRIORITY.index(best["label"])):
            best = topic
            best_score = s

    if best is None or best_score == 0:
        return FALLBACK

    return best["answer"]


def run_selftest(questions):
    for question in questions:
        print(f"Q: {question}")
        print(f"A: {get_answer(question)}")
        print("-" * 60)
    return 0
# ---------------------------------------------------------------------------
# GUI (tkinter) ---------------------------------------------------------------
# ---------------------------------------------------------------------------
class ChatApp:
    def __init__(self, root):
        self.root = root
        root.title("Dr. Shamima Jahan - Profile Chatbot")
        root.geometry("680x580")
        root.configure(bg="#f5f5f5")
        self._build_ui()

        self._add_line("Dr. Shamima Jahan - Profile Chatbot", "title")
        self._add_line(
            "Ask about her name, age, educational qualification, occupation, "
            "responsibility or job station.", "hint",
        )

    def _build_ui(self):
        frame = tk.Frame(self.root, bg="#f5f5f5", padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        chat_frame = tk.Frame(frame, bg="#f5f5f5")
        chat_frame.pack(fill="both", expand=True)

        self.chat = tk.Text(
            chat_frame, wrap="word", font=("Consolas", 10),
            bg="#ffffff", fg="#1a1a1a", padx=10, pady=10,
            state="disabled", relief="flat",
        )
        self.chat.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat.configure(yscrollcommand=scrollbar.set)

        self.chat.tag_configure("title", foreground="#124a75",
                                font=("Segoe UI", 14, "bold"))
        self.chat.tag_configure("hint", foreground="#888888",
                                font=("Consolas", 9, "italic"))
        self.chat.tag_configure("usr", foreground="#0b5cad",
                                font=("Consolas", 10, "bold"))
        self.chat.tag_configure("bot", foreground="#0a7d34",
                                font=("Consolas", 10))

        input_frame = tk.Frame(frame, bg="#f5f5f5")
        input_frame.pack(fill="x", pady=(10, 0))

        self.entry = tk.Entry(input_frame, font=("Consolas", 11),
                              relief="solid", bd=1)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self._on_send())

        send_btn = tk.Button(
            input_frame, text="Send", command=self._on_send,
            bg="#0b57d0", fg="white", activebackground="#0a4ab0",
            activeforeground="white", relief="flat", padx=18,
            font=("Segoe UI", 10, "bold"),
        )
        send_btn.pack(side="left", padx=(8, 0))

        clear_btn = tk.Button(input_frame, text="Clear", command=self._on_clear,
                              bg="#e0e0e0", relief="flat", padx=12,
                              font=("Segoe UI", 10))
        clear_btn.pack(side="left", padx=(6, 0))

        self.entry.focus_set()

    def _on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._add_line("You: " + text, "usr")
        self._add_line("Bot: " + get_answer(text), "bot")

    def _on_clear(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

    def _add_line(self, text, tag=None):
        self.chat.configure(state="normal")
        self.chat.insert("end", text + "\n", tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")


# ---------------------------------------------------------------------------
# Entry point -----------------------------------------------------------------
# ---------------------------------------------------------------------------
TEST_QUESTIONS = [
    "What is her name?",
    "What is her educational qualification?",
    "Where did she complete her AI training?",
    "Is she one of the masterminds of AIAB?",
    "What does she do?",
    "What is her occupation?",
    "What is her responsibility?",
    "Where does she work?",
    "What is her job station?",
    "What is the capital of France?",
]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return run_selftest(TEST_QUESTIONS)

    root = tk.Tk()
    ChatApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())