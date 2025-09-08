# tests/smoke_spark_x1.py
from integrations.spark_x1 import get_llm_with_fallback

if __name__ == "__main__":
    llm = get_llm_with_fallback()
    out = llm("用一句话说你好。", role="system:test")
    print("LLM output:", out[:200])
