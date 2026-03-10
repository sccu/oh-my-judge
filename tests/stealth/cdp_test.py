import time
import random
from playwright.sync_api import sync_playwright

def human_type(page, selector, text):
    """
    글자별로 랜덤한 지연 시간을 두어 사람처럼 타이핑합니다.
    """
    page.click(selector)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.1, 0.3))

def test_cdp_search_flow():
    """
    메인 페이지 접속 후 검색어 입력 및 결과 페이지 진입까지 테스트합니다.
    """
    target_url = "https://www.coupang.com"
    endpoint_url = "http://127.0.0.1:9222"
    
    print(f"Connecting to existing browser via CDP: {endpoint_url}")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Navigating to {target_url}...")
            # domcontentloaded로 대기하고, 요소는 따로 기다림
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            try:
                # 검색창이 나타날 때까지 최대 15초 대기
                search_input_selector = "#headerSearchKeyword"
                page.wait_for_selector(search_input_selector, timeout=15000)
            except Exception as e:
                print(f"Failed to find search input: {e}")
                page.screenshot(path="tests/stealth/failed_to_find_search.png")
                print(f"Screenshot saved to tests/stealth/failed_to_find_search.png")
                print(f"Current Title: {page.title()}")
                print(f"Body snippet: {page.content()[:1000]}")
                return
            
            print("Search input found. Starting human-like interaction...")
            
            # 2. 마우스를 검색창으로 이동 후 클릭
            box = page.locator(search_input_selector).bounding_box()
            if box:
                page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                time.sleep(0.5)
            
            # 3. 사람처럼 타이핑 ('노트북')
            human_type(page, search_input_selector, "노트북")
            time.sleep(1)
            
            # 4. 검색 버튼 클릭 (ID: headerSearchBtn)
            print("Clicking search button...")
            page.click("#headerSearchBtn")
            
            # 5. 검색 결과 페이지 로드 대기
            print("Waiting for search results...")
            # 검색 결과 페이지 로딩은 networkidle 대신 domcontentloaded로 느슨하게 확인
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            time.sleep(5) # Akamai 분석 및 결과물 렌더링 대기
            
            title = page.title()
            print(f"Result Page Title: {title}")
            
            # 결과 스크린샷 저장
            page.screenshot(path="tests/stealth/coupang_search_result.png")
            
            if "노트북" in title:
                print("Successfully bypassed Akamai and reached search results!")
            else:
                print("Bypass failed at search step. Check screenshot.")
                print(f"Body snippet: {page.content()[:500]}")

            browser.close()
            
        except Exception as e:
            print(f"Test failed: {e}")

if __name__ == "__main__":
    test_cdp_search_flow()
