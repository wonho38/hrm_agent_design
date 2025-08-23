import sys
import requests
from flask import Flask, render_template, jsonify, send_from_directory, request, Response, stream_template
import json
import os
from flask_cors import CORS
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from configure.json at project root."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "configure.json")
        if not os.path.exists(config_path):
            return {"retriever": {"api_base_url": "http://localhost:5001"}}
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"retriever": {"api_base_url": "http://localhost:5001"}}
        return data
    except Exception:
        return {"retriever": {"api_base_url": "http://localhost:5001"}}

app = Flask(__name__)
CORS(app)  # CORS 설정으로 브라우저에서 JSON 데이터 요청 허용

# Configuration 로드
config = load_config()
retriever_config = config.get("retriever", {})

# API 서버 설정
API_BASE_URL = retriever_config.get("api_base_url", "http://localhost:5001")
HRM_AGENT_API_URL = "http://localhost:8000"  # HRM Agent API 서버 URL
logger.info(f"[App] GuideRetriever API URL configured: {API_BASE_URL}")
logger.info(f"[App] HRM Agent API URL configured: {HRM_AGENT_API_URL}")

# JSON 데이터를 메모리에 로드 (서버 시작 시 한 번만 로드)
json_data = []

def load_json_data():
    """sample_original.json 파일을 로드합니다."""
    global json_data
    try:
        json_file_path = os.path.join('data', 'sample_original.json')
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"JSON 데이터 로드 완료: {len(json_data)}개 항목")
        else:
            print(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
    except Exception as e:
        print(f"JSON 데이터 로드 오류: {e}")
        json_data = []

def check_api_server_health():
    """HRM Agent API 서버의 상태를 확인합니다."""
    try:
        response = requests.get(f"{HRM_AGENT_API_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API 서버 상태 확인 실패: {e}")
        return False

def truncate_json_data(data, max_length=1000):
    """JSON 데이터를 문자열로 변환하고 필요시 길이를 제한합니다."""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    if len(json_str) > max_length:
        truncated_str = json_str[:max_length] + f"\n\n... (데이터가 길어서 앞부분 {max_length}자만 표시됩니다. 전체 길이: {len(json_str)}자)"
        return truncated_str, True  # True indicates truncation occurred
    else:
        return json_str, False  # False indicates no truncation

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/data-review')
def data_review():
    """데이터 리뷰 페이지를 렌더링합니다."""
    return render_template('data_review.html')

@app.route('/api/data')
def get_all_data():
    """전체 JSON 데이터를 반환합니다."""
    return jsonify(json_data)

@app.route('/api/data/<string:item_id>')
def get_item_data(item_id):
    """특정 ID의 데이터를 반환합니다."""
    try:
        # 선택된 ID에 해당하는 데이터 찾기
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        
        if item_data:
            return jsonify(item_data)
        else:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': f'데이터 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/api/products')
def get_products():
    """사용 가능한 제품 타입과 해당 ID 목록을 반환합니다."""
    try:
        products = {}
        
        for item in json_data:
            item_id = item.get('id', '')
            device_type = item.get('analytics', {}).get('deviceType', '')
            
            # ID에서 제품 타입 추출
            if '_' in item_id:
                product_type = item_id.split('_')[0]
                
                if product_type not in products:
                    products[product_type] = []
                
                products[product_type].append(item_id)
        
        # 각 제품 타입별로 ID 정렬
        for product_type in products:
            products[product_type].sort()
        
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': f'제품 목록 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/api/diagnosis/<string:item_id>')
def get_diagnosis_data(item_id):
    """특정 ID의 진단 데이터만 반환합니다."""
    try:
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        
        if item_data:
            diagnosis_data = item_data.get('analytics', {}).get('diagnosisLists', [])
            return jsonify(diagnosis_data)
        else:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': f'진단 데이터 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/api/operation-history/<string:item_id>')
def get_operation_history(item_id):
    """특정 ID의 운영 이력 데이터만 반환합니다."""
    try:
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        
        if item_data:
            # 운영 이력 데이터는 root level의 operation_history에 있음
            operation_history = item_data.get('operation_history', {})
            
            # 데이터 길이 확인 및 필요시 잘라내기 (5000자로 증가)
            json_str, was_truncated = truncate_json_data(operation_history, 5000)
            
            if was_truncated:
                return json_str, 200, {'Content-Type': 'text/plain; charset=utf-8'}
            else:
                return jsonify(operation_history)
        else:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': f'운영 이력 데이터 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/data/<path:filename>')
def serve_data_files(filename):
    """data 폴더의 파일들을 직접 서빙합니다."""
    return send_from_directory('data', filename)

@app.route('/api/stream/diagnosis/<string:item_id>')
def stream_diagnosis(item_id):
    """특정 ID의 진단 데이터를 스트리밍으로 요약합니다."""
    try:
        # HRM Agent API 서버 상태 확인
        if not check_api_server_health():
            return jsonify({'error': 'HRM Agent API 서버에 연결할 수 없습니다.'}), 503
            
        # 언어 및 LLM 설정 가져오기
        language = request.args.get('language', 'ko')
        llm_provider = request.args.get('llm', 'openai')
        
        # 선택된 ID에 해당하는 데이터 찾기
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        
        if not item_data:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404
            
        # analytics 데이터 추출
        analytics = item_data.get('analytics', {})
        
        def generate():
            try:
                # HRM Agent API 서버에 스트리밍 요청
                api_payload = {
                    "analytics": analytics,
                    "language": language,
                    "llm_provider": llm_provider
                }
                
                response = requests.post(
                    f"{HRM_AGENT_API_URL}/api/diagnosis/stream",
                    json=api_payload,
                    stream=True,
                    timeout=300
                )
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': 'API 서버 오류', 'done': True})}\n\n"
                    return
                
                # API 서버로부터 스트리밍 응답을 그대로 전달
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        yield f"{line}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 진단 요약 중 오류: {e}")
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
        return jsonify({'error': f'스트리밍 중 오류 발생: {str(e)}'}), 500

