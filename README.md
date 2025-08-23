# HRM Agent Design

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Server](https://img.shields.io/badge/API-REST-orange.svg)](http://localhost:8000)
[![Web UI](https://img.shields.io/badge/Web%20UI-Flask-red.svg)](http://localhost:5000)

가전 제품 진단·사용 이력 분석 및 가이드 제공을 위한 **모듈형 AI 에이전트 아키텍처**입니다. 각 에이전트는 설정 가능한 LLM(OpenAI, Amazon Bedrock, Gauss, GaussO)을 사용하며, 결과를 **실시간 스트리밍**으로 제공합니다. Root 에이전트는 **MCP 스타일 레지스트리**를 통해 에이전트/툴을 오케스트레이션하고, **LangSmith 추적**을 지원합니다.

## 🏗️ 마이크로서비스 아키텍처

HRM Agent는 확장 가능한 **마이크로서비스 아키텍처**로 구성됩니다:

- **🚀 HRM Agent API** (`hrm_agent_api.py`): RootAgent의 주요 기능들을 RESTful API로 제공하는 Flask 기반 API 서버 (포트 8000)
- **🌐 Web Application** (`app.py`): 사용자 친화적인 웹 UI를 제공하고 HRM Agent API를 사용하는 웹 서버 (포트 5000)
- **📊 Guide Retriever API**: 문서 검색 및 가이드 제공 서비스 (포트 5001)

## ✨ 핵심 기능

### 🤖 AI 에이전트들
- **📋 DiagnosisSummarizer**: 가전 진단 정보 분석 및 요약
- **📈 OperationHistorySummarizer**: 제품 사용 이력 분석 및 패턴 파악
- **📝 GuideProvider**: 진단/이력 기반 맞춤형 조치 가이드 생성
- **🖼️ ImageAnalyzer**: 이미지 기반 결함 탐지 및 증상 분석 (계획)

### 🛠️ 지원 시스템
- **🎯 RootAgent**: 모든 에이전트/툴을 통합 실행하는 중앙 오케스트레이터
- **🔧 MCP Registry**: 동적 에이전트/도구 등록 및 관리 시스템
- **📄 PromptBuilder**: LLM별, 에이전트별 최적화된 프롬프트 구성
- **🛡️ Guardrails**: 입출력 검증 및 후처리 시스템
- **🔍 GuideRetriever**: 키워드 기반 실시간 가이드 검색 도구
- **📊 Logger**: 구조화된 이벤트 로깅 및 추적 시스템

## 📁 프로젝트 구조

```
hrm_agent_design/
├── 🚀 API & Web Servers
│   ├── hrm_agent_api.py          # RESTful API 서버 (포트 8000)
│   ├── app.py                    # 웹 UI 서버 (포트 5000)
│   ├── run_api_server.py         # API 서버 실행 스크립트
│   ├── run_web_server.py         # 웹 서버 실행 스크립트
│   └── test_api_integration.py   # 통합 테스트 스크립트
│
├── 🤖 AI Agents & Core
│   └── agents/
│       ├── root_agent.py         # 중앙 오케스트레이터
│       ├── mcp.py                # MCP 레지스트리 시스템
│       ├── diagnosis_summarizer.py
│       ├── op_history_summarizer.py
│       ├── guide_provider.py
│       ├── image_analyzer.py     # 이미지 분석 에이전트
│       ├── llm_providers.py      # LLM 프로바이더 팩토리
│       ├── llm_client_*.py       # 개별 LLM 클라이언트들
│       ├── prompt_builder.py     # 프롬프트 구성 시스템
│       ├── guardrails.py         # 검증 & 후처리 시스템
│       ├── retriever.py          # 문서 검색 도구
│       └── logger.py             # 구조화된 로깅 시스템
│
├── 🌐 Web Interface
│   └── templates/
│       ├── index.html            # 메인 대시보드
│       ├── data_review.html      # 데이터 검토 페이지
│       ├── guide_retriever.html  # 가이드 검색 페이지
│       └── prompt_editor.html    # 프롬프트 편집기
│
├── 📊 Data & Configuration
│   ├── data/
│   │   └── sample_original.json  # 샘플 진단 데이터
│   ├── configure.json            # 시스템 설정
│   ├── prompt.json               # 프롬프트 템플릿
│   └── hrm_agent_log.json        # 이벤트 로그
│
├── 📚 Documentation
│   └── documents/
│       ├── README.md             # 문서 가이드
│       ├── context_diagram.md    # 컨텍스트 다이어그램
│       ├── component_connector_view.md  # C&C 뷰
│       ├── module_view.md        # 모듈 뷰
│       ├── deployment_view.md    # 배포 뷰
│       ├── class_diagram.md      # 클래스 다이어그램
│       ├── sequence_diagram.md   # 시퀀스 다이어그램
│       ├── design_patterns.md    # 디자인 패턴 정리
│       ├── architecture_overview.md     # 아키텍처 개요
│       └── api_documentation.md  # API 문서
│
└── 🛠️ Development & Legacy
    ├── main.py                   # 단일 실행 데모
    ├── requirements.txt          # Python 의존성
    ├── MCP_DOCUMENT_RETRIEVER_GUIDE.md
    └── reference_code/           # 레퍼런스 구현
```

## 🔧 시스템 요구사항

### 기본 요구사항
- **Python**: 3.9 이상
- **메모리**: 최소 4GB RAM (권장 8GB)
- **네트워크**: 인터넷 연결 (LLM API 사용 시)
- **포트**: 5000 (웹 UI), 8000 (API 서버), 5001 (가이드 검색)

### 지원되는 LLM 프로바이더
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-4V (이미지 분석)
- **Amazon Bedrock**: Claude, Titan 모델
- **Gauss**: 전용 LLM 서비스
- **GaussO**: Gauss Vision (이미지 분석 지원)

## 🚀 빠른 설치

### 1. 저장소 클론 및 의존성 설치
```bash
git clone <repository-url>
cd hrm_agent_design
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하거나 시스템 환경 변수로 설정:
```bash
# OpenAI (선택)
export OPENAI_API_KEY="your-openai-api-key"

# AWS Bedrock (선택)
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"

# Gauss (선택)
export GAUSS_ACCESS_KEY="your-gauss-access-key"
export GAUSS_SECRET_KEY="your-gauss-secret-key"

# GaussO (선택)
export GAUSSO_ACCESS_KEY="your-gausso-access-key"
export GAUSSO_SECRET_KEY="your-gausso-secret-key"

# LangSmith 추적 (선택)
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="your-langsmith-api-key"
export LANGCHAIN_PROJECT="hrm-agent"
```

## 🎯 빠른 시작

### 방법 1: 마이크로서비스 모드 (권장) 🌟

**단계 1**: API 서버 시작
```bash
# 터미널 1
python run_api_server.py
# 또는
python hrm_agent_api.py
```

**단계 2**: 웹 서버 시작  
```bash
# 터미널 2
python run_web_server.py
# 또는
python app.py
```

**단계 3**: 브라우저에서 접속
```
🌐 웹 UI: http://localhost:5000
🚀 API 문서: http://localhost:8000/health
```

### 방법 2: 통합 테스트 실행 🧪

```bash
# 시스템 전체 테스트
python test_api_integration.py

# 개별 컴포넌트 테스트
python -m pytest agents/test_*.py
```

### 방법 3: 단일 데모 모드 (레거시) 🔧
```bash
python main.py
```
> 진단 요약, 사용 이력 요약, 가이드 생성을 순차적으로 실행합니다.

## 🔗 API 엔드포인트 개요

HRM Agent API (`http://localhost:8000`)는 RESTful API를 제공합니다:

| 카테고리 | 엔드포인트 | 기능 |
|---------|-----------|------|
| **🏥 헬스 체크** | `GET /health` | 서버 상태 확인 |
| **📋 진단 분석** | `POST /api/diagnosis/stream` | 실시간 진단 요약 |
| **📈 이력 분석** | `POST /api/operation-history/stream` | 실시간 운영 이력 분석 |
| **📝 가이드 생성** | `POST /api/actions-guide/stream` | 실시간 조치 가이드 (한국어) |
| **🖼️ 이미지 분석** | `POST /api/image-analysis/stream` | 실시간 이미지 결함 분석 (계획) |
| **🔧 도구 관리** | `GET /api/capabilities` | 사용 가능한 에이전트/도구 조회 |
| **🛠️ MCP 도구** | `POST /api/mcp/tools/<name>` | MCP 도구 안전 호출 |

> 📖 **상세 API 문서**: [`documents/api_documentation.md`](documents/api_documentation.md)

### 빠른 API 테스트

```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 진단 요약 (스트리밍)
curl -X POST http://localhost:8000/api/diagnosis/stream \
  -H "Content-Type: application/json" \
  -d '{"analytics": {"deviceType": "AC", "diagnosisLists": []}, "language": "ko"}'
```

## 💻 프로그래밍 가이드

### Python SDK 사용법

```python
from agents.root_agent import RootAgent

# RootAgent 초기화 (설정 파일 기반)
root = RootAgent()

# 또는 특정 LLM 프로바이더 지정
root = RootAgent(provider_override="openai", 
                provider_kwargs_override={"model": "gpt-4"})

# 사용 가능한 기능 확인
capabilities = root.list_capabilities()
print(f"에이전트: {list(capabilities['agents'].keys())}")
print(f"도구: {list(capabilities['tools'].keys())}")

# 🔥 실시간 스트리밍 진단
for chunk in root.run_diagnosis(
    {"deviceType": "AC", "diagnosisLists": [...]}, 
    language="ko"
):
    print(chunk, end="", flush=True)

# 📊 운영 이력 분석
for chunk in root.run_op_history(
    {"events": [{"timestamp": "2024-01-01", "temp": 22.5}]},
    language="ko"
):
    print(chunk, end="", flush=True)

# 📝 맞춤형 조치 가이드 (한국어 전용)
for chunk in root.run_actions_guide(
    diagnosis_summary="냉각 효율 저하 감지",
    category="AC",
    language="ko"
):
    print(chunk, end="", flush=True)
```

### 개별 에이전트 활용

```python
from agents.diagnosis_summarizer import DiagnosisSummarizer
from agents.image_analyzer import ImageAnalyzer

# 🎯 특정 LLM으로 진단 에이전트 생성
diagnosis_agent = DiagnosisSummarizer(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

# 🖼️ 이미지 분석 에이전트 (GPT-4V 활용)
image_agent = ImageAnalyzer(
    provider="openai",
    model="gpt-4-vision-preview"
)

# 이미지 분석 실행
with open("product_image.jpg", "rb") as f:
    image_data = f.read()
    
result = image_agent.analyze_single_image(
    image_data=image_data,
    filename="product_image.jpg",
    analysis_type="DEFECT_DETECTION",
    language="ko"
)
```

## 🎨 고급 설정 및 커스터마이징

### LLM 프로바이더 설정

| 프로바이더 | 설정 방법 | 추가 매개변수 |
|-----------|----------|-------------|
| **OpenAI** | `provider="openai"` | `model`, `api_key`, `temperature` |
| **Bedrock** | `provider="bedrock"` | `model_id`, `region`, `max_tokens` |
| **Gauss** | `provider="gauss"` | `access_key`, `secret_key` |
| **GaussO** | `provider="gausso"` | `access_key`, `secret_key` |

```python
# 예시: 고급 설정
agent = DiagnosisSummarizer(
    provider="openai",
    model="gpt-4-turbo",
    temperature=0.3,
    max_tokens=2000
)
```

### 프롬프트 엔지니어링

```python
from agents.prompt_builder import PromptBuilder

class CustomPromptBuilder(PromptBuilder):
    def build_diagnosis_prompt(self, device_type, diagnosis_text, provider, language):
        # 커스텀 프롬프트 로직
        return super().build_diagnosis_prompt(device_type, diagnosis_text, provider, language)

# 커스텀 프롬프트 빌더 사용
root = RootAgent()
root.prompt_builder = CustomPromptBuilder()
```

### 보안 가드레일 구현

```python
from agents.guardrails import Guardrail

class ProductionGuardrail(Guardrail):
    def pre_guard(self, payload: dict) -> dict:
        # 입력 데이터 검증 및 정제
        if not payload.get("deviceType"):
            raise ValueError("deviceType is required")
        return payload
    
    def post_guard(self, output: str) -> str:
        # 출력 결과 필터링 및 검증
        return self.remove_sensitive_info(output)
```

## 🔧 확장 가능한 아키텍처

### MCP 스타일 플러그인 시스템

```python
from agents.root_agent import RootAgent
from agents.mcp import AgentMetadata, ToolMetadata

root = RootAgent()

# 커스텀 에이전트 등록
class CustomAgent:
    def process(self, data, **kwargs):
        yield f"Processing {data}"

root.register_agent(
    "custom_agent", 
    CustomAgent(),
    metadata=AgentMetadata(
        name="Custom Agent",
        description="사용자 정의 분석 에이전트",
        capabilities=["analysis", "reporting"]
    )
)

# 커스텀 도구 등록
def custom_tool(query: str, **kwargs):
    return f"Tool result for: {query}"

root.register_tool("custom_tool", custom_tool)
```

## 📚 문서 및 아키텍처

### 🏗️ 아키텍처 문서
- **[📋 전체 문서 가이드](documents/README.md)**: 모든 아키텍처 문서 목록
- **[🎨 디자인 패턴](documents/design_patterns.md)**: 적용된 16가지 디자인 패턴
- **[🏛️ 아키텍처 개요](documents/architecture_overview.md)**: 시스템 전체 구조
- **[📊 API 문서](documents/api_documentation.md)**: 상세 API 명세

### 📐 다이어그램
- **[🌐 컨텍스트 다이어그램](documents/context_diagram.md)**: 시스템 경계
- **[🔗 컴포넌트 & 커넥터 뷰](documents/component_connector_view.md)**: 런타임 구조
- **[📦 모듈 뷰](documents/module_view.md)**: 정적 코드 구조
- **[🚀 배포 뷰](documents/deployment_view.md)**: 인프라 구성

## 🛡️ 보안 및 모범 사례

### 보안 체크리스트
- ✅ **환경 변수**: API 키를 코드에 하드코딩하지 않음
- ✅ **입력 검증**: 모든 사용자 입력에 대한 검증 적용
- ✅ **출력 필터링**: 민감한 정보 자동 제거
- ✅ **로깅**: 구조화된 로그로 보안 이벤트 추적
- ✅ **HTTPS**: 프로덕션에서 TLS/SSL 사용

### 성능 최적화
- **스트리밍**: 실시간 응답으로 사용자 경험 향상
- **캐싱**: 자주 사용되는 결과 캐싱
- **비동기 처리**: 동시 요청 처리 능력 향상
- **리소스 관리**: 메모리 효율적인 데이터 처리

## 🤝 기여 및 지원

### 개발 환경 설정
```bash
# 개발 의존성 설치
pip install -r requirements-dev.txt

# 코드 품질 검사
flake8 agents/
black agents/
mypy agents/

# 테스트 실행
pytest tests/
```

### 라이선스
이 프로젝트는 참조 및 프로토타이핑 목적으로 제공됩니다.


