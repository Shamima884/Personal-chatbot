/* ---------------------------------------------------------------------------
 * Dr. Shamima Jahan — Chatbot web app
 *
 * Implements the same knowledge bases + keyword-matching logic as the
 * Python bots in this project:
 *   custom_chatbot.py  -> "Custom"
 *   profile_chatbot.py -> "Profile"
 *   story_chatbot.py   -> "Story"
 *   main.py            -> "Groq AI" (talks to the local server /api/chat)
 * ------------------------------------------------------------------------- */

"use strict";

/* ============================================================
 * 1. Custom chatbot (custom_chatbot.py)
 * ============================================================ */

const CUSTOM_KNOWLEDGE = [
  {
    label: "introduction",
    keywords: ["introduce", "about", "who are you", "who is", "tell me",
               "yourself", "describe", "bio", "profile", "background",
               "shamima", "shamima jahan", "dr shamima jahan"],
    answer: (
      "Dr. Shamima Jahan is an Associate Professor in the Physiology " +
      "department at Tairunnessa Memorial Medical College, Gazipur."
    ),
    details: (
      "Dr. Shamima Jahan is an Associate Professor in the Physiology " +
      "department at Tairunnessa Memorial Medical College, Gazipur. She " +
      "completed her M.B.B.S from Z.H. Sikder Women's Medical College " +
      "under Dhaka University and her postgraduate M.Phil in Physiology " +
      "under B.S.M.M.U. She has been working as a medical teacher for " +
      "the last 14 years, and every year she has 105 students. She has " +
      "also completed her AI training under the AI Academy of Bangladesh " +
      "(AIAB) and is one of the masterminds of AIAB. She is the founder " +
      "of Dr. Jahan's AI Academy and the first AI trainer among the " +
      "Physiologists of Bangladesh."
    ),
  },
  {
    label: "mbbs",
    keywords: ["mbbs", "mbbs degree", "her mbbs", "medical college",
               "bachelor", "undergraduate", "under graduate",
               "first degree", "medicine degree", "medical degree",
               "degree", "z.h. sikder", "z h sikder"],
    answer: (
      "She completed her M.B.B.S degree from Z.H. Sikder Women's Medical " +
      "College under Dhaka University."
    ),
  },
  {
    label: "postgraduate",
    keywords: ["mphil", "m.phil", "postgraduate", "post graduate",
               "higher study", "higher education", "masters", "master",
               "fellowship", "specialization", "b.s.m.m.u", "bsmmu"],
    answer: (
      "She completed her postgraduate M.Phil in Physiology under B.S.M.M.U."
    ),
  },
  {
    label: "position",
    keywords: ["position", "designation", "job", "role", "post",
               "professor", "prof.", "title", "rank", "status",
               "what is her job", "her job", "her position",
               "her job position"],
    answer: (
      "Her job position is Associate Professor in the Physiology " +
      "department at Tairunnessa Memorial Medical College, Gazipur."
    ),
  },
  {
    label: "institution",
    keywords: ["institution", "college", "university", "workplace",
               "where do you work", "where you work", "where does she work",
               "where do she work", "where do she works", "does she work",
               "she works", "where she work", "shamima work",
               "does shamima work", "school",
               "tairunnessa", "memorial", "gazipur", "organization",
               "employer", "place"],
    answer: (
      "She works at Tairunnessa Memorial Medical College, Gazipur, as an " +
      "Associate Professor in the Physiology department."
    ),
  },
  {
    label: "subject",
    keywords: ["subject", "specialty", "speciality", "physiology",
               "department", "teach", "teaching", "field", "subject matter"],
    answer: "Her subject / department is Physiology.",
  },
  {
    label: "experience",
    keywords: ["experience", "how long", "how many years", "14 years",
               "years", "been working", "she has been working",
               "has she been working", "she been working", "seniority",
               "since", "tenure", "duration", "career"],
    answer: (
      "She has been working for the last 14 years as Associate Professor " +
      "in the Physiology department at Tairunnessa Memorial Medical " +
      "College, Gazipur."
    ),
  },
  {
    label: "students",
    keywords: ["student", "students", "how many students", "batch",
               "pupil", "admission", "enroll", "class size", "105",
               "she gets", "her students"],
    answer: "Every year she gets 105 students.",
  },
  {
    label: "ai_qualifications",
    keywords: ["ai", "artificial intelligence", "a i", "ai training",
               "aiab", "academy of bangladesh", "ai academy",
               "mastermind", "founder", "dr jahan", "dr jahans",
               "ai trainer", "first ai trainer", "physiologist",
               "training"],
    answer: (
      "She has completed her AI training under the AI Academy of " +
      "Bangladesh (AIAB). She is one of the masterminds of AIAB, the " +
      "founder of Dr. Jahan's AI Academy, and the first AI trainer " +
      "among the Physiologists of Bangladesh."
    ),
  },
  {
    label: "help",
    keywords: ["help", "command", "menu", "what can you", "what do you",
               "options", "about you"],
    answer: (
      "I can tell you about Dr. Shamima Jahan's education, qualifications, " +
      "AI training, job position, workplace, experience, subject and " +
      "students. For example, ask: \"Who is Dr. Shamima Jahan?\", " +
      "\"Where did she complete her M.B.B.S degree?\", \"Where did she " +
      "complete her AI training?\", or \"What is her job position?\""
    ),
  },
];

