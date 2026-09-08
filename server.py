import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from anthropic import Anthropic

import naver_ads

BASE_DIR = Path(__file__).parent
INDEX_FILE = BASE_DIR / "index.html"
STATIC_FILES = {
    "/manifest.json": ("manifest.json", "application/json; charset=utf-8"),
    "/icon.svg": ("icon.svg", "image/svg+xml"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
}

client = Anthropic()

SYSTEM_PROMPT = """당신은 아이언맨의 자비스(J.A.R.V.I.S.)입니다.
- 한국어로만 대화합니다.
- 정중하고 위트 있는 집사처럼 응답합니다.
- 답변은 항상 2~3문장 이내로 간결하게, 음성 대화에 자연스럽게 말합니다.
- 사용자를 "선생님"이라고 부릅니다.
- 이모지나 마크다운 기호(**, #, - 등)는 절대 사용하지 않습니다 (음성 출력이므로).
- 최신 뉴스, 날씨, 실시간 정보 등 알고 있는 지식만으로 답할 수 없는 질문은 웹 검색을 사용해서 답합니다.
- 네이버 검색량/검색 순위를 물어보면 naver_search_volume 도구로 조회해서 답합니다."""

SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
TOOLS = [SEARCH_TOOL, naver_ads.VOLUME_TOOL]
TOOL_HANDLERS = {"naver_search_volume": lambda inp: naver_ads.search_volume(inp.get("keyword", ""))}


def run_with_tools(messages):
    # web_search resolves itself server-side; naver_search_volume is a
    # client-side tool, so loop until Claude stops asking for one.
    for _ in range(3):
        resp = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )
        if resp.stop_reason != "tool_use":
            return resp
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = [
            {"type": "tool_result", "tool_use_id": block.id, "content": TOOL_HANDLERS[block.name](block.input)}
            for block in resp.content
            if block.type == "tool_use" and block.name in TOOL_HANDLERS
        ]
        if not tool_results:
            return resp
        messages.append({"role": "user", "content": tool_results})
    return resp


def extract_reply(resp):
    text = "".join(b.text for b in resp.content if b.type == "text")
    # web_search citations leave cite-tag markup in the response text -
    # strip it, this is spoken aloud, not rendered as a web page.
    text = re.sub(r'</?cite[^>]*>?', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


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
            return

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

        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, b'{"error":"invalid json"}', "application/json")
            return

        messages = payload.get("messages", [])
        try:
            resp = run_with_tools(messages)
            reply = extract_reply(resp)
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
    server = ThreadingHTTPServer(("127.0.0.1", port), JarvisHandler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")
        server.shutdown()


if __name__ == "__main__":
    main()
