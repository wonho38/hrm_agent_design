#!/usr/bin/env python3
"""
HRM Agent API 통합 테스트 스크립트
"""

import requests
import json
import time
import sys

# API 서버 설정
HRM_AGENT_API_URL = "http://localhost:8000"
WEB_SERVER_URL = "http://localhost:5000"

def test_api_server_health():
    """API 서버 헬스 체크 테스트"""
    print("1. API 서버 헬스 체크 테스트...")
    try:
        response = requests.get(f"{HRM_AGENT_API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API 서버 상태: {data.get('status', 'unknown')}")
            print(f"   ✓ RootAgent 초기화: {data.get('root_agent_initialized', False)}")
            return True
        else:
            print(f"   ✗ API 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ API 서버 연결 실패: {e}")
        return False

def test_web_server_health():
    """웹 서버 헬스 체크 테스트"""
    print("2. 웹 서버 헬스 체크 테스트...")
    try:
        response = requests.get(f"{WEB_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 웹 서버 상태: {data.get('web_server', 'unknown')}")
            print(f"   ✓ HRM Agent API 상태: {data.get('hrm_agent_api', 'unknown')}")
            return True
        else:
            print(f"   ✗ 웹 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 웹 서버 연결 실패: {e}")
        return False

def test_api_capabilities():
    """API 기능 목록 테스트"""
    print("3. API 기능 목록 테스트...")
    try:
        response = requests.get(f"{HRM_AGENT_API_URL}/api/capabilities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                capabilities = data.get('data', {})
                print(f"   ✓ 등록된 에이전트 수: {len(capabilities.get('agents', {}))}")
                print(f"   ✓ 등록된 도구 수: {len(capabilities.get('tools', {}))}")
                return True
            else:
                print(f"   ✗ API 응답 실패: {data.get('error', 'unknown error')}")
                return False
        else:
            print(f"   ✗ API 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ API 기능 목록 조회 실패: {e}")
        return False

def test_diagnosis_api():
    """진단 API 테스트"""
    print("4. 진단 API 테스트...")
    try:
        # 테스트용 analytics 데이터
        test_data = {
            "analytics": {
                "deviceType": "test_device",
                "diagnosisLists": [
                    {
                        "category": "test",
                        "diagnosis": "테스트 진단",
                        "severity": "low"
                    }
                ]
            },
            "language": "ko",
            "llm_provider": "openai"
        }
        
        response = requests.post(
            f"{HRM_AGENT_API_URL}/api/diagnosis", 
            json=test_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                diagnosis = data.get('data', {}).get('diagnosis', '')
                print(f"   ✓ 진단 결과 생성됨 (길이: {len(diagnosis)}자)")
                return True
            else:
                print(f"   ✗ 진단 API 실패: {data.get('error', 'unknown error')}")
                return False
        else:
            print(f"   ✗ 진단 API 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 진단 API 테스트 실패: {e}")
        return False

def test_streaming_diagnosis():
    """스트리밍 진단 API 테스트"""
    print("5. 스트리밍 진단 API 테스트...")
    try:
        # 테스트용 analytics 데이터
        test_data = {
            "analytics": {
                "deviceType": "test_device",
                "diagnosisLists": [
                    {
                        "category": "test",
                        "diagnosis": "테스트 진단",
                        "severity": "low"
                    }
                ]
            },
            "language": "ko",
            "llm_provider": "openai"
        }
        
        response = requests.post(
            f"{HRM_AGENT_API_URL}/api/diagnosis/stream", 
            json=test_data, 
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    chunk_count += 1
                    try:
                        data = json.loads(line[6:])  # 'data: ' 제거
                        if data.get('done'):
                            break
                    except:
                        pass
            
            print(f"   ✓ 스트리밍 청크 수신됨 (총 {chunk_count}개)")
            return True
        else:
            print(f"   ✗ 스트리밍 진단 API 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 스트리밍 진단 API 테스트 실패: {e}")
        return False

def main():
    """통합 테스트 실행"""
    print("=" * 60)
    print("HRM Agent API 통합 테스트 시작")
    print("=" * 60)
    
    tests = [
        test_api_server_health,
        test_web_server_health,
        test_api_capabilities,
        test_diagnosis_api,
        test_streaming_diagnosis
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except KeyboardInterrupt:
            print("\n테스트가 중단되었습니다.")
            sys.exit(1)
        except Exception as e:
            print(f"   ✗ 테스트 실행 중 오류: {e}")
            print()
    
    print("=" * 60)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("✓ 모든 테스트 통과!")
        sys.exit(0)
    else:
        print("✗ 일부 테스트 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
