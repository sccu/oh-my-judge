# Task & Evaluation Specification

## 1. 태스크(Task) 구조
각 평가는 독립적인 태스크들로 구성되며, JSON 또는 YAML 형식으로 관리됩니다.
- **Task Description**: 수행해야 할 작업의 구체적 설명.
- **Max Score**: 해당 항목의 배점.
- **Grading Guidelines**: 채점 기준 (Pass/Fail 조건, 부분 점수 기준).

## 2. 데이터 추출 및 분석
- **DOM Snapshot**: 정적 분석을 위한 핵심 노드 추출.
- **Visual Evidence**: LLM Vision 모델을 위한 주요 시점의 스크린샷.

## 3. 평가 검증 (Validation)
LLM의 평가 결과가 구체적이고 일관적인지 검증하는 단계를 둡니다.
- **Self-Correction**: LLM이 산출한 점수의 근거가 가이드라인과 일치하는지 재검토.
- **Consistency Check**: 동일 태스크에 대해 반복 실행 시 점수 편차 확인.
