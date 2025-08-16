from flask import Flask, render_template, jsonify, send_from_directory, request, Response, stream_template
import json
import os
from flask_cors import CORS
from agents.root_agent import RootAgent

app = Flask(__name__)
CORS(app)  # CORS 설정으로 브라우저에서 JSON 데이터 요청 허용

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
                
                # 스트리밍으로 진단 요약 생성
                for chunk in agent.run_diagnosis(analytics, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(generate(), mimetype='text/plain; charset=utf-8')
        
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
                
                # 스트리밍으로 운영 이력 요약 생성
                for chunk in agent.run_op_history(operation_history, language=language):
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(generate(), mimetype='text/plain; charset=utf-8')
        
    except Exception as e:
        return jsonify({'error': f'스트리밍 중 오류 발생: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """404 에러 처리"""
    return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 처리"""
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

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
