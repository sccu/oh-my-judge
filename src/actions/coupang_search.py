import time
import random
import re
import json
from src.core.base_action import BaseAction

class CoupangSearchAction(BaseAction):
    """
    쿠팡 검색 결과를 기계적 처리에 용이한 정형 데이터(JSON)로 추출하는 액션입니다.
    """
    def run(self, keyword=None, **kwargs):
        if not keyword:
            raise ValueError("Keyword is required for CoupangSearchAction")

        url = "https://www.coupang.com"
        print(f"[CoupangAction] >>> START_SEARCH: {keyword}")

        try:
            # 1. 페이지 접속 상태 확인
            current_url = self.page.url
            if "coupang.com" not in current_url:
                self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
            
            # 2. 검색창 입력 및 검색
            search_selectors = ["input[name='q']", "input[title='쿠팡 상품 검색']", ".headerSearchKeyword"]
            search_input = None
            for selector in search_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    search_input = selector
                    break
                except:
                    continue

            if not search_input:
                raise Exception("Search input not found")
            
            # 기존 텍스트 삭제 및 입력
            self.page.click(search_input, click_count=3)
            self.page.keyboard.press("Backspace")
            time.sleep(0.5)
            self.humanoid.type_humanly(search_input, keyword)
            time.sleep(0.5)
            self.page.keyboard.press("Enter")
            
            # 3. 검색 결과 로드 대기
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            time.sleep(5) # 안정적인 로드 대기
            
            # 4. 데이터 추출
            print("[CoupangAction] Extracting top 3 products and their attributes...")
            item_selector = "li[class*='ProductUnit_productUnit']"
            self.page.wait_for_selector(item_selector, timeout=10000)
            items = self.page.locator(item_selector).all()
            
            extracted_results = []
            
            for i, item in enumerate(items[:3]): # 상위 3개
                try:
                    data = item.evaluate("""(node) => {
                        const res = { 
                            raw_attributes: {}, 
                            display_info: {} 
                        };
                        
                        // 모든 data-* 및 aria-label 속성 수집
                        const allEls = [node, ...Array.from(node.querySelectorAll('*'))];
                        allEls.forEach(el => {
                            for (let attr of el.attributes) {
                                if (attr.name.startsWith('data-') || attr.name === 'aria-label') {
                                    res.raw_attributes[attr.name] = attr.value;
                                }
                            }
                        });

                        const getT = (sel) => node.querySelector(sel)?.innerText?.trim() || "";
                        
                        // 핵심 필드 정규화
                        res.display_info.name = getT("div[class*='productName']");
                        res.display_info.original_price = getT("del[class*='line-through']");
                        res.display_info.final_price = getT("div[class*='PriceArea_priceArea'] span");
                        res.display_info.discount_rate = Array.from(node.querySelectorAll("div[class*='font-bold']"))
                                                        .find(el => el.innerText.includes('%'))?.innerText || "";
                        res.display_info.rating = node.querySelector("div[aria-label]")?.getAttribute("aria-label") || "";
                        res.display_info.review_count = getT("div[class*='productRating'] span")?.replace(/[()]/g, "") || "";
                        res.display_info.delivery_badge = getT("div[class*='TextBadge']");
                        res.display_info.is_ad = !!node.querySelector("div[class*='AdMark_adMark']");
                        res.display_info.link = node.querySelector('a')?.href || "";

                        return res;
                    }""")

                    result_entry = {
                        "rank": i + 1,
                        "keyword": keyword,
                        "timestamp": time.time(),
                        **data['display_info'],
                        "metadata": data['raw_attributes']
                    }
                    extracted_results.append(result_entry)
                    
                    # 기계가 파싱하기 좋게 한 줄씩 JSON 출력
                    print(f"JSON_RESULT: {json.dumps(result_entry, ensure_ascii=False)}")

                except Exception as e:
                    print(f"ERROR_ITEM_{i+1}: {str(e)}")

            self.results["extracted_products"] = extracted_results
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
