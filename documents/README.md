# HRM Agent 시스템 문서

이 폴더에는 HRM Agent 시스템의 아키텍처, 설계, API 문서가 포함되어 있습니다.

## 문서 목록

### 🌐 [컨텍스트 다이어그램 (context_diagram.md)](./context_diagram.md)
- 시스템과 외부 엔티티 간의 상호작용을 보여주는 컨텍스트 다이어그램
- 주요 내용:
  - 외부 사용자 (최종 사용자, 서비스 엔지니어, 관리자, 개발자)
  - 클라이언트 애플리케이션 (웹 브라우저, 모바일 앱, API 클라이언트)
  - 외부 시스템 (LLM 서비스, 가이드 검색 API, 파일 시스템)
  - 데이터 플로우 및 보안 고려사항

### 🔧 [컴포넌트 & 커넥터 뷰 (component_connector_view.md)](./component_connector_view.md)
- 런타임 시스템의 구조와 컴포넌트 간 상호작용을 보여주는 C&C 뷰
- 주요 내용:
  - 티어별 컴포넌트 구조 (Client, Presentation, API, Business Logic, Integration)
  - 커넥터 유형 및 통신 패턴
  - 런타임 시나리오 (진단 요약, 이미지 분석)
  - 품질 속성 분석 (성능, 확장성, 가용성, 보안성)

### 📦 [모듈 뷰 (module_view.md)](./module_view.md)
- 시스템의 정적 구조와 모듈 간 의존성을 보여주는 모듈 뷰
- 주요 내용:
  - 레이어별 모듈 구조 (Application, Core Agent, Specialized Agents, Support Services)
  - 의존성 분석 및 레벨링
  - 모듈별 인터페이스 정의
  - 확장성 및 유지보수성 고려사항

### 🚀 [배포 뷰 (deployment_view.md)](./deployment_view.md)
- 시스템이 실제 하드웨어와 네트워크 인프라에 배포되는 방식
- 주요 내용:
  - 환경별 배포 전략 (개발, 테스트, 스테이징, 프로덕션)
  - 컨테이너 배포 전략 (Docker, Kubernetes)
  - 네트워크 구성 및 보안
  - CI/CD 파이프라인 및 모니터링

### 📋 [클래스 다이어그램 (class_diagram.md)](./class_diagram.md)
- 전체 시스템의 클래스 구조와 관계를 보여주는 Mermaid 다이어그램
- 주요 컴포넌트:
  - API Layer (HRMAgentAPI, WebApp)
  - Core Agent Layer (RootAgent)
  - Specialized Agents (DiagnosisSummarizer, OperationHistorySummarizer, GuideProvider, ImageAnalyzer)
  - Supporting Components (PromptBuilder, Guardrails, MCPRegistry)
  - Data Classes and Enums

### 🔄 [시퀀스 다이어그램 (sequence_diagram.md)](./sequence_diagram.md)
- 주요 비즈니스 플로우의 상호작용을 보여주는 시퀀스 다이어그램
- 포함된 플로우:
  1. 진단 요약 생성 플로우
  2. 이미지 분석 플로우
  3. 고객 조치 가이드 생성 플로우
  4. MCP 도구 호출 플로우
  5. 시스템 초기화 플로우

### 🏗️ [아키텍처 개요 (architecture_overview.md)](./architecture_overview.md)
- 전체 시스템 아키텍처의 상위 수준 개요
- 주요 내용:
  - 시스템 구조 및 레이어
  - 주요 컴포넌트 설명
  - 데이터 플로우
  - 설계 원칙
  - 기술 스택
  - 보안 고려사항
  - 성능 최적화
  - 확장 계획

### 📖 [API 문서 (api_documentation.md)](./api_documentation.md)
- HRM Agent API의 상세한 사용 방법
- 주요 내용:
  - 모든 엔드포인트 설명
  - 요청/응답 형식
  - 에러 코드 및 처리
  - 사용 예시 (cURL, Python, JavaScript)
  - 제한사항 및 문제 해결

