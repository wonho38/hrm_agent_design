# HRM Agent API 문서

## 개요

HRM Agent API는 가전 제품 진단, 운영 이력 분석, 고객 조치 가이드 생성, 이미지 분석 등의 기능을 RESTful API로 제공합니다.

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **Response Format**: JSON

## 인증

현재 버전에서는 인증이 필요하지 않습니다. 프로덕션 환경에서는 API 키 또는 OAuth 인증을 구현할 예정입니다.

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": {
    // 응답 데이터
  }
}
```

### 에러 응답
```json
{
  "success": false,
  "error": "에러 메시지"
}
```

## 엔드포인트

### 1. 헬스 체크

#### GET /health
시스템 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "service": "hrm_agent_api",
  "root_agent_initialized": true
}
```

---

### 2. 기능 조회

#### GET /api/capabilities
등록된 에이전트와 도구 목록을 조회합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "agents": {
      "diagnosis_summarizer": {
        "name": "diagnosis_summarizer",
        "description": "가전 진단 정보 요약",
        "capabilities": ["diagnosis_analysis", "streaming"]
      }
    },
    "tools": {
      "document_retriever": {
        "name": "document_retriever",
        "description": "문서 검색 도구",
        "inputSchema": {...}
      }
    }
  }
}
```

#### GET /api/mcp/manifest
MCP 매니페스트를 조회합니다.

**응답 예시:**
```json
{
  "version": "1.0.0",
  "name": "HRM Agent MCP Server",
  "description": "MCP server for HRM agent tools and capabilities",
  "tools": {...},
  "agents": {...}
}
```

---

### 3. 진단 요약

#### POST /api/diagnosis
진단 데이터를 분석하여 요약을 생성합니다.

**요청 본문:**
```json
{
  "analytics": {
    "deviceType": "AC",
    "diagnosisLists": [
      {
        "deviceSubType": "Wall Mount AC",
        "diagnosisResult": "Cooling Inefficiency",
        "diagnosisList": [
          {
            "title": "Temperature Sensor",
            "diagnosisLabel": "Normal",
            "diagnosisCode": "T001",
            "diagnosisResult": "OK",
            "diagnosisDescription": "센서 정상 작동"
          }
        ]
      }
    ]
  },
  "language": "ko",
  "llm_provider": "openai"
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "diagnosis": "에어컨 냉각 효율이 저하되었습니다. 온도 센서는 정상 작동하고 있으나...",
    "language": "ko",
    "llm_provider": "openai"
  }
}
```

#### POST /api/diagnosis/stream
진단 요약을 스트리밍으로 생성합니다.

**요청 본문:** 위와 동일

**응답 형식:** Server-Sent Events
```
data: {"chunk": "에어컨", "done": false}
data: {"chunk": " 냉각", "done": false}
data: {"chunk": " 효율이", "done": false}
...
data: {"chunk": "", "done": true}
```

---

### 4. 운영 이력 요약

#### POST /api/operation-history
운영 이력 데이터를 분석하여 요약을 생성합니다.

**요청 본문:**
```json
{
  "operation_history": {
    "events": [
      {
        "timestamp": "2024-01-01T10:00:00Z",
        "temperature": 22.5,
        "humidity": 45,
        "power_consumption": 150
      }
    ],
    "summary_period": "1_month"
  },
  "language": "ko",
  "llm_provider": "openai"
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "operation_history_summary": "지난 한 달간 에어컨 운영 상태는 전반적으로 양호합니다...",
    "language": "ko",
    "llm_provider": "openai"
  }
}
```

#### POST /api/operation-history/stream
운영 이력 요약을 스트리밍으로 생성합니다.

**요청 본문:** 위와 동일

**응답 형식:** Server-Sent Events (진단 요약과 동일)

---

### 5. 고객 조치 가이드 (한국어 전용)

#### POST /api/actions-guide
진단 요약을 기반으로 고객 조치 가이드를 생성합니다.

**요청 본문:**
```json
{
  "diagnosis_summary": "에어컨 냉각 효율이 저하되었습니다.",
  "category": "AC",
  "language": "ko"
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "actions_guide": "다음 조치 사항을 확인해 주세요:\n1. 필터 청소...",
    "category": "AC",
    "language": "ko",
    "llm_provider": "openai"
  }
}
```

#### POST /api/actions-guide/stream
고객 조치 가이드를 스트리밍으로 생성합니다.

**요청 본문:** 위와 동일

**응답 형식:** Server-Sent Events

---

### 6. 이미지 분석 (계획)

#### POST /api/image-analysis
이미지를 분석하여 결함을 탐지하고 증상을 분석합니다.

**요청 본문:**
```json
{
  "image_data": "base64_encoded_image_data",
  "filename": "ac_unit.jpg",
  "analysis_type": "DEFECT_DETECTION",
  "language": "ko"
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "img_001",
    "analysis_type": "DEFECT_DETECTION",
    "severity": "MEDIUM",
    "confidence_score": 0.85,
    "primary_symptoms": ["필터 오염", "먼지 축적"],
    "detailed_description": "에어컨 필터에 상당한 먼지가 축적되어 있습니다...",
    "defect_locations": [
      {
        "x": 100,
        "y": 150,
        "width": 200,
        "height": 100,
        "confidence": 0.9,
        "description": "필터 영역"
      }
    ],
    "recommendations": [
      "필터 청소 또는 교체",
      "정기적인 유지보수 스케줄 수립"
    ],
    "processing_time": 2.5
  }
}
```

#### POST /api/image-analysis/stream
이미지 분석을 스트리밍으로 수행합니다.

**응답 형식:** Server-Sent Events

---

### 7. 도구 호출

#### POST /api/tools/{tool_name}
등록된 도구를 호출합니다.

**경로 매개변수:**
- `tool_name`: 호출할 도구 이름 (예: `guider_retriever`)

**요청 본문:**
```json
{
  "args": ["검색어"],
  "kwargs": {
    "category_filter": "AC",
    "top_k": 3
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "tool_name": "guider_retriever",
    "result": "검색 결과 텍스트...",
    "args": ["검색어"],
    "kwargs": {"category_filter": "AC", "top_k": 3}
  }
}
```

#### POST /api/tools/{tool_name}/stream
등록된 도구를 스트리밍으로 호출합니다.

**응답 형식:** Server-Sent Events

#### POST /api/mcp/tools/{tool_name}
MCP 도구를 안전하게 호출합니다.

**요청 본문:** 위와 동일

**응답 예시:** 위와 동일

---

## 에러 코드

| HTTP 상태 코드 | 설명 |
|---------------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (필수 매개변수 누락, 잘못된 형식 등) |
| 404 | 리소스를 찾을 수 없음 (존재하지 않는 도구/엔드포인트) |
| 500 | 내부 서버 오류 (RootAgent 초기화 실패, LLM 오류 등) |
| 503 | 서비스 사용 불가 (외부 API 연결 실패) |

## 사용 예시

### cURL 예시

#### 진단 요약 생성
```bash
curl -X POST http://localhost:8000/api/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "analytics": {
      "deviceType": "AC",
      "diagnosisLists": [
        {
          "deviceSubType": "Wall Mount AC",
          "diagnosisResult": "Cooling Inefficiency"
        }
      ]
    },
    "language": "ko"
  }'
