# HRM Agent 시스템 컨텍스트 다이어그램

## 개요

컨텍스트 다이어그램은 HRM Agent 시스템과 외부 엔티티 간의 상호작용을 보여줍니다. 시스템의 경계와 외부 의존성을 명확히 파악할 수 있습니다.

## 시스템 컨텍스트 다이어그램

```mermaid
graph TB
    subgraph "External Users"
        EndUser[최종 사용자<br/>End User]
        ServiceEngineer[서비스 엔지니어<br/>Service Engineer]
        Administrator[시스템 관리자<br/>Administrator]
        Developer[개발자<br/>Developer]
    end
    
    subgraph "External Systems"
        LLMProviders[LLM 서비스<br/>OpenAI, Bedrock, Gauss]
        GuideAPI[가이드 검색 API<br/>Guide Retriever API]
        LangSmith[LangSmith<br/>AI 추적 서비스]
        FileSystem[파일 시스템<br/>JSON 데이터, 설정]
        ImageStorage[이미지 저장소<br/>Image Storage]
    end
    
    subgraph "HRM Agent System"
        HRMSystem[HRM Agent<br/>AI 진단 & 분석 시스템]
    end
    
    subgraph "Client Applications"
        WebBrowser[웹 브라우저<br/>Web Browser]
        MobileApp[모바일 앱<br/>Mobile App]
        APIClient[API 클라이언트<br/>Third-party Apps]
        CLITool[CLI 도구<br/>Command Line Tool]
    end
    
    %% User Interactions
    EndUser --> WebBrowser : "웹 UI 사용"
    ServiceEngineer --> WebBrowser : "진단 결과 조회"
    ServiceEngineer --> MobileApp : "현장 진단"
    Administrator --> WebBrowser : "시스템 관리"
    Developer --> APIClient : "API 통합"
    Developer --> CLITool : "개발/테스트"
    
    %% Client to System
    WebBrowser --> HRMSystem : "HTTP/HTTPS 요청"
    MobileApp --> HRMSystem : "REST API 호출"
    APIClient --> HRMSystem : "REST API 호출"
    CLITool --> HRMSystem : "API 요청"
    
    %% System to External Services
    HRMSystem --> LLMProviders : "AI 모델 호출<br/>(진단, 요약, 분석)"
    HRMSystem --> GuideAPI : "문서 검색 요청<br/>(HTTP/REST)"
    HRMSystem --> LangSmith : "추적 데이터 전송<br/>(선택적)"
    HRMSystem --> FileSystem : "데이터 읽기/쓰기<br/>(JSON, Config)"
    HRMSystem --> ImageStorage : "이미지 업로드/다운로드<br/>(분석용)"
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef systemClass fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    classDef externalClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef clientClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class EndUser,ServiceEngineer,Administrator,Developer userClass
    class HRMSystem systemClass
    class LLMProviders,GuideAPI,LangSmith,FileSystem,ImageStorage externalClass
    class WebBrowser,MobileApp,APIClient,CLITool clientClass
```

## 외부 엔티티 설명

### 사용자 (Users)

#### 최종 사용자 (End User)
- **역할**: 가전제품 소유자, 일반 고객
- **상호작용**: 웹 브라우저를 통한 진단 결과 조회, 조치 가이드 확인
- **요구사항**: 직관적인 UI, 한국어 지원, 실시간 결과

#### 서비스 엔지니어 (Service Engineer)
- **역할**: 가전제품 수리/점검 전문가
- **상호작용**: 웹/모바일을 통한 상세 진단, 이미지 분석, 기술 정보 조회
- **요구사항**: 전문적인 분석 도구, 현장 접근성, 오프라인 기능

#### 시스템 관리자 (Administrator)
- **역할**: HRM Agent 시스템 운영 담당자
- **상호작용**: 시스템 모니터링, 설정 관리, 사용자 관리
- **요구사항**: 관리 대시보드, 로그 분석, 성능 모니터링

#### 개발자 (Developer)
- **역할**: 시스템 개발자, 통합 개발자
- **상호작용**: API 사용, 시스템 확장, 커스터마이징
- **요구사항**: API 문서, SDK, 개발 도구

### 클라이언트 애플리케이션 (Client Applications)

#### 웹 브라우저 (Web Browser)
- **기술**: HTML5, CSS3, JavaScript, Server-Sent Events
- **통신**: HTTP/HTTPS, WebSocket (향후)
- **지원 브라우저**: Chrome, Firefox, Safari, Edge