### 🎨 [디자인 패턴 (design_patterns.md)](./design_patterns.md)
- HRM Agent 시스템에 적용된 디자인 패턴 종합 정리
- 주요 내용:
  - 생성 패턴 (Factory Method, Builder)
  - 구조 패턴 (Adapter, Facade, Proxy)
  - 행동 패턴 (Strategy, Command, Observer, Template Method, Iterator)
  - 아키텍처 패턴 (Registry, Dependency Injection, Pipeline, Repository, Layered)
  - 동시성 패턴 (Producer-Consumer)
  - 패턴 적용 위치 및 이유

### 📚 [기존 아키텍처 문서](./architecture.md)
- 기존의 상세한 아키텍처 문서 (유지됨)

### 🏢 [레이어드 아키텍처 문서](./layered_architecture.md)
- 레이어드 아키텍처 설계 문서 (유지됨)

## 문서 사용 가이드

### 아키텍트를 위한 읽기 순서
1. **컨텍스트 다이어그램** - 시스템 경계 및 외부 의존성 파악
2. **컴포넌트 & 커넥터 뷰** - 런타임 구조 이해
3. **모듈 뷰** - 정적 구조 및 의존성 분석
4. **배포 뷰** - 인프라 및 배포 전략
5. **디자인 패턴** - 적용된 패턴 및 설계 결정
6. **아키텍처 개요** - 전체적인 설계 원칙

### 개발자를 위한 읽기 순서
1. **아키텍처 개요** - 전체 시스템 이해
2. **디자인 패턴** - 코드 구조의 설계 원칙 이해
3. **모듈 뷰** - 코드 구조 및 의존성 파악
4. **클래스 다이어그램** - 상세 클래스 구조
5. **시퀀스 다이어그램** - 동작 플로우 이해
6. **API 문서** - 실제 사용 방법

### 운영자를 위한 읽기 순서
1. **컨텍스트 다이어그램** - 외부 시스템과의 연동 이해
2. **배포 뷰** - 인프라 구성 및 배포 방식
3. **컴포넌트 & 커넥터 뷰** - 런타임 동작 및 장애 지점
4. **API 문서** - 서비스 사용 방법
5. **아키텍처 개요** - 전체 시스템 구성

### 신규 개발자를 위한 읽기 순서
1. **README.md** (프로젝트 루트) - 프로젝트 개요
2. **컨텍스트 다이어그램** - 시스템이 해결하는 문제 이해
3. **아키텍처 개요** - 전체 구조 파악
4. **디자인 패턴** - 코드 작성 시 따라야 할 패턴 이해
5. **모듈 뷰** - 코드 구조 학습
6. **클래스 다이어그램** - 상세 구현 이해
7. **시퀀스 다이어그램** - 동작 원리 이해
8. **API 문서** - 실제 구현 방법

## 다이어그램 렌더링

### Mermaid 다이어그램 보기
이 문서들의 다이어그램은 Mermaid 형식으로 작성되어 있습니다. 다음 방법으로 볼 수 있습니다:

1. **GitHub**: GitHub에서 자동으로 렌더링됩니다
2. **VS Code**: Mermaid Preview 확장 프로그램 설치
3. **온라인**: [Mermaid Live Editor](https://mermaid.live/)
4. **로컬**: Mermaid CLI 도구 사용

### 다이어그램 편집
다이어그램을 수정하려면:
1. Mermaid 문법을 학습하세요 ([공식 문서](https://mermaid-js.github.io/mermaid/))
2. 온라인 에디터에서 테스트하세요
3. 문서 파일을 직접 편집하세요

## 문서 업데이트

### 언제 업데이트해야 하나요?
- 새로운 에이전트나 도구 추가 시
- API 엔드포인트 변경 시
- 아키텍처 구조 변경 시
- 새로운 기능 추가 시

### 업데이트 방법
1. 해당 문서 파일 편집
2. 다이어그램이 있다면 함께 업데이트
3. 변경 로그 추가
4. 코드 리뷰 요청

## 피드백 및 기여

문서에 대한 피드백이나 개선 제안이 있으시면:
1. GitHub Issue 생성
2. Pull Request 제출
3. 팀 내 논의

---

📝 **마지막 업데이트**: 2024-01-01  
👥 **관리자**: HRM Agent 개발팀  
🔄 **버전**: 1.0.0
