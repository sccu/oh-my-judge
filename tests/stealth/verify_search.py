import subprocess
import time
import os
import random
from playwright.sync_api import sync_playwright

def human_type(page, selector, text):
    page.click(selector)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.1, 0.3))

def verify_search_flow():
    """
    Chrome을 띄우고, 접속하여 검색까지 수행하는 통합 검증 함수
    """
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    user_data_dir = os.path.abspath("tests/stealth/chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    print("Launching Chrome...")
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5) # 브라우저 부팅 대기
    
    target_url = "https://www.coupang.com"
    endpoint_url = "http://127.0.0.1:9222"
    
    try:
        with sync_playwright() as p:
            print(f"Connecting to CDP: {endpoint_url}")
            browser = p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Navigating to {target_url}...")
            # 타임아웃을 넉넉히 90초로 설정
            page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
            
            # 검색창 요소 대기
            search_input_selector = "#headerSearchKeyword"
            try:
                page.wait_for_selector(search_input_selector, timeout=20000)
                print("Search input found. Performing human-like typing...")
                
                # 검색창 클릭 및 타이핑
                box = page.locator(search_input_selector).bounding_box()
                if box:
                    page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    time.sleep(0.5)
                
                human_type(page, search_input_selector, "노트북")
                time.sleep(1)
                
                print("Clicking search button...")
                page.click("#headerSearchBtn")
                
                # 검색 결과 페이지 대기
                print("Waiting for search results...")
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                time.sleep(5)
                
                title = page.title()
                print(f"Result Page Title: {title}")
                page.screenshot(path="tests/stealth/search_success.png")
                
                if "노트북" in title:
                    print("SUCCESS: Akamai search bypass verified!")
                else:
                    print(f"FAILED: Reached but title mismatch. Title: {title}")
                    page.screenshot(path="tests/stealth/search_mismatch.png")
            
            except Exception as e:
                print(f"FAILED: Search input not found or blocked. Error: {e}")
                page.screenshot(path="tests/stealth/search_failed.png")
                print(f"Current Title: {page.title()}")
                # 차단 페이지 여부 확인용 바디 일부 출력
                print(f"Body snippet: {page.content()[:1000]}")
            
            browser.close()
    finally:
        print("Terminating Chrome process...")
        process.terminate()

if __name__ == "__main__":
    verify_search_flow()
