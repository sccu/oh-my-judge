#!/bin/bash

PORT=9222
CHROME_PID=""

# 종료 시 크롬 프로세스를 함께 정리하는 함수
cleanup() {
    if [ -n "$CHROME_PID" ]; then
        echo "[Shell] Finished all tasks. Waiting 5 seconds before closing browser..."
        sleep 5
        echo "[Shell] Cleaning up Chrome process (PID: $CHROME_PID)..."
        kill $CHROME_PID 2>/dev/null
    fi
}

# 스크립트가 종료되거나 인터럽트(Ctrl+C)를 받을 때 cleanup 함수 실행
trap cleanup EXIT

# 1. CDP 포트(9222)가 이미 점유 중인지 확인
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "[Shell] Port $PORT is already in use. Reusing existing browser."
else
    # 포트가 비어 있으면 크롬 브라우저 백그라운드 실행
    echo "[Shell] Port $PORT is free. Launching new Chrome instance..."
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
      --remote-debugging-port=$PORT \
      --user-data-dir="$(pwd)/tests/stealth/chrome_profile" \
      --no-first-run \
      --no-default-browser-check \
      https://www.coupang.com > /dev/null 2>&1 &
    
    CHROME_PID=$! # 방금 실행한 크롬의 PID 저장
    echo "[Shell] Chrome launched with PID: $CHROME_PID"
    
    # 브라우저 초기 로드 대기 (5초로 단축)
    echo "[Shell] Waiting 5 seconds for browser process to initialize..."
    sleep 5
fi

# 2. 파이썬 스크립트 실행
echo "[Shell] Starting Python automation script..."
PYTHONPATH=. python3 src/main.py --task tasks/sample_task.yaml --keywords search_keywords.txt --warmup

echo "[Shell] Automation script finished."
# 여기서 스크립트가 끝나면 trap에 의해 cleanup이 호출되어 5초 대기 후 CHROME_PID가 종료됨