@app.route('/api/stream/operation-history/<string:item_id>')
def stream_operation_history(item_id):
    """특정 ID의 운영 이력 데이터를 스트리밍으로 요약합니다."""
    try:
        # HRM Agent API 서버 상태 확인
        if not check_api_server_health():
            return jsonify({'error': 'HRM Agent API 서버에 연결할 수 없습니다.'}), 503
            
        # 언어 및 LLM 설정 가져오기
        language = request.args.get('language', 'ko')
        llm_provider = request.args.get('llm', 'openai')
        
        # 선택된 ID에 해당하는 데이터 찾기
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        
        if not item_data:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404
            
        # operation history 데이터 추출 (root level의 operation_history)
        operation_history = item_data.get('operation_history', {})
        
        def generate():
            try:
                # HRM Agent API 서버에 스트리밍 요청
                api_payload = {
                    "operation_history": operation_history,
                    "language": language,
                    "llm_provider": llm_provider
                }
                
                response = requests.post(
                    f"{HRM_AGENT_API_URL}/api/operation-history/stream",
                    json=api_payload,
                    stream=True,
                    timeout=300
                )
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': 'API 서버 오류', 'done': True})}\n\n"
                    return
                
                # API 서버로부터 스트리밍 응답을 그대로 전달
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        yield f"{line}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 운영 이력 요약 중 오류: {e}")
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
        return jsonify({'error': f'스트리밍 중 오류 발생: {str(e)}'}), 500

@app.route('/guide-retriever')
def guide_retriever():
    """메인 페이지"""
    return render_template('guide_retriever.html')

@app.route('/api/stream/actions-guide/<string:item_id>', methods=['GET', 'POST'])
def stream_actions_guide(item_id):
    """진단 결과 기반 고객 조치 가이드를 스트리밍 생성 (한국어 전용)."""
    try:
        # HRM Agent API 서버 상태 확인
        if not check_api_server_health():
            return jsonify({'error': 'HRM Agent API 서버에 연결할 수 없습니다.'}), 503

        # POST 요청에서 데이터 가져오기
        if request.method == 'POST':
            data = request.get_json() or {}
            language = data.get('language', 'ko')
            category = data.get('category', '')
            diagnosis_summary = data.get('diagnosis_summary', '')
        else:
            # GET 요청 (기존 호환성)
            language = request.args.get('language', 'ko')
            category = request.args.get('category', '')
            diagnosis_summary = request.args.get('diagnosis_summary', '')

        if language.lower() != 'ko':
            return jsonify({'error': '한국어에서만 지원됩니다.'}), 400

        # 선택된 ID에 해당하는 데이터 찾기
        item_data = next((item for item in json_data if item.get('id') == item_id), None)
        if not item_data:
            return jsonify({'error': f'ID {item_id}에 해당하는 데이터를 찾을 수 없습니다.'}), 404

        # 진단 요약이 없으면 기본값 생성
        if not diagnosis_summary:
            analytics = item_data.get('analytics', {})
            device_type = analytics.get('deviceType', category)
            diagnosis_summary = f"제품군: {category or device_type} - 사용자가 자가 조치 가능 결론에 해당하는 증상으로 판단됨"

        # Get device type as fallback
        analytics = item_data.get('analytics', {})
        device_type = analytics.get('deviceType', category or 'unknown')
        final_category = category or device_type

        def generate():
            try:
                logger.info(f"[stream_actions_guide] 시작 - category: {final_category}, diagnosis_summary: {diagnosis_summary[:100]}...")
                
                # HRM Agent API 서버에 스트리밍 요청
                api_payload = {
                    "diagnosis_summary": diagnosis_summary,
                    "category": final_category,
                    "language": language
                }
                
                response = requests.post(
                    f"{HRM_AGENT_API_URL}/api/actions-guide/stream",
                    json=api_payload,
                    stream=True,
                    timeout=300
                )
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': 'API 서버 오류', 'done': True})}\n\n"
                    return
                
                # API 서버로부터 스트리밍 응답을 그대로 전달
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        yield f"{line}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 고객 조치 가이드 중 오류: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no'}
        )
    except Exception as e:
        return jsonify({'error': f'스트리밍 중 오류 발생: {str(e)}'}), 500

