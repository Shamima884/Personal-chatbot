"""
Custom Chatbot for Dr. Shamima Jahan.

This chatbot ONLY answers based on the information that was provided about
Dr. Shamima Jahan. If a question is outside that information, it politely
explains it cannot answer.

Built with Python's built-in tkinter (no external packages required).

Usage:
    python custom_chatbot.py            # launch the GUI
    python custom_chatbot.py --selftest # test several questions in console
"""

import sys
import tkinter as tk

# ---------------------------------------------------------------------------
# Knowledge base -------------------------------------------------------------
# Each topic has a label, a list of keywords, and the answer to give.
# The chatbot picks the topic whose keywords match the user's question best.
# ---------------------------------------------------------------------------
KNOWLEDGE = [
    {
        "label": "introduction",
        "keywords": ["introduce", "about", "who are you", "who is", "tell me",
                     "yourself", "describe", "bio", "profile", "background",
                     "shamima", "shamima jahan", "dr shamima jahan"],
        "answer": (
            "Dr. Shamima Jahan is an Associate Professor in the Physiology "
            "department at Tairunnessa Memorial Medical College, Gazipur."
        ),
        "details": (
            "Dr. Shamima Jahan is an Associate Professor in the Physiology "
            "department at Tairunnessa Memorial Medical College, Gazipur. She "
            "completed her M.B.B.S from Z.H. Sikder Women's Medical College "
            "under Dhaka University and her postgraduate M.Phil in Physiology "
            "under B.S.M.M.U. She has been working as a medical teacher for "
            "the last 14 years, and every year she has 105 students. She has "
            "also completed her AI training under the AI Academy of Bangladesh "
            "(AIAB) and is one of the masterminds of AIAB. She is the founder "
            "of Dr. Jahan's AI Academy and the first AI trainer among the "
            "Physiologists of Bangladesh."
        ),
    },
    {
        "label": "mbbs",
        "keywords": ["mbbs", "mbbs degree", "her mbbs", "medical college",
                     "bachelor", "undergraduate", "under graduate",
                     "first degree", "medicine degree", "medical degree",
                     "degree", "z.h. sikder", "z h sikder"],
        "answer": (
            "She completed her M.B.B.S degree from Z.H. Sikder Women's Medical "
            "College under Dhaka University."
        ),
    },
    {
        "label": "postgraduate",
        "keywords": ["mphil", "m.phil", "postgraduate", "post graduate",
                     "higher study", "higher education", "masters", "master",
                     "fellowship", "specialization", "b.s.m.m.u", "bsmmu"],
        "answer": (
            "She completed her postgraduate M.Phil in Physiology under B.S.M.M.U."
        ),
    },
    {
        "label": "position",
        "keywords": ["position", "designation", "job", "role", "post",
                     "professor", "prof.", "title", "rank", "status",
                     "what is her job", "her job", "her position",
                     "her job position"],
        "answer": (
            "Her job position is Associate Professor in the Physiology "
            "department at Tairunnessa Memorial Medical College, Gazipur."
        ),
    },
    {
        "label": "institution",
        "keywords": ["institution", "college", "university", "workplace",
                     "where do you work", "where you work", "where does she work",
                     "where do she work", "where do she works", "does she work",
                     "she works", "where she work", "shamima work",
                     "does shamima work", "school", "tairunnessa", "memorial",
                     "gazipur", "organization", "employer", "place"],
        "answer": (
            "She works at Tairunnessa Memorial Medical College, Gazipur, as an "
            "Associate Professor in the Physiology department."
        ),
    },
    {
        "label": "subject",
        "keywords": ["subject", "specialty", "speciality", "physiology",
                     "department", "teach", "teaching", "field", "subject matter"],
        "answer": (
            "Her subject / department is Physiology."
        ),
    },
    {
        "label": "experience",
        "keywords": ["experience", "how long", "how many years", "14 years",
                     "years", "been working", "she has been working",
                     "has she been working", "she been working", "seniority",
                     "since", "tenure", "duration", "career"],
        "answer": (
            "She has been working for the last 14 years as Associate Professor "
            "in the Physiology department at Tairunnessa Memorial Medical "
            "College, Gazipur."
        ),
    },
    {
        "label": "students",
        "keywords": ["student", "students", "how many students", "batch",
                     "pupil", "admission", "enroll", "class size", "105",
                     "she gets", "her students"],
        "answer": (
            "Every year she gets 105 students."
        ),
    },
    {
        "label": "ai_qualifications",
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
        "label": "help",
        "keywords": ["help", "command", "menu", "what can you", "what do you",
                     "options", "about you"],
        "answer": (
            "I can tell you about Dr. Shamima Jahan's education, qualifications, "
            "AI training, job position, workplace, experience, subject and "
            "students. For example, ask: \"Who is Dr. Shamima Jahan?\", "
            "\"Where did she complete her M.B.B.S degree?\", \"Where did she "
            "complete her AI training?\", or \"What is her job position?\""
        ),
    },
]

