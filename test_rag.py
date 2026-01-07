#!/usr/bin/env python3
"""
RAG 기능 테스트 스크립트
Usage: python test_rag.py
"""
import requests
import json
import os
from pathlib import Path

# API 기본 URL
BASE_URL = "http://localhost:8000"

def get_api_key_from_system():
    """시스템 설정에서 GROQ API 키 가져오기"""
    try:
        response = requests.get(f"{BASE_URL}/api/system-settings")
        if response.status_code == 200:
            data = response.json()
            return data.get('groq_api_key', '')
    except:
        pass
    return None

def print_section(title):
    """섹션 헤더 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_rag_status():
    """RAG 상태 확인"""
    print_section("1. RAG 상태 확인")
    try:
        response = requests.get(f"{BASE_URL}/api/rag/status")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG 시스템 상태:")
            print(f"   - 초기화 여부: {data.get('initialized', False)}")
            print(f"   - 문서 수: {data.get('document_count', 0)}")
            print(f"   - 임베딩 모델: {data.get('embedding_model', 'N/A')}")
            print(f"   - 컬렉션: {data.get('collection_name', 'N/A')}")
            return True
        else:
            print(f"❌ 오류: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def create_test_documents():
    """테스트용 문서 생성"""
    print_section("2. 테스트 문서 생성")
    
    # 테스트 문서 디렉토리 생성 (현재 디렉토리 기준)
    test_dir = Path("./test_documents")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 바이오헬스 관련 테스트 문서들
    documents = {
        "biohealth_basic.txt": """
바이오헬스 산업 기초

바이오헬스 산업은 생명과학 기술과 정보통신 기술이 융합된 미래 성장 산업입니다.

주요 분야:
1. 의약품 개발
   - 신약 개발
   - 바이오시밀러
   - 항체 치료제

2. 의료기기
   - 진단기기
   - 치료기기
   - 모니터링 장비

3. 디지털 헬스케어
   - 원격의료
   - 웨어러블 디바이스
   - AI 진단 시스템

4. 유전자 치료
   - 유전자 편집 (CRISPR)
   - 세포 치료
   - 면역 치료

국내 바이오헬스 산업은 정부의 적극적인 지원과 함께 빠르게 성장하고 있습니다.
""",
        
        "mrna_vaccine.txt": """
mRNA 백신의 작동 원리

mRNA(메신저 RNA) 백신은 COVID-19 팬데믹을 계기로 주목받은 혁신적인 백신 기술입니다.

작동 원리:
1. mRNA 주입
   - 합성된 mRNA가 체내에 주입됩니다
   - mRNA는 바이러스의 스파이크 단백질 정보를 담고 있습니다

2. 단백질 생성
   - 우리 세포가 이 mRNA를 읽어 스파이크 단백질을 생성합니다
   - 생성된 단백질은 세포 표면에 나타납니다

3. 면역 반응
   - 면역 체계가 이 단백질을 인식하고 항체를 만듭니다
   - T세포도 활성화되어 면역 기억을 형성합니다

4. 보호 효과
   - 실제 바이러스 감염 시 빠르게 대응할 수 있습니다
   - mRNA는 며칠 내에 분해되어 사라집니다

장점:
- 빠른 개발 가능
- 높은 효능
- 조정이 용이함

mRNA 백신 기술은 앞으로 다양한 질병 예방에 활용될 전망입니다.
""",
        
        "gene_cell_therapy.txt": """
유전자 치료와 세포 치료의 차이

유전자 치료 (Gene Therapy):
- 정의: 결함이 있는 유전자를 교정하거나 새로운 유전자를 도입하는 치료법
- 방법:
  * 유전자 추가: 정상 유전자를 세포에 삽입
  * 유전자 편집: CRISPR 등으로 결함 유전자 수정
  * 유전자 억제: 문제가 되는 유전자의 활동 차단

- 적용 분야:
  * 유전성 질환 (혈우병, 근이영양증)
  * 일부 암
  * 유전적 면역 결핍증

- 예시: 
  * Luxturna (유전성 망막 질환 치료제)
  * Zolgensma (척수성 근위축증 치료제)

세포 치료 (Cell Therapy):
- 정의: 환자의 세포나 타인의 세포를 치료 목적으로 투여하는 방법
- 방법:
  * 줄기세포 치료
  * CAR-T 세포 치료
  * NK 세포 치료

- 적용 분야:
  * 혈액암 (백혈병, 림프종)
  * 재생 의학
  * 면역 질환

- 예시:
  * Kymriah (CAR-T 세포 치료제)
  * Yescarta (B세포 림프종 치료)

주요 차이점:
1. 유전자 치료 → 유전자 수준의 변화
2. 세포 치료 → 세포 자체를 치료 도구로 사용

두 기술은 때때로 결합되기도 합니다 (예: CAR-T는 세포를 유전자 조작함).
""",
        
        "training_sample.txt": """
훈련일지 - 2024년 1월 15일

교육 과정: 바이오헬스 아카데미
교육생: 홍길동

1. 오늘 학습한 내용:
   - Python 기초 문법 (변수, 조건문, 반복문)
   - 데이터 분석 라이브러리 소개 (Pandas, NumPy)
   - 바이오 데이터 전처리 기초

2. 실습 내용:
   - COVID-19 데이터셋 로드 및 기본 통계 분석
   - 결측치 처리 및 데이터 정제
   - 간단한 시각화 (matplotlib)

3. 새로 배운 점:
   - Pandas의 DataFrame 구조 이해
   - groupby를 활용한 그룹별 집계
   - 의료 데이터 특성 (개인정보 보호의 중요성)

