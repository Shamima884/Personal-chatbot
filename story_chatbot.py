"""
Custom Chatbot based on the story of Dr. Shamima Jahan.

This chatbot ONLY answers questions that are based on the story provided. If a
question is outside the story, it politely explains it cannot answer.

Built with Python's built-in tkinter (no external packages required).

Usage:
    python story_chatbot.py            # launch the GUI
    python story_chatbot.py --selftest # test several questions in console
"""

import sys
import tkinter as tk

# ---------------------------------------------------------------------------
# Knowledge base -------------------------------------------------------------
# Each topic: a label, keywords used for matching, and the answer to give.
# ---------------------------------------------------------------------------
KNOWLEDGE = [
    {
        "label": "introduction",
        "keywords": ["who", "about", "introduce", "name", "yourself", "bio",
                     "profile", "description", "background"],
        "answer": "I am Dr. Shamima Jahan.",
        "details": (
            "I am Dr. Shamima Jahan, a girl from a small village in rural "
            "Bangladesh. I came from a Bengali medium background and moved to "
            "the bustling streets of Dhaka to pursue my dreams of becoming a "
            "doctor. Today I carry my medical degree and the lessons learned "
            "through my struggles."
        ),
    },
    {
        "label": "origin",
        "keywords": ["village", "rural", "where from", "hometown", "born",
                     "origin", "native", "from"],
        "answer": (
            "I am from a small village in rural Bangladesh."
        ),
    },
    {
        "label": "background_language",
        "keywords": ["bengali", "medium", "language", "tongue", "native",
                     "mother", "english"],
        "answer": (
            "I come from a Bengali medium background and always communicated "
            "in my native tongue, Bengali."
        ),
    },
    {
        "label": "dream_goal",
        "keywords": ["dream", "goal", "aspiration", "ambition", "become doctor",
                     "wanted", "purpose", "intention", "why"],
        "answer": (
            "My dream was to become a doctor. I journeyed to Dhaka to pursue "
            "this dream."
        ),
    },
    {
        "label": "journey_dhaka",
        "keywords": ["dhaka", "journey", "moved", "shift", "stepped", "start",
                     "begin", "go", "city", "embark", "left", "travell"],
        "answer": (
            "As I stepped into the bustling streets of Dhaka, my heart raced "
            "with excitement and trepidation -- I had just embarked on a "
            "journey from my small rural village to pursue my dreams of "
            "becoming a doctor."
        ),
    },
    {
        "label": "challenge",
        "keywords": ["barrier", "challenge", "struggle", "difficult", "problem",
                     "obstacle", "hurdle", "hard", "trouble", "issue"],
        "answer": (
            "The formidable challenge I faced was the language barrier. "
            "Coming from a Bengali medium background, I found myself suddenly "
            "in a world where every lecture and textbook was in English -- a "
            "language that felt foreign and intimidating."
        ),
    },
    {
        "label": "emotions",
        "keywords": ["feel", "emot", "despair", "demoralize", "scare",
                     "afraid", "fear", "overwhelm", "nervous", "sad",
                     "nightmare", "lost", "doubt"],
        "answer": (
            "My first few weeks were a nightmare. I felt despair wash over me "
            "like a dark cloud, became demoralized, questioned my abilities and "
            "worthiness, and feared I did not belong. Limiting beliefs crept "
            "in, whispering that perhaps I was not cut out for this path, and "
            "the fear of failure loomed so large that I felt like a ship lost "
            "at sea."
        ),
    },
    {
        "label": "choice",
        "keywords": ["choice", "decision", "choose", "surrender", "give up",
                     "quit", "rise above", "stay"],
        "answer": (
            "I realized I had a choice: I could either succumb to the struggle "
            "or rise above it. I chose to rise above."
        ),
    },
    {
        "label": "process",
        "keywords": ["dedicate", "focus", "commit", "learning english",
                     "dictionary", "senior", "classmates", "support", "practice",
                     "study", "improve english", "improve my english"],
        "answer": (
            "I committed to transform my fear into focus. I dedicated myself "
            "to learning English, reached out to seniors and classmates for "
            "support, and spent countless nights poring over dictionaries and "
            "practicing conversations -- slowly turning my weaknesses into "
            "strengths. I realized that a specific target and a clear course "
            "can change a life."
        ),
    },
    {
        "label": "improvement",
        "keywords": ["confide", "excel", "better", "improve", "successful",
                     "improvement", "hope", "strong", "succeed", "progress",
                     "pay off", "perseverance", "paid off"],
        "answer": (
            "With each new word I learned and each concept I understood, a "
            "spark of hope ignited within me. As my English improved, so did "
            "my confidence. I began to succeed in my studies, and the dream "
            "that once felt so distant became a tangible reality. My "
            "perseverance paid off."
        ),
    },
    {
        "label": "lesson",
        "keywords": ["lesson", "teach", "learned", "realise", "realize", "message",
                     "takeaway", "moral", "meaning", "insight", "stepping"],
        "answer": (
            "I learned that challenges are not roadblocks; they are stepping "
            "stones to greatness. And most importantly, I discovered that the "
            "power to overcome adversity lies within each of us."
        ),
    },
    {
        "label": "advice",
        "keywords": ["advice", "obstacle", "break through", "barrier", "motivat",
                     "inspire", "encourage", "tip", "suggest", "message",
                     "background", "define"],
        "answer": (
            "If you ever find yourself facing obstacles, remember that with "
            "determination and the right support, you can break through any "
            "barrier. Our backgrounds do not define our futures -- my journey "
            "is a testament to that."
        ),
    },
    {
        "label": "help",
        "keywords": ["help", "what can you", "what do you", "options", "ask"],
        "answer": (
            "I can tell you about Dr. Shamima Jahan's inspiring journey -- her "
            "rural and Bangladesh background, her move to Dhaka, the language "
            "barrier she faced, her struggle, how she overcame it, and the "
            "lessons she learned. Ask me things like \"What challenge did you "
            "face?\", \"How did you improve your English?\", or \"What lesson "
            "did you learn?\""
        ),
    },
]

