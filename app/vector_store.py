from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# 임베딩 모델 초기화
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 비용 절감형
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Chroma 벡터 DB 클라이언트
vector_client = Chroma(
    collection_name="rag_documents",
    embedding_function=embedding,
    persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma"),
)

def add_documents(chunks: List[Document], clear_existing: bool = False):
    """
    청크를 벡터 DB에 저장
    
    Args:
        chunks: 저장할 Document 리스트
        clear_existing: 기존 데이터 삭제 여부 (테스트 시 중복 방지용)
    """
    global vector_client  # 함수 시작 부분에 global 선언
    
    # 기존 데이터 삭제 (테스트 시 중복 방지)
    if clear_existing:
        try:
            # ChromaDB 컬렉션 초기화
            vector_client.delete_collection()
            # 새로 생성
            vector_client = Chroma(
                collection_name="rag_documents",
                embedding_function=embedding,
                persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma"),
            )
            print("🗑️  기존 벡터 DB 데이터 삭제됨")
        except Exception as e:
            print(f"⚠️  컬렉션 삭제 실패 (이미 비어있을 수 있음): {e}")
    
    vector_client.add_documents(chunks)
    vector_client.persist()
    print(f"✅ {len(chunks)}개 청크를 벡터 DB에 저장했습니다.")

def search_documents(query: str, k: int = 5, score_threshold: float = None):
    """
    질문과 유사한 문서 검색
    
    Args:
        query: 검색 질문
        k: 반환할 문서 개수
        score_threshold: 최소 유사도 점수 (None이면 필터링 안 함, 0.0~1.0 범위)
                        기본값은 None (모든 결과 반환)
    
    Returns:
        List[Tuple[Document, float]]: (문서, 유사도 점수) 리스트
    """
    # ChromaDB의 similarity_search_with_score는 거리(distance)를 반환
    # 코사인 거리: 0 (완전히 동일) ~ 2 (완전히 반대)
    # L2 거리: 0 이상의 값 (작을수록 유사)
    results = vector_client.similarity_search_with_score(
        query=query,
        k=k,
    )
    
    # 거리 점수를 유사도 점수로 변환
    # ChromaDB는 기본적으로 L2 거리를 사용
    # OpenAI 임베딩은 정규화된 벡터이므로 코사인 유사도를 사용하는 것이 더 적합
    # 하지만 ChromaDB는 L2 거리를 반환하므로 이를 적절히 변환해야 함
    
    normalized_results = []
    seen_content = set()  # 중복 제거용
    
    # ChromaDB는 L2 거리를 사용하지만, 정규화된 벡터의 경우
    # 거리 범위는 0 ~ sqrt(2) ≈ 1.414
    # 실제 유사도 점수 분포를 기반으로 거리 변환 최적화
    
    for doc, distance in results:
        # 중복 제거: 동일한 내용의 문서는 건너뛰기
        content_hash = hash(doc.page_content[:100])  # 첫 100자로 중복 판단
        if content_hash in seen_content:
            continue
        seen_content.add(content_hash)
        
        # 거리를 유사도로 변환
        # OpenAI 임베딩(text-embedding-3-small)은 정규화된 벡터를 반환
        # 정규화된 벡터의 L2 거리 범위: 0 ~ sqrt(2) ≈ 1.414
        # 
        # 실제 테스트 결과: 유사도 0.318~0.383 → 거리 약 0.9~1.1
        # 더 나은 변환: 코사인 유사도 = 1 - (거리^2 / 2)
        # 또는 단순 선형: similarity = max(0, 1 - distance / sqrt(2))
        
        # 방법 1: 정규화된 벡터의 L2 거리를 코사인 유사도로 변환
        # 코사인 유사도 = 1 - (L2거리^2 / 2) (정규화된 벡터의 경우)
        max_distance = 1.414  # sqrt(2) for normalized vectors
        
        if distance <= max_distance:
            # 정규화된 벡터의 경우: similarity = 1 - (distance^2 / 2)
            # 또는 선형 변환: similarity = 1 - (distance / max_distance)
            # 실험적으로 제곱 공식이 더 나은 결과를 제공
            similarity = max(0.0, 1.0 - (distance * distance) / 2.0)
        else:
            # 범위를 벗어난 경우: 지수 감쇠
            similarity = max(0.0, 1.0 / (1.0 + distance))
        
        normalized_results.append((doc, similarity))
    
    # threshold 필터링 (지정된 경우)
    if score_threshold is not None and score_threshold > 0:
        filtered_results = [
            (doc, sim) for doc, sim in normalized_results 
            if sim >= score_threshold
        ]
        return filtered_results
    
    return normalized_results
