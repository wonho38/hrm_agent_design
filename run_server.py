#!/usr/bin/env python
"""
HRM AI Agent 웹 서버 실행 스크립트

이 스크립트는 Flask 웹 서버를 시작하고 HRM AI Agent 인터페이스를 제공합니다.

사용법:
    python run_server.py
    
또는:
    python app.py
"""

import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import app, load_json_data, initialize_root_agent
    
    if __name__ == '__main__':
        print("=" * 60)
        print("🤖 HRM AI Agent 웹 서버를 시작합니다...")
        print("=" * 60)
        
        # JSON 데이터 로드
        print("📂 JSON 데이터를 로딩중...")
        load_json_data()
        
        # RootAgent 초기화
        print("🤖 RootAgent를 초기화중...")
        initialize_root_agent()
        
        print("🌐 서버 정보:")
        print("   - URL: http://localhost:5000")
        print("   - 환경: 개발 모드")
        print("   - 디버그: 활성화")
        print("=" * 60)
        print("서버를 중지하려면 Ctrl+C를 누르세요.")
        print("=" * 60)
        
        # Flask 서버 실행
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
except ImportError as e:
    print(f"❌ 모듈 import 오류: {e}")
    print("💡 다음 명령어로 필요한 패키지를 설치하세요:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 서버 시작 오류: {e}")
    sys.exit(1)