@app.route('/prompt-editor')
def prompt_editor():
    """프롬프트 편집기 페이지"""
    return render_template('prompt_editor.html')

@app.route('/api/prompt', methods=['GET', 'POST'])
def api_prompt():
    """prompt.json 읽기/저장 API"""
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.json')
        if request.method == 'GET':
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            # 파일로 저장
            with open(prompt_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """검색 API 프록시"""
    try:
        # 요청 데이터 파싱
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400
        
        query = data.get('query', '').strip()
        category_filter = data.get('category_filter', '')
        
        if not query:
            return jsonify({
                "error": "검색어를 입력해주세요."
            }), 400
        
        # GuideRetriever API 호출
        api_payload = {
            "query": query,
            "top_k": 3,
            "parallel": True
        }
        
        # 카테고리 필터가 있으면 추가
        if category_filter and category_filter != "all":
            api_payload["category_filter"] = category_filter
        
        logger.info(f"API 호출: query='{query}', category='{category_filter}'")
        
        # GuideRetriever API 서버에 요청
        response = requests.post(
            f"{API_BASE_URL}/search",
            json=api_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            api_data = response.json()
            
            # 결과 포맷팅
            formatted_results = []
            for result in api_data.get('results', []):
                formatted_result = {
                    "title": result.get('title', '제목 없음'),
                    "content": result.get('content', '내용 없음'),
                    "category": result.get('category', '카테고리 없음'),
                    "score": result.get('scores', {}).get('final_score', 0),
                    "url": result.get('url', ''),
                    "search_sources": result.get('search_sources', [])
                }
                formatted_results.append(formatted_result)
            
            return jsonify({
                "success": True,
                "query": query,
                "category_filter": category_filter,
                "results_count": len(formatted_results),
                "search_time_ms": api_data.get('search_time_ms', 0),
                "results": formatted_results
            })
        else:
            # API 에러 응답
            try:
                error_data = response.json()
                error_message = error_data.get('error', f'API 오류 (상태코드: {response.status_code})')
            except:
                error_message = f'API 서버 오류 (상태코드: {response.status_code})'
            
            return jsonify({
                "success": False,
                "error": error_message
            }), response.status_code
    
    except requests.exceptions.ConnectionError:
        logger.error("GuideRetriever API 서버에 연결할 수 없습니다")
        return jsonify({
            "success": False,
            "error": "GuideRetriever API 서버에 연결할 수 없습니다. API 서버(포트 5001)가 실행 중인지 확인해주세요."
        }), 503
    
    except requests.exceptions.Timeout:
        logger.error("API 요청 타임아웃")
        return jsonify({
            "success": False,
            "error": "검색 요청이 시간 초과되었습니다. 다시 시도해주세요."
        }), 504
    
    except Exception as e:
        logger.error(f"검색 중 오류 발생: {e}")
        return jsonify({
            "success": False,
            "error": f"검색 중 오류가 발생했습니다: {str(e)}"
        }), 500


@app.route('/health')
def health():
    """헬스 체크"""
    try:
        # GuideRetriever API 서버 상태 확인
        retriever_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        retriever_status = retriever_response.status_code == 200
        
        # HRM Agent API 서버 상태 확인
        hrm_agent_status = check_api_server_health()
        
        return jsonify({
            "web_server": "healthy",
            "guide_retriever_api": "healthy" if retriever_status else "unhealthy",
            "guide_retriever_url": API_BASE_URL,
            "hrm_agent_api": "healthy" if hrm_agent_status else "unhealthy",
            "hrm_agent_api_url": HRM_AGENT_API_URL
        })
    except:
        return jsonify({
            "web_server": "healthy",
            "guide_retriever_api": "unreachable",
            "guide_retriever_url": API_BASE_URL,
            "hrm_agent_api": "unreachable",
            "hrm_agent_api_url": HRM_AGENT_API_URL
        })


@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 서버 시작 시 JSON 데이터 로드
    load_json_data()
    
    # HRM Agent API 서버 상태 확인
    if check_api_server_health():
        logger.info("HRM Agent API 서버에 연결되었습니다.")
    else:
        logger.warning("HRM Agent API 서버에 연결할 수 없습니다. API 서버를 먼저 시작해주세요.")
    
    # 개발 모드로 Flask 서버 실행
    print("HRM AI Agent 웹 서버를 시작합니다...")
    print("브라우저에서 http://localhost:5000 으로 접속하세요.")
    print(f"HRM Agent API: {HRM_AGENT_API_URL}")
    print(f"GuideRetriever API: {API_BASE_URL}")
    
    app.run(
        host='0.0.0.0',  # 모든 네트워크 인터페이스에서 접근 허용
        port=5000,       # 포트 5000 사용
        debug=True,      # 디버그 모드 활성화 (개발 시에만)
        threaded=True    # 멀티스레드 지원
    )
