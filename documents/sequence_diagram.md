# HRM Agent 시스템 시퀀스 다이어그램

## 1. 진단 요약 생성 플로우

```mermaid
sequenceDiagram
    participant User as 사용자
    participant WebApp as 웹 애플리케이션<br/>(app.py:5000)
    participant API as HRM Agent API<br/>(hrm_agent_api.py:8000)
    participant RootAgent as RootAgent
    participant DiagAgent as DiagnosisSummarizer
    participant PromptBuilder as PromptBuilder
    participant LLM as LLM Provider
    participant Guardrail as Guardrail

    User->>WebApp: POST /api/stream/diagnosis/{item_id}
    WebApp->>WebApp: 데이터 조회 (json_data)
    WebApp->>API: POST /api/diagnosis/stream<br/>{"analytics": {...}, "language": "ko"}
    
    API->>RootAgent: run_diagnosis(analytics, language)
    RootAgent->>DiagAgent: summarize(analytics, language, stream=True)
    
    DiagAgent->>Guardrail: pre_guard(payload)
    Guardrail-->>DiagAgent: validated_payload
    
    DiagAgent->>DiagAgent: _build_diagnosis_text(analytics)
    DiagAgent->>PromptBuilder: build_diagnosis_prompt(device_type, diagnosis_text, provider, language)
    PromptBuilder-->>DiagAgent: prompt
    
    DiagAgent->>LLM: generate(prompt, stream=True)
    
    loop 스트리밍 응답
        LLM-->>DiagAgent: chunk
        DiagAgent-->>RootAgent: chunk
        RootAgent-->>API: chunk
        API-->>WebApp: SSE: data: {"chunk": "...", "done": false}
        WebApp-->>User: 실시간 스트리밍 표시
    end
    
    DiagAgent->>Guardrail: post_guard(complete_output)
    Guardrail-->>DiagAgent: processed_output
    
    API-->>WebApp: SSE: data: {"chunk": "", "done": true}
    WebApp-->>User: 완료 표시
```

## 2. 이미지 분석 플로우

```mermaid
sequenceDiagram
    participant User as 사용자
    participant WebApp as 웹 애플리케이션
    participant API as HRM Agent API
    participant RootAgent as RootAgent
    participant ImageAnalyzer as ImageAnalyzer
    participant Preprocessor as ImagePreprocessor
    participant VisionModel as VisionModelInterface
    participant Classifier as DefectClassifier
    participant Guardrail as ImageAnalysisGuardrail

    User->>WebApp: 이미지 업로드 + 분석 요청
    WebApp->>API: POST /api/image-analysis/stream<br/>{"image_data": "...", "analysis_type": "DEFECT_DETECTION"}
    
    API->>RootAgent: call_tool("image_analyzer", image_data, analysis_type)
    RootAgent->>ImageAnalyzer: analyze_single_image(image_data, filename, analysis_type)
    
    ImageAnalyzer->>Guardrail: pre_guard(payload)
    Guardrail-->>ImageAnalyzer: validated_payload
    
    ImageAnalyzer->>Preprocessor: validate_image(image_data, filename)
    Preprocessor-->>ImageAnalyzer: validation_result
    
    ImageAnalyzer->>Preprocessor: extract_metadata(image_data, filename)
    Preprocessor-->>ImageAnalyzer: image_metadata
    
    ImageAnalyzer->>Preprocessor: convert_to_base64(image_data, format)
    Preprocessor-->>ImageAnalyzer: base64_image
    
    ImageAnalyzer->>ImageAnalyzer: _build_analysis_prompt(analysis_type, language)
    ImageAnalyzer->>VisionModel: analyze_image(base64_image, prompt)
    VisionModel-->>ImageAnalyzer: raw_analysis_result
    
    ImageAnalyzer->>Classifier: classify_defect(raw_analysis_result)
    Classifier-->>ImageAnalyzer: defect_category, severity
    
    ImageAnalyzer->>Classifier: get_recommendations(defect_category, severity)
    Classifier-->>ImageAnalyzer: recommendations
    
    ImageAnalyzer->>ImageAnalyzer: _post_process_result(raw_result, metadata, analysis_type)
    ImageAnalyzer->>Guardrail: post_guard(analysis_result)
    Guardrail-->>ImageAnalyzer: processed_result
    
    ImageAnalyzer-->>RootAgent: AnalysisResult
    RootAgent-->>API: analysis_result
    API-->>WebApp: {"success": true, "data": {...}}
    WebApp-->>User: 분석 결과 표시
```

