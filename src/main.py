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

def run_pipeline(task_path, keyword_file=None, do_warmup=False, max_products=3):
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

    # 2. 브라우저 준비
    browser_launched_by_me = False
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
            browser = p.chromium.launch(headless=False) # 자동 실행 시에도 안정성을 위해 Headful
            context = browser.new_context()
            page = context.new_page()
            browser_launched_by_me = True

        # 3. 액션 초기화
        action_type = task['action']['type']
        action = None
        if action_type == "SEARCH_AND_EXTRACT":
            action = CoupangSearchAction(page)
        elif action_type == "NAVER_SEARCH":
            action = NaverSearchAction(page)

        # 웜업 수행 (최초 1회)
        if do_warmup and action:
            print("[Main] Running initial automated warmup (once)...")
            action.warmup()

        # 4. 액션 실행 루프
        for i, kw in enumerate(keywords):
            print(f"\n[Main] Processing Keyword {i+1}/{len(keywords)}: {kw}")
            
            if action:
                result = action.run(keyword=kw, max_products=max_products)
                
                if result['success']:
                    print(f"[Main] Action for '{kw}' successful.")
                else:
                    print(f"[Main] Action for '{kw}' failed: {result.get('error')}")
            
            # 마지막 키워드가 아니면 사람처럼 대기
            if i < len(keywords) - 1:
                wait_time = random.uniform(5, 10)
                print(f"[Main] Waiting {wait_time:.1f}s before next keyword...")
                time.sleep(wait_time)

        print("\n[Main] All tasks completed.")
        
        if browser_launched_by_me:
            print("[Main] Closing the browser instance I launched...")
            browser.close()
        else:
            print("[Main] Disconnecting from existing browser (keeping it open).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oh-My-Judge Runner")
    parser.add_argument("--task", type=str, default="tasks/sample_task.yaml", help="Path to task YAML file")
    parser.add_argument("--keywords", type=str, help="Path to keywords file")
    parser.add_argument("--warmup", action="store_true", help="Perform automated warmup before search")
    parser.add_argument("--max-products", type=int, default=3, help="Number of top products to extract")
    args = parser.parse_args()

    os.makedirs("outputs", exist_ok=True)
    run_pipeline(args.task, args.keywords, args.warmup, args.max_products)