const CUSTOM_PRIORITY = ["introduction", "institution", "postgraduate", "position",
                         "mbbs", "students", "experience", "subject",
                         "ai_qualifications", "help"];

const CUSTOM_FALLBACK = (
  "Sorry, I can only answer questions that are based on the information " +
  "provided about Dr. Shamima Jahan. I have no information about that. " +
  "You can ask me about her education, degrees, AI training, job, " +
  "workplace, subject, or her students."
);

const SHOW_DETAILS_KEYWORDS = ["detail", "more detail", "full", "everything",
                               "all about", "describe yourself", "tell me about"];
/* ============================================================
 * 2. Profile chatbot (profile_chatbot.py)
 * ============================================================ */

const PROFILE_KNOWLEDGE = [
  {
    label: "name",
    keywords: ["name", "who", "called", "your name", "introduce"],
    answer: "Her name is Dr. Shamima Jahan.",
  },
  {
    label: "age",
    keywords: ["age", "old", "how old", "born", "year old", "44"],
    answer: "She is 44 years old.",
  },
  {
    label: "qualification",
    keywords: ["qualification", "degree", "education", "educated",
               "mbbs", "mphil", "m.phil", "physiology", "study", "studied",
               "academic", "graduated", "doctor degree", "certificate",
               "ai", "artificial intelligence"],
    answer: (
      "Her educational qualifications are M.B.B.S, M.Phil in Physiology, " +
      "and AI training from the AI Academy of Bangladesh."
    ),
  },
  {
    label: "ai",
    keywords: ["ai", "artificial intelligence", "a i", "ai training",
               "aiab", "academy of bangladesh", "ai academy",
               "mastermind", "founder", "dr jahan", "dr jahans",
               "ai trainer", "first ai trainer", "physiologist",
               "training"],
    answer: (
      "She has completed her AI training under the AI Academy of " +
      "Bangladesh (AIAB). She is one of the masterminds of AIAB, the " +
      "founder of Dr. Jahan's AI Academy, and the first AI trainer " +
      "among the Physiologists of Bangladesh."
    ),
  },
  {
    label: "occupation",
    keywords: ["occupation", "job", "profession", "work", "do you do",
               "what does she do", "does she do", "professionally",
               "career", "employment", "role", "earning",
               "teaching", "teacher", "lecture"],
    answer: "Her occupation is medical teaching.",
  },
  {
    label: "responsibility",
    keywords: ["responsibility", "duties", "duty", "work do", "do in",
               "teach", "lecture", "class", "students", "take", "classes",
               "responsibilities", "day"],
    answer: (
      "Her responsibility is to take the lecture class to the first year " +
      "medical students."
    ),
  },
  {
    label: "jobstation",
    keywords: ["job station", "jobstation", "workplace", "college",
               "institution", "where do you work", "where does she work",
               "where do she work", "does she work", "university", "gazipur",
               "tairunnessa", "hospital", "organization", "employer"],
    answer: "Her job station is Tairunnessa Medical College, Gazipur.",
  },
];

const PROFILE_PRIORITY = ["name", "age", "qualification", "ai", "jobstation", "occupation",
                          "responsibility"];

const PROFILE_FALLBACK = (
  "Sorry, I can only answer questions that are based on Dr. Shamima Jahan's " +
  "profile. I have no information about that. You can ask about her name, " +
  "age, educational qualification, AI training, occupation, responsibility, " +
  "or job station."
);
/* ============================================================
 * 3. Story chatbot (story_chatbot.py)
 * ============================================================ */

