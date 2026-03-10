# Oh-My-Judge (OMJ)

**Oh-My-Judge**는 사람이 수행하는 온라인 서비스 평가 작업을 LLM 에이전트로 자동화하는 프로젝트입니다. 단순한 크롤링을 넘어, 강력한 봇 탐지 시스템(Akamai 등)을 우회하며 실제 사람과 유사한 인터랙션을 재현하고 이를 바탕으로 서비스의 질을 정밀하게 평가합니다.

## 핵심 목표
- **실제 행동 재현**: 로그인, 검색, 클릭 등 인간의 주요 행동 패턴을 스크립트로 정밀하게 모사합니다.
- **안티-봇 우회**: Akamai Bot Manager 등 고도화된 탐지 솔루션을 우회하기 위한 Stealth 기술을 적용합니다.
- **객관적 LLM 평가**: 추출된 데이터와 스크린샷을 바탕으로, 사전에 정의된 태스크 가이드라인에 따라 LLM이 정량적/정성적 평가를 수행합니다.

## 기술 스택 (검토 중)
- **Browser Automation**: Playwright with CDP, Scrapling, OpenChrome
- **Stealth**: Human-like Mouse/Keyboard Interaction, TLS Fingerprinting
- **Evaluation**: LLM (OpenAI, Anthropic, etc.)
