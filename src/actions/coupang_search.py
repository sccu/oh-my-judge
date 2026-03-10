import time
from src.core.base_action import BaseAction

class CoupangSearchAction(BaseAction):
    """
    쿠팡에서 상품을 검색하고 결과 데이터를 수집하는 액션입니다.
    """
    def run(self, keyword=None, **kwargs):
        if not keyword:
            raise ValueError("Keyword is required for CoupangSearchAction")

        url = "https://www.coupang.com"
        print(f"[CoupangAction] Starting search for '{keyword}'...")

        try:
            # 1. 메인 페이지 접속
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.humanoid.wait_randomly(1, 2)
            
            # 2. 검색창 입력 및 검색
            search_input = "#headerSearchKeyword"
            self.page.wait_for_selector(search_input, timeout=10000)
            
            # 사람처럼 검색어 입력
            self.humanoid.type_humanly(search_input, keyword)
            self.humanoid.wait_randomly(0.5, 1.5)
            
            # 검색 버튼 클릭
            search_button = "#headerSearchBtn"
            self.humanoid.click_humanly(search_button)
            
            # 3. 검색 결과 로드 대기
            print("[CoupangAction] Waiting for search results to load...")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.humanoid.wait_randomly(2, 4) # Akamai 분석 피하기 위한 충분한 대기
            
            # 4. 데이터 수집 (증거 확보)
            self.capture_evidence("search_result")
            self.extract_dom()
            
            # 5. 결과 요약 (간단한 파싱 테스트)
            title = self.page.title()
            product_count = self.page.locator("ul#productList li.search-product").count()
            
            print(f"[CoupangAction] Search completed. Page Title: {title}")
            print(f"[CoupangAction] Found approximately {product_count} products on the first page.")
            
            return {
                "success": True,
                "title": title,
                "product_count": product_count,
                "data": self.results
            }

        except Exception as e:
            print(f"[CoupangAction] Action failed: {e}")
            self.capture_evidence("failure_state")
            return {
                "success": False,
                "error": str(e),
                "data": self.results
            }