const STORY_KNOWLEDGE = [
  {
    label: "introduction",
    keywords: ["who", "about", "introduce", "name", "yourself", "bio",
               "profile", "description", "background"],
    answer: "She is Dr. Shamima Jahan.",
    details: (
      "Dr. Shamima Jahan is a girl from a small village in rural " +
      "Bangladesh. She came from a Bengali medium background and moved to " +
      "the bustling streets of Dhaka to pursue her dreams of becoming a " +
      "doctor. Today she carries her medical degree and the lessons learned " +
      "through her struggles."
    ),
  },
  {
    label: "origin",
    keywords: ["village", "rural", "where from", "where is she from",
               "hometown", "born", "origin", "native", "from"],
    answer: "She is from a small village in rural Bangladesh.",
  },
  {
    label: "background_language",
    keywords: ["bengali", "medium", "language", "tongue", "native",
               "mother", "english"],
    answer: (
      "She comes from a Bengali medium background and always communicated " +
      "in her native tongue, Bengali."
    ),
  },
  {
    label: "dream_goal",
    keywords: ["dream", "goal", "aspiration", "ambition", "become doctor",
               "wanted", "purpose", "intention", "why"],
    answer: (
      "Her dream was to become a doctor. She journeyed to Dhaka to pursue " +
      "this dream."
    ),
  },
  {
    label: "journey_dhaka",
    keywords: ["dhaka", "journey", "moved", "shift", "stepped", "start",
               "begin", "go", "city", "embark", "left", "travell"],
    answer: (
      "As she stepped into the bustling streets of Dhaka, her heart raced " +
      "with excitement and trepidation -- she had just embarked on a " +
      "journey from her small rural village to pursue her dreams of " +
      "becoming a doctor."
    ),
  },
  {
    label: "challenge",
    keywords: ["barrier", "challenge", "struggle", "difficult", "problem",
               "obstacle", "hurdle", "hard", "trouble", "issue"],
    answer: (
      "The formidable challenge she faced was the language barrier. " +
      "Coming from a Bengali medium background, she found herself suddenly " +
      "in a world where every lecture and textbook was in English -- a " +
      "language that felt foreign and intimidating."
    ),
  },
  {
    label: "emotions",
    keywords: ["feel", "emot", "despair", "demoralize", "scare",
               "afraid", "fear", "overwhelm", "nervous", "sad",
               "nightmare", "lost", "doubt"],
    answer: (
      "Her first few weeks were a nightmare. She felt despair wash over her " +
      "like a dark cloud, became demoralized, questioned her abilities and " +
      "worthiness, and feared she did not belong. Limiting beliefs crept " +
      "in, whispering that perhaps she was not cut out for this path, and " +
      "the fear of failure loomed so large that she felt like a ship lost " +
      "at sea."
    ),
  },
  {
    label: "choice",
    keywords: ["choice", "decision", "choose", "surrender", "give up",
               "quit", "rise above", "stay"],
    answer: (
      "She realized she had a choice: she could either succumb to the " +
      "struggle or rise above it. She chose to rise above."
    ),
  },
  {
    label: "process",
    keywords: ["dedicate", "focus", "commit", "learning english",
               "dictionary", "senior", "classmates", "support", "practice",
               "study", "improve english", "improve my english",
               "improve her english"],
    answer: (
      "She committed to transform her fear into focus. She dedicated herself " +
      "to learning English, reached out to seniors and classmates for " +
      "support, and spent countless nights poring over dictionaries and " +
      "practicing conversations -- slowly turning her weaknesses into " +
      "strengths. She realized that a specific target and a clear course " +
      "can change a life."
    ),
  },
  {
    label: "improvement",
    keywords: ["confide", "excel", "better", "improve", "successful",
               "improvement", "hope", "strong", "succeed", "progress",
               "pay off", "perseverance", "paid off"],
    answer: (
      "With each new word she learned and each concept she understood, a " +
      "spark of hope ignited within her. As her English improved, so did " +
      "her confidence. She began to succeed in her studies, and the dream " +
      "that once felt so distant became a tangible reality. Her " +
      "perseverance paid off."
    ),
  },
  {
    label: "lesson",
    keywords: ["lesson", "teach", "learned", "realise", "realize", "message",
               "takeaway", "moral", "meaning", "insight", "stepping"],
    answer: (
      "She learned that challenges are not roadblocks; they are stepping " +
      "stones to greatness. And most importantly, she discovered that the " +
      "power to overcome adversity lies within each of us."
    ),
  },
  {
    label: "advice",
    keywords: ["advice", "obstacle", "break through", "barrier", "motivat",
               "inspire", "encourage", "tip", "suggest", "message",
               "background", "define"],
    answer: (
      "If you ever find yourself facing obstacles, remember that with " +
      "determination and the right support, you can break through any " +
      "barrier. Our backgrounds do not define our futures -- her journey " +
      "is a testament to that."
    ),
  },
  {
    label: "help",
    keywords: ["help", "what can you", "what do you", "options", "ask"],
    answer: (
      "I can tell you about Dr. Shamima Jahan's inspiring journey -- her " +
      "rural and Bangladesh background, her move to Dhaka, the language " +
      "barrier she faced, her struggle, how she overcame it, and the " +
      "lessons she learned. Ask me things like \"What challenge did she " +
      "face?\", \"How did she improve her English?\", or \"What lesson " +
      "did she learn?\""
    ),
  },
];

