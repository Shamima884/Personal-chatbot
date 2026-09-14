"""
Local web server for the "Dr. Shamima Jahan" chatbot web app.

- Serves the static frontend (index.html / style.css / script.js) from this
  folder.
- POST /api/chat              -> CrewAI chat (also persists the exchange)
- GET  /api/history           -> list saved conversations (for the drawer)
- GET  /api/history/<id>      -> one conversation with its messages
- POST /api/history           -> create an empty conversation
- POST /api/history/messages  -> save an exchange (offline tab bots)
- DELETE /api/history/<id>    -> delete a conversation

The answer is produced by a CrewAI agent (crew_agent.py). No API key is
stored in the project: Groq is used when GROQ_API_KEY is set (e.g. the
Render env var), otherwise a local Ollama server — so the browser never
sees any key.

Optional PostgreSQL persistence:
- Set DATABASE_URL (in the environment or in the .env files) to a
  PostgreSQL connection string, e.g.
      DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
- Install the driver:   pip install "psycopg[binary]"
Without a working database the server keeps history in memory instead, so
the app always runs (history is simply lost on restart).

Usage (from this folder):
    python server.py            # serves at http://127.0.0.1:8000
    python server.py 9000       # serve on a custom port
"""

import json
import os
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

try:  # Optional PostgreSQL driver (psycopg 3).
    import psycopg
    from psycopg.rows import dict_row
    PSYCOPG_AVAILABLE = True
except ImportError:
    psycopg = None
    PSYCOPG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # the folder that holds .env
DEFAULT_PORT = 8000

# The CrewAI agent engine lives in the project root (crew_agent.py).
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from crew_agent import crew_chat  # noqa: E402

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


# ---------------------------------------------------------------------------
# Storage layer — PostgreSQL (psycopg) with an in-memory fallback
#
# - If DATABASE_URL is set AND the psycopg driver is installed, the chat
#   history (sessions + messages) is persisted in PostgreSQL.
# - Otherwise the server keeps history in memory so the app works with
#   zero setup; the history is lost when the server restarts.
# ---------------------------------------------------------------------------
STORE_LOCK = threading.Lock()
store = None  # initialised from main() via create_store()


def get_database_url():
    """Return DATABASE_URL from the environment or from the .env files."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    for path in (os.path.join(PROJECT_ROOT, ".env"),
                 os.path.join(BASE_DIR, ".env")):
        url = load_env(path).get("DATABASE_URL", "").strip()
        if url:
            return url
    return ""


def _iso(value):
    """Serialize a datetime (or any value) to an ISO-8601 string."""
    if value is None:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat(timespec="seconds")
    return str(value)


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PostgresStore:
    """Persistent history stored in PostgreSQL (psycopg 3)."""

    DDL = [
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id BIGSERIAL PRIMARY KEY,
            bot TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT 'New chat',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id BIGSERIAL PRIMARY KEY,
            session_id BIGINT NOT NULL
                REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session
            ON chat_messages (session_id)
        """,
    ]

    def __init__(self, url):
        self.url = url
        with self._connect() as conn:
            for statement in self.DDL:
                conn.execute(statement)

    def _connect(self):
        try:
            # connect_timeout keeps a dead/unreachable Postgres from hanging
            # the server; we fall back to in-memory storage in that case.
            conn = psycopg.connect(self.url, autocommit=True,
                                   connect_timeout=5)
        except Exception as exc:
            raise RuntimeError(
                "Could not connect to PostgreSQL: %s" % exc
            ) from exc
        conn.row_factory = dict_row
        return conn

    # -- queries ---------------------------------------------------------
    def create_session(self, bot, title="New chat"):
        with self._connect() as conn:
            row = conn.execute(
                "INSERT INTO chat_sessions (bot, title, updated_at) "
                "VALUES (%s, %s, now()) "
                "RETURNING id, bot, title, created_at, updated_at",
                (bot, title[:120]),
            ).fetchone()
        return self._row(row, 0)

    @staticmethod
    def _row(row, message_count):
        return {
            "id": row["id"],
            "bot": row["bot"],
            "title": row["title"],
            "created_at": _iso(row["created_at"]),
            "updated_at": _iso(row["updated_at"]),
            "message_count": message_count,
        }

    def append_messages(self, session_id, messages):
        if not messages:
            return
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO chat_messages (session_id, role, content) "
                "VALUES (%s, %s, %s)",
                [(session_id, m.get("role"), m.get("content"))
                 for m in messages],
            )
            conn.execute(
                "UPDATE chat_sessions SET updated_at = now() WHERE id = %s",
                (session_id,),
            )

    def set_title(self, session_id, title):
        with self._connect() as conn:
            conn.execute(
                "UPDATE chat_sessions SET title = %s, updated_at = now() "
                "WHERE id = %s AND title = 'New chat'",
                (title[:120], session_id),
            )

    def list_sessions(self):
        sql = """
            SELECT s.id, s.bot, s.title, s.created_at, s.updated_at,
                   COUNT(m.id)::int AS message_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON m.session_id = s.id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            LIMIT 200
        """
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [self._row(r, r["message_count"]) for r in rows]

    def get_session(self, session_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, bot, title, created_at, updated_at "
                "FROM chat_sessions WHERE id = %s",
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            rows = conn.execute(
                "SELECT role, content, created_at FROM chat_messages "
                "WHERE session_id = %s ORDER BY id",
                (session_id,),
            ).fetchall()
        session = self._row(row, len(rows))
        session["messages"] = [
            {
                "role": m["role"],
                "content": m["content"],
                "created_at": _iso(m["created_at"]),
            }
            for m in rows
        ]
        return session

    def delete_session(self, session_id):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM chat_sessions WHERE id = %s", (session_id,)
            )


