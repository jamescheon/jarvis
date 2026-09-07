@echo off
title J.A.R.V.I.S.
chcp 65001 > nul
cd /d "%~dp0"

REM 이전 로그 삭제
if exist server.log del server.log

echo ============================================================ > server.log
echo  J.A.R.V.I.S. 실행 로그 >> server.log
echo ============================================================ >> server.log
echo. >> server.log

REM 환경 정보 기록
echo [환경 정보] >> server.log
echo 현재 폴더: %CD% >> server.log
where python >> server.log 2>&1
where py >> server.log 2>&1
python --version >> server.log 2>&1
if "%ANTHROPIC_API_KEY%"=="" (
    echo API_KEY: 미설정 >> server.log
) else (
    echo API_KEY: 설정됨 >> server.log
)
echo. >> server.log

echo ============================================================
echo   J.A.R.V.I.S. 시스템 부팅 중...
echo ============================================================
echo.
echo   실행 로그는 server.log 파일에 저장됩니다.
echo.

if "%ANTHROPIC_API_KEY%"=="" (
    echo [오류] ANTHROPIC_API_KEY 환경변수가 없습니다.
    echo        새 PowerShell을 열고 API 키를 다시 등록하세요.
    echo.
    echo Enter를 눌러 종료:
    set /p x=
    exit /b 1
)

echo [O] API 키 확인됨
echo [O] 브라우저 자동 오픈 → http://localhost:5000
echo.
start "" "http://localhost:5000"

echo ------------------------------------------------------------
echo  서버 시작 (종료: Ctrl+C 또는 창 닫기)
echo ------------------------------------------------------------
echo.

echo [서버 출력] >> server.log
python server.py >> server.log 2>&1

echo. >> server.log
echo ============================================================ >> server.log
echo  서버가 종료되었습니다 >> server.log
echo ============================================================ >> server.log

REM 로그 화면에 출력
echo.
echo ============================================================
echo  서버가 종료되었습니다. 로그 내용:
echo ============================================================
type server.log
echo.
echo ------------------------------------------------------------
echo  Enter를 눌러 창 닫기 (스크린샷 먼저 찍어주세요):
echo ------------------------------------------------------------
set /p x=