const STORY_PRIORITY = ["introduction", "challenge", "emotions", "lesson", "process",
                        "improvement", "advice", "journey_dhaka", "origin",
                        "background_language", "dream_goal", "choice", "help"];

const STORY_FALLBACK = (
  "Sorry, I can only answer questions that are based on Dr. Shamima Jahan's " +
  "story. I have no information about that. You can ask about her rural " +
  "background, her journey to Dhaka, the language barrier she faced, her " +
  "feelings, how she overcame her difficulties, or the lesson she learned."
);

const STORY_DETAIL_WORDS = ["details", "detail", "full", "whole", "complete",
                            "everything", "all about", "describe yourself",
                            "tell me about"];
/* ============================================================
 * 4. Matching / answering engine (ported from the Python bots)
 * ============================================================ */

function normalize(text) {
  const cleaned = text.toLowerCase().trim().replace(/[.,;:!?()'"]/g, "");
  return " " + cleaned + " ";
}

function scoreTopic(topic, question) {
  const q = normalize(question);
  let score = 0;
  for (const keyword of topic.keywords) {
    const kw = keyword.toLowerCase();
    if (q.includes(kw)) {
      score += 1;
      score += (kw.length > 7) ? 0.5 : 0;
    }
  }
  return score;
}

function pickBest(knowledge, priority, question) {
  let best = null;
  let bestScore = 0;
  for (const topic of knowledge) {
    const s = scoreTopic(topic, question);
    const tieWins = (
      s === bestScore && s > 0 && best !== null &&
      priority.indexOf(topic.label) < priority.indexOf(best.label)
    );
    if (s > bestScore || tieWins) {
      best = topic;
      bestScore = s;
    }
  }
  return { topic: best, score: bestScore };
}

function getCustomAnswer(question) {
  const q = question.trim();
  if (!q) return "Please type a question.";

  const nq = normalize(q);
  const detailQ = SHOW_DETAILS_KEYWORDS.some((k) => nq.includes(k));
  const wantYourself = ["about", "yourself", "who", "describe", "tell me",
                        "her", "shamima"]
    .some((k) => q.toLowerCase().includes(k));
  if (detailQ && wantYourself) {
    const intro = CUSTOM_KNOWLEDGE.find((t) => t.label === "introduction");
    return intro.details;
  }

  const { topic, score } = pickBest(CUSTOM_KNOWLEDGE, CUSTOM_PRIORITY, q);
  let best = topic;
  let bestScore = score;
  if (best !== null && best.label === "help" && bestScore < 3) {
    best = null;
  }
  if (best === null || bestScore === 0) return CUSTOM_FALLBACK;
  return best.answer;
}

function getProfileAnswer(question) {
  const q = question.trim();
  if (!q) return "Please type a question.";

  const { topic, score } = pickBest(PROFILE_KNOWLEDGE, PROFILE_PRIORITY, q);
  if (topic === null || score === 0) return PROFILE_FALLBACK;
  return topic.answer;
}

function getStoryAnswer(question) {
  const q = question.trim();
  if (!q) return "Please type a question.";

  const nq = normalize(q);
  if (
    STORY_DETAIL_WORDS.some((d) => nq.includes(d)) &&
    ["who", "about", "describe", "yourself", "intro", "story"]
      .some((k) => nq.includes(k))
  ) {
    const intro = STORY_KNOWLEDGE.find((t) => t.label === "introduction");
    return intro.details;
  }

  const { topic, score } = pickBest(STORY_KNOWLEDGE, STORY_PRIORITY, q);
  let best = topic;
  let bestScore = score;
  if (best !== null && best.label === "help" && bestScore < 3) {
    best = null;
  }
  if (best === null || bestScore === 0) return STORY_FALLBACK;
  return best.answer;
}
/* ============================================================
 * 5. Chat UI — bot configuration
 * ============================================================ */

const BOTS = {
  custom: {
    name: "Custom",
    title: "Ask about Dr. Shamima Jahan's education, degrees, AI training, job, workplace, experience, subject or students.",
    suggestions: [
      "Who is Dr. Shamima Jahan?",
      "Where did she complete her M.B.B.S degree?",
      "Where did she complete her AI training?",
      "What is her job position?",
      "Where does she work?",
      "How many years has she been working?",
      "Tell everything about her",
    ],
    ask: (text) => getCustomAnswer(text),
  },
  profile: {
    name: "Profile",
    title: "Ask about her name, age, educational qualification, AI training, occupation, responsibility or job station.",
    suggestions: [
      "What is her name?",
      "How old is she?",
      "What is her educational qualification?",
      "Where did she complete her AI training?",
      "What does she do?",
      "What is her responsibility?",
      "Where does she work?",
    ],
    ask: (text) => getProfileAnswer(text),
  },
  story: {
    name: "Story",
    title: "Ask about Dr. Shamima Jahan's background, her move to Dhaka, the language barrier, her feelings, how she overcame the odds, and the lesson she learned.",
    suggestions: [
      "Who is Dr. Shamima Jahan?",
      "Where is she from?",
      "What challenge did she face?",
      "How did she feel in her first weeks?",
      "How did she improve her English?",
      "What lesson did she learn?",
      "What advice does she have?",
    ],
    ask: (text) => getStoryAnswer(text),
  },
  main: {
    name: "Groq AI",
    title: "Powered by Groq — connects to the LLM through the local server. Ask anything!",
    suggestions: [
      "Hello, who is Dr. Shamima Jahan?",
      "Write a short greeting from Dr. Shamima Jahan for her students.",
      "What is physiology?",
      "Explain the heart in one paragraph.",
    ],
    ask: async (text) => {
      const messages = [...(chat.HISTORY.main || [])];
      messages.push({ role: "user", content: text });
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Server error " + res.status);
      }
      return data.reply;
    },
  },
};

const chat = {
  active: "custom",
  HISTORY: { custom: [], profile: [], story: [], main: [] },
  busy: false,
};

/* ---------- DOM references ---------- */
const chatEl = document.getElementById("chat");
const form = document.getElementById("input-form");
const input = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");
const tabsEl = document.getElementById("tabs");
const suggestionsEl = document.getElementById("suggestions");
/* ---------- Rendering ---------- */
function scrollToBottom() {
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addMessage(text, kind) {
  const div = document.createElement("div");
  const cls =
    kind === "user" ? "msg user"
    : kind === "error" ? "msg error"
    : kind === "meta" ? "msg meta"
    : "msg bot";
  div.className = cls;

  const who = document.createElement("span");
  who.className = "who";
  who.textContent =
    kind === "user" ? "You"
    : kind === "meta" ? "Note"
    : kind === "error" ? "Error"
    : "Dr. Shamima Jahan";
  div.appendChild(who);
  div.appendChild(document.createTextNode(text));
  chatEl.appendChild(div);
  scrollToBottom();
  return div;
}

function addTyping() {
  const div = document.createElement("div");
  div.className = "typing";
  div.setAttribute("data-typing", "true");
  div.innerHTML = "<span></span><span></span><span></span>";
  chatEl.appendChild(div);
  scrollToBottom();
  return div;
}

function removeTyping() {
  const t = chatEl.querySelector('[data-typing="true"]');
  if (t) t.remove();
}

function renderHistory(botId) {
  chatEl.innerHTML = "";
  const history = chat.HISTORY[botId] || [];
  if (history.length === 0) {
    const hi = document.createElement("div");
    hi.className = "msg meta";
    hi.textContent = BOTS[botId].title;
    chatEl.appendChild(hi);
  } else {
    for (const m of history) {
      addMessage(m.content, m.role === "user" ? "user" : "bot");
    }
  }
  scrollToBottom();
}

function renderSuggestions() {
  suggestionsEl.innerHTML = "";
  BOTS[chat.active].suggestions.forEach((s) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = s;
    chip.addEventListener("click", () => {
      input.value = s;
      sendMessage();
    });
    suggestionsEl.appendChild(chip);
  });
}

/* ---------- Logic ---------- */
function switchBot(botId) {
  chat.active = botId;
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.bot === botId);
  });
  renderHistory(botId);
  renderSuggestions();
  input.focus();
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text || chat.busy) return;
  input.value = "";
  chat.busy = true;
  sendBtn.disabled = true;

  addMessage(text, "user");
  chat.HISTORY[chat.active].push({ role: "user", content: text });

  const typingEl = addTyping();
  try {
    const reply = await BOTS[chat.active].ask(text);
    removeTyping();
    if (!reply) throw new Error("Empty reply.");
    addMessage(reply, "bot");
    chat.HISTORY[chat.active].push({ role: "assistant", content: reply });
  } catch (err) {
    removeTyping();
    addMessage(
      "Sorry, something went wrong. " + err.message + "\n\n" +
      "Hints:\n- Make sure the local server is running (python server.py).\n" +
      "- Make sure API_KEY is set in the .env file in the project folder.",
      "error"
    );
  } finally {
    chat.busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

/* ---------- Wire-up ---------- */
tabsEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".tab");
  if (btn && !btn.classList.contains("active")) {
    switchBot(btn.dataset.bot);
  }
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage();
});

