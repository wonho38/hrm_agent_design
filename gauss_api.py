import requests
import base64
import json
import os
from typing import Dict, Any, Optional


class GaussAPI:
    def __init__(self, access_key: str, secret_key: str):
        """
        Initialize GaussAPI client
        
        Args:
            access_key: AI-Asset-HUB에서 발급받은 Access Key
            secret_key: AI-Asset-HUB에서 발급받은 Secret Key
        """
        self.base_url = "https://inference-webtrial-api.shuttle.sr-cloud.com/gauss2-2-37b-instruct/v1"
        self.api_key = self._encode_credentials(access_key, secret_key)
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
            "accept": "*/*"
        }
    
    def _encode_credentials(self, access_key: str, secret_key: str) -> str:
        """
        Access Key와 Secret Key를 base64로 인코딩
        
        Args:
            access_key: Access Key
            secret_key: Secret Key
            
        Returns:
            base64 encoded credentials
        """
        credentials = f"{access_key}:{secret_key}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return encoded
    
    def get_models(self) -> Optional[Dict[str, Any]]:
        """
        GET /models - 사용 가능한 모델 목록 조회
        
        Returns:
            API 응답 또는 None (에러 시)
        """
        try:
            url = f"{self.base_url}/models"
            print(f"🔍 GET 요청: {url}")
            
            response = requests.get(url, headers=self.headers)
            
            print(f"📡 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ GET 요청 성공!")
                print("📋 사용 가능한 모델:")
                for model in result.get('data', []):
                    print(f"  - ID: {model.get('id')}")
                    print(f"    Max Length: {model.get('max_model_len')}")
                return result
            elif response.status_code == 429:
                print("⚠️  Rate limit 초과 (분당 20회 제한)")
                return None
            else:
                print(f"❌ GET 요청 실패: {response.status_code}")
                print(f"에러 메시지: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 에러: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 에러: {e}")
            return None
    
    def chat_completion(self, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        POST /chat/completions - 채팅 완성 요청
        
        Args:
            message: 사용자 메시지
            **kwargs: 추가 파라미터 (top_p, temperature, repetition_penalty 등)
            
        Returns:
            API 응답 또는 None (에러 시)
        """
        try:
            url = f"{self.base_url}/chat/completions"
            #print(f"💬 POST 요청: {url}")
            #print(f"📝 메시지: {message}")
            
            # 기본 파라미터 설정
            payload = {
                "model": "gauss2.2-37b",
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "top_p": kwargs.get('top_p', 0.96),
                "temperature": kwargs.get('temperature', 0.3),
                "repetition_penalty": kwargs.get('repetition_penalty', 1.03),
                "stream": kwargs.get('stream', False)
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            print(f"📡 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ POST 요청 성공!")
                
                # 응답 내용 출력
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print("🤖 AI 응답:")
                    print("-" * 50)
                    print(content)
                    print("-" * 50)
                    
                    # 토큰 사용량 정보
                    if 'usage' in result:
                        usage = result['usage']
                        print(f"📊 토큰 사용량:")
                        print(f"  - 프롬프트 토큰: {usage.get('prompt_tokens', 0)}")
                        print(f"  - 완성 토큰: {usage.get('completion_tokens', 0)}")
                        print(f"  - 총 토큰: {usage.get('total_tokens', 0)}")
                
                return result
            elif response.status_code == 429:
                print("⚠️  Rate limit 초과 (분당 20회 제한)")
                return None
            else:
                print(f"❌ POST 요청 실패: {response.status_code}")
                print(f"에러 메시지: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 에러: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 에러: {e}")
            return None


def main():
    """
    메인 실행 함수
    """
    print("🚀 Gauss2 API 테스트 시작")
    print("=" * 60)
    
    # API 키 설정 (환경변수 또는 직접 입력)
    access_key = "0cc59f74-5ffa-11f0-9221-a6b6d355ca09"
    secret_key = "3bc705fe-47c3-4d73-bfa7-ad15a66e59b9"
    
    if not access_key or not secret_key:
        print("🔑 API 키를 입력해주세요:")
        access_key = input("Access Key: ").strip()
        secret_key = input("Secret Key: ").strip()
        
        if not access_key or not secret_key:
            print("❌ API 키가 필요합니다!")
            return
    
    # API 클라이언트 초기화
    client = GaussAPI(access_key, secret_key)
    
    print("\n1️⃣ GET 요청 - 모델 목록 조회")
    print("=" * 40)
    models = client.get_models()
    
    if models:
        print(f"📄 전체 응답 JSON:")
        print(json.dumps(models, indent=2, ensure_ascii=False))
    
    print("\n2️⃣ POST 요청 - 채팅 완성")
    print("=" * 40)
    
    # 예제 메시지들
    test_messages = [
        "Write 3 sentences that start with SAMSUNG.",
        "안녕하세요! 간단한 인사말을 해주세요.",
        "Python으로 간단한 계산기를 만드는 방법을 알려주세요."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📤 테스트 메시지 {i}:")
        result = client.chat_completion(message)
        
        if result:
            print(f"📄 전체 응답 JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60)
    
    print("✨ 테스트 완료!")


if __name__ == "__main__":
    main() 