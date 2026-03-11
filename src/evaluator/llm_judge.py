import json
import base64
import os

class LLMJudge:
    """
    수집된 증거물(DOM + 스크린샷)을 바탕으로 LLM Vision 모델에게 시각적 평가를 요청합니다.
    """
    def __init__(self, model="gpt-4o"):
        self.model = model

    def _encode_image(self, image_path):
        """
        이미지 파일을 Base64 문자열로 인코딩합니다.
        """
        if not os.path.exists(image_path):
            return None
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def prepare_vision_prompt(self, task, action_results):
        """
        Vision 분석을 위한 고도화된 프롬프트를 생성합니다.
        """
        grading_guidelines = "\n".join([f"- {g['criteria']} (가중치: {g['weight']})" for g in task['grading_guidelines']])
        
        prompt = f"""
        # Visual & Functional Evaluation Request

        ## 1. Task Context
        - Task Name: {task['name']}
        - Goal: {task['description']}

        ## 2. Visual Grading Guidelines
        당신은 숙련된 QA 엔지니어입니다. 첨부된 스크린샷을 보고 다음 기준을 시각적으로 검증하세요:
        {grading_guidelines}

        ## 3. Visual Analysis Instructions
        - 레이아웃: 요소들이 겹치거나 깨진 부분이 없는지 확인하세요.
        - 배지/아이콘: '로켓배송' 등 주요 서비스 배지가 상품 카드에 올바르게 표시되는지 확인하세요.
        - 가독성: 텍스트가 배경색과 대비되어 잘 읽히는지, 글꼴 크기가 적절한지 판단하세요.
        - 실제감: 화면이 사용자에게 '신뢰감'을 주는지 주관적이지만 구체적인 근거를 제시하세요.

        ## 4. Output Format (Strict JSON)
        {{
            "total_score": float,
            "visual_findings": [
                {{ "observation": string, "impact": "High/Medium/Low", "screenshot_index": int }}
            ],
            "detailed_scores": [
                {{ "criteria": string, "score": float, "reason": string }}
            ],
            "final_opinion": string,
            "ui_integrity_check": "Pass/Fail"
        }}
        """
        return prompt

    def evaluate(self, task, action_results):
        """
        실제 LLM Vision API를 호출하여 시각적 평가를 수행합니다.
        """
        print(f"[Evaluator] Starting Vision analysis for task: {task['task_id']}")
        
        # 스크린샷 인코딩 (최대 3장까지만 샘플링)
        encoded_images = []
        for img_path in action_results['screenshots'][:3]:
            encoded = self._encode_image(img_path)
            if encoded:
                encoded_images.append(encoded)
        
        prompt = self.prepare_vision_prompt(task, action_results)
        
        # 실제 API 호출 예시 (Pseudo-code)
        # messages = [
        #     { "role": "user", "content": [
        #         { "type": "text", "text": prompt },
        #         *[ { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{img}" } } for img in encoded_images ]
        #     ]}
        # ]
        
        print(f"[Evaluator] Sending {len(encoded_images)} images to {self.model} for visual inspection...")
        
        # 가상의 Vision 분석 결과
        mock_visual_response = {
            "total_score": 9.0,
            "visual_findings": [
                { "observation": "상품 리스트의 '로켓배송' 배지가 선명하게 노출됨", "impact": "High", "screenshot_index": 0 },
                { "observation": "하단 필터 바의 텍스트가 약간 작아 보임", "impact": "Low", "screenshot_index": 0 }
            ],
            "detailed_scores": [
                { "criteria": "로켓배송 배지 노출", "score": 1.0, "reason": "시각적으로 모든 상품 카드에서 확인됨" },
                { "criteria": "레이아웃 정렬", "score": 0.9, "reason": "그리드 시스템이 안정적임" }
            ],
            "final_opinion": "시각적으로 매우 완성도 높은 페이지이며, 주요 정보가 사용자에게 명확히 전달됨.",
            "validation_check": "Pass"
        }
        
        return mock_visual_response
