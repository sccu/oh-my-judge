# Coupang Reproduction Test Log (2026-03-11)

## 1. 개요
쿠팡의 강력한 안티봇 솔루션(Akamai Premier)을 우회하여 상품 검색 및 데이터 추출을 자동화하기 위한 재현 테스트 기록입니다.

## 2. 시도된 가설 및 결과

### 가설 1: 기본 Playwright Headless + 단순 랜덤 대기
*   **내용**: Playwright의 기본 Chromium Headless 모드와 `time.sleep` 기반의 랜덤 대기로 접속 시도.
*   **결과**: **실패 (즉시 차단)**.
*   **상세**: `goto()` 호출 직후 Akamai에 의해 403 Forbidden ("Access Denied") 응답을 받음. 브라우저 지문(Fingerprint) 및 Headless 여부가 즉시 식별됨.

### 가설 2: 행동 분석 우회 (Bezier 곡선 마우스 + 타이핑 모사)
*   **내용**: `HumanoidInteractor`를 고도화하여 베지에 곡선 기반의 비선형 마우스 이동과 가변 지연 타이핑 적용.
*   **결과**: **실패 (진입 전 차단)**.
*   **상세**: 상호작용 단계(검색창 입력)에 도달하기 전, 페이지 로드 시점에서 이미 "Access Denied" 상태가 됨. 이는 행동 분석 이전에 TLS/IP/브라우저 환경 검증 단계에서 차단되었음을 의미함.

## 3. 확인된 사실 (Facts)
1.  **즉각적 차단**: 일반적인 데이터센터 IP 및 기본 Headless 설정으로는 메인 페이지 진입조차 불가능함.
2.  **Akamai Premier 확인**: 차단 화면의 Reference ID 및 `errors.edgesuite.net` 링크를 통해 Akamai의 고도화된 봇 매니저가 작동 중임을 확인.
3.  **탐지 레벨**: 인터랙션(Behavioral) 보다는 환경(Fingerprinting) 및 네트워크(IP Reputation) 레벨에서의 차단이 우선적으로 발생함.
4.  **차단 해제 추정**: 단순 대기만으로는 차단이 풀리지 않으며, 세션(쿠키) 및 IP가 Akamai의 블랙리스트에 등록될 경우 일정 시간(수 시간~수 일) 동안 지속될 수 있음.

## 4. 진행 중인 시도
*   **CDP (Chrome DevTools Protocol) 연결**: 실제 유저가 사용하는 일반 크롬 브라우저를 9222 포트로 띄우고, Playwright가 이를 제어하도록 하여 '자동화 도구'라는 낙인을 피하는 방식 시도 중.
*   **Warm Profile 활용**: 기존 로그인 기록이나 쿠키가 남아있는 유저 프로필(`user-data-dir`)을 로드하여 신뢰도를 높임.

## 5. 향후 계획 (Planned)
1.  **Nodriver 도입**: WebDriver의 흔적을 남기지 않는 `nodriver` 라이브러리로 Action 엔진 교체 검토.
2.  **Residential Proxy 테스트**: IP 신뢰도 문제를 해결하기 위해 주거용/모바일 프록시 연동.
3.  **Stealth JS 삽입**: `navigator.webdriver` 등을 변조하는 스텔스 스크립트 최적화.
4.  **Headful 실행**: 실제 GUI 환경에서 브라우저를 노출시킨 상태로 재현 시도.
