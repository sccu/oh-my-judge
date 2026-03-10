import time
import os
import json
from abc import ABC, abstractmethod
from src.utils.humanoid import HumanoidInteractor
from src.utils.extractor import DataExtractor

class BaseAction(ABC):
    """
    모든 서비스 액션의 기본 클래스입니다.
    """
    def __init__(self, page):
        self.page = page
        self.humanoid = HumanoidInteractor(page)
        self.extractor = DataExtractor(max_chars=20000, timeout=5) # 엄격한 제한
        self.results = {
            "screenshots": [],
            "dom_path": None,
            "structured_data": None
        }

    @abstractmethod
    def run(self, **kwargs):
        pass

    def capture_evidence(self, name):
        timestamp = int(time.time())
        path = f"outputs/{name}_{timestamp}.png"
        self.page.screenshot(path=path)
        self.results["screenshots"].append(path)
        print(f"[Action] Captured screenshot: {path}")

    def extract_dom(self, name):
        """
        DOM 데이터를 정제하여 파일로 저장하고, 메타데이터만 결과에 포함합니다.
        """
        print(f"[Action] Extracting and cleaning DOM: {name}")
        raw_html = self.page.content()
        
        # 1. 정제된 텍스트 추출 (타임아웃 및 길이 제한 적용)
        cleaned_text = self.extractor.clean_html(raw_html)
        
        # 2. 파일 저장 (LLM 직접 전송 방지)
        timestamp = int(time.time())
        dom_file_path = f"outputs/{name}_{timestamp}.txt"
        with open(dom_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        self.results["dom_path"] = dom_file_path
        
        # 3. 간단한 구조화 데이터 미리 추출 (옵션)
        self.results["structured_data"] = self.extractor.extract_structured_data(raw_html)
        
        print(f"[Action] DOM data saved to: {dom_file_path} ({len(cleaned_text)} chars)")