## 3. 고객 조치 가이드 생성 플로우

```mermaid
sequenceDiagram
    participant User as 사용자
    participant WebApp as 웹 애플리케이션
    participant API as HRM Agent API
    participant RootAgent as RootAgent
    participant GuideProvider as GuideProvider
    participant GuideRetriever as GuideRetriever
    participant ExternalAPI as Guide Retriever API<br/>(port:5001)
    participant PromptBuilder as PromptBuilder
    participant LLM as LLM Provider
    participant Guardrail as GuideGuardrail

    User->>WebApp: POST /api/stream/actions-guide/{item_id}<br/>{"diagnosis_summary": "...", "category": "AC"}
    WebApp->>API: POST /api/actions-guide/stream<br/>{"diagnosis_summary": "...", "category": "AC"}
    
    API->>RootAgent: run_actions_guide(diagnosis_summary, category, language="ko")
    
    Note over RootAgent: 한국어에서만 동작
    alt language == "ko"
        RootAgent->>GuideRetriever: stream(query=diagnosis_summary, category_filter=category)
        GuideRetriever->>ExternalAPI: POST /search<br/>{"query": "...", "category_filter": "AC", "top_k": 3}
        ExternalAPI-->>GuideRetriever: {"results": [...]}
        
        loop 문서 검색 결과
            GuideRetriever-->>RootAgent: document_chunk
        end
        
        RootAgent->>GuideProvider: provide_actions_guide(diagnosis_summary, retrieved_docs, language="ko")
        
        GuideProvider->>Guardrail: pre_guard(payload)
        Guardrail-->>GuideProvider: validated_payload
        
        GuideProvider->>PromptBuilder: build_actions_guide_prompt(diagnosis_summary, retrieved_docs, language)
        PromptBuilder-->>GuideProvider: prompt
        
        GuideProvider->>LLM: generate(prompt, stream=True)
        
        loop 스트리밍 응답
            LLM-->>GuideProvider: chunk
            GuideProvider-->>RootAgent: chunk
            RootAgent-->>API: chunk
            API-->>WebApp: SSE: data: {"chunk": "...", "done": false}
            WebApp-->>User: 실시간 가이드 표시
        end
        
        GuideProvider->>Guardrail: post_guard(complete_output)
        Guardrail-->>GuideProvider: processed_output (with readability report)
        GuideProvider-->>RootAgent: additional_content
        RootAgent-->>API: additional_content
        API-->>WebApp: SSE: data: {"chunk": "추가 내용", "done": false}
        
        API-->>WebApp: SSE: data: {"chunk": "", "done": true}
    else language != "ko"
        RootAgent-->>API: (no output - Korean only)
    end
    
    WebApp-->>User: 완료 표시
```

## 4. MCP 도구 호출 플로우

```mermaid
sequenceDiagram
    participant Client as 클라이언트
    participant API as HRM Agent API
    participant RootAgent as RootAgent
    participant MCPRegistry as MCPRegistry
    participant Tool as MCP Tool
    participant Metadata as ToolMetadata

    Client->>API: POST /api/mcp/tools/{tool_name}<br/>{"args": [...], "kwargs": {...}}
    
    API->>RootAgent: invoke_mcp_tool(tool_name, *args, **kwargs)
    RootAgent->>MCPRegistry: invoke_tool(tool_name, *args, **kwargs)
    
    MCPRegistry->>MCPRegistry: get_tool(tool_name)
    
    alt 도구가 존재하는 경우
        MCPRegistry->>Tool: __call__(*args, **kwargs)
        Tool-->>MCPRegistry: result
        MCPRegistry-->>RootAgent: result
        RootAgent-->>API: result
        API-->>Client: {"success": true, "data": {"result": "...", "tool_name": "..."}}
    else 도구가 존재하지 않는 경우
        MCPRegistry-->>RootAgent: ValueError("Tool not found")
        RootAgent-->>API: RuntimeError("Error invoking tool")
        API-->>Client: {"success": false, "error": "Tool 'xxx' not found"}
    end
```

