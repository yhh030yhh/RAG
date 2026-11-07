"""DeepSeek LLM（OpenAI 兼容接口）。"""
import json
from typing import Iterator

import httpx

from app.rag.llm.base import LLM


class DeepSeekLLM(LLM):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _ensure_key(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "未配置 DEEPSEEK_API_KEY。请在 backend/.env 中填写，"
                "或将 LLM_PROVIDER 设为 fake 进行离线测试。"
            )

    def _url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def generate(self, messages: list[dict]) -> str:
        self._ensure_key()
        resp = httpx.post(
            self._url(),
            headers=self._headers(),
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def stream(self, messages: list[dict]) -> Iterator[str]:
        self._ensure_key()
        with httpx.stream(
            "POST",
            self._url(),
            headers=self._headers(),
            json={"model": self.model, "messages": messages, "stream": True},
            timeout=120.0,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                    delta = obj["choices"][0].get("delta", {}).get("content")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
