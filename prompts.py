# -*- coding: utf-8 -*-
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# 1. 질문 분석 노드용 프롬프트 (엄격한 단일 형식 고정)
analyze_system_prompt = SystemMessagePromptTemplate.from_template(
    "당신은 AI 교육 수석 조교입니다. 수강생 질문을 분석하여 지정된 텍스트 외에 어떠한 부가 설명도 출력하지 마세요."
)
analyze_human_prompt = HumanMessagePromptTemplate.from_template(
    """[질문]
{question}

[규칙]
1. category: '학습 상담 (Learning/Concept)', '프로젝트 멘토링 (Project/Troubleshooting)', '기타/일반 (General/Admin)' 중 택1
2. difficulty: 'Simple', 'Moderate', 'Complex' 중 택1

반드시 아래 형식 두 줄만 출력하세요:
CATEGORY: [결과]
DIFFICULTY: [결과]"""
)
ANALYZE_PROMPT = ChatPromptTemplate.from_messages([analyze_system_prompt, analyze_human_prompt])


# 2. 초안 생성 노드용 프롬프트 (토큰 낭비 방지를 위한 길이 압축)
draft_system_prompt = SystemMessagePromptTemplate.from_template(
    "당신은 테크니컬 인스트루릭터입니다. 핵심만 3~4문장으로 아주 간결하게 초안을 작성하세요."
)
draft_human_prompt = HumanMessagePromptTemplate.from_template(
    "[질문]\n{question}"
)
DRAFT_PROMPT = ChatPromptTemplate.from_messages([draft_system_prompt, draft_human_prompt])


# 3. 최종 템플릿 통합 노드용 프롬프트 (옵션 2 누락 및 포맷 이탈 방지 강화)
synthesize_system_prompt = SystemMessagePromptTemplate.from_template(
    "당신은 프로페셔널 AI 인스트루릭터입니다. 반드시 옵션 1과 옵션 2를 모두 빠짐없이 작성해야 합니다. 지정된 구분자('###OPTION_SPLIT###')를 기준으로 위에는 정석 분석, 아래에는 실용적 해결 템플릿을 명확히 완성하세요."
)
synthesize_human_prompt = HumanMessagePromptTemplate.from_template(
    """- 질문: {question}
- 성격: {category}
- 난이도: {difficulty}
- 초안 참고: {draft}

반드시 아래 형식을 정확히 지켜서 옵션 1과 옵션 2를 모두 작성하세요 (생략 절대 금지):
[옵션 1: 정석/원인 분석 중심 템플릿 내용]
###OPTION_SPLIT###
[옵션 2: 실용/빠른 해결 중심 템플릿 내용]"""
)
SYNTHESIZE_PROMPT = ChatPromptTemplate.from_messages([synthesize_system_prompt, synthesize_human_prompt])