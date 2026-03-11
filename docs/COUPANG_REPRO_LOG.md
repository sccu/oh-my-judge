# Coupang Reproduction Test Log (2026-03-11)

## 1. 개요
쿠팡의 강력한 안티봇 솔루션(Akamai Premier)을 우회하여 상품 검색 및 데이터 추출을 자동화하기 위한 재현 테스트 기록입니다.

## 2. 시도된 가설 및 결과

### 가설 1: 기본 Playwright Headless + 단순 랜덤 대기
*   **내용**: Playwright의 기본 Chromium Headless 모드와 `time.sleep` 기반의 랜덤 대기로 접속 시도.
*   **결과**: **실패 (즉시 차단)**.
*   **상세**: `goto()` 호출 직후 Akamai에 의해 403 Forbidden ("Access Denied") 응답을 받음. 브라우저 지문(Fingerprint) 및 Headless 여부가 즉시 식별됨.

### 가설 3: CDP(Chrome DevTools Protocol) + Real Browser
*   **내용**: 실제 설치된 크롬을 9222 포트로 실행하고 Playwright를 연결하여 '환경 검증' 우회.
*   **결과**: **부분 성공 (입구 컷 우회 완료)**.
*   **상세**: 
    - 더 이상 "Access Denied" (403)가 발생하지 않으며, 쿠팡 메인 페이지 로드에 성공함.
    - 하지만 `#headerSearchKeyword` 등 기존 셀렉터로 검색창을 찾지 못하는 현상 발생. 
    - 이는 Akamai가 자동화 도구 연결을 감지하여 DOM 구조를 변조했거나, 렌더링 방식에 차이를 두었을 가능성이 있음 (또는 단순 셀렉터 변경).

## 3. 확인된 사실 (Facts)
1.  **즉각적 차단**: 일반적인 데이터센터 IP 및 기본 Headless 설정으로는 메인 페이지 진입조차 불가능함.
2.  **Akamai Premier 확인**: 차단 화면의 Reference ID 및 `errors.edgesuite.net` 링크를 통해 Akamai의 고도화된 봇 매니저가 작동 중임을 확인.
3.  **환경 우회 가능성 확인**: CDP를 통해 실제 유저 브라우저에 연결할 경우, Fingerprinting 기반의 초기 차단(403)은 확실히 우회 가능함.
4.  **UI 렌더링 지연/변조**: 환경 우회 후에도 검색창 등 핵심 요소가 즉시 나타나지 않거나 기존 셀렉터가 작동하지 않는 2차 장애물이 존재함.

## 4. 진행 중인 시도
*   **CDP (Chrome DevTools Protocol) 연결**: 실제 유저가 사용하는 일반 크롬 브라우저를 9222 포트로 띄우고, Playwright가 이를 제어하도록 하여 '자동화 도구'라는 낙인을 피하는 방식 시도 중.
*   **Warm Profile 활용**: 기존 로그인 기록이나 쿠키가 남아있는 유저 프로필(`user-data-dir`)을 로드하여 신뢰도를 높임.

## 5. 향후 계획 (Planned)
1.  **Nodriver 도입**: WebDriver의 흔적을 남기지 않는 `nodriver` 라이브러리로 Action 엔진 교체 검토.
2.  **Residential Proxy 테스트**: IP 신뢰도 문제를 해결하기 위해 주거용/모바일 프록시 연동.
3.  **Stealth JS 삽입**: `navigator.webdriver` 등을 변조하는 스텔스 스크립트 최적화.
4.  **Headful 실행**: 실제 GUI 환경에서 브라우저를 노출시킨 상태로 재현 시도.
