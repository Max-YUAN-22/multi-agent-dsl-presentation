# -*- coding: utf-8 -*-
"""
Spark X1-32K WebSocket 适配器
- 提供与 DSL 兼容的 llm_callable: (prompt:str, role:str|None) -> str
- 采用 WebSocket 流式返回；自动聚合增量文本直到结束
- 通过环境变量读取 APP_ID / API_KEY / API_SECRET；URL/DOMAIN 可覆盖
"""

import os
import ssl
import json
import time
import base64
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from typing import Optional
from websocket import create_connection


def _rfc1123_gmt_now() -> str:
    # WebAPI 鉴权常用：RFC1123 GMT
    return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')


def _assemble_auth_url(api_url: str, api_key: str, api_secret: str) -> str:
    """
    构造带鉴权参数的 wss URL。
    对于 Spark X1-32K：wss://spark-api.xf-yun.com/v1/x1
    签名字符串采用 "host/date/request-line" 规范（若你的控制台示例有差异，请按示例微调）。
    """
    parsed = urllib.parse.urlparse(api_url)
    assert parsed.scheme == "wss", "Spark API must be wss"
    host = parsed.netloc
    path = parsed.path
    date = _rfc1123_gmt_now()

    signature_origin = f"host: {host}\n" \
                       f"date: {date}\n" \
                       f"GET {path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")

    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")

    qs = urllib.parse.urlencode({"authorization": authorization, "date": date, "host": host})
    return f"{api_url}?{qs}"


class SparkX1LLM:
    """
    用法：
        from integrations.spark_x1 import SparkX1LLM
        dsl.use_llm(SparkX1LLM.from_env())

    环境变量（必填）：
        SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET
    可选：
        SPARK_X1_URL= wss://spark-api.xf-yun.com/v1/x1
        SPARK_X1_DOMAIN= x1-32k
        SPARK_TEMPERATURE= 0.7
        SPARK_MAX_TOKENS= 2048
        SPARK_TIMEOUT= 45
    """
    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 api_url: str = "wss://spark-api.xf-yun.com/v1/x1",
                 domain: str = "x1-32k",
                 temperature: float = 0.7,
                 max_tokens: int = 2048,
                 timeout: int = 45):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = api_url
        self.domain = domain
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "SparkX1LLM":
        return cls(
            app_id=os.environ["SPARK_APP_ID"],
            api_key=os.environ["SPARK_API_KEY"],
            api_secret=os.environ["SPARK_API_SECRET"],
            api_url=os.environ.get("SPARK_X1_URL", "wss://spark-api.xf-yun.com/v1/x1"),
            domain=os.environ.get("SPARK_X1_DOMAIN", "x1-32k"),
            temperature=float(os.environ.get("SPARK_TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("SPARK_MAX_TOKENS", "2048")),
            timeout=int(os.environ.get("SPARK_TIMEOUT", "45")),
        )

    def __call__(self, prompt: str, role: Optional[str] = None) -> str:
        # 1) 鉴权 URL
        url = _assemble_auth_url(self.api_url, self.api_key, self.api_secret)

        # 2) 构造消息体（X1-32K 常见字段：header/parameter/payload）
        req = {
            "header": {
                "app_id": self.app_id,
                "uid": f"x1_{int(time.time()*1000)}"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "system", "content": role or "You are a helpful assistant."},
                        {"role": "user",   "content": prompt}
                    ]
                }
            }
        }

        # 3) WebSocket 发送并流式接收
        ws = create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=self.timeout)
        try:
            ws.send(json.dumps(req))
            chunks = []
            while True:
                raw = ws.recv()
                if not raw:
                    break
                resp = json.loads(raw)

                # 错误码检查
                code = resp.get("header", {}).get("code", 0)
                if code != 0:
                    msg = resp.get("header", {}).get("message", "spark error")
                    raise RuntimeError(f"spark x1 error code={code}, msg={msg}")

                payload = resp.get("payload", {})
                choices = payload.get("choices", {})
                texts = choices.get("text", []) or []

                for t in texts:
                    # X1-32K 增量返回：role=assistant 的 content 为片段
                    if t.get("role") == "assistant" and t.get("content"):
                        chunks.append(t["content"])

                # status == 2 表示结束（如你的版本文档用其它字段，请替换）
                status = choices.get("status")
                if status == 2:
                    break
            return "".join(chunks).strip()
        finally:
            try:
                ws.close()
            except Exception:
                pass


def get_llm_with_fallback():
    """
    优先使用 Spark X1-32K；环境变量缺失则回退 mock，
    避免 demo 现场“没配好 Key 就挂”。
    """
    ok = all(k in os.environ for k in ("SPARK_APP_ID", "SPARK_API_KEY", "SPARK_API_SECRET"))
    if ok:
        return SparkX1LLM.from_env()
    # fallback：与现有框架兼容的 mock
    return lambda prompt, role=None: f"[mock:{role}] {prompt}"
