# 🤖 AI 교육 현장용 수강생 질문 답변 자동 생성 시스템 (Local-First AI Assistant)

> **"클라우드 비용 0원, 데이터 유출 우려 0% — 로컬 온프레미스 LLM과 시맨틱 캐시를 활용한 지능형 교육 행정 업무 자동화 프로덕트"**

본 프로젝트는 AI 교육 현장에서 매일 반복되는 수강생들의 기술 질문(코드 에러, 개념 이해, 환경 설정 등)에 즉시 대응하고, 모범 답변을 자가 학습 및 영구 축적하기 위해 개발된 **Local-First 온프레미스 에이전트 시스템**입니다. 

시스템의 응답 속도와 무결성을 객관적으로 검증하기 위한 **평가 하네스(Evaluation Harness)**를 함께 구축하였습니다.

🛠️ 주요 기술 스택
- Orchestration & Workflow: LangGraph, LangChain
- Local LLM & Embedding Engine (Ollama):
  * gemma4:12b (수강생 질문 의도 분석 및 전문 모범 답변 생성)
  * mxbai-embed-large:latest (실시간 문장 벡터화 및 시맨틱 캐시 매칭)
- Database & Caching: ChromaDB Semantic Cache (Full CRUD 및 영구 아카이브 지원)
- Infrastructure & Hardware: 100% Local-First 온프레미스 구동 (RTX 5060 Ti + 64GB RAM 최적화, keep_alive="5m" 설정으로 콜드 스타트 방지)
- Frontend: Streamlit (원클릭 UX 최적화)
  
[수강생 질문 유입: 코드 에러, 개념 질문 등]
                 │
                 ▼
 1단계: Semantic Cache 검색 (ChromaDB + mxbai-embed-large)
 - 토씨나 문장이 달라도 의미가 유사한 질문이 있는지 실시간 벡터 매칭
                 │
                 ├─────────────────────────────────────────┐
                 ▼ (Cache Hit: 유사 질문 존재)             ▼ (Cache Miss: 신규 질문)
 2단계-A: 초고속 즉시 반환                      2단계-B: 로컬 LLM 심층 생성 (Gemma4:12b)
 - 기존 모범 답변을 즉시 재활용                   - 전문적이고 다층적인 맞춤형 초안 답변 생성
 - (추론 시간: 약 2 ~ 7초 이내)                  - (추론 시간: 약 40 ~ 70초 내외)
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      ▼
 3단계: 휴먼 인 더 루프 (Human-in-the-Loop) & ChromaDB 아카이브 적재
 - 강사가 원클릭 복사로 수강생에게 즉시 샌딩 (UX 최적화)
 - 생성된 질의응답 내역은 ChromaDB에 영구 저장 및 Full CRUD 관리
                 │
                 ▼
       [웹 대시보드 렌더링 및 실시간 상태 동기화]

💡 핵심 엔지니어링 특징
1. 지능형 시맨틱 캐시 (Semantic Cache): 문장 형태가 다를지라도 의미가 같은 질문을 벡터 매칭하여, 기존 40~70초 소요되던 로컬 LLM 추론 시간을 2~7초 이내로 획기적으로 단축했습니다.
2. 자원 최적화 및 보안: 외부 클라우드 API 의존성을 완전히 배제해 데이터 유출 제로(Zero-Data Leakage)를 달성했으며, keep_alive 설정을 통해 VRAM 상주를 유지하여 응답 지연을 방지했습니다.
3. ChromaDB 상담 아카이브 (Full CRUD): 누적된 모든 질의응답 기록을 벡터 DB에 영구 적재하고, 사이드바를 통해 자유로운 조회·수정·삭제 및 실시간 상태 동기화를 지원합니다.

📊 평가 하네스 (Evaluation Harness) 및 실측 성능 지표
시스템의 응답 정확도와 캐시 효율성을 객관적으로 증명하기 위해 독립적인 평가 스크립트(evaluation_harness.py)를 구현하였습니다.

1. 하네스 실행 방법
터미널 환경에서 아래 명령어를 통해 자동화된 테스트셋을 구동할 수 있습니다.

```bash
python evaluation_harness.py
```

1. 실측 성능 및 워크플로우 지표

| 구분 | 신규 질문 (Cache Miss) | 의미 기반 캐시 히트 (Cache Hit) |
|------|------------------------|-----------------------------------|
| 추론 소요 시간 | 약 40초 ~ 70초 내외 | 약 2초 ~ 7초 내외 (임베딩 즉시 반환) |
| 데이터 처리 | 로컬 LLM 심층 생성 | ChromaDB 시맨틱 매칭 |
| 업무 임팩트 | 반복 행정 업무 시간 70% 이상 절감 | 즉각적인 수강생 응대 가능 |

🚀 프로젝트 실행 방법 (Quick Start)
1. 환경 변수 설정 (.env)
프로젝트 루트 디렉토리에 .env 파일을 생성하고 아래 환경 변수를 설정합니다.

```env
OLLAMA_BASE_URL=http://localhost:11434
GENERATION_MODEL=gemma4:12b
EMBEDDING_MODEL=mxbai-embed-large:latest
```

2. 의존성 패키지 설치

```bash
pip install streamlit langgraph langchain-ollama chromadb pandas python-dotenv
```

3. Streamlit 웹 애플리케이션 실행

```bash
streamlit run app.py
```