#### 모바일 앱 (Mobile App)
- **플랫폼**: iOS, Android (향후 개발)
- **기능**: 현장 진단, 이미지 촬영/분석, 오프라인 모드
- **통신**: REST API, 이미지 업로드

#### API 클라이언트 (API Client)
- **유형**: 타사 시스템, 통합 솔루션
- **통신**: REST API, JSON 형식
- **인증**: API 키 (향후 구현)

#### CLI 도구 (CLI Tool)
- **용도**: 개발, 테스트, 자동화
- **기능**: 배치 처리, 스크립팅, CI/CD 통합
- **형식**: Python 스크립트, Shell 명령어

### 외부 시스템 (External Systems)

#### LLM 서비스 (LLM Providers)
- **OpenAI**: GPT-4, GPT-4V (이미지 분석)
- **Amazon Bedrock**: Claude, Titan 모델
- **Gauss/GaussO**: 전용 LLM 서비스
- **통신**: REST API, 스트리밍 지원
- **인증**: API 키, AWS 자격증명

#### 가이드 검색 API (Guide Retriever API)
- **포트**: 5001
- **기능**: 문서 검색, 카테고리 필터링
- **통신**: HTTP REST API
- **데이터**: 기술 문서, 매뉴얼, FAQ

#### LangSmith (AI 추적 서비스)
- **기능**: AI 애플리케이션 추적, 성능 모니터링
- **데이터**: 프롬프트, 응답, 메트릭
- **통신**: HTTPS API
- **선택적**: 환경 변수로 활성화/비활성화

#### 파일 시스템 (File System)
- **데이터 파일**: 
  - `sample_original.json`: 샘플 진단 데이터
  - `configure.json`: 시스템 설정
  - `prompt.json`: 프롬프트 템플릿
- **접근 방식**: 로컬 파일 I/O
- **백업**: 정기적 백업 권장

#### 이미지 저장소 (Image Storage)
- **유형**: 로컬 저장소, 클라우드 스토리지 (향후)
- **형식**: JPEG, PNG, WEBP 등
- **처리**: 업로드, 전처리, 분석, 임시 저장
- **보안**: 접근 제어, 암호화

## 데이터 플로우

### 1. 진단 요약 플로우
```
사용자 → 웹 브라우저 → HRM Agent → LLM 서비스 → 진단 결과 → 사용자
```

### 2. 이미지 분석 플로우
```
서비스 엔지니어 → 모바일 앱 → HRM Agent → 이미지 저장소 → LLM 서비스 → 분석 결과
```

### 3. 조치 가이드 플로우
```
사용자 → 웹 브라우저 → HRM Agent → 가이드 검색 API → LLM 서비스 → 맞춤형 가이드
```

### 4. 시스템 모니터링 플로우
```
HRM Agent → LangSmith → 관리자 대시보드 → 시스템 관리자
```

## 보안 및 신뢰성 고려사항

### 외부 의존성 관리
- **LLM 서비스**: API 키 보안, 요청 제한, 장애 복구
- **가이드 검색 API**: 연결 타임아웃, 재시도 로직
- **파일 시스템**: 백업, 권한 관리, 무결성 검사

### 네트워크 보안
- **HTTPS**: 모든 외부 통신 암호화
- **API 인증**: 향후 OAuth 2.0 구현 계획
- **방화벽**: 필요한 포트만 개방

### 데이터 보호
- **개인정보**: 최소 수집, 암호화 저장
- **이미지 데이터**: 임시 저장, 자동 삭제
- **로그 데이터**: 민감 정보 마스킹

## 확장성 고려사항

### 수평적 확장
- **로드 밸런서**: 다중 인스턴스 지원
- **데이터베이스**: 향후 관계형/NoSQL DB 도입
- **캐시**: Redis/Memcached 도입 계획

### 지리적 확장
- **CDN**: 정적 리소스 배포
- **멀티 리전**: 글로벌 서비스 제공
- **지역화**: 다국어 지원 확대

## 장애 시나리오 및 대응

### 외부 서비스 장애
- **LLM 서비스 장애**: 대체 프로바이더 자동 전환
- **가이드 API 장애**: 캐시된 데이터 사용, 기본 응답 제공
- **네트워크 장애**: 재시도 로직, 사용자 알림

### 시스템 내부 장애
- **메모리 부족**: 자동 재시작, 리소스 모니터링
- **디스크 공간 부족**: 로그 로테이션, 임시 파일 정리
- **프로세스 장애**: 헬스 체크, 자동 복구
