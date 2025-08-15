HRM Agent Design

가전 제품 진단·사용 이력 분석 및 가이드 제공을 위한 모듈형 에이전트 아키텍처입니다. 각 에이전트는 설정 가능한 LLM(OpenAI, Amazon Bedrock, Gauss, GaussO)을 사용하며, 결과를 스트리밍 형태로 제공합니다. Root 에이전트는 MCP 스타일 레지스트리를 통해 에이전트/툴을 오케스트레이션하고, LangSmith 트레이싱을 지원합니다.

## 핵심 기능
- diagnosis_summarizer: 가전 진단 정보 요약
- op_history_summarizer: 제품 사용 이력 요약
- guide_provider: 진단/이력 요약 기반 조치 가이드 생성
- guider_retriever(tool): 키워드/코드 기반 간단 가이드 검색(stream)
- Root 에이전트: 위 에이전트/툴을 통합 실행, MCP 스타일 확장 지원
- PromptBuilder: LLM·에이전트별 프롬프트 구성(교체/확장 가능)
- Guardrail(더미): Pre-/Post- 가드레일 훅 인터페이스 제공

## 레퍼런스 코드 연계
- 진단 요약: `reference_code/analytics_gauss.py`, `reference_code/analytics_amazon.py`
- 사용 이력 요약: `reference_code/operation_history_gauss.py`, `reference_code/operation_history_amazon.py`, `reference_code/operation_history_openai.py`

## 디렉터리 구조
```
hrm_agent_design/
  agents/
    __init__.py
    llm_providers.py      # OpenAI / Bedrock / Gauss / GaussO 어댑터(스트리밍 지원)
    prompt_builder.py     # 에이전트/LLM별 프롬프트 빌더
    guardrails.py         # Pre/Post 가드레일 더미 클래스
    retriever.py          # guider_retriever 도구(간단 in-memory)
    diagnosis_summarizer.py
    op_history_summarizer.py
    guide_provider.py
    mcp.py                # MCP 유사 레지스트리(플러그인형 확장)
  reference_code/         # 레퍼런스 스크립트
  data/
  main.py                 # 실행 데모(스트리밍 출력)
  requirements.txt
  README.md
```

## 요구 사항
- Python 3.9+
- 네트워크 접근(해당 LLM API 사용 시)

## 설치
```bash
pip install -r requirements.txt
```

## 환경 변수 설정
- OpenAI: `OPENAI_API_KEY`
- Amazon Bedrock: `AWS_REGION` 또는 `AWS_DEFAULT_REGION` (자격증명은 표준 AWS 방식)
- Gauss: `GAUSS_ACCESS_KEY`, `GAUSS_SECRET_KEY`
- GaussO: `GAUSSO_ACCESS_KEY`, `GAUSSO_SECRET_KEY`
- LangSmith(선택): `LANGCHAIN_TRACING_V2=TRUE`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`

## 빠른 시작
```bash
python main.py
```
- 진단 요약, 사용 이력 요약, 가이드 생성, 리트리버 호출을 스트리밍으로 출력합니다.

## 프로그래밍 사용법
### Root 에이전트 사용
```python
from agents.root_agent import RootAgent

root = RootAgent()
print(root.list_capabilities())  # {'agents': [...], 'tools': [...]} 

# 스트리밍 실행 예시
for chunk in root.run_diagnosis({"deviceType": "AC", "diagnosisLists": []}, language="ko"):
    print(chunk, end="")

for chunk in root.run_op_history({"events": [{"t":0,"temp":8.5}]}, language="both"):
    print(chunk, end="")

for chunk in root.run_guide("Cooling inefficiency.", "Stable ops.", language="en"):
    print(chunk, end="")

# retriever tool
for chunk in root.call_tool("guider_retriever", "Cooling", top_k=3):
    print(chunk, end="")
```

### 개별 에이전트 직접 사용
```python
from agents.diagnosis_summarizer import DiagnosisSummarizer
from agents.op_history_summarizer import OperationHistorySummarizer
from agents.guide_provider import GuideProvider

# LLM 프로바이더 변경 가능: 'openai' | 'bedrock' | 'gauss' | 'gausso'
diagnosis = DiagnosisSummarizer(provider="gauss")
for chunk in diagnosis.summarize({"deviceType": "Washer", "diagnosisLists": []}, language="ko", stream=True):
    print(chunk, end="")

op_hist = OperationHistorySummarizer(provider="bedrock", region="ap-northeast-2")
for chunk in op_hist.summarize({"events": []}, language="both", stream=True):
    print(chunk, end="")

guide = GuideProvider(provider="openai")
for chunk in guide.provide("Diagnosis summary...", "Op summary...", language="en", stream=True):
    print(chunk, end="")
```

## LLM 프로바이더 설정
각 에이전트 생성자에 `provider`와 관련 파라미터를 전달하여 설정합니다.
- OpenAI: `provider="openai"`, 추가: `model`, `api_key`
- Bedrock: `provider="bedrock"`, 추가: `model_id`, `region`
- Gauss: `provider="gauss"`, 추가: `access_key`, `secret_key`
- GaussO: `provider="gausso"`, 추가: `access_key`, `secret_key`

예: 
```python
op_hist = OperationHistorySummarizer(provider="openai", model="gpt-4o-mini")
```

## 프롬프트 커스터마이징
- `agents/prompt_builder.py`의 `PromptBuilder`를 수정하거나 상속하여 프롬프트 규칙을 변경할 수 있습니다.
- 언어 파라미터는 `language`(기본 `ko`), `both` 지정 시 영문/국문 모두 출력하도록 힌트를 제공합니다.

## 가드레일(더미)
- `agents/guardrails.py`는 함수 시그니처만 있는 더미 클래스입니다.
- 실제 사용 시 `pre_guard`/`post_guard`에 검증·필터링 로직을 구현해 주십시오.

## MCP 스타일 확장
- Root 에이전트는 내부 `MCPRegistry`를 통해 에이전트/툴을 등록합니다.
```python
from agents.root_agent import RootAgent

root = RootAgent()
root.register_agent("my_agent", object())
root.register_tool("my_tool", lambda q: (y for y in ["hit1\n", "hit2\n"]))
print(root.list_capabilities())
```

## 스트리밍 동작
- OpenAI: SDK의 스트리밍 이벤트를 통해 청크를 방출합니다.
- Bedrock/Gauss/GaussO: 예제에서는 전체 응답 수신 후 줄 단위 청크로 쪼개는 유사 스트리밍을 제공합니다(실 서비스에서는 이벤트 스트리밍 연동 권장).

## 주의 사항
- API 키/자격증명을 코드에 하드코딩하지 말고 환경 변수로 주입해 주세요.
- 레퍼런스 스크립트의 하드코딩 키는 프로젝트 설명용 예시일 뿐 실제 배포 코드에서는 제거해야 합니다.

## License
This project is provided as-is for reference and prototyping.