## 5. 시스템 초기화 플로우

```mermaid
sequenceDiagram
    participant Server as 서버 시작
    participant API as HRM Agent API
    participant RootAgent as RootAgent
    participant MCPRegistry as MCPRegistry
    participant DiagAgent as DiagnosisSummarizer
    participant OpAgent as OperationHistorySummarizer
    participant GuideProvider as GuideProvider
    participant ImageAnalyzer as ImageAnalyzer
    participant GuideRetriever as GuideRetriever
    participant Config as configure.json

    Server->>API: python hrm_agent_api.py
    API->>API: initialize_root_agent()
    API->>RootAgent: RootAgent()
    
    RootAgent->>Config: _load_config()
    Config-->>RootAgent: configuration
    
    RootAgent->>RootAgent: _configure_langsmith()
    RootAgent->>MCPRegistry: MCPRegistry()
    MCPRegistry-->>RootAgent: registry
    
    RootAgent->>DiagAgent: DiagnosisSummarizer(provider, **kwargs)
    DiagAgent-->>RootAgent: diagnosis_agent
    RootAgent->>MCPRegistry: register_agent("diagnosis_summarizer", diagnosis_agent)
    
    RootAgent->>OpAgent: OperationHistorySummarizer(provider, **kwargs)
    OpAgent-->>RootAgent: op_history_agent
    RootAgent->>MCPRegistry: register_agent("op_history_summarizer", op_history_agent)
    
    RootAgent->>GuideProvider: GuideProvider(provider, **kwargs)
    GuideProvider-->>RootAgent: guide_agent
    RootAgent->>MCPRegistry: register_agent("guide_provider", guide_agent)
    
    RootAgent->>ImageAnalyzer: ImageAnalyzer(provider, **kwargs)
    ImageAnalyzer-->>RootAgent: image_agent
    RootAgent->>MCPRegistry: register_agent("image_analyzer", image_agent)
    
    RootAgent->>GuideRetriever: GuideRetriever(api_base_url)
    GuideRetriever-->>RootAgent: retriever_tool
    RootAgent->>MCPRegistry: register_tool("guider_retriever", retriever_tool.stream)
    RootAgent->>MCPRegistry: register_tool("document_retriever", retriever_tool.as_mcp_tool())
    
    RootAgent-->>API: initialized_agent
    API->>API: Flask app.run(host='0.0.0.0', port=8000)
    
    Note over API: API 서버 준비 완료<br/>http://localhost:8000
```

## 주요 플로우 설명

### 1. 진단 요약 생성
- 웹 애플리케이션에서 특정 제품 ID의 진단 데이터를 API 서버로 전송
- API 서버는 RootAgent를 통해 DiagnosisSummarizer를 호출
- 스트리밍 방식으로 실시간 요약 결과를 사용자에게 전달

### 2. 이미지 분석
- 사용자가 업로드한 이미지를 ImageAnalyzer가 분석
- 이미지 전처리, 메타데이터 추출, 비전 모델 분석, 결함 분류 과정을 거침
- 구조화된 분석 결과를 반환

### 3. 고객 조치 가이드 생성
- 진단 요약을 바탕으로 관련 문서를 검색
- 검색된 문서와 진단 요약을 결합하여 맞춤형 조치 가이드 생성
- 한국어에서만 동작하는 특화 기능

### 4. MCP 도구 호출
- MCP 레지스트리를 통한 안전한 도구 호출
- 도구 존재 여부 확인 및 오류 처리

### 5. 시스템 초기화
- 설정 파일 로드, 에이전트 등록, 도구 등록 과정
- 모든 컴포넌트의 체계적인 초기화
