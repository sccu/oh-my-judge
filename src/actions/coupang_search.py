import time
import random
import re
import json
from src.core.base_action import BaseAction

class CoupangSearchAction(BaseAction):
    """
    쿠팡 검색 결과를 기계적 처리에 용이한 정형 데이터(JSON)로 추출하는 액션입니다.
    웜업은 외부에서 최초 1회만 호출하는 것을 권장합니다.
    """
    def warmup(self):
        """
        검색 전 수행하는 자동 웜업 로직입니다.
        """
        url = "https://www.coupang.com"
        print(f"[CoupangAction] Navigating to {url} for initial warmup...")
        try:
            self.page.goto(url, wait_until="commit", timeout=10000)
        except:
            pass
        
        search_selectors = ["input[name='q']", "input[title='쿠팡 상품 검색']", ".headerSearchKeyword"]
        self.humanoid.warmup(search_selectors=search_selectors)

    def run(self, keyword=None, max_products=3, **kwargs):
        if not keyword:
            raise ValueError("Keyword is required for CoupangSearchAction")

        print(f"\n[CoupangAction] >>> START_SEARCH: {keyword} (Target: Top {max_products})")

        try:
            # 1. 검색창 찾기 (현재 페이지에서 바로 시도)
            search_selectors = ["input[name='q']", "input[title='쿠팡 상품 검색']", ".headerSearchKeyword"]
            search_input = None

            # 검색창이 나타날 때까지 최대 10초 대기
            for selector in search_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    search_input = selector
                    break
                except:
                    continue

            if not search_input:
                # 검색창을 못 찾으면 메인으로 이동 시도 (최후의 수단)
                print("[CoupangAction] Search input not found. Attempting recovery to home page...")
                self.page.goto("https://www.coupang.com", wait_until="commit")
                time.sleep(2)
                # 재시도
                for selector in search_selectors:
                    try:
                        self.page.wait_for_selector(selector, timeout=5000)
                        search_input = selector
                        break
                    except:
                        continue
                if not search_input:
                    raise Exception("Search input not found even after recovery")
            
            # 2. 검색 수행 (기존 텍스트 삭제 -> 입력 -> 엔터)
            self.page.click(search_input, click_count=3)
            self.page.keyboard.press("Backspace")
            time.sleep(0.3)
            self.humanoid.type_humanly(search_input, keyword)
            time.sleep(0.3)
            self.page.keyboard.press("Enter")
            
            # 3. 검색 결과 로드 대기
            print("[CoupangAction] Waiting for SERP...")
            item_selector = "li[class*='ProductUnit_productUnit']"
            try:
                self.page.wait_for_selector(item_selector, timeout=20000)
            except:
                print("[CoupangAction] Warning: SERP items not detected within 20s.")
            
            # 안정화를 위해 조금 더 대기
            time.sleep(3)
            
            # 4. 데이터 추출
            print(f"[CoupangAction] Extracting top {max_products} products...")
            items = self.page.locator(item_selector).all()
            
            extracted_results = []
            
            for i, item in enumerate(items[:max_products]):
                try:
                    data = item.evaluate("""(node) => {
                        const res = { raw_attributes: {}, display_info: {} };
                        const allEls = [node, ...Array.from(node.querySelectorAll('*'))];
                        allEls.forEach(el => {
                            for (let attr of el.attributes) {
                                if (attr.name.startsWith('data-') || attr.name === 'aria-label') {
                                    res.raw_attributes[attr.name] = attr.value;
                                }
                            }
                        });
                        const getT = (sel) => node.querySelector(sel)?.innerText?.trim() || "";
                        res.display_info.name = getT("div[class*='productName']");
                        res.display_info.final_price = getT("div[class*='PriceArea_priceArea'] span");
                        res.display_info.is_ad = !!node.querySelector("div[class*='AdMark_adMark']");
                        return res;
                    }""")

                    result_entry = {
                        "rank": i + 1,
                        "keyword": keyword,
                        "timestamp": time.time(),
                        **data['display_info']
                    }
                    extracted_results.append(result_entry)
                    print(f"JSON_RESULT: {json.dumps(result_entry, ensure_ascii=False)}")

                except Exception as e:
                    print(f"ERROR_ITEM_{i+1}: {str(e)}")

            # 5. 증거 확보
            self.capture_evidence(f"result_{keyword}")
            
            return {
                "success": True,
                "keyword": keyword,
                "count": len(extracted_results),
                "data": self.results
            }

        except Exception as e:
            print(f"ACTION_FAILED: {str(e)}")
            self.capture_evidence("failure_state")
            return {"success": False, "error": str(e)}
