import yaml
import os
import argparse
import time
import random
from playwright.sync_api import sync_playwright
from src.actions.coupang_search import CoupangSearchAction
from src.actions.naver_search import NaverSearchAction
from src.evaluator.llm_judge import LLMJudge

def load_task(task_path):
    with open(task_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_pipeline(task_path, keyword_file=None):
    # 1. 태스크 로드
    task = load_task(task_path)
    print(f"[Main] Loaded Task: {task['name']} ({task['task_id']})")

    # 키워드 목록 준비
    keywords = []
    if keyword_file and os.path.exists(keyword_file):
        with open(keyword_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        print(f"[Main] Loaded {len(keywords)} keywords from {keyword_file}")
    else:
        keywords = [task['action']['params'].get('keyword', '노트북')]

    # 2. 브라우저 준비 (CDP 전략 활용 권장)
    with sync_playwright() as p:
        print("[Main] Preparing browser...")
        try:
            # 127.0.0.1:9222 연결 시도
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("[Main] Connected to existing browser via CDP.")
            
            if browser.contexts:
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
            else:
                context = browser.new_context()
                page = context.new_page()
        except Exception as e:
            print(f"[Main] CDP Connection failed ({e}). Launching new instance...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

        # 3. 액션 실행 루프
        action_type = task['action']['type']
        
        for i, kw in enumerate(keywords):
            print(f"\n[Main] Processing Keyword {i+1}/{len(keywords)}: {kw}")
            
            action = None
            if action_type == "SEARCH_AND_EXTRACT":
                action = CoupangSearchAction(page)
            elif action_type == "NAVER_SEARCH":
                action = NaverSearchAction(page)
            
            if action:
                result = action.run(keyword=kw)
                
                if result['success']:
                    print(f"[Main] Action for '{kw}' successful.")
                else:
                    print(f"[Main] Action for '{kw}' failed: {result.get('error')}")
            
            # 마지막 키워드가 아니면 사람처럼 대기
            if i < len(keywords) - 1:
                wait_time = random.uniform(5, 15)
                print(f"[Main] Waiting {wait_time:.1f}s before next keyword...")
                time.sleep(wait_time)

        print("\n[Main] All tasks completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oh-My-Judge Runner")
    parser.add_argument("--task", type=str, default="tasks/sample_task.yaml", help="Path to task YAML file")
    parser.add_argument("--keywords", type=str, help="Path to keywords file")
    args = parser.parse_args()

    os.makedirs("outputs", exist_ok=True)
    run_pipeline(args.task, args.keywords)
