#!/usr/bin/env python3
"""API 엔드포인트 테스트 스크립트"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, description):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        
        print(f"✅ {method} {path}: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:200]}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {path}: 서버 연결 실패 - 서버가 실행 중인지 확인하세요")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️ {method} {path}: 타임아웃")
        return False
    except Exception as e:
        print(f"❌ {method} {path}: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API 엔드포인트 테스트")
    print("=" * 60)
    print()
    
    endpoints = [
        ("GET", "/api/documents/list", "문서 목록"),
        ("GET", "/api/rag/status", "RAG 상태"),
        ("GET", "/api/rag/documents", "RAG 문서 목록"),
    ]
    
    for method, path, description in endpoints:
        test_endpoint(method, path, description)
        print()
    
    print("=" * 60)
    print("서버가 실행 중이 아니라면:")
    print("  cd backend")
    print("  python main.py")
    print("=" * 60)
