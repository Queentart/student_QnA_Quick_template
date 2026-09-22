# -*- coding: utf-8 -*-
import time
from graph import app_graph

# 1. 테스트용 수강생 질문 데이터셋 (실제 교육 현장 시나리오 기반)
TEST_DATASET = [
    {
        "id": "Q-01",
        "question": "선생님, 파이썬에서 virtualenv랑 venv 차이가 정확히 뭔가요? 어떤 걸 쓰는 게 좋나요?",
        "expected_category": "Official/Technical",
        "expected_difficulty": "Moderate"
    },
    {
        "id": "Q-02",
        "question": "강의 들으면서 공부하다가 갑자기 머리가 너무 아프네요 ㅠㅠ 오늘 커피 한 잔 마시고 조금 늦게 들어와도 될까요?",
        "expected_category": "Private/General",
        "expected_difficulty": "Simple"
    },
    {
        "id": "Q-03",
        "question": "Docker 컨테이너 안에서 LangGraph 구동할 때 포트포워딩 에러(Address already in use)가 계속 나는데 어떻게 해결하나요? 로그 첨부합니다.",
        "expected_category": "Official/Technical",
        "expected_difficulty": "Complex"
    },
    {
        "id": "Q-04",
        "question": "다음 주 팀 프로젝트 조 편성은 어떻게 되나요? 아직 공지가 안 올라온 것 같아서요!",
        "expected_category": "Private/General",
        "expected_difficulty": "Simple"
    }
]

def run_evaluation():
    print("=" * 60)
    print("🚀 수강생 질문 분석 에이전트 평가 하네스(Evaluation Harness) 실행")
    print("=" * 60)
    
    total_tests = len(TEST_DATASET)
    passed_category_count = 0
    passed_difficulty_count = 0
    total_latency = 0.0

    for idx, test_case in enumerate(TEST_DATASET, 1):
        test_id = test_case["id"]
        question = test_case["question"]
        exp_cat = test_case["expected_category"]
        exp_diff = test_case["expected_difficulty"]

        print(f"\n[테스트 {idx}/{total_tests}] ID: {test_id}")
        print(f"질문: {question}")
        
        # 실행 시간 측정 시작
        start_time = time.time()
        
        try:
            # LangGraph 에이전트 호출
            result = app_graph.invoke({"question": question})
            
            elapsed_time = time.time() - start_time
            total_latency += elapsed_time
            
            pred_cat = result.get("category", "Unknown")
            pred_diff = result.get("difficulty", "Unknown")
            templates = result.get("templates", [])
            
            print(f"⏱️ 소요 시간: {elapsed_time:.2f초}")
            print(f"📌 예측 결과 -> 성격: {pred_cat} (기대: {exp_cat}) | 난이도: {pred_diff} (기대: {exp_diff})")
            print(f"📝 생성된 템플릿 개수: {len(templates)}개 옵션")
            
            # 검증 체크
            cat_match = exp_cat.lower() in pred_cat.lower()
            diff_match = exp_diff.lower() in pred_diff.lower()
            
            if cat_match:
                passed_category_count += 1
            if diff_match:
                passed_difficulty_count += 1
                
        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")

    print("\n" + "=" * 60)
    print("📊 최종 평가 리포트 (Evaluation Summary)")
    print("=" * 60)
    print(f"- 총 테스트 케이스: {total_tests}개")
    print(f"- 성격 분류 정확도: {(passed_category_count / total_tests) * 100:.1f}%")
    print(f"- 난이도 분류 정확도: {(passed_difficulty_count / total_tests) * 100:.1f}%")
    print(f"- 평균 처리 속도(Latency): {total_latency / total_tests:.2f}초 / 건")
    print("=" * 60)
    print("💡 이 하네스 결과는 LangSmith 및 최종 README 지표 증빙 자료로 활용됩니다.")

if __name__ == "__main__":
    run_evaluation()