"""
Local web server for the "Dr. Shamima Jahan" chatbot web app.

- Serves the static frontend (index.html / style.css / script.js) from this
  folder.
- Exposes one JSON API endpoint:  POST /api/chat
  It forwards the chat messages to the Groq API (the same logic as main.py)
  so the API key stays in the .env file and never reaches the browser.

No third-party packages are required (Python standard library only).

Usage (from this folder):
    python server.py            # serves at http://127.0.0.1:8000
    python server.py 9000       # serve on a custom port
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # the folder that holds .env
DEFAULT_PORT = 8000

API_BASE = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.8-27b"
MAX_RETRIES = 4
RETRY_DELAY = 2.0

# Groq / its WAF rejects the default "Python-urllib" User-Agent (403).
BROWSER_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}


# ---------------------------------------------------------------------------
# .env handling (no python-dotenv dependency)
# ---------------------------------------------------------------------------
def load_env(path):
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


def get_api_key():
    # Cloud platforms (Render, etc.) inject the key via environment variables.
    env_key = os.environ.get("API_KEY", "").strip()
    if env_key:
        return env_key
    for path in (os.path.join(PROJECT_ROOT, ".env"),
                 os.path.join(BASE_DIR, ".env")):
        key = load_env(path).get("API_KEY", "").strip()
        if key:
            return key
    return ""


# ---------------------------------------------------------------------------
# Groq API call (mirrors main.py)
# ---------------------------------------------------------------------------
def chat_completion(messages, model=DEFAULT_MODEL, api_key=None):
    """Send one request to Groq and return the assistant's reply text."""
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
# HTTP handler
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    # -- helpers ---------------------------------------------------------
    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        full = os.path.realpath(os.path.join(BASE_DIR, path.lstrip("/")))
        # Guard against path traversal.
        if not full.startswith(os.path.realpath(BASE_DIR)) or not os.path.isfile(full):
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return
        ext = os.path.splitext(full)[1].lower()
        content_type = MIME_TYPES.get(ext, "application/octet-stream")
        try:
            with open(full, "rb") as f:
                data = f.read()
        except OSError:
            self._send(500, "Server error", "text/plain; charset=utf-8")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    # -- requests --------------------------------------------------------
    def do_GET(self):
        self._serve_static(urlparse(self.path).path)

    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            self._send(404, json.dumps({"error": "Not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            messages = data.get("messages") or []
            if not messages:
                self._send(400, json.dumps({"error": "messages is required"}))
                return
            reply = chat_completion(messages)
            self._send(200, json.dumps({"reply": reply}))
        except Exception as exc:
            self._send(500, json.dumps({"error": str(exc)}))

    def log_message(self, fmt, *args):
        sys.stderr.write("[webapp] " + fmt % args + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # Render injects PORT (and expects the server to bind to 0.0.0.0).
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    if argv and argv[0].isdigit():
        port = int(argv[0])
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving chatbot web app at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())