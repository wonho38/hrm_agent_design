# Layered Architecture View

설계 요소를 계층(Layer)로 정리한 뷰입니다. 상위 계층은 오직 바로 아래 계층에만 의존하도록(단방향) 설계 가이드를 포함합니다.

```mermaid
flowchart TB
  %% LAYERS
  subgraph L1[Presentation Layer]
    Client[Client (Browser/App)]
    Flask[Flask API & SSE]
  end

  subgraph L2[Application/Orchestration Layer]
    RootAgent[RootAgent (Use-Case Orchestrator)]
    Router[Action Router / UseCase Facade]
  end

  subgraph L3[Domain Layer]
    Agents[Domain Services: Diagnosis/OpHistory/Guide/Image]
    Guardrails[Guardrails (Base & Domain-Specific)]
    PromptBuilder[PromptBuilder (Policies/Templates)]
    Policies[Domain Policies / Contracts]
  end

  subgraph L4[Integration Layer]
    MCP[MCP Registry & Tools]
    LLMClient[LLM Clients (OpenAI/Bedrock/Gauss)]
    ExtDocAPI[External Document API Adapter]
  end

  subgraph L5[Infrastructure Layer]
    Logging[Logging/Tracing/Metric Exporter]
    Secrets[Secrets/KMS]
    Cache[(Cache/SSE Buffer - optional)]
  end

  %% DEPENDENCIES (top -> bottom only)
  Client -->|HTTPS| Flask
  Flask --> RootAgent
  RootAgent --> Router
  Router --> Agents
  Router --> Guardrails
  Router --> PromptBuilder
  Agents --> Guardrails
  Agents --> PromptBuilder
  Guardrails --> Policies
  PromptBuilder --> Policies

  %% Integration calls
  Agents --> MCP
  Agents --> LLMClient
  Agents --> ExtDocAPI
  PromptBuilder -.-> LLMClient

  %% Infra (cross-cutting)
  Flask --> Logging
  RootAgent --> Logging
  Agents --> Logging
  MCP --> Logging
  LLMClient --> Logging
  ExtDocAPI --> Logging

  Flask --> Secrets
  RootAgent --> Secrets
  LLMClient --> Secrets
  MCP --> Secrets

  Flask <-->|pub/sub| Cache

  %% STYLES
  classDef layer fill:#f7f7ff,stroke:#667,stroke-width:1px
  classDef comp fill:#ffffff,stroke:#888,stroke-dasharray:3 2
  class L1,L2,L3,L4,L5 layer
  class Client,Flask,RootAgent,Router,Agents,Guardrails,PromptBuilder,Policies,MCP,LLMClient,ExtDocAPI,Logging,Secrets,Cache comp

  %% LEGEND
  subgraph Legend[Legend]
    direction TB
    U[Solid arrow: allowed dependency]
    C[Dashed arrow: template/policy influence]
    X[Cross-cutting: Logging/Secrets available to all]
  end
```

### 설계 규칙(요약)
- 상위 → 하위 단방향 의존(순환 금지). Application은 Domain만, Domain은 Integration만 의존.
- Presentation은 비즈니스 규칙을 갖지 않고, 오케스트레이션은 RootAgent/Router에서 담당.
- Guardrails/Policies는 Domain 규칙으로서 프롬프트·출력·에러 처리 정책을 표준화.
- Integration 계층은 외부 시스템(LLM, 문서 API, MCP Tool)을 어댑터로 캡슐화.
- Logging/Secrets/Cache는 횡단 관심사로 주입(injection)받아 사용.
