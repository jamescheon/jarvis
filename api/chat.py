from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json

from anthropic import Anthropic

BASE_DIR = Path(__file__).parent.parent
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/manifest.json": ("manifest.json", "application/json; charset=utf-8"),
    "/icon.svg": ("icon.svg", "image/svg+xml"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
}

SYSTEM_PROMPT = """당신은 아이언맨의 자비스(J.A.R.V.I.S.)입니다.
- 한국어로만 대화합니다.
- 정중하고 위트 있는 집사처럼 응답합니다.
- 답변은 항상 2~3문장 이내로 간결하게, 음성 대화에 자연스럽게 말합니다.
- 사용자를 "선생님"이라고 부릅니다.
- 이모지나 마크다운 기호(**, #, - 등)는 절대 사용하지 않습니다 (음성 출력이므로)."""


class handler(BaseHTTPRequestHandler):
    def _send(self, status, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        entry = STATIC_FILES.get(self.path)
        if entry:
            filename, content_type = entry
            try:
                body = (BASE_DIR / filename).read_bytes()
                self._send(200, body, content_type)
                return
            except FileNotFoundError:
                pass
        self._send(404, b"Not Found", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, b"Not Found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            payload = json.loads(body)
            messages = payload.get("messages", [])

            client = Anthropic()
            resp = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            reply = resp.content[0].text
            out = json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8")
            self._send(200, out, "application/json; charset=utf-8")
        except Exception as exc:
            err = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(500, err, "application/json; charset=utf-8")
