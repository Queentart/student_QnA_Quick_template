# -*- coding: utf-8 -*-
import time
import pandas as pd
import streamlit as st

from graph import app_graph
from database import (
    save_to_chromadb, 
    find_semantic_cache, 
    get_all_history, 
    update_history, 
    delete_history
)
from utils import check_ollama_health

# 1. 페이지 설정
st.set_page_config(
    page_title="수강생 질문 분석 및 템플릿 생성기",
    page_icon="🤖",
    layout="wide"
)

# 2. 메인 타이틀 및 소개
st.title("🎓 수강생 질문 자동 분석 및 대응 템플릿 생성기")
st.markdown("""
AI 교육 현장에서 수동으로 처리하던 **수강생 질문 분류 및 답변 템플릿 작성**을 자동화하여, 
강사의 응대 시간을 획기적으로 단축하고 일관된 피드백 퀄리티를 보장하는 **LangGraph 기반 온프레미스 에이전트 프로덕트**입니다.
""")

st.divider()

# 💡 [사이드바 구성] 시스템 헬스체크 및 ChromaDB 로컬 아카이브 (CRUD)
with st.sidebar:
    st.subheader("🔌 시스템 상태 점검")
    is_alive, msg = check_ollama_health()
    
    if is_alive:
        st.success(f"🟢 {msg}")
    else:
        st.error(f"🔴 {msg}")
        st.warning("⚠️ 백그라운드에서 Ollama 앱을 실행해 주세요!")
        
    st.divider()
    
    st.subheader("📂 ChromaDB 로컬 아카이브 (CRUD)")
    st.markdown("로컬 벡터 DB에 영구 저장된 기록을 관리하고 수정·삭제할 수 있습니다.")
    
    db_results = get_all_history()
    
    if db_results and len(db_results['ids']) > 0:
        st.metric("누적 상담 기록", f"{len(db_results['ids'])}건")
        
        df_history = pd.DataFrame(db_results['metadatas'])
        df_history['id'] = db_results['ids']
        df_history['question'] = db_results['documents']
        
        # 전체 목록 미리보기 표
        st.dataframe(df_history[['timestamp', 'category', 'question']], height=200)
        
        st.divider()
        st.markdown("#### ⚙️ 개별 기록 관리 (수정/삭제)")
        
        # 관리를 위해 특정 기록 선택 selectbox
        selected_id = st.selectbox(
            "관리할 기록 선택 (시간순 고유 ID)", 
            options=df_history['id'].tolist()
        )
        
        if selected_id:
            target_row = df_history[df_history['id'] == selected_id].iloc[0]
            
            with st.expander("📝 선택된 기록 상세 수정"):
                st.text(f"질문: {target_row['question']}")
                
                # 수정 폼 입력 필드
                edit_opt1 = st.text_area("옵션 1 내용 수정", value=target_row['option_1'], key=f"edit_opt1_{selected_id}")
                edit_opt2 = st.text_area("옵션 2 내용 수정", value=target_row['option_2'], key=f"edit_opt2_{selected_id}")
                
                col_u, col_d = st.columns(2)
                with col_u:
                    if st.button("💾 변경 저장", use_container_width=True):
                        update_history(
                            doc_id=selected_id,
                            question=target_row['question'],
                            category=target_row['category'],
                            difficulty=target_row['difficulty'],
                            option_1=edit_opt1,
                            option_2=edit_opt2
                        )
                        st.success("수정 완료!")
                        st.rerun()
                        
                with col_d:
                    if st.button("🗑️ 기록 삭제", type="primary", use_container_width=True):
                        delete_history(selected_id)
                        st.warning("삭제되었습니다.")
                        st.rerun()

        st.divider()
        
        # 전체 다운로드 버튼
        csv_export_df = df_history[['timestamp', 'category', 'difficulty', 'question', 'option_1', 'option_2']]
        csv_data = csv_export_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 전체 히스토리 엑셀(CSV) 다운로드",
            data=csv_data,
            file_name="chroma_history_export.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("아직 저장된 히스토리가 없습니다. 질문을 생성해 보세요!")

