# System Design & Stealth Strategy

## 1. 아키텍처 상세 설계

본 시스템은 모듈 간 결합도를 낮추기 위해 다음과 같은 구조로 설계되었습니다.

### 1.1. Action Layer (`src/core`, `src/actions`)
- **BaseAction**: 모든 서비스별 액션의 추상 클래스로, `run()` 메서드를 통해 인터페이스를 통일합니다.
- **Service-specific Scripts**: `src/actions/` 아래에 위치하며, 특정 사이트(쿠팡, 네이버 등)의 특성에 맞는 행동을 정의합니다.
- **HumanoidInteractor**: `src/utils/`에 위치하며, 베지에 곡선 이동, 가변 타이핑 등 사람의 행동을 모사하는 핵심 유틸리티입니다.

### 1.2. Evaluation Layer (`src/evaluator`)
- **Evidence Collector**: 액션 실행 중 획득한 스크린샷, DOM 데이터, 네트워크 로그를 취합합니다.
- **LLM Judge**: 취합된 증거물과 `tasks/`에 정의된 가이드라인을 LLM(Vision 지원 모델 권장)에 전달하여 최종 점수를 산출합니다.

## 2. 인터랙션 전략 (Stealth & Humanoid)
- **Direct CDP Control**: 라이브러리가 아닌 브라우저에 직접 접속하여 자동화 플래그를 최소화합니다.
- **Non-linear Mouse Movement**: 직선이 아닌 무작위성이 가미된 경로로 마우스를 이동시켜 행동 분석 탐지를 우회합니다.
- **Probabilistic Typing**: 타이핑 속도에 무작위 지연 시간을 부여합니다.

## 3. 실행 흐름
1. 태스크 정의 수신
2. 대응하는 Action 스크립트 실행 (Stealth 모드)
3. 결과물(DOM, Screenshot, Network Log) 저장
4. LLM 에이전트에게 가이드라인과 함께 결과 전달
5. 최종 점수 및 근거 산출
