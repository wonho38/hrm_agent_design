# Architecture Views

이 문서는 시스템을 설명하는 5가지 주요 아키텍처 뷰를 담고 있습니다.

---

## 1. 컨텍스트(시스템 경계) 뷰

```mermaid
flowchart TB
    User[사용자/클라이언트] -->|HTTP REST/SSE| Flask[Flask App API]
    subgraph System["HRM Agent System"]
      Flask --> RootAgent[RootAgent]
      RootAgent --> MCP[MCP Registry]
      RootAgent --> Agents[AI Agents<br/>Diagnosis, OpHistory, Guide]
      Agents --> Guardrails[Guardrails<br/>Base/Derived]
      RootAgent --> Logger[Logger]
    end

    MCP -->|문서 검색| ExtDocAPI[외부 문서 API]
    Agents -->|프롬프트/생성| LLM[LLM Provider<br/>OpenAI/Bedrock/Gauss]
    Logger --> Obs[모니터링/로그 스토리지]

    classDef ext fill:#fff,stroke:#555,stroke-width:1px
    classDef sys fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    class ExtDocAPI,LLM,Obs,User ext
    class Flask,RootAgent,MCP,Agents,Guardrails,Logger sys
```

---

## 2. C&C(컴포넌트 & 커넥터) / 런타임 뷰

```mermaid
flowchart LR
    User[사용자] -->|GET/POST| Flask[Flask App]
    Flask --> RootAgent[RootAgent]
    RootAgent --> DiagAgent[DiagnosisSummarizer]
    RootAgent --> OpAgent[OperationHistorySummarizer]
    RootAgent --> GuideProvider[GuideProvider]
    RootAgent --> MCP[MCP Registry]
    MCP --> GuideRetriever[Document Retriever<br/>MCP Tool]
    GuideRetriever -->|HTTP| ExtDocAPI[외부 문서 API]

    DiagAgent --> Guardrails[Guardrails]
    OpAgent --> Guardrails
    GuideProvider --> Guardrails

    DiagAgent -->|stream/generate| LLM[LLM Provider]
    OpAgent -->|stream/generate| LLM
    GuideProvider -->|stream/generate| LLM

    RootAgent --> Logger[Logger]

    classDef svc fill:#eef,stroke:#667,stroke-width:2px
    classDef tool fill:#efe,stroke:#484,stroke-width:2px
    classDef ext fill:#fff,stroke:#555,stroke-width:1px
    class Flask,RootAgent,DiagAgent,OpAgent,GuideProvider,Guardrails,Logger,LLM,MCP svc
    class GuideRetriever tool
    class ExtDocAPI,User ext
```

---

## 3. 모듈(정적 구조) 뷰

```mermaid
flowchart TB
    subgraph app["Application Layer"]
      FlaskApp[app.py<br/>Flask Application]
      RootAgentMod[agents/root_agent.py<br/>Agent Orchestration]
      Config[configure.json<br/>Configuration]
    end

    subgraph agents["AI Agents Layer"]
      Diag[agents/diagnosis_summarizer.py<br/>Diagnosis Agent]
      OpHist[agents/op_history_summarizer.py<br/>Operation History Agent]
      GuideProv[agents/guide_provider.py<br/>Guide Provider]
      ImageAnalyzer[agents/image_analyzer.py<br/>Image Analyzer]
    end

    subgraph guardrails["Guardrails Layer"]
      BaseGR[agents/guardrails.py<br/>Base Guardrail]
      Readability[agents/readability_checker.py<br/>Readability Checker]
    end

    subgraph tools["Tools Layer"]
      MCPReg[agents/mcp.py<br/>MCP Registry]
      GuideRet[agents/retriever.py<br/>Guide Retriever]
      PromptBuilder[agents/prompt_builder.py<br/>Prompt Builder]
    end

    subgraph llm["LLM Integration Layer"]
      LLMProviders[agents/llm_providers.py<br/>LLM Provider Factory]
      OpenAIClient[agents/llm_client_openai.py<br/>OpenAI Client]
      BedrockClient[agents/llm_client_bedrock.py<br/>Bedrock Client]
      GaussClient[agents/llm_client_gauss.py<br/>Gauss Client]
    end

    FlaskApp --> RootAgentMod
    RootAgentMod --> Diag
    RootAgentMod --> OpHist
    RootAgentMod --> GuideProv
    RootAgentMod --> ImageAnalyzer
    RootAgentMod --> MCPReg
    MCPReg --> GuideRet
    Diag --> BaseGR
    OpHist --> BaseGR
    GuideProvider --> BaseGR
    ImageAnalyzer --> BaseGR
    BaseGR --> Readability
    GuideProv --> PromptBuilder
    Diag --> PromptBuilder
    OpHist --> PromptBuilder
    ImageAnalyzer --> PromptBuilder
    Diag --> LLMProviders
    OpHist --> LLMProviders
    GuideProvider --> LLMProviders
    ImageAnalyzer --> LLMProviders
    LLMProviders --> OpenAIClient
    LLMProviders --> BedrockClient
    LLMProviders --> GaussClient
    RootAgentMod --> Config

    classDef appLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef agentLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef guardLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef toolLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef llmLayer fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class FlaskApp,RootAgentMod,Config appLayer
    class Diag,OpHist,GuideProv,ImageAnalyzer agentLayer
    class BaseGR,Readability guardLayer
    class MCPReg,GuideRet,PromptBuilder toolLayer
    class LLMProviders,OpenAIClient,BedrockClient,GaussClient llmLayer
```

