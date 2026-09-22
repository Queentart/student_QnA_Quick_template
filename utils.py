# -*- coding: utf-8 -*-
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_ollama_health():
    """
    Ollama 로컬 서버(기본 포트: 11434)가 정상적으로 켜져 있는지 확인하는 함수
    """
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        # 2초 내에 응답이 오는지 확인
        response = requests.get(ollama_base_url, timeout=2)
        if response.status_code == 200:
            return True, f"Ollama 로컬 서버 연결됨 ({ollama_base_url})"
    except requests.exceptions.ConnectionError:
        pass
    except Exception:
        pass
        
    return False, f"Ollama 서버가 꺼져 있거나 응답이 없습니다 ({ollama_base_url})"