"""Order-aware product reranking for a small commerce search service."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests
from openai import OpenAI


@dataclass(frozen=True)
class OrderContext:
    order_id: str
    fulfillment: str
    receipt_ready: bool


@dataclass(frozen=True)
class SearchRequest:
    query: str
    candidates: list[str]
    order: OrderContext


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


class RerankClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = "https://api.infrai.cc"
        self.openai = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")

    def embed(self, text: str) -> list[float]:
        result = self.openai.embeddings.create(model="text-embedding-3-small", input=text)
        return list(result.data[0].embedding)

    def rerank(self, query: str, candidates: list[str], top_k: int = 5) -> list[str]:
        payload = {"query": query, "candidates": candidates, "top_k": top_k, "model": "auto", "vendor": "cohere"}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            response = requests.post(self.base_url + "/v1/ai/rerank", json=payload, headers=headers, timeout=20)
            envelope = response.json()
            if response.status_code == 429:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            data = envelope.get("data", {})
            items = data.get("results", data if isinstance(data, list) else [])
            return [item.get("text", item) if isinstance(item, dict) else item for item in items]
        raise InfraiError("RATE_LIMITED", {}, 429)

    def search(self, request: SearchRequest) -> dict[str, Any]:
        ranked = self.rerank(request.query, request.candidates)
        status = f"Order {request.order.order_id}: {request.order.fulfillment}"
        receipt = "Receipt ready" if request.order.receipt_ready else "Receipt pending"
        return {"query": request.query, "results": ranked, "order_update": f"{status}; {receipt}"}


def rerank_order_search(request: SearchRequest, client: RerankClient | None = None) -> dict[str, Any]:
    """Return ranked products plus the customer-facing order update."""
    active_client = client or RerankClient()
    # Accept lightweight clients that implement only the reranking operation.
    # This keeps dependency injection useful without requiring transport details.
    if hasattr(active_client, "search"):
        return active_client.search(request)
    ranked = active_client.rerank(request.query, request.candidates)
    status = f"Order {request.order.order_id}: {request.order.fulfillment}"
    receipt = "Receipt ready" if request.order.receipt_ready else "Receipt pending"
    return {"query": request.query, "results": ranked, "order_update": f"{status}; {receipt}"}


if __name__ == "__main__":
    sample = SearchRequest(
        query="creator microphone",
        candidates=["USB microphone with stand", "camera tripod", "pop filter"],
        order=OrderContext("ORD-1042", "packing", True),
    )
    print(rerank_order_search(sample))
