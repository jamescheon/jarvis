import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE_CLI = shutil.which("claude") or "claude"
WORK_DIR = Path.home()

REQUEST_TOOL = {
    "name": "request_pc_task",
    "description": "사용자가 이 컴퓨터에서 실제로 파일을 만들거나 열거나, 프로그램을 실행하거나, "
    "명령을 실행하는 등 구체적인 작업을 원할 때 사용합니다. 정보를 묻는 질문이나 "
    "일반 대화에는 사용하지 마세요.",
    "input_schema": {
        "type": "object",
        "properties": {
            "instruction": {"type": "string", "description": "사용자가 요청한 작업 내용, 그대로"},
        },
        "required": ["instruction"],
    },
}
# Suppress the console window the npm-shimmed `claude.cmd` -> node.exe chain
# otherwise pops up on Windows, which steals focus from the browser tab and
# can interrupt an active speech-recognition session.
CREATIONFLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def run_task(instruction: str) -> str:
    """Run a natural-language instruction through the local Claude Code CLI,
    headless, scoped to the user's home folder. Local-only - never wired
    into the Vercel deployment, which has no access to this machine."""
    try:
        proc = subprocess.run(
            [
                CLAUDE_CLI, "-p", instruction,
                "--output-format", "text",
                "--permission-mode", "bypassPermissions",
                "--no-session-persistence",
                "--max-budget-usd", "2",
            ],
            cwd=str(WORK_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            creationflags=CREATIONFLAGS,
        )
    except subprocess.TimeoutExpired:
        return "작업이 시간 초과됐습니다."
    except FileNotFoundError:
        return "claude CLI를 찾을 수 없습니다."

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    return out or err or "작업을 완료했습니다."
