import yaml
import os
import argparse
from playwright.sync_api import sync_playwright
from src.actions.coupang_search import CoupangSearchAction
from src.actions.naver_search import NaverSearchAction
from src.evaluator.llm_judge import LLMJudge

def load_task(task_path):
    with open(task_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_pipeline(task_path):
    # 1. 태스크 로드
    task = load_task(task_path)
    print(f"[Main] Loaded Task: {task['name']} ({task['task_id']})")

    # 2. 브라우저 준비 (CDP 전략 활용 권장)
    with sync_playwright() as p:
        print("[Main] Preparing browser...")
        try:
            # 검증된 우회 전략: 127.0.0.1:9222 연결 시도
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("[Main] Connected to existing browser via CDP.")
        except:
            print("[Main] Failed to connect to existing browser. Launching new instance...")
            browser = p.chromium.launch(headless=True)
        
        context = browser.new_context()
        page = context.new_page()

        # 3. 액션 선택 및 실행
        action_type = task['action']['type']
        action_params = task['action']['params']
        
        action = None
        if action_type == "SEARCH_AND_EXTRACT":
            action = CoupangSearchAction(page)
        elif action_type == "NAVER_SEARCH":
            action = NaverSearchAction(page)
        
        if action:
            print(f"[Main] Executing action: {action_type}")
            result = action.run(**action_params)
            
            if result['success']:
                print("[Main] Action execution successful. Proceeding to evaluation...")
                # 4. Evaluator 호출
                judge = LLMJudge()
                evaluation = judge.evaluate(task, result['data'])
                
                print(f"\n[Main] --- Evaluation Results ---")
                print(f"Total Score: {evaluation['total_score']} / {task['max_score']}")
                print(f"Final Opinion: {evaluation['final_opinion']}")
                print(f"Validation Check: {evaluation['validation_check']}")
                print(f"--------------------------------\n")
            else:
                print(f"[Main] Action failed: {result.get('error')}")
        else:
            print(f"[Main] Unsupported action type: {action_type}")

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oh-My-Judge Runner")
    parser.add_argument("--task", type=str, default="tasks/sample_task.yaml", help="Path to task YAML file")
    args = parser.parse_args()

    # 출력 디렉토리 생성
    os.makedirs("outputs", exist_ok=True)
    
    run_pipeline(args.task)
