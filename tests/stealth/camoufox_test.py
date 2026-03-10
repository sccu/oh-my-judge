import time
from camoufox.sync_api import Camoufox

def test_camoufox_stealth():
    """
    Camoufox(Firefox based)를 사용한 Akamai 우회 테스트
    """
    target_url = "https://www.coupang.com"
    
    print(f"Connecting to {target_url} using Playwright + Camoufox...")
    
    # Camoufox context를 생성하면 C++ 레벨의 지문 변조가 자동 적용됨
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        
        # 실제 사용자처럼 보이도록 접근 시도
        try:
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # 페이지 로드 후 추가 대기 (Akamai는 JS 실행 후 쿠키 생성이 핵심)
            time.sleep(5) 
            
            # 페이지 상태 확인
            status = page.evaluate("() => document.readyState")
            print(f"Document Ready State: {status}")
            
            # 화면 캡처 및 텍스트 확인 (증거 남기기)
            page.screenshot(path="tests/stealth/coupang_camoufox.png")
            title = page.title()
            print(f"Page Title: {title}")
            
            if "쿠팡" in title or "Coupang" in title:
                print("Successfully bypassed Akamai and verified via title!")
            else:
                print("Bypass verification failed. Title may be empty or blocked.")
                print(f"Body snippet: {page.content()[:500]}")
        except Exception as e:
            print(f"Error during navigation: {e}")

if __name__ == "__main__":
    test_camoufox_stealth()
