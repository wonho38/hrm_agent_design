#!/usr/bin/env python3
"""
HRM Agent API Server 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    """API 서버를 실행합니다."""
    print("HRM Agent API Server를 시작합니다...")
    print("포트: 8000")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    try:
        # Python 스크립트 실행
        subprocess.run([sys.executable, "hrm_agent_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n서버가 종료되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"서버 실행 중 오류 발생: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
