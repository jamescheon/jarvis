import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from anthropic import Anthropic

BASE_DIR = Path(__file__).parent
INDEX_FILE = BASE_DIR / "index.html"

client = Anthropic()

SYSTEM_PROMPT = """당신은 아이언맨의 자비스(J.A.R.V.I.S.)입니다.
- 한국어로만 대화합니다.
- 정중하고 위트 있는 집사처럼 응답합니다.
- 답변은 항상 2~3문장 이내로 간결하게, 음성 대화에 자연스럽게 말합니다.
- 사용자를 "선생님"이라고 부릅니다.
- 이모지나 마크다운 기호(**, #, - 등)는 절대 사용하지 않습니다 (음성 출력이므로)."""


class JarvisHandler(BaseHTTPRequestHandler):
    def _send(self, status, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                body = INDEX_FILE.read_bytes()
                self._send(200, body, "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, b"index.html not found", "text/plain; charset=utf-8")
        else:
            self._send(404, b"Not Found", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, b"Not Found", "text/plain; charset=utf-8")
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, b'{"error":"invalid json"}', "application/json")
            return

        messages = payload.get("messages", [])
        try:
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

    def log_message(self, fmt, *args):
        return


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

    port = int(os.environ.get("JARVIS_PORT", "5000"))
    print("=" * 60)
    print(f"  J.A.R.V.I.S. 서버 시작")
    print(f"  브라우저에서 여세요 → http://localhost:{port}")
    print(f"  (Chrome 또는 Edge 권장 — 음성 인식 지원)")
    print(f"  종료: Ctrl+C")
    print("=" * 60)
    HTTPServer(("127.0.0.1", port), JarvisHandler).serve_forever()


if __name__ == "__main__":
    main()