---

## 4. 주요 시나리오(시퀀스) 뷰

```mermaid
sequenceDiagram
    participant U as 사용자
    participant F as Flask
    participant R as RootAgent
    participant G as Guardrails
    participant L as LLM
    participant M as MCP Registry
    participant D as Ext Doc API

    rect rgb(240,248,255)
    Note over U,L: A 진단 스트리밍
    U->>F: GET /api/stream/diagnosis/{id}
    F->>R: run_diagnosis(stream=True)
    R->>G: pre_guard / post_guard
    R->>L: 생성 요청 (stream)
    L-->>U: 진단 결과 스트림
    end

    rect rgb(248,255,240)
    Note over U,L: B 운영 이력 요약
    U->>F: GET /api/stream/operation-history/{id}
    F->>R: run_op_history(stream=True)
    R->>G: pre/post_guard
    R->>L: 요약 생성
    L-->>U: 요약 스트림
    end

    rect rgb(255,248,240)
    Note over U,L: C 문서 검색 + 실행 가이드
    U->>F: POST /api/generate-guide
    F->>R: run_actions_guide()
    R->>M: invoke_tool(document_retriever)
    M->>D: 외부 문서 검색
    D-->>M: 검색 결과
    R->>G: pre/post_guard
    R->>L: 가이드 생성 (stream)
    L-->>U: 실행 가이드 스트림
    end
```

---

## 5. 배포/인프라(Deployment/Allocation) 뷰

```mermaid
flowchart TB
    subgraph ClientNet["클라이언트 네트워크"]
      Browser[사용자 브라우저]
    end

    subgraph DMZ["DMZ / API 게이트웨이"]
      Ingress[API Gateway / Nginx]
    end

    subgraph AppVPC["App VPC"]
      subgraph ASG["App Tier (무상태, 수평확장)"]
        FlaskPod1[Flask+RootAgent Pod 1]
        FlaskPod2[Flask+RootAgent Pod 2]
      end
      Redis[(Redis Cache<br/>SSE/세션)]
      LoggerSidecar[(로깅 사이드카)]
    end

    subgraph ExtServices["외부 서비스"]
      DocAPI[외부 문서 API]
      LLM1[LLM Provider A]
      LLM2[LLM Provider B]
    end

    subgraph Ops["관측성/보안"]
      LogStore[(Log Storage)]
      Metrics[(Metrics/Tracing)]
      KMS[(Secret/KMS)]
    end

    Browser -->|HTTPS| Ingress
    Ingress -->|HTTP/gRPC| FlaskPod1
    Ingress -->|HTTP/gRPC| FlaskPod2

    FlaskPod1 <-->|pub/sub| Redis
    FlaskPod1 -->|SSE stream| Browser
    FlaskPod1 -->|HTTPS| DocAPI
    FlaskPod1 -->|HTTPS| LLM1
    FlaskPod1 -->|HTTPS| LLM2
    FlaskPod1 --> LoggerSidecar
    LoggerSidecar --> LogStore
    FlaskPod1 --> Metrics
    FlaskPod1 --> KMS

    classDef client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef dmz fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef app fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef ext fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef ops fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class Browser client
    class Ingress dmz
    class FlaskPod1,FlaskPod2,Redis,LoggerSidecar app
    class DocAPI,LLM1,LLM2 ext
    class LogStore,Metrics,KMS ops
```

---

## 6. 이미지 분석 시나리오

```mermaid
sequenceDiagram
    participant U as 사용자
    participant F as Flask
    participant R as RootAgent
    participant IA as ImageAnalyzer
    participant G as ImageGuardrail
    participant V as VisionModel
    participant L as LLM Provider

    U->>F: POST /api/analyze/image
    F->>R: analyze_product_image()
    R->>IA: analyze_single_image()
    IA->>G: pre_guard(validation)
    G-->>IA: validated_request
    
    IA->>IA: preprocess_image()
    IA->>V: analyze_image()
    V->>L: Vision LLM API 호출
    L-->>V: analysis_result
    V-->>IA: raw_result
    
    IA->>G: post_guard(readability)
    G-->>IA: enhanced_result
    IA-->>R: AnalysisResult
    R-->>F: structured_result
    F-->>U: JSON Response
```

---

## 다이어그램 렌더링 가이드

### Mermaid 뷰어 사용법:
1. **온라인 뷰어**: https://mermaid.live/
2. **VS Code 확장**: Mermaid Preview
3. **GitHub**: 마크다운에서 자동 렌더링

### 주요 문법 규칙:
- 노드명에 특수문자 사용 시 대괄호 `[]` 사용
- 서브그래프는 `subgraph name["표시명"]` 형식
- 화살표 라벨은 `|라벨|` 형식
- 클래스 정의는 `classDef` 사용

### 문제 해결:
- **노드명 충돌**: 고유한 이름 사용
- **특수문자**: 이스케이프 처리
- **긴 텍스트**: `<br/>` 사용하여 줄바꿈
- **한글**: UTF-8 인코딩 확인
