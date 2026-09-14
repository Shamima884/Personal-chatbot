# Chatbot Web App

A browser version of the four tkinter chatbots in this project
(`main.py`, `custom_chatbot.py`, `profile_chatbot.py`, `story_chatbot.py`).

- **Custom / Profile / Story** tabs run entirely in JavaScript (the same
  knowledge bases and keyword-matching logic as the Python bots — no server
  round-trip, no API needed).
- **Groq AI** tab talks to the Python local server, which answers through a
  **CrewAI agent** (`crew_agent.py`). No API key is stored in the project:
  Groq is used when `GROQ_API_KEY` is set (e.g. on Render), otherwise a
  local Ollama server handles it — fully key-less.
- **History drawer** — the **☰ History** button opens a slide-out panel with
  every conversation. Click a conversation to reopen it, **✕** deletes it,
  **＋ New chat** starts a fresh conversation. History is stored in
  PostgreSQL when configured, otherwise in memory + the browser's
  `localStorage`.

## How to run

From the project folder:

```powershell
cd "Second project\webapp"
pip install -r requirements.txt   # optional — only needed for PostgreSQL
python server.py
```

Then open **http://127.0.0.1:8000** in your browser.

To use a different port:

```powershell
python server.py 9000
```

> The Groq AI tab is answered by a CrewAI agent. Install Ollama
> (https://ollama.com) and run it for a key-less setup, or set the
> `GROQ_API_KEY` env var (Render does this for you). The other three tabs
> work offline.

## History drawer

Click **☰ History** in the tab bar to open the slide-out drawer.

- Every conversation across all four tabs is listed there, newest first,
  with a bot badge, the first question as the title, and a relative time.
- Click a conversation to reopen it (it switches to the right tab).
- **✕** deletes a conversation; **＋ New chat** starts a fresh conversation
  for the currently active tab.
- When the server/PostgreSQL is unreachable the drawer falls back to the
  browser's `localStorage`, so offline chats are still saved.

## PostgreSQL storage

By default history is kept in memory (plus the localStorage fallback
above). To store history permanently in PostgreSQL:

1. Create a database, e.g. `CREATE DATABASE chatbot;`
2. Set `DATABASE_URL` in the project root `.env` file:

   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
   ```

3. Install the driver: `pip install "psycopg[binary]"` (it is already
   listed in `requirements.txt`).
4. Restart the server. On startup it prints
   `[webapp] Storage engine: PostgresStore` and creates the tables
   automatically. The app falls back to in-memory storage with a warning if
   PostgreSQL is unavailable.

On Render: add a **PostgreSQL** service and Render sets `DATABASE_URL`
automatically — the server picks it up on start.

## API

| Endpoint                 | Method | Purpose                             |
| ------------------------ | ------ | ----------------------------------- |
| `/api/chat`              | POST   | CrewAI chat; also saves the exchange |
| `/api/history`           | GET    | List conversation sessions          |
| `/api/history`           | POST   | Create an empty session             |
| `/api/history/<id>`      | GET    | One session with its messages       |
| `/api/history/<id>`      | DELETE | Delete a session                    |
| `/api/history/messages`  | POST   | Save an exchange for the offline bots |

## Files

| File          | Purpose                                        |
| ------------- | ---------------------------------------------- |
| `index.html`  | Page structure and layout (incl. the history drawer)  |
| `style.css`   | Styling for the chat UI and the drawer                |
| `script.js`   | Chatbots + matching engine + UI + drawer logic        |
| `server.py`   | Static files + `/api/chat` CrewAI engine + history API (PostgreSQL or memory) |