# Topics whose keywords overlap heavily; give these a boost so a specific
# question (e.g. about the workplace) is not swallowed by a general topic.
TOPIC_PRIORITY = ["introduction", "institution", "postgraduate", "position",
                  "mbbs", "students", "experience", "subject",
                  "ai_qualifications", "help"]

FALLBACK = (
    "Sorry, I can only answer questions that are based on the information "
    "provided about Dr. Shamima Jahan. I have no information about that. "
    "You can ask me about her education, degrees, AI training, job, "
    "workplace, subject, or her students."
)

SHOW_DETAILS_KEYWORDS = ["detail", "more detail", "full", "everything",
                         "all about", "describe yourself", "tell me about"]
# ---------------------------------------------------------------------------
# Matching / answering logic -------------------------------------------------
# ---------------------------------------------------------------------------
def normalize(text):
    cleaned = text.lower().strip()
    # Remove punctuation so "M.B.B.S" -> "mbbs" and "M.Phil" -> "mphil".
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
            # Bonus for longer (more specific) keywords.
            score += 0.5 if len(kw) > 7 else 0
    return score


def get_answer(question):
    """Return the best matching answer for the user's question."""
    q = question.strip()
    if not q:
        return "Please type a question."

    # Show the full profile summary when a "detail/complete" word is used
    # together with a general who/describe query.
    detail_q = any(k in normalize(q) for k in SHOW_DETAILS_KEYWORDS)
    want_yourself = any(k in q.lower() for k in ["about", "yourself", "who",
                                                 "describe", "tell me", "her",
                                                 "shamima"])
    if detail_q and want_yourself:
        intro = next(t for t in KNOWLEDGE if t["label"] == "introduction")
        return intro["details"]

    # Score every topic and pick the best match (ties broken by priority).
    best = None
    best_score = 0
    for topic in KNOWLEDGE:
        s = score_topic(topic, q)
        if s > best_score or (s == best_score and s > 0 and best is not None
                              and TOPIC_PRIORITY.index(topic["label"])
                              < TOPIC_PRIORITY.index(best["label"])):
            best = topic
            best_score = s

    # The "help" topic is broad; only use it if nothing specific matched.
    if best is not None and best["label"] == "help" and best_score < 3:
        best = None
        best_score = 0

    if best is None or best_score == 0:
        return FALLBACK

    return best["answer"]


def run_selftest(questions):
    """Print model answers for a list of test questions (console only)."""
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
        root.title("Dr. Shamima Jahan Chatbot")
        root.geometry("680x580")
        root.configure(bg="#f5f5f5")
        self._build_ui()

        self._add_line("Dr. Shamima Jahan Chatbot", "title")
        self._add_line(
            "Ask me about her education, degrees, job, workplace, "
            "experience, subject or students.", "hint"
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

        self.chat.tag_configure("title", foreground="#124e78",
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
        answer = get_answer(text)
        self._add_line("Bot: " + answer, "bot")

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
DEFAULT_TEST_QUESTIONS = [
    "Who is Dr. Shamima Jahan?",
    "Where did she complete her M.B.B.S degree?",
    "Where did she complete her AI training?",
    "Is she one of the masterminds of AIAB?",
    "Who is the founder of Dr. Jahan's AI Academy?",
    "Is she the first AI trainer among the Physiologists of Bangladesh?",
    "What is her job position?",
    "Where does she work?",
    "How many years has she been working?",
    "Tell everything about her",
    "What is her subject?",
    "How many students does she get every year?",
    "What is the capital of France?",
]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return run_selftest(DEFAULT_TEST_QUESTIONS)

    root = tk.Tk()
    ChatApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())