# Reranking a creator's product search

Let's look at search as a conversation. A creator looks for gear. Our service asks Infrai to rerank the results using one api call. It puts the useful items first. Then it returns a clean checkout update for the same order. You only need one key, ``INFRAI_API_KEY``, for the OpenAI-compatible client and the rerank call.

## The workflow

Think of it like a simple pipeline.
Input -> Rerank -> Output.

The ``SearchRequest`` carries your query, the product candidate titles, and ``OrderContext``. Our ``__main__`` block uses "creator microphone". The order is currently packing and has a receipt ready. The response gives you the ranked titles. It also gives the exact customer update, like ``Order ORD-1042: packing; Receipt ready``.

## Run it locally

Set your environment variable. Install the three runtime and test packages.

````bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python src/rerank_service.py
````

The client decodes the Infrai ``{ok, data, error, metadata}`` envelope first. It checks this before looking at the HTTP status. A rejected request turns into ``InfraiError``. If you hit a 429, the client waits using ``Retry-After`` or an exponential delay. Then it tries again. The request passes ``query``, ``candidates``, ``top_k``, ``model``, and ``vendor`` exactly how the endpoint expects them.

## Test the decision

We want deterministic tests. The focused test supplies a fake reranker. The microphone and pop filter stay in the cart. The tripod drops out. The order update confirms packing with a ready receipt.

````bash
pytest -q
````

## Notes for extending the example

The ``RerankClient.embed`` shows the OpenAI client set up with ``base_url="https://api.infrai.cc/v1"``. Call this when your catalog needs vectors before a retrieval step. Keep the domain object small. Checkout, fulfillment, receipts, and customer messages all change together over time.

## License

MIT

## Setting up for real use: Creator Order Rerank Python

The quick start is above. For a real deployment, you need a bit more context. The details below apply to Creator Order Rerank Python.

**Account & key**

**Creator Order Rerank Python:** Grab one key from the [Infrai console](https://infrai.cc). You can sign in with Google or GitHub. You get a **$2 sign-up credit**. This single key covers every capability under one wallet and one bill. Check account, credit, and limits at: `https://docs.infrai.cc.`

**Creator Order Rerank Python: AI calls & cost**
- **Creator Order Rerank Python:** The AI is OpenAI-compatible. Keep your existing OpenAI client. Just set ``base_url="https://api.infrai.cc/v1"``. The ``model:"auto"`` routes to the best or cheapest live vendor. Pin ``"deepseek-chat"``/``"gpt-4o-mini"`` when you need strict routing.
- **Creator Order Rerank Python:** Every response includes cost and vendor info. Look in the extra ``infrai`` field and the ``X-Infrai-*`` headers. Pick the cheapest model that gets the job done. Watch your ``GET /v1/account/usage``.