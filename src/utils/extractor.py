import re
import time
from bs4 import BeautifulSoup

class DataExtractor:
    """
    DOM 데이터를 안전하고 효율적으로 추출 및 정제합니다.
    """
    def __init__(self, max_chars=50000, timeout=10):
        self.max_chars = max_chars  # LLM 토큰 낭비 방지를 위한 최대 글자 수
        self.timeout = timeout      # 추출 작업 최대 허용 시간 (초)

    def clean_html(self, html_content):
        """
        불필요한 태그를 제거하고 텍스트 위주로 정제합니다.
        """
        start_time = time.time()
        
        # 1. BeautifulSoup을 이용한 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 2. 불필요한 태그 제거 (성능을 위해 루프 내 시간 체크)
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'noscript', 'svg']):
            if time.time() - start_time > self.timeout:
                print("[Extractor] Warning: Extraction timed out during cleaning.")
                break
            tag.decompose()

        # 3. 텍스트 추출 및 공백 정리
        # 가독성을 위해 줄바꿈은 유지하되 중복 공백 제거
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        # 4. 데이터 크기 제한 (Trimming)
        if len(cleaned_text) > self.max_chars:
            print(f"[Extractor] Trimming content from {len(cleaned_text)} to {self.max_chars} chars.")
            cleaned_text = cleaned_text[:self.max_chars] + "\n... (Content truncated for token safety) ..."

        return cleaned_text

    def extract_structured_data(self, html_content):
        """
        (Optional) 특정 패턴(가격, 상품명 등)을 정규식으로 미리 뽑아 구조화합니다.
        """
        # 예: 가격 패턴 추출 시도
        prices = re.findall(r'(\d{1,3}(?:,\d{3})+)원', html_content)
        return {
            "found_prices": list(set(prices))[:20], # 최대 20개만
            "timestamp": time.time()
        }