class MemoryStore:
    """In-memory fallback with the same interface as PostgresStore."""

    def __init__(self):
        self._sessions = {}
        self._seq = 0

    def _public(self, session, message_count=None):
        out = {
            "id": session["id"],
            "bot": session["bot"],
            "title": session["title"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
        }
        out["message_count"] = (
            len(session["messages"])
            if message_count is None else message_count
        )
        return out

    def create_session(self, bot, title="New chat"):
        self._seq += 1
        now = _now_iso()
        session = {
            "id": self._seq,
            "bot": bot,
            "title": title[:120],
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        self._sessions[self._seq] = session
        return self._public(session)

    def append_messages(self, session_id, messages):
        session = self._sessions.get(session_id)
        if not session:
            return
        for message in messages:
            session["messages"].append({
                "role": message.get("role"),
                "content": message.get("content"),
                "created_at": _now_iso(),
            })
        session["updated_at"] = _now_iso()

    def set_title(self, session_id, title):
        session = self._sessions.get(session_id)
        if session and session["title"] == "New chat":
            session["title"] = title[:120]

    def list_sessions(self):
        sessions = [
            self._public(s) for s in self._sessions.values()
        ]
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions[:200]

    def get_session(self, session_id):
        session = self._sessions.get(session_id)
        if session is None:
            return None
        out = self._public(session)
        out["messages"] = list(session["messages"])
        return out

    def delete_session(self, session_id):
        self._sessions.pop(session_id, None)


def create_store():
    """Pick the best available storage engine for this run."""
    url = get_database_url()
    if not url:
        print("[webapp] DATABASE_URL not set — using in-memory history.")
        return MemoryStore()
    if not PSYCOPG_AVAILABLE:
        print("[webapp] DATABASE_URL is set but the psycopg driver is "
              "missing.")
        print('[webapp] Install it with:  pip install "psycopg[binary]"')
        print("[webapp] Falling back to in-memory history.")
        return MemoryStore()
    try:
        return PostgresStore(url)
    except Exception as exc:
        print("[webapp] %s" % exc)
        print("[webapp] Falling back to in-memory history.")
        return MemoryStore()


def save_exchange(bot, session_id, exchange):
    """Persist a user/assistant exchange, creating the session if needed.

    exchange: list of {"role": ..., "content": ...} dicts (usually the new
    user message followed by the assistant reply).
    Returns the updated session dict (without the message list).
    """
    first_user = next(
        (m.get("content") for m in exchange
         if m.get("role") == "user" and m.get("content")),
        None,
    )
    session = (
        store.get_session(session_id) if session_id is not None else None
    )
    if session is None:
        title = ("New chat" if not first_user
                 else first_user.replace("\n", " ").strip()[:120]
                 or "New chat")
        session = store.create_session(bot, title)
        session_id = session["id"]
    store.append_messages(session_id, exchange)
    if first_user:
        store.set_title(session_id,
                        first_user.replace("\n", " ").strip() or "New chat")
    session = store.get_session(session_id)
    if "messages" in session:
        session.pop("messages")  # keep the JSON response small
    return session


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
    @staticmethod
    def _path_id(path):
        try:
            return int(path.rsplit("/", 1)[-1])
        except (ValueError, AttributeError):
            return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/history":
            try:
                with STORE_LOCK:
                    sessions = store.list_sessions()
            except Exception as exc:
                sys.stderr.write("[webapp] history list failed: %s\n" % exc)
                sessions = []
            self._send(200, json.dumps({"sessions": sessions}))
            return
        if path.startswith("/api/history/"):
            session_id = self._path_id(path)
            if session_id is None:
                self._send(404, json.dumps({"error": "Not found"}))
                return
            try:
                with STORE_LOCK:
                    session = store.get_session(session_id)
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
                return
            if session is None:
                self._send(404, json.dumps({"error": "Session not found"}))
                return
            self._send(200, json.dumps({"session": session}))
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(
                self.rfile.read(length).decode("utf-8")
            ) if length else {}
        except (ValueError, TypeError) as exc:
            self._send(400, json.dumps({"error": "Invalid JSON body: %s" % exc}))
            return

        if path == "/api/chat":
            messages = data.get("messages") or []
            if not messages:
                self._send(400, json.dumps({"error": "messages is required"}))
                return
            bot = data.get("bot") or "main"
            session_id = data.get("session_id")
            try:
                reply = crew_chat(messages)
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
                return
            # Persist only the newest user turn + the assistant reply.
            user_msgs = [m for m in messages if m.get("role") == "user"]
            exchange = (user_msgs[-1:] if user_msgs else []) + [
                {"role": "assistant", "content": reply}
            ]
            session = None
            try:
                with STORE_LOCK:
                    session = save_exchange(bot, session_id, exchange)
            except Exception as exc:
                # Saving history must never break the chat answer.
                sys.stderr.write("[webapp] history save failed: %s\n" % exc)
            body = {"reply": reply}
            if session:
                body["session"] = session
            self._send(200, json.dumps(body))
            return

        if path == "/api/history/messages":
            messages = data.get("messages") or []
            if not messages:
                self._send(400, json.dumps({"error": "messages is required"}))
                return
            bot = data.get("bot") or "custom"
            session_id = data.get("session_id")
            try:
                with STORE_LOCK:
                    session = save_exchange(bot, session_id, messages)
                self._send(200, json.dumps({"session": session}))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return

        if path == "/api/history":
            bot = data.get("bot") or "custom"
            title = (data.get("title") or "New chat")[:120]
            try:
                with STORE_LOCK:
                    session = store.create_session(bot, title)
                self._send(200, json.dumps({"session": session}))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return

        self._send(404, json.dumps({"error": "Not found"}))

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/history/"):
            session_id = self._path_id(path)
            if session_id is None:
                self._send(404, json.dumps({"error": "Not found"}))
                return
            try:
                with STORE_LOCK:
                    store.delete_session(session_id)
                self._send(200, json.dumps({"ok": True}))
            except Exception as exc:
                self._send(500, json.dumps({"error": str(exc)}))
            return
        self._send(404, json.dumps({"error": "Not found"}))

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
    global store
    store = create_store()
    print(f"[webapp] Storage engine: {type(store).__name__}")
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