/* ---------- Initial render ---------- */
renderHistory(chat.active);
renderSuggestions();
input.focus();

/* ---------------------------------------------------------------------------
 * Console self-test -- mirrors the --selftest of the Python chatbots.
 * Run the app with  http://127.0.0.1:8000/#selftest  to see results in DOM.
 * ------------------------------------------------------------------------- */
function runSelfTest() {
  const tests = [
    ["custom", "Who is Dr. Shamima Jahan?", "Associate Professor"],
    ["custom", "Where did she complete her M.B.B.S degree?", "Z.H. Sikder"],
    ["custom", "Where did she complete her AI training?", "AI Academy of Bangladesh"],
    ["custom", "Is she one of the masterminds of AIAB?", "masterminds"],
    ["custom", "Who is the founder of Dr. Jahan's AI Academy?", "founder"],
    ["custom", "Is she the first AI trainer among the Physiologists of Bangladesh?", "first AI trainer"],
    ["custom", "What is her job position?", "Associate Professor"],
    ["custom", "Where does she work?", "Tairunnessa Memorial Medical College"],
    ["custom", "How many years has she been working?", "14 years"],
    ["custom", "Tell everything about her", "M.Phil in Physiology"],
    ["custom", "What is the capital of France?", "Sorry, I can only answer"],
    ["profile", "What is her name?", "Her name is Dr. Shamima Jahan."],
    ["profile", "How old is she?", "44 years old"],
    ["profile", "What is her educational qualification?", "AI training"],
    ["profile", "Where did she complete her AI training?", "AI Academy of Bangladesh"],
    ["profile", "What does she do?", "medical teaching"],
    ["profile", "Where does she work?", "Tairunnessa Medical College"],
    ["profile", "What is the capital of France?", "Sorry, I can only answer"],
    ["story", "Who is Dr. Shamima Jahan?", "Dr. Shamima Jahan"],
    ["story", "Where is she from?", "village in rural Bangladesh"],
    ["story", "What challenge did she face?", "language barrier"],
    ["story", "How did she improve her English?", "learning English"],
    ["story", "What lesson did she learn?", "stepping stones to greatness"],
    ["story", "What advice does she have?", "break through any barrier"],
    ["story", "What is the capital of France?", "Sorry, I can only answer"],
  ];
  const results = [];
  for (const [bot, question, expected] of tests) {
    let answer;
    if (bot === "custom") answer = getCustomAnswer(question);
    else if (bot === "profile") answer = getProfileAnswer(question);
    else answer = getStoryAnswer(question);
    const ok = answer.toLowerCase().includes(expected.toLowerCase());
    results.push((ok ? "PASS " : "FAIL ") + "[" + bot + "] " +
                 question + " => " + answer.split("\n")[0]);
  }
  const fails = results.filter((r) => r.startsWith("FAIL")).length;
  const pre = document.createElement("pre");
  pre.id = "selftest-results";
  pre.textContent = results.join("\n") + "\n\n" +
                    (fails === 0 ? "ALL TESTS PASSED" : fails + " TEST(S) FAILED");
  document.body.appendChild(pre);
}

if (window.location.hash === "#selftest") {
  runSelfTest();
}