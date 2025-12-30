"""
벡터 스토어 관리 모듈
ChromaDB를 사용하여 문서 임베딩 저장 및 검색
"""

import os
from typing import List, Dict, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import chromadb


class VectorStoreManager:
    """벡터 스토어 관리 클래스"""
    
    def __init__(self, 
                 persist_directory: str = "./backend/chroma_db",
                 collection_name: str = "biohealth_docs",
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Args:
            persist_directory: ChromaDB 저장 디렉토리
            collection_name: 컬렉션 이름
            embedding_model: 임베딩 모델 (한국어 지원)
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 디렉토리 생성
        os.makedirs(persist_directory, exist_ok=True)
        
        # 임베딩 모델 초기화 (한국어 지원)
        print(f"🔄 임베딩 모델 로딩 중: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"✅ 임베딩 모델 로드 완료")
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 벡터 스토어 초기화
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """기존 벡터 스토어 로드 또는 새로 생성"""
        try:
            # 기존 컬렉션 로드 시도
            collection = self.client.get_collection(name=self.collection_name)
            count = collection.count()
            
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            print(f"✅ 기존 벡터 스토어 로드 완료: {count}개 문서")
            
        except Exception as e:
            # 컬렉션이 없으면 새로 생성
            print(f"🆕 새 벡터 스토어 생성 중...")
            
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            print(f"✅ 새 벡터 스토어 생성 완료")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        문서 추가
        
        Args:
            documents: Document 리스트
            
        Returns:
            추가된 문서 ID 리스트
        """
        if not documents:
            print("⚠️ 추가할 문서가 없습니다")
            return []
        
        print(f"📝 {len(documents)}개 문서 추가 중...")
        
        try:
            ids = self.vectorstore.add_documents(documents)
            print(f"✅ {len(ids)}개 문서 추가 완료")
            return ids
            
        except Exception as e:
            print(f"❌ 문서 추가 실패: {e}")
            return []
    
    def search(self, 
               query: str, 
               k: int = 3,
               filter: Optional[Dict] = None) -> List[Document]:
        """
        유사도 검색
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            filter: 메타데이터 필터 (예: {"subject": "바이오헬스"})
            
        Returns:
            유사한 문서 리스트
        """
        try:
            if filter:
                results = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            print(f"🔍 검색 완료: {len(results)}개 문서")
            return results
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def search_with_score(self, 
                          query: str, 
                          k: int = 3,
                          filter: Optional[Dict] = None) -> List[tuple]:
        """
        유사도 점수와 함께 검색
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            filter: 메타데이터 필터
            
        Returns:
            (Document, score) 튜플 리스트
        """
        try:
            if filter:
                results = self.vectorstore.similarity_search_with_score(
                    query, 
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            print(f"🔍 검색 완료: {len(results)}개 문서")
            return results
            
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def delete_collection(self):
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"🗑️ 컬렉션 삭제 완료: {self.collection_name}")
            
            # 새로 생성
            self._load_or_create_vectorstore()
            
        except Exception as e:
            print(f"❌ 컬렉션 삭제 실패: {e}")
    
    def get_document_count(self) -> int:
        """저장된 문서 개수 반환"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            return collection.count()
        except:
            return 0
    
    def list_documents(self, limit: int = 100) -> List[Dict]:
        """
        저장된 문서 목록 조회
        
        Args:
            limit: 반환할 최대 문서 수
            
        Returns:
            문서 메타데이터 리스트
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            results = collection.get(limit=limit, include=['metadatas'])
            
            return results.get('metadatas', [])
            
        except Exception as e:
            print(f"❌ 문서 목록 조회 실패: {e}")
            return []


if __name__ == "__main__":
    # 테스트
    from document_loader import DocumentLoader
    
    # 문서 로더
    loader = DocumentLoader(chunk_size=500, chunk_overlap=50)
    
    # 샘플 문서 생성
    sample_text = """
    바이오헬스 산업 개요
    
    바이오헬스 산업은 생명공학 기술을 활용하여 인간의 건강과 삶의 질을 향상시키는 산업입니다.
    주요 분야로는 신약 개발, 의료기기, 디지털 헬스케어 등이 있습니다.
    
    mRNA 백신 기술
    
    mRNA 백신은 메신저 RNA를 이용하여 우리 몸의 세포가 특정 단백질을 생성하도록 지시합니다.
    이 기술은 COVID-19 팬데믹 동안 빠르게 발전하였으며, 향후 암 치료 등에도 활용될 전망입니다.
    """
    
    os.makedirs("./test_docs", exist_ok=True)
    with open("./test_docs/sample.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    # 문서 로드
    docs = loader.load_document("./test_docs/sample.txt", {"subject": "바이오헬스 기초"})
    
    # 벡터 스토어 초기화
    vector_store = VectorStoreManager(
        persist_directory="./test_chroma_db",
        collection_name="test_collection"
    )
    
    # 문서 추가
    vector_store.add_documents(docs)
    
    # 검색 테스트
    print("\n=== 검색 테스트 ===")
    query = "mRNA 백신이란?"
    results = vector_store.search_with_score(query, k=2)
    
    for i, (doc, score) in enumerate(results):
        print(f"\n📄 결과 {i+1} (유사도: {score:.4f}):")
        print(f"내용: {doc.page_content[:200]}...")
        print(f"메타데이터: {doc.metadata}")
