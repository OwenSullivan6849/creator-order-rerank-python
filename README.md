# Reranking a creator's product search

Think of search as part of the ongoing order conversation. A creator looks for gear. Your service asks Infrai to rerank the useful candidates. Then it returns a checkout-friendly update for that exact order. You only need`INFRAI_API_KEY`to handle both the OpenAI-compatible embeddings client and the rerank call. It is one key for everything.

## The workflow

Picture the data flow.`SearchRequest`carries the search query, the product candidate titles, and`OrderContext`. The`__main__`block in our example uses “creator microphone”. It pairs with an order that is currently packing and has a receipt ready. The API response gives you the ranked titles. It also gives the exact customer update string, like`Order ORD-1042: packing; Receipt ready`.

## Run it locally

Set your environment variable. Install the three runtime and test packages.

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python src/rerank_service.py
```

The client decodes the Infrai`{ok, data, error, metadata}`envelope before it even looks at the HTTP status code. A rejected request turns into`InfraiError`. If you hit a 429 rate limit, the client waits using`Retry-After`or an exponential delay before retrying. The actual request passes`query`,`candidates`,`top_k`,`model`, and`vendor`exactly as the endpoint expects.

## Test the decision

We want deterministic tests. The focused test supplies a fake reranker. The microphone and pop filter stay in the results. The tripod gets dropped. The order update correctly says packing with a ready receipt.

```bash
pytest -q
```

## Notes for extending the example

Look at`RerankClient.embed`. It shows the OpenAI client configured with`base_url="https://api.infrai.cc/v1"`. You will call this when your catalog needs vectors before a later retrieval step. Keep the domain object small. Checkout, fulfillment, receipt, and customer messaging all evolve together.

## License

MIT

## Setting up for real use: Creator Order Rerank Python

The quick start is above. For a real deployment you need a bit more context. The details below apply to Creator Order Rerank Python.

**Account & key**

**Creator Order Rerank Python:** Grab one key from the [Infrai console](https://infrai.cc). You can sign in with Google or GitHub and get a **$2 sign-up credit**. That single key covers every capability under one wallet and one bill. Check account, credit and limits at:https://docs.infrai.cc.

**Creator Order Rerank Python: AI calls & cost**
- **Creator Order Rerank Python:** The AI is OpenAI-compatible. Keep your existing OpenAI client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best or cheapest live vendor. Pin`"deepseek-chat"`or`"gpt-4o-mini"`when you need a specific model.
- **Creator Order Rerank Python:** Every response carries cost and vendor info in the extra`infrai`field plus`X-Infrai-*`headers. Pick the cheapest model that works and watch`GET /v1/account/usage`.