PRIORITY = ["introduction", "challenge", "emotions", "lesson", "process",
            "improvement", "advice", "journey_dhaka", "origin",
            "background_language", "dream_goal", "choice", "help"]

FALLBACK = (
    "Sorry, I can only answer questions that are based on the story I was "
    "given. I have no information about that. You can ask me about my "
    "background, my journey to Dhaka, the language barrier I faced, my "
    "feelings, how I overcame my difficulties, or the lesson I learned."
)

# Words that request the fuller profile summary.
DETAIL_WORDS = ["details", "detail", "full", "whole", "complete", "everything",
                "all about", "describe yourself", "tell me about"]
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

    # Full summary when a detail-word appears with a general intro/describe ask.
    nq = normalize(q)
    if any(d in nq for d in DETAIL_WORDS) and any(k in nq for k in
            ["who", "about", "describe", "yourself", "intro", "story"]):
        intro = next(t for t in KNOWLEDGE if t["label"] == "introduction")
        return intro["details"]

    best = None
    best_score = 0
    for topic in KNOWLEDGE:
        s = score_topic(topic, q)
        if s > best_score or (s == best_score and s > 0 and best is not None
                              and PRIORITY.index(topic["label"])
                              < PRIORITY.index(best["label"])):
            best = topic
            best_score = s

    if best is not None and best["label"] == "help" and best_score < 3:
        best = None
        best_score = 0

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
        root.title("Dr. Shamima Jahan - Journey Story Chatbot")
        root.geometry("680x580")
        root.configure(bg="#f5f5f5")
        self._build_ui()

        self._add_line("Dr. Shamima Jahan - Journey Story", "title")
        self._add_line(
            "Ask about my background, my move to Dhaka, the language barrier, "
            "my feelings, how I overcame the odds, and the lesson I learned.",
            "hint",
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
    "Who are you?",
    "Where are you from?",
    "What was your dream?",
    "What happened when you came to Dhaka?",
    "What was the barrier you faced?",
    "How did you feel in your first weeks?",
    "How did you improve your English?",
    "What did your perseverance lead to?",
    "What lesson did you learn?",
    "What advice do you have for someone facing obstacles?",
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