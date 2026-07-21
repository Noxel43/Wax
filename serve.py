#!/usr/bin/env python3
"""Wax dev server: serves the static app AND proxies fun-fact requests to Groq.

The Groq API key is read server-side from config.json (preferred) or the
API_KEY_GROQ_LLAMA environment variable. It is NEVER sent to the browser or
committed to the repo (config.json is gitignored, and this server refuses to
serve it statically). The browser only ever calls the same-origin /api/funfact.

Run:  python serve.py        (defaults to http://127.0.0.1:5173)
"""
import os
import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))


def load_config():
    try:
        with open(os.path.join(HERE, "config.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


CONFIG = load_config()
GROQ_KEY = (CONFIG.get("API_KEY_GROQ_LLAMA") or os.environ.get("API_KEY_GROQ_LLAMA") or "").strip()
GROQ_MODEL = CONFIG.get("GROQ_MODEL") or os.environ.get("GROQ_MODEL") or "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
PORT = int(os.environ.get("PORT", "5173"))

SYSTEM_PROMPT = (
    "You are a music trivia expert. Given a song, reply with ONE short, surprising, "
    "and TRUE fun fact (1-2 sentences, max ~40 words) about the song, its artist, its "
    "album, or how it was made. No preamble, no quotation marks, no 'Did you know' - "
    "just the fact. If you are not confident about a specific fact for the song, give a "
    "genuinely interesting, accurate fact about the artist instead."
)


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/funfact":
            return self._funfact()
        # Never expose the secret config over HTTP.
        if os.path.basename(path).lower() == "config.json":
            return self._send_json(404, {"error": "not found"})
        return super().do_GET()

    def _funfact(self):
        if not GROQ_KEY:
            return self._send_json(500, {"error": "No Groq key. Put it in config.json (API_KEY_GROQ_LLAMA) and restart serve.py."})
        q = parse_qs(urlparse(self.path).query)
        title = (q.get("title", [""])[0] or "").strip()
        artist = (q.get("artist", [""])[0] or "").strip()
        album = (q.get("album", [""])[0] or "").strip()
        if not title and not artist:
            return self._send_json(400, {"error": "No track provided"})

        user_msg = 'Song: "{}" by {}'.format(title or "Unknown", artist or "Unknown")
        if album:
            user_msg += " (album: {})".format(album)

        payload = {
            "model": GROQ_MODEL,
            "temperature": 0.9,
            "max_tokens": 130,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        }
        req = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + GROQ_KEY,
                "Content-Type": "application/json",
                # Groq is behind Cloudflare, which blocks urllib's default
                # User-Agent (error 1010). Send a normal browser UA.
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            fact = data["choices"][0]["message"]["content"].strip().strip('"')
            return self._send_json(200, {"fact": fact})
        except urllib.error.HTTPError as e:
            # Surface Groq's own error message (helpful for e.g. a decommissioned
            # model id). The API key is never part of the response body.
            detail = ""
            try:
                detail = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                pass
            msg = "Groq error {}".format(e.code) + (": " + detail if detail else "")
            return self._send_json(502, {"error": msg})
        except Exception as e:
            return self._send_json(502, {"error": "Groq request failed: {}".format(e)})


if __name__ == "__main__":
    status = "ready" if GROQ_KEY else "NO KEY (add it to config.json)"
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Wax dev server: http://127.0.0.1:{}/index.html".format(PORT))
    print("Groq fun facts: {}  (model: {})".format(status, GROQ_MODEL))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
