import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE_CLI = shutil.which("claude") or "claude"
WORK_DIR = Path.home()
SYSTEM_PROMPT_APPEND = (
    "당신은 이 컴퓨터에서 사용자의 요청을 직접 실행하는 로컬 자동화 에이전트입니다. "
    "Bash 도구로 프로그램 실행, `start` 명령으로 URL이나 앱 열기(예: 브라우저에서 "
    "검색), 파일 생성/수정 등 무엇이든 직접 수행할 수 있습니다. 사용자에게 방법을 "
    "안내만 하지 말고, 실제로 작업을 완료한 뒤 결과를 한두 문장으로 요약해서 "
    "보고하세요."
)

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
        # Pass the instruction via stdin instead of as a CLI argument. On
        # Windows, `claude` resolves to a npm .cmd shim, which Python's
        # subprocess launches through a second cmd.exe pass - that pass
        # re-parses quoting, and instructions containing literal double
        # quotes (very common - "file.xlsx", column names, etc) were
        # getting truncated at the wrong point. Stdin bypasses argv
        # parsing entirely, so no amount of embedded quoting can break it.
        proc = subprocess.run(
            [
                CLAUDE_CLI, "-p",
                "--output-format", "text",
                "--permission-mode", "bypassPermissions",
                "--no-session-persistence",
                "--max-budget-usd", "2",
                "--append-system-prompt", SYSTEM_PROMPT_APPEND,
            ],
            input=instruction,
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