4. 어려웠던 점:
   - 인덱싱과 슬라이싱의 차이 이해
   - 데이터 타입 변환 시 발생하는 오류

5. 질문 사항:
   - 대용량 데이터 처리 시 메모리 최적화 방법?
   - 실무에서 가장 많이 사용하는 전처리 기법은?

6. 다음 학습 계획:
   - 고급 Pandas 기능 학습
   - 통계 분석 기초
   - 바이오 통계 개념 이해

7. 소감:
Python을 처음 접해봤는데 생각보다 직관적이고 배우기 쉬웠습니다.
바이오 데이터 분석에 활용할 수 있다는 점이 매우 흥미롭습니다.
"""
    }
    
    created_files = []
    for filename, content in documents.items():
        filepath = test_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        created_files.append(str(filepath))
        print(f"✅ 생성됨: {filename}")
    
    print(f"\n총 {len(created_files)}개 테스트 문서 생성 완료")
    return created_files

def test_document_upload(file_paths):
    """문서 업로드 테스트"""
    print_section("3. 문서 업로드 테스트")
    
    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            print(f"\n업로드 중: {filename}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                response = requests.post(
                    f"{BASE_URL}/api/rag/upload",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 업로드 성공")
                print(f"   - 문서 ID: {data.get('document_id')}")
                print(f"   - 청크 수: {data.get('chunks_count')}")
            else:
                print(f"❌ 업로드 실패: {response.text}")
        except Exception as e:
            print(f"❌ 오류: {e}")

def test_document_list():
    """문서 목록 조회 테스트"""
    print_section("4. 문서 목록 조회")
    
    try:
        response = requests.get(f"{BASE_URL}/api/rag/documents")
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"✅ 총 {data.get('unique_documents', 0)}개 문서 ({data.get('total_chunks', 0)}개 청크):")
            for i, doc in enumerate(documents, 1):
                print(f"\n{i}. {doc.get('filename')}")
                print(f"   - ID: {doc.get('document_id')}")
                print(f"   - 업로드: {doc.get('uploaded_at')}")
                print(f"   - 청크: {doc.get('chunks_count')}개")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def test_rag_search(query):
    """RAG 검색 테스트"""
    print_section(f"5. RAG 검색 테스트: '{query}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rag/search",
            data={"query": query, "k": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ 검색 완료 (상위 {len(results)}개 결과):\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. 문서: {result.get('metadata', {}).get('filename', 'Unknown')}")
                print(f"   유사도: {result.get('similarity', 0):.4f}")
                print(f"   내용: {result.get('content', '')[:200]}...")
                print()
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def test_rag_chat(question, api_key=None):
    """RAG 챗봇 테스트"""
    print_section(f"6. RAG 챗봇 테스트: '{question}'")
    
    try:
        payload = {"message": question, "k": 3}
        headers = {}
        if api_key:
            headers["X-GROQ-API-Key"] = api_key
            
        response = requests.post(
            f"{BASE_URL}/api/rag/chat",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 답변 생성 완료:\n")
            print(f"질문: {data.get('question')}")
            print(f"\n답변:\n{data.get('answer')}")
            print(f"\n참고 문서:")
            for i, source in enumerate(data.get('sources', []), 1):
                print(f"  {i}. {source.get('filename')} (유사도: {source.get('score', 0):.4f})")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("\n" + "🧬" * 30)
    print("  RAG 시스템 종합 테스트")
    print("🧬" * 30)
    
    # 1. RAG 상태 확인
    if not test_rag_status():
        print("\n❌ 백엔드 서버가 실행 중인지 확인하세요!")
        print("   실행 방법: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # 2. 테스트 문서 생성
    file_paths = create_test_documents()
    
    # 3. 문서 업로드
    test_document_upload(file_paths)
    
    # 4. 문서 목록 조회
    test_document_list()
    
    # 5. RAG 검색 테스트
    test_queries = [
        "mRNA 백신의 작동 원리",
        "유전자 치료와 세포 치료의 차이",
        "바이오헬스 산업의 주요 분야"
    ]
    
    for query in test_queries:
        test_rag_search(query)
    
    # 6. RAG 챗봇 테스트
    print("\n" + "="*60)
    print("  RAG 챗봇 테스트 (API 키 필요)")
    print("="*60)
    
    # 시스템 설정에서 API 키 자동 가져오기
    api_key_from_system = get_api_key_from_system()
    
    if api_key_from_system:
        print(f"\n✅ 시스템 설정에서 GROQ API 키를 찾았습니다: {api_key_from_system[:10]}...")
        api_key_input = api_key_from_system
    else:
        print("\n⚠️  시스템 설정에서 API 키를 찾을 수 없습니다.")
        api_key_input = input("GROQ API 키를 입력하세요 (Enter로 건너뛰기): ").strip()
    
    test_questions = [
        "mRNA 백신은 어떻게 작동하나요?",
        "유전자 치료와 세포 치료의 차이점을 설명해주세요.",
        "바이오헬스 산업의 미래 전망은?"
    ]
    
    for question in test_questions:
        if api_key_input:
            test_rag_chat(question, api_key_input)
        else:
            print(f"\n질문: {question}")
            print("⏭️  API 키 없이 건너뜁니다.")
    
    # 최종 상태 확인
    test_rag_status()
    
    print("\n" + "="*60)
    print("  테스트 완료! 🎉")
    print("="*60)
    print("\n다음 단계:")
    print("1. 프론트엔드 UI에서 문서 업로드 기능 추가")
    print("2. 챗봇에 RAG 기능 통합")
    print("3. 시스템 설정에서 RAG 관련 설정 추가")
    print()

if __name__ == "__main__":
    main()
