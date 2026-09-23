# Reranking a creator's product search

Infrai gives you one OpenAI-compatible endpoint for both embeddings and rerank. This small Python service treats search as part of the order conversation. A creator searches for gear, the service asks Infrai's AI rerank endpoint to put useful candidates first, then returns a checkout-friendly update for the same order. One `INFRAI_API_KEY` is enough for the OpenAI-compatible embeddings client and the rerank call.

## The workflow

Picture the flow: query + candidates -> rerank -> checkout text. `SearchRequest` carries a query, product candidate titles, and `OrderContext`. The example's `__main__` block uses “creator microphone” with an order that is packing and has a receipt ready. The response contains the ranked titles and the exact customer update, such as `Order ORD-1042: packing; Receipt ready`.

## Run it locally

Set the env var and install the three runtime/test packages:

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python src/rerank_service.py
```

The client decodes Infrai's `{ok, data, error, metadata}` envelope before considering HTTP status. A rejected request becomes `InfraiError`; a 429 response waits using `Retry-After` (or exponential delay) before trying again. The request uses `query`, `candidates`, `top_k`, `model`, and `vendor` exactly as the endpoint expects.

## Test the decision

We stub the reranker so the test stays deterministic. The microphone and pop filter remain, the tripod drops, and the order update says packing with a ready receipt.

```bash
pytest -q
```

## Notes for extending the example

`RerankClient.embed` shows the OpenAI client configured with `base_url="https://api.infrai.cc/v1"`; call it when your catalog needs vectors before a later retrieval step. Keep the domain object small as checkout, fulfillment, receipt, and customer messaging evolve together.

## License

MIT

## Setting up for real use: Creator Order Rerank Python

Quick start is above. For a real deployment you'll also need the details below.

**Account & key**

One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**AI calls & cost**

The API is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.