```

#### 스트리밍 진단 요약
```bash
curl -X POST http://localhost:8000/api/diagnosis/stream \
  -H "Content-Type: application/json" \
  -d '{
    "analytics": {
      "deviceType": "AC",
      "diagnosisLists": [{"diagnosisResult": "Cooling Issue"}]
    },
    "language": "ko"
  }'
```

### Python 예시

```python
import requests
import json

# 진단 요약 생성
url = "http://localhost:8000/api/diagnosis"
data = {
    "analytics": {
        "deviceType": "AC",
        "diagnosisLists": [
            {
                "deviceSubType": "Wall Mount AC",
                "diagnosisResult": "Cooling Inefficiency"
            }
        ]
    },
    "language": "ko",
    "llm_provider": "openai"
}

response = requests.post(url, json=data)
result = response.json()
print(result["data"]["diagnosis"])
```

### JavaScript 예시 (스트리밍)

```javascript
const eventSource = new EventSource('http://localhost:8000/api/diagnosis/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    analytics: {
      deviceType: "AC",
      diagnosisLists: [
        {
          deviceSubType: "Wall Mount AC",
          diagnosisResult: "Cooling Inefficiency"
        }
      ]
    },
    language: "ko"
  })
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.done) {
    eventSource.close();
    console.log('스트리밍 완료');
  } else {
    console.log('청크:', data.chunk);
  }
};

eventSource.onerror = function(event) {
  console.error('스트리밍 오류:', event);
  eventSource.close();
};
```

## 제한사항

### 1. 언어 지원
- 고객 조치 가이드는 한국어만 지원
- 다른 기능들은 한국어/영어 지원

### 2. 파일 크기
- 이미지 업로드: 최대 10MB
- JSON 요청: 최대 1MB

### 3. 속도 제한
- 현재 속도 제한 없음
- 프로덕션 환경에서는 구현 예정

### 4. 동시 요청
- 스트리밍 요청: 사용자당 최대 5개
- 일반 요청: 제한 없음

## 문제 해결

### 1. 연결 오류
- API 서버가 실행 중인지 확인 (`http://localhost:8000/health`)
- 방화벽 설정 확인

### 2. 응답 지연
- LLM 프로바이더 상태 확인
- 네트워크 연결 상태 확인

### 3. 스트리밍 중단
- 브라우저 호환성 확인 (Server-Sent Events 지원)
- 프록시/로드밸런서 설정 확인

## 변경 로그

### v1.0.0 (2024-01-01)
- 초기 API 릴리스
- 진단 요약, 운영 이력 요약, 고객 조치 가이드 기능
- 스트리밍 지원
- MCP 도구 호출 지원
