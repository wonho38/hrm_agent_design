import sys
import requests
from flask import Flask, render_template, jsonify, send_from_directory, request, Response, stream_template
import json
import os
from flask_cors import CORS
from agents.root_agent import RootAgent
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORS 설정으로 브라우저에서 JSON 데이터 요청 허용

# GuideRetriever API 설정
API_BASE_URL = "http://localhost:5001"

# JSON 데이터를 메모리에 로드 (서버 시작 시 한 번만 로드)
json_data = []

# RootAgent 인스턴스 (전역으로 관리)
root_agent = None

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

def initialize_root_agent():
    """RootAgent를 초기화합니다."""
    global root_agent
    try:
        root_agent = RootAgent()
        print("RootAgent 초기화 완료")
    except Exception as e:
        print(f"RootAgent 초기화 오류: {e}")
        root_agent = None

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
        if not root_agent:
            return jsonify({'error': 'RootAgent가 초기화되지 않았습니다.'}), 500
            
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
                # RootAgent를 새 설정으로 재초기화 (선택된 LLM 사용)
                agent = RootAgent(provider_override=llm_provider)
                
                # 초기 하트비트 전송 (버퍼링 방지 및 즉시 표시 유도)
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"

                # 스트리밍으로 진단 요약 생성
                for chunk in agent.run_diagnosis(analytics, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
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
        if not root_agent:
            return jsonify({'error': 'RootAgent가 초기화되지 않았습니다.'}), 500
            
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
                # RootAgent를 새 설정으로 재초기화 (선택된 LLM 사용)
                agent = RootAgent(provider_override=llm_provider)
                
                # 초기 하트비트 전송 (버퍼링 방지 및 즉시 표시 유도)
                yield f"data: {json.dumps({'chunk': '', 'done': False})}\n\n"

                # 스트리밍으로 운영 이력 요약 생성
                for chunk in agent.run_op_history(operation_history, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
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
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        api_status = response.status_code == 200
        
        return jsonify({
            "web_server": "healthy",
            "api_server": "healthy" if api_status else "unhealthy",
            "api_url": API_BASE_URL
        })
    except:
        return jsonify({
            "web_server": "healthy",
            "api_server": "unreachable",
            "api_url": API_BASE_URL
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
    # 서버 시작 시 JSON 데이터 및 RootAgent 로드
    load_json_data()
    initialize_root_agent()
    
    # 개발 모드로 Flask 서버 실행
    print("HRM AI Agent 서버를 시작합니다...")
    print("브라우저에서 http://localhost:5000 으로 접속하세요.")
    
    app.run(
        host='0.0.0.0',  # 모든 네트워크 인터페이스에서 접근 허용
        port=5000,       # 포트 5000 사용
        debug=True,      # 디버그 모드 활성화 (개발 시에만)
        threaded=True    # 멀티스레드 지원
    )
