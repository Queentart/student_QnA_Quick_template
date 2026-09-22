# -*- coding: utf-8 -*-
import time
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions

# 💡 Ollama의 mxbai-embed-large 모델을 임베딩 함수로 지정
ollama_embed_fn = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="mxbai-embed-large:latest"
)

# 💡 ChromaDB 로컬 영구 저장소 초기화 (코사인 거리 공간 사용)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="consultation_history",
    embedding_function=ollama_embed_fn,
    metadata={"hnsw:space": "cosine"} # 의미 유사도 측정을 위한 코사인 공간 설정
)

def save_to_chromadb(question: str, category: str, difficulty: str, templates: list):
    """[Create] 생성된 템플릿 히스토리를 ChromaDB에 영구 저장 (자동 벡터화)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_id = f"qna_{int(time.time())}"
    
    collection.add(
        documents=[question],
        metadatas=[{
            "timestamp": timestamp,
            "category": category,
            "difficulty": difficulty,
            "option_1": templates[0] if len(templates) > 0 else "",
            "option_2": templates[1] if len(templates) > 1 else ""
        }],
        ids=[doc_id]
    )

def find_semantic_cache(question: str, threshold: float = 0.85):
    """
    [Semantic Cache Check] 
    입력된 질문과 의미가 유사한(코사인 유사도 >= threshold) 과거 기록이 있는지 검사
    """
    try:
        results = collection.query(
            query_texts=[question],
            n_results=1
        )
        
        if results and results['ids'] and len(results['ids'][0]) > 0:
            # ChromaDB cosine distance: 0에 가까울수록 유사함 (Similarity = 1 - distance)
            distance = results['distances'][0][0]
            similarity = 1.0 - distance
            
            if similarity >= threshold:
                meta = results['metadatas'][0][0]
                matched_q = results['documents'][0][0]
                return {
                    "hit": True,
                    "similarity": similarity,
                    "matched_question": matched_q,
                    "category": meta.get("category"),
                    "difficulty": meta.get("difficulty"),
                    "templates": [meta.get("option_1"), meta.get("option_2")]
                }
    except Exception:
        pass
        
    return {"hit": False}

def get_all_history():
    """[Read] ChromaDB에 저장된 모든 히스토리 조회"""
    return collection.get()

def update_history(doc_id: str, question: str, category: str, difficulty: str, option_1: str, option_2: str):
    """[Update] 특정 ID의 상담 기록 수정"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S (수정됨)")
    
    collection.update(
        ids=[doc_id],
        documents=[question],
        metadatas=[{
            "timestamp": timestamp,
            "category": category,
            "difficulty": difficulty,
            "option_1": option_1,
            "option_2": option_2
        }]
    )

def delete_history(doc_id: str):
    """[Delete] 특정 ID의 상담 기록 삭제"""
    collection.delete(ids=[doc_id])