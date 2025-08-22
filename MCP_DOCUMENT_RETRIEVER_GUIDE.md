# Document Retriever MCP 사용 가이드

## 개요

Document Retriever를 MCP(Model Context Protocol) 도구로 사용하는 방법을 설명합니다. MCP는 AI 모델과 외부 도구 간의 표준화된 통신 프로토콜로, 구조화된 입출력과 메타데이터를 제공합니다.

## 🚀 주요 기능

- **표준화된 인터페이스**: MCP 표준을 따르는 일관된 도구 인터페이스
- **자동 스키마 검증**: 입력/출력 데이터의 자동 검증
- **메타데이터 지원**: 도구의 기능과 사용법을 설명하는 메타데이터
- **오류 처리**: 내장된 오류 처리 및 복구 메커니즘
- **도구 발견**: 등록된 모든 도구의 자동 발견 및 나열

## 📋 MCP 도구 등록 방법

### 1. 기본 등록 (RootAgent 사용)

```python
from agents.root_agent import RootAgent

# RootAgent 초기화 시 자동으로 MCP 도구 등록됨
root_agent = RootAgent()

# 등록된 도구 확인
capabilities = root_agent.list_capabilities()
print(capabilities["tools"])
```

### 2. 수동 등록 (직접 레지스트리 사용)

```python
from agents.mcp import MCPRegistry
from agents.retriever import GuideRetriever

# 레지스트리 생성
registry = MCPRegistry()

# GuideRetriever 인스턴스 생성
retriever = GuideRetriever(api_base_url="http://localhost:5001")

# MCP 도구로 등록
registry.register_tool(
    "document_retriever",
    retriever.as_mcp_tool(),
    metadata=retriever.get_mcp_metadata()
)
```

## 🎯 MCP 도구 사용 방법

### 1. RootAgent를 통한 사용

```python
# 도구 호출
result = root_agent.invoke_mcp_tool(
    "document_retriever",
    query="서버 장애 해결 방법",
    top_k=3,
    category_filter="troubleshooting"
)

# 결과 확인
print(f"총 {result['total_found']}개 문서 발견")
for doc in result['results']:
    print(doc)
```

### 2. 직접 도구 호출

```python
# 도구 가져오기
tool = registry.get_tool("document_retriever")

# 도구 호출
result = tool(
    query="데이터베이스 백업 방법",
    top_k=5
)

# 결과 처리
if "error" in result:
    print(f"오류 발생: {result['error']}")
else:
    print(f"검색 완료: {result['total_found']}개 결과")
```

## 📊 입력/출력 스키마

### 입력 스키마

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "검색할 쿼리 문자열",
      "required": true
    },
    "top_k": {
      "type": "integer",
      "description": "반환할 결과 수 (기본값: 3)",
      "minimum": 1,
      "maximum": 10,
      "default": 3
    },
    "category_filter": {
      "type": "string",
      "description": "카테고리 필터 (선택사항)",
      "enum": ["troubleshooting", "maintenance", "configuration", "user_guide"]
    }
  }
}
```

### 출력 스키마

```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "string",
        "description": "제목, 요약, URL이 포함된 문서 스니펫"
      }
    },
    "total_found": {
      "type": "integer",
      "description": "발견된 총 문서 수"
    },
    "query": {
      "type": "string",
      "description": "검색에 사용된 쿼리"
    },
    "top_k": {
      "type": "integer",
      "description": "요청된 결과 수"
    },
    "category_filter": {
      "type": "string",
      "description": "사용된 카테고리 필터"
    }
  }
}
```

## ⚙️ 설정 방법

### configure.json 설정

```json
{
  "retriever": {
    "api_base_url": "http://your-api-server:5001"
  }
}
```

### 환경별 설정 예시

```json
// 개발 환경
{
  "retriever": {
    "api_base_url": "http://localhost:5001"
  }
}

// 운영 환경
{
  "retriever": {
    "api_base_url": "http://production-api:5001"
  }
}
```

## 🔍 메타데이터 활용

### 도구 메타데이터 확인

```python
# 특정 도구의 메타데이터 가져오기
metadata = registry.get_tool_metadata("document_retriever")

print(f"도구 이름: {metadata.name}")
print(f"설명: {metadata.description}")
print(f"입력 스키마: {metadata.input_schema}")
print(f"출력 스키마: {metadata.output_schema}")
```

### MCP 매니페스트 생성

```python
# 전체 MCP 매니페스트 생성
manifest = registry.to_mcp_manifest()

# JSON 파일로 저장
with open("mcp_manifest.json", "w", encoding="utf-8") as f:
    f.write(manifest)