# 3. 레이아웃 구성 (좌측: 입력 및 제어 / 우측: 결과 및 메트릭)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 수강생 질문 입력")
    
    example_learning = "선생님, 파이썬에서 virtualenv랑 venv 차이가 정확히 뭔가요? 어떤 걸 쓰는 게 좋나요?"
    example_project = "Docker 컨테이너 안에서 LangGraph 구동할 때 포트포워딩 에러(Address already in use)가 계속 나는데 어떻게 해결하나요?"
    example_etc = "선생님, 오늘 컨디션이 조금 안 좋아서 오후 세션 실습을 녹화본으로 대체해서 들어도 출석 인정이 될까요?"
    
    selected_category_radio = st.radio(
        "빠른 테스트용 카테고리 선택 (선택 시 아래 입력창에 예시 질문 자동 입력)",
        ["학습 상담", "프로젝트 멘토링", "기타"]
    )
    
    default_text = ""
    if selected_category_radio == "학습 상담":
        default_text = example_learning
    elif selected_category_radio == "프로젝트 멘토링":
        default_text = example_project
    elif selected_category_radio == "기타":
        default_text = example_etc
        
    user_question = st.text_area(
        "질문 내용을 입력하세요", 
        value=default_text, 
        height=150,
        placeholder="예: 과제 제출 오류가 자꾸 나는데 어떻게 해야 하나요?"
    )
    
    run_btn = st.button("🚀 질문 분석 및 템플릿 생성", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 분석 결과 및 대응 템플릿")
    
    if run_btn:
        if not user_question.strip():
            st.warning("⚠️ 질문 내용을 입력해주세요!")
        else:
            start_time = time.time()
            
            # 💡 [핵심 로직] LLM 호출 전, ChromaDB 의미 기반 캐시(Semantic Cache) 검사
            cache_result = find_semantic_cache(user_question, threshold=0.85)
            
            if cache_result["hit"]:
                # 의미가 유사한 과거 기록이 존재할 경우 (즉시 반환)
                elapsed_time = time.time() - start_time
                category = cache_result["category"]
                difficulty = "Cached (유사 질문 참조)"
                templates = cache_result["templates"]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("처리 소요 시간", f"{elapsed_time:.2f} 초", "⚡ Semantic Cache Hit")
                m2.metric("질문 카테고리", category)
                m3.metric("매칭 상태", f"유사도: {cache_result['similarity']:.2f}")
                
                st.info(f"💡 기존에 답변한 유사한 질문을 참조했습니다:\n> *\"{cache_result['matched_question']}\"*")
                st.divider()
                
                # 생성된 템플릿 옵션 탭 제공 (원클릭 복사 st.code 적용)
                if templates:
                    tab1, tab2 = st.tabs(["📌 옵션 1 (정석/원인 분석)", "⚡ 옵션 2 (실용/빠른 해결)"])
                    
                    with tab1:
                        st.markdown("##### [정석적 가이드라인 및 원인 분석 톤]")
                        st.caption("📋 우측 상단의 복사 버튼을 누르면 클립보드에 즉시 복사됩니다.")
                        st.code(templates[0] if len(templates) > 0 else "내용 없음", language="markdown")
                        
                    with tab2:
                        st.markdown("##### [직관적이고 빠른 액션 아이템 중심 톤]")
                        st.caption("📋 우측 상단의 복사 버튼을 누르면 클립보드에 즉시 복사됩니다.")
                        st.code(templates[1] if len(templates) > 1 else templates[0], language="markdown")
                else:
                    st.error("템플릿 생성 결과가 없습니다.")
            else:
                # 새로운 의미의 질문인 경우 로컬 에이전트(Gemma 4:12B) 구동 후 DB 저장
                with st.spinner("🤖 로컬 에이전트(Gemma 4:12B)가 새로운 질문을 분석하고 템플릿을 생성 중입니다..."):
                    try:
                        result = app_graph.invoke({"question": user_question})
                        elapsed_time = time.time() - start_time
                        
                        category = result.get("category", "N/A")
                        difficulty = result.get("difficulty", "N/A")
                        templates = result.get("templates", [])
                        
                        # 로컬 ChromaDB에 영구 저장 (mxbai-embed-large 임베딩 자동 적용)
                        save_to_chromadb(user_question, category, difficulty, templates)
                        
                        # 💡 [핵심 수정] 신규 데이터 저장 직후 즉시 화면을 리로드하여 사이드바 카운트 실시간 갱신
                        st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ 에러 발생: {str(e)}")
    else:
        st.info("👈 왼쪽에서 수강생 질문을 입력하고 **[질문 분석 및 템플릿 생성]** 버튼을 눌러주세요.")

st.divider()

# 4. 하단 생산성 및 아키텍처 요약
with st.expander("💡 [System Metrics] 100% 로컬 온프레미스 아키텍처 및 생산성 요약"):
    st.markdown("""
    - **핵심 기술 스택:** Python, Streamlit, LangChain & LangGraph, Ollama (`gemma4:12b` + `mxbai-embed-large`), **ChromaDB Semantic Cache (Full CRUD)**
    - **실측 성능 및 워크플로우 지표 (Empirical Metrics):** 
      - **로컬 추론 소요 시간:** 신규 질문(Cache Miss) 시 약 40초~70초 내외 / **의미 기반 캐시 히트(Cache Hit) 시 로컬 임베딩 연산을 거쳐 `약 2초~7초 내외`로 즉시 반환**
      - **휴먼 인 더 루프(Human-in-the-loop) 샌딩:** AI가 초안과 투 트랙 옵션을 구조화하고, **원클릭 복사 버튼**을 통해 강사가 마우스 드래그 없이 즉시 샌딩 가능 (총 응대 시간 획기적 단축)
      - **시맨틱 캐시(Semantic Cache):** `mxbai-embed-large` 모델을 통한 실시간 문장 벡터화로, 토씨가 달라도 의미가 유사한 질문이면 과거 모범 답변을 지능적으로 재활용
      - **벡터 DB(Chroma) CRUD 및 실시간 동기화:** 생성된 모든 상담 기록이 영구 저장되며, 사이드바를 통한 자유로운 조회·수정·삭제 및 `st.rerun` 기반의 실시간 상태 동기화 완료
      - **시스템 헬스체크:** `utils.py`를 통한 Ollama 로컬 서버 실시간 통신 모니터링 적용
    - **아키텍처 특징 및 보안 내역:** 
      - **100% 온프레미스 (Local-First):** 클라우드 API 의존성을 완전히 배제하고, 로컬 하드웨어(RTX 5060 Ti + 64GB RAM) 기반의 고성능 오픈소스 모델을 단독 구동하여 **데이터 유출 제로(Zero-Data Leakage) 및 비용 0원** 달성
      - **자원 최적화:** `keep_alive="5m"` 설정을 통해 첫 로딩 후 VRAM 상주 및 콜드 스타트 방지
      - **보안 및 환경 설정:** `.env` 기반의 엔드포인트 및 로컬 모델명 관리(Configuration Management) 적용 완료
    """)