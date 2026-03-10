import time
from src.core.base_action import BaseAction

class NaverSearchAction(BaseAction):
    """
    네이버 쇼핑에서 상품을 검색하고 결과 데이터를 수집하는 액션입니다.
    """
    def run(self, keyword=None, **kwargs):
        if not keyword:
            raise ValueError("Keyword is required for NaverSearchAction")

        # 네이버 쇼핑 메인 URL
        url = "https://shopping.naver.com/home"
        print(f"[NaverAction] Starting search for '{keyword}'...")

        try:
            # 1. 메인 페이지 접속
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self.humanoid.wait_randomly(2, 3) # 네이버는 초기 로딩 대기가 중요
            
            # 2. 검색창 입력 및 검색
            # 네이버 쇼핑 검색창 input selector (최신 기준 확인 필요)
            search_input = "input[class*='_searchInput_search_input_']" 
            # 만약 위 셀렉터가 안 잡힐 경우를 대비한 대안 셀렉터
            try:
                self.page.wait_for_selector(search_input, timeout=5000)
            except:
                search_input = "input[title='검색어 입력']"
                self.page.wait_for_selector(search_input, timeout=5000)
            
            # 사람처럼 검색어 입력
            self.humanoid.type_humanly(search_input, keyword)
            self.humanoid.wait_randomly(0.5, 1.0)
            
            # 엔터 키 입력으로 검색 실행 (버튼 클릭보다 탐지 회피에 유리할 때가 있음)
            self.page.keyboard.press("Enter")
            
            # 3. 검색 결과 로드 대기
            print("[NaverAction] Waiting for search results...")
            # 네이버 쇼핑은 검색 결과가 비동기로 로드되므로 특정 요소 대기
            result_list_selector = "div[class*='product_list_item']"
            try:
                self.page.wait_for_selector(result_list_selector, timeout=15000)
            except:
                print("[NaverAction] Warning: Specific product item not found, waiting for network idle.")
                self.page.wait_for_load_state("networkidle", timeout=10000)
            
            self.humanoid.wait_randomly(3, 5)
            
            # 4. 데이터 수집 (증거 확보)
            self.capture_evidence("naver_search_result")
            self.extract_dom("naver_dom")
            
            # 5. 결과 요약
            title = self.page.title()
            print(f"[NaverAction] Search completed. Page Title: {title}")
            
            return {
                "success": True,
                "title": title,
                "data": self.results
            }

        except Exception as e:
            print(f"[NaverAction] Action failed: {e}")
            self.capture_evidence("naver_failure")
            return {
                "success": False,
                "error": str(e),
                "data": self.results
            }