```

## 🛠️ 고급 사용법

### 1. 커스텀 오류 처리

```python
try:
    result = root_agent.invoke_mcp_tool(
        "document_retriever",
        query="검색어"
    )
    
    if "error" in result:
        # 도구 내부 오류 처리
        print(f"검색 실패: {result['error']}")
    else:
        # 성공적인 결과 처리
        process_results(result['results'])
        
except ValueError as e:
    # 도구를 찾을 수 없는 경우
    print(f"도구 오류: {e}")
except RuntimeError as e:
    # 도구 실행 오류
    print(f"실행 오류: {e}")
```

### 2. 배치 검색

```python
queries = [
    "서버 모니터링",
    "데이터베이스 최적화",
    "네트워크 보안"
]

results = []
for query in queries:
    result = root_agent.invoke_mcp_tool(
        "document_retriever",
        query=query,
        top_k=2
    )
    results.append(result)

# 모든 결과 통합 처리
all_documents = []
for result in results:
    if "error" not in result:
        all_documents.extend(result['results'])
```

### 3. 카테고리별 검색

```python
categories = ["troubleshooting", "maintenance", "configuration"]

for category in categories:
    print(f"\n=== {category} 카테고리 검색 ===")
    result = root_agent.invoke_mcp_tool(
        "document_retriever",
        query="시스템 관리",
        top_k=3,
        category_filter=category
    )
    
    if result.get('total_found', 0) > 0:
        for i, doc in enumerate(result['results'], 1):
            print(f"{i}. {doc[:100]}...")
```

## 🔄 스트리밍 vs MCP 비교

### 스트리밍 방식 (기존)

```python
# 스트리밍 도구 사용
streaming_tool = root_agent.tools["guider_retriever"]
for chunk in streaming_tool(query="검색어", top_k=3):
    print(chunk)  # 실시간 스트림 출력
```

### MCP 방식 (새로운)

```python
# MCP 도구 사용
result = root_agent.invoke_mcp_tool(
    "document_retriever",
    query="검색어",
    top_k=3
)
print(result)  # 구조화된 결과 반환
```

| 특징 | 스트리밍 방식 | MCP 방식 |
|------|---------------|----------|
| 출력 형태 | 실시간 스트림 | 구조화된 객체 |
| 오류 처리 | 수동 처리 필요 | 자동 처리 |
| 메타데이터 | 없음 | 완전한 스키마 |
| 검증 | 수동 검증 | 자동 검증 |
| 호환성 | 기존 코드용 | 표준 준수 |

## 🚨 문제 해결

### 1. API 연결 실패

```python
result = root_agent.invoke_mcp_tool("document_retriever", query="test")

if "error" in result:
    if "연결" in result["error"]:
        print("💡 해결 방법:")
        print("1. API 서버가 실행 중인지 확인")
        print("2. configure.json의 api_base_url 확인")
        print("3. 방화벽/네트워크 설정 확인")
```

### 2. 스키마 검증 오류

```python
# 잘못된 매개변수
try:
    result = root_agent.invoke_mcp_tool(
        "document_retriever",
        query="",  # 빈 쿼리
        top_k=15   # 최대값 초과
    )
except Exception as e:
    print(f"스키마 검증 실패: {e}")
```

### 3. 도구 등록 확인

```python
# 등록된 도구 목록 확인
tools = root_agent.list_capabilities()["tools"]
if "document_retriever" not in tools:
    print("❌ Document Retriever가 등록되지 않음")
    print("💡 RootAgent 초기화 과정을 확인하세요")
```

## 📚 참고 자료

- **MCP 표준**: [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- **설정 파일**: `configure.json`
- **예제 코드**: `simple_mcp_example.py`, `mcp_retriever_examples.py`
- **소스 코드**: `agents/mcp.py`, `agents/retriever.py`

## 🎯 베스트 프랙티스

1. **항상 오류 처리**: MCP 도구 호출 시 항상 오류 상황을 고려
2. **메타데이터 활용**: 도구의 스키마를 확인하여 올바른 매개변수 사용
3. **설정 관리**: 환경별로 다른 API 엔드포인트 설정
4. **배치 처리**: 여러 검색 시 효율적인 배치 처리 구현
5. **결과 캐싱**: 동일한 쿼리의 결과는 캐싱하여 성능 향상

---

이 가이드를 통해 Document Retriever를 MCP 도구로 효과적으로 활용할 수 있습니다. 추가 질문이나 문제가 있으면 언제든 문의해주세요! 🚀
