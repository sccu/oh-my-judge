# Research Log

## 1. Akamai Bot Manager & Bypass Tech (2025-2026 Update)

### 1.1. 주요 탐지 메커니즘
- **JA4 Fingerprinting**: TLS 핸드쉐이크 단계에서 자동화 도구를 식별하는 차세대 지문 인식.
- **Sensor Data Analysis**: 브라우저 런타임에서 수집된 마우스 궤적, WebGL, 캔버스, 폰트, 배터리 정보 등을 통합 분석하여 `_abck` 쿠키 발급 여부 결정.
- **CDP (Chrome DevTools Protocol) Side-effects**: 자동화 도구가 브라우저를 제어할 때 발생하는 미세한 속성 변화 감지.

### 1.2. 검토 기술 및 라이브러리
- **Scrapling**: 
  - **장점**: TLS/JA4 및 HTTP/2-3 Impersonation 내장. `StealthyFetcher`를 통해 Akamai 수준의 보호막을 비교적 쉽게 통과.
  - **상태**: 최우선 검토 대상.
- **Camoufox**:
  - **장점**: Playwright와 호환되는 Firefox 기반 커스텀 빌드. C++ 레벨에서 지문 변조를 수행하여 탐지 회피력이 매우 높음.
  - **상태**: Chromium 기반 우회 실패 시 대안으로 검토.
- **Nodriver**:
  - **장점**: WebDriver를 사용하지 않고 CDP를 직접 조작하여 `navigator.webdriver` 감지 원천 차단.
  - **상태**: Playwright 기반 구현이 차단될 경우 검토.
- **curl_cffi**:
  - **장점**: 브라우저 오버헤드 없이 완벽한 TLS 지문 모사 가능.
  - **상태**: 단순 데이터 추출이나 API 요청 시 활용.

## 2. 세부 구현 기술 조사

### 2.1. Human-like Interaction
- **Mouse Trajectory**: Bezier 곡선을 활용하여 가속/감속이 포함된 비선형 궤적 생성 필요.
- **Typing Simulation**: 일정한 속도가 아닌, 오타 후 수정이나 가변적인 키 입력 간격 적용.

### 2.2. IP Reputation
- **Residential/Mobile Proxies**: 데이터센터 IP는 Akamai에 의해 즉시 차단됨. 4G/5G 모바일 프록시가 가장 신뢰도가 높음.

## 3. 향후 실행 계획 (Next Steps)
- [ ] Scrapling을 활용한 Akamai 적용 사이트(예: 특정 쇼핑몰) 접속 테스트.
- [ ] Playwright + Camoufox 조합의 성능 및 탐지 회피력 벤치마크.
- [ ] 베지에 곡선 기반의 마우스 이동 유틸리티 코드 작성.
