# -*- coding: utf-8 -*-
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from prompts import ANALYZE_PROMPT, SYNTHESIZE_PROMPT

load_dotenv()

class AgentState(TypedDict):
    question: str
    category: str
    difficulty: str
    draft_template: str
    templates: List[str]
    error: str

def get_llm():
    local_model_name = os.environ.get("LOCAL_MODEL_NAME", "gemma4:12b")
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    local_llm = ChatOllama(
        model=local_model_name,
        base_url=ollama_base_url,
        temperature=0.2,           # 👈 살짝 유연성을 주어 포맷 이탈 방지 (0.1 -> 0.2)
        num_ctx=2048,
        num_predict=1280,          # 👈 옵션 2가 잘리지 않도록 토큰 여유 폭 약간 상향
        repeat_penalty=1.1,
        extra_body={"keep_alive": "5m"}
    )
    return local_llm, f"Local (Ollama: {local_model_name})"

def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(item.get("text", str(item)))
            else:
                text_parts.append(str(item))
        return "".join(text_parts)
    return str(content)

def analyze_and_draft_node(state: AgentState):
    try:
        llm, _ = get_llm()
        prompt_value = ANALYZE_PROMPT.format_messages(question=state["question"])
        response = llm.invoke(prompt_value)
        content = extract_text(response.content)
        
        category = "학습 상담 (Learning/Concept)"
        difficulty = "Moderate"
        
        for line in content.split("\n"):
            if "CATEGORY:" in line:
                category = line.replace("CATEGORY:", "").strip()
            elif "DIFFICULTY:" in line:
                difficulty = line.replace("DIFFICULTY:", "").strip()
                
        draft_template = f"수강생 질문 관련 가이드라인 초안 (분류: {category}, 난이도: {difficulty})"
        
        return {
            "category": category, 
            "difficulty": difficulty,
            "draft_template": draft_template
        }
    except Exception as e:
        return {
            "error": str(e), 
            "category": "학습 상담 (Learning/Concept)", 
            "difficulty": "Moderate", 
            "draft_template": "초안 생성 실패"
        }

def synthesize_templates_node(state: AgentState):
    try:
        llm, _ = get_llm()
        prompt_value = SYNTHESIZE_PROMPT.format_messages(
            question=state["question"],
            category=state.get("category", "학습 상담 (Learning/Concept)"),
            difficulty=state.get("difficulty", "Moderate"),
            draft=state.get("draft_template", "")
        )
        response = llm.invoke(prompt_value)
        content = extract_text(response.content)
        
        templates = []
        if "###OPTION_SPLIT###" in content:
            templates = [t.strip() for t in content.split("###OPTION_SPLIT###") if t.strip()]
        
        # 💡 만약 구분자 파싱에 실패했거나 옵션 2가 누락된 경우 지능형 분할 폴백 실행
        if len(templates) < 2:
            parts = content.split("\n\n")
            if len(parts) >= 2:
                mid = len(parts) // 2
                opt1 = "\n\n".join(parts[:mid])
                opt2 = "\n\n".join(parts[mid:])
                templates = [opt1, opt2]
            else:
                # 최후의 보완: 전체 내용을 옵션 1로 두고, 옵션 2는 실용적 액션 가이드 자동 생성
                templates = [
                    content, 
                    f"💡 [실용/빠른 해결 액션 가이드]\n- 위 정석 내용을 바탕으로 즉시 실습 환경을 재확인하고 트러블슈팅을 진행해 주세요."
                ]
            
        return {"templates": templates}
    except Exception as e:
        return {"error": str(e), "templates": ["에러가 발생했습니다.", str(e)]}

def create_assistant_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze_and_draft", analyze_and_draft_node)
    workflow.add_node("synthesize", synthesize_templates_node)
    
    workflow.add_edge(START, "analyze_and_draft")
    workflow.add_edge("analyze_and_draft", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

app_graph = create_assistant_graph()