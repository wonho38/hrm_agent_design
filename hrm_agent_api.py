"""
HRM Agent API Server
RootAgent의 주요 기능들을 RESTful API로 제공하는 Flask 기반 API 서버
"""

import sys
import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import logging
from typing import Dict, Any, Optional, Generator
from agents.root_agent import RootAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# RootAgent 인스턴스 (전역으로 관리)
root_agent: Optional[RootAgent] = None

def load_config() -> Dict[str, Any]:
    """Load configuration from configure.json at project root."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "configure.json")
        if not os.path.exists(config_path):
            return {"language": "ko", "llm": {"provider": "openai"}}
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"language": "ko", "llm": {"provider": "openai"}}
        return data
    except Exception:
        return {"language": "ko", "llm": {"provider": "openai"}}

def initialize_root_agent():
    """RootAgent를 초기화합니다."""
    global root_agent
    try:
        root_agent = RootAgent()
        logger.info("RootAgent 초기화 완료")
    except Exception as e:
        logger.error(f"RootAgent 초기화 오류: {e}")
        root_agent = None

def create_error_response(message: str, status_code: int = 500) -> tuple:
    """에러 응답을 생성합니다."""
    return jsonify({"success": False, "error": message}), status_code

def create_success_response(data: Any) -> dict:
    """성공 응답을 생성합니다."""
    return jsonify({"success": True, "data": data})

@app.route('/health')
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "service": "hrm_agent_api",
        "root_agent_initialized": root_agent is not None
    })

@app.route('/api/capabilities')
def get_capabilities():
    """RootAgent의 기능 목록을 반환합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        capabilities = root_agent.list_capabilities()
        return create_success_response(capabilities)
        
    except Exception as e:
        logger.error(f"기능 목록 조회 중 오류: {e}")
        return create_error_response(f"기능 목록 조회 중 오류 발생: {str(e)}")

@app.route('/api/mcp/manifest')
def get_mcp_manifest():
    """MCP 매니페스트를 반환합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        manifest = root_agent.get_mcp_manifest()
        return Response(manifest, mimetype='application/json')
        
    except Exception as e:
        logger.error(f"MCP 매니페스트 조회 중 오류: {e}")
        return create_error_response(f"MCP 매니페스트 조회 중 오류 발생: {str(e)}")

@app.route('/api/diagnosis', methods=['POST'])
def run_diagnosis():
    """진단 요약을 생성합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        analytics = data.get('analytics')
        if not analytics:
            return create_error_response("analytics 데이터가 필요합니다.", 400)
        
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
        agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
        
        # 진단 결과 수집
        diagnosis_result = ""
        for chunk in agent.run_diagnosis(analytics, language=language):
            diagnosis_result += chunk
        
        return create_success_response({
            "diagnosis": diagnosis_result,
            "language": language,
            "llm_provider": llm_provider or agent.provider
        })
        
    except Exception as e:
        logger.error(f"진단 요약 생성 중 오류: {e}")
        return create_error_response(f"진단 요약 생성 중 오류 발생: {str(e)}")

@app.route('/api/diagnosis/stream', methods=['POST'])
def stream_diagnosis():
    """진단 요약을 스트리밍으로 생성합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        analytics = data.get('analytics')
        if not analytics:
            return create_error_response("analytics 데이터가 필요합니다.", 400)
        
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        def generate():
            try:
                # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
                agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
                
                # 초기 하트비트 전송
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"
                
                # 스트리밍으로 진단 요약 생성
                for chunk in agent.run_diagnosis(analytics, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 진단 요약 생성 중 오류: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 진단 요약 생성 중 오류: {e}")
        return create_error_response(f"스트리밍 진단 요약 생성 중 오류 발생: {str(e)}")

@app.route('/api/operation-history', methods=['POST'])
def run_operation_history():
    """운영 이력 요약을 생성합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        operation_history = data.get('operation_history')
        if not operation_history:
            return create_error_response("operation_history 데이터가 필요합니다.", 400)
        
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
        agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
        
        # 운영 이력 요약 결과 수집
        history_result = ""
        for chunk in agent.run_op_history(operation_history, language=language):
            history_result += chunk
        
        return create_success_response({
            "operation_history_summary": history_result,
            "language": language,
            "llm_provider": llm_provider or agent.provider
        })
        
    except Exception as e:
        logger.error(f"운영 이력 요약 생성 중 오류: {e}")
        return create_error_response(f"운영 이력 요약 생성 중 오류 발생: {str(e)}")

@app.route('/api/operation-history/stream', methods=['POST'])
def stream_operation_history():
    """운영 이력 요약을 스트리밍으로 생성합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        operation_history = data.get('operation_history')
        if not operation_history:
            return create_error_response("operation_history 데이터가 필요합니다.", 400)
        
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        def generate():
            try:
                # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
                agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
                
                # 초기 하트비트 전송
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"
                
                # 스트리밍으로 운영 이력 요약 생성
                for chunk in agent.run_op_history(operation_history, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 운영 이력 요약 생성 중 오류: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 운영 이력 요약 생성 중 오류: {e}")
        return create_error_response(f"스트리밍 운영 이력 요약 생성 중 오류 발생: {str(e)}")

@app.route('/api/actions-guide', methods=['POST'])
def run_actions_guide():
    """고객 조치 가이드를 생성합니다 (한국어 전용)."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        diagnosis_summary = data.get('diagnosis_summary')
        if not diagnosis_summary:
            return create_error_response("diagnosis_summary가 필요합니다.", 400)
        
        category = data.get('category', '')
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        if language.lower() != 'ko':
            return create_error_response("한국어에서만 지원됩니다.", 400)
        
        # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
        agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
        
        # 고객 조치 가이드 결과 수집
        guide_result = ""
        for chunk in agent.run_actions_guide(diagnosis_summary, category=category, language=language):
            guide_result += chunk
        
        return create_success_response({
            "actions_guide": guide_result,
            "category": category,
            "language": language,
            "llm_provider": llm_provider or agent.provider
        })
        
    except Exception as e:
        logger.error(f"고객 조치 가이드 생성 중 오류: {e}")
        return create_error_response(f"고객 조치 가이드 생성 중 오류 발생: {str(e)}")

@app.route('/api/actions-guide/stream', methods=['POST'])
def stream_actions_guide():
    """고객 조치 가이드를 스트리밍으로 생성합니다 (한국어 전용)."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json()
        if not data:
            return create_error_response("JSON 데이터가 필요합니다.", 400)
        
        diagnosis_summary = data.get('diagnosis_summary')
        if not diagnosis_summary:
            return create_error_response("diagnosis_summary가 필요합니다.", 400)
        
        category = data.get('category', '')
        language = data.get('language', 'ko')
        llm_provider = data.get('llm_provider')
        
        if language.lower() != 'ko':
            return create_error_response("한국어에서만 지원됩니다.", 400)
        
        def generate():
            try:
                # LLM provider가 지정된 경우 새로운 RootAgent 인스턴스 생성
                agent = RootAgent(provider_override=llm_provider) if llm_provider else root_agent
                
                # 초기 하트비트 전송
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"
                
                # 스트리밍으로 고객 조치 가이드 생성
                for chunk in agent.run_actions_guide(diagnosis_summary, category=category, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 고객 조치 가이드 생성 중 오류: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 고객 조치 가이드 생성 중 오류: {e}")
        return create_error_response(f"스트리밍 고객 조치 가이드 생성 중 오류 발생: {str(e)}")

@app.route('/api/tools/<tool_name>', methods=['POST'])
def call_tool(tool_name: str):
    """등록된 도구를 호출합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        # 도구 호출 결과 수집
        tool_result = ""
        for chunk in root_agent.call_tool(tool_name, *args, **kwargs):
            tool_result += chunk
        
        return create_success_response({
            "tool_name": tool_name,
            "result": tool_result,
            "args": args,
            "kwargs": kwargs
        })
        
    except Exception as e:
        logger.error(f"도구 '{tool_name}' 호출 중 오류: {e}")
        return create_error_response(f"도구 '{tool_name}' 호출 중 오류 발생: {str(e)}")

@app.route('/api/tools/<tool_name>/stream', methods=['POST'])
def stream_tool(tool_name: str):
    """등록된 도구를 스트리밍으로 호출합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        def generate():
            try:
                # 초기 하트비트 전송
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"
                
                # 스트리밍으로 도구 호출
                for chunk in root_agent.call_tool(tool_name, *args, **kwargs):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 도구 '{tool_name}' 호출 중 오류: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 도구 '{tool_name}' 호출 중 오류: {e}")
        return create_error_response(f"스트리밍 도구 '{tool_name}' 호출 중 오류 발생: {str(e)}")

@app.route('/api/mcp/tools/<tool_name>', methods=['POST'])
def invoke_mcp_tool(tool_name: str):
    """MCP 도구를 안전하게 호출합니다."""
    try:
        if not root_agent:
            return create_error_response("RootAgent가 초기화되지 않았습니다.", 500)
        
        data = request.get_json() or {}
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        # MCP 도구 호출
        result = root_agent.invoke_mcp_tool(tool_name, *args, **kwargs)
        
        return create_success_response({
            "tool_name": tool_name,
            "result": result,
            "args": args,
            "kwargs": kwargs
        })
        
    except Exception as e:
        logger.error(f"MCP 도구 '{tool_name}' 호출 중 오류: {e}")
        return create_error_response(f"MCP 도구 '{tool_name}' 호출 중 오류 발생: {str(e)}")

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return create_error_response("요청한 엔드포인트를 찾을 수 없습니다.", 404)

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"Internal server error: {error}")
    return create_error_response("내부 서버 오류가 발생했습니다.", 500)

if __name__ == '__main__':
    # 서버 시작 시 RootAgent 초기화
    initialize_root_agent()
    
    # Flask 서버 실행
    logger.info("HRM Agent API 서버를 시작합니다...")
    logger.info("API 엔드포인트: http://localhost:8000")
    
    app.run(
        host='0.0.0.0',  # 모든 네트워크 인터페이스에서 접근 허용
        port=8000,       # 포트 8000 사용 (기존 app.py와 구분)
        debug=True,      # 디버그 모드 활성화
        threaded=True    # 멀티스레드 지원
    )
