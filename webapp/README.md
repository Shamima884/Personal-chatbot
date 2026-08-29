# Chatbot Web App

A browser version of the four tkinter chatbots in this project
(`main.py`, `custom_chatbot.py`, `profile_chatbot.py`, `story_chatbot.py`).

- **Custom / Profile / Story** tabs run entirely in JavaScript (the same
  knowledge bases and keyword-matching logic as the Python bots — no server
  round-trip, no API needed).
- **Groq AI** tab talks to the Python local server, which proxies messages
  to the Groq API using the `API_KEY` from the project's `.env` file. The API
  key never reaches the browser.

## How to run

From the project folder:

```powershell
cd "Second project\webapp"
python server.py
```

Then open **http://127.0.0.1:8000** in your browser.

To use a different port:

```powershell
python server.py 9000
```

> The Groq AI tab needs a valid `API_KEY` in the `.env` file in the project
> root (one folder above `webapp`). The other three tabs work offline.

## Files

| File          | Purpose                                        |
| ------------- | ---------------------------------------------- |
| `index.html`  | Page structure and layout                      |
| `style.css`   | Styling for the chat UI                        |
| `script.js`   | Chatbots + matching engine + UI logic          |
| `server.py`   | Static file server + `/api/chat` Groq proxy    |