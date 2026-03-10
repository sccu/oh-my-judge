from scrapling import StealthyFetcher

def test_scrapling_stealth():
    """
    Scrapling의 StealthyFetcher를 사용하여 Akamai 보호 사이트 접속 테스트
    """
    target_url = "https://www.coupang.com"
    
    print(f"Connecting to {target_url} using Scrapling (fetch method)...")
    
    # fetch 메서드 사용, humanize=True로 사람 행동 모사 활성화
    fetcher = StealthyFetcher()
    response = fetcher.fetch(target_url, headless=True, humanize=True)
    
    print(f"Status Code: {response.status}")
    
    if response.status == 200:
        print("Successfully bypassed Akamai (200 OK)!")
        
        # html_content 또는 body 확인
        content = response.html_content or ""
        if "쿠팡" in content or "Coupang" in content:
             print("Content verified: Found '쿠팡' or 'Coupang' in page source.")
             # 간단한 정보 출력 (예: 페이지 제목 추출 시도)
             title = response.css_first("title").text if response.css_first("title") else "No title"
             print(f"Page Title: {title}")
        else:
             print("Bypassed but content seems different. Preview:")
             print(content[:500])
    else:
        print(f"Failed to bypass. Status: {response.status}")
        print(f"Response content preview: {response.html_content[:500] if response.html_content else 'None'}")

if __name__ == "__main__":
    test_scrapling_stealth()
