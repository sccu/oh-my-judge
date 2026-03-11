#!/bin/bash

PORT=9222

# 1. CDP 포트(9222)가 이미 점유 중인지 확인
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "[Shell] Port $PORT is already in use. Assuming an existing browser is ready."
else
    # 포트가 비어 있으면 크롬 브라우저 백그라운드 실행
    echo "[Shell] Port $PORT is free. Launching new Chrome instance in background..."
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
      --remote-debugging-port=$PORT \
      --user-data-dir="$(pwd)/tests/stealth/chrome_profile" \
      --no-first-run \
      --no-default-browser-check \
      https://www.coupang.com > /dev/null 2>&1 &
    
    # 브라우저 초기 로드 대기 (15초)
    echo "[Shell] Waiting 15 seconds for initial browser load..."
    sleep 15
fi

# 2. 파이썬 스크립트 실행 (키워드 파일 포함)
echo "[Shell] Starting Python automation script..."
PYTHONPATH=. python3 src/main.py --task tasks/sample_task.yaml --keywords search_keywords.txt

echo "[Shell] Process completed."
