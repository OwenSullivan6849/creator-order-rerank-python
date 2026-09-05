from src.rerank_service import OrderContext, SearchRequest, rerank_order_search


class FakeClient:
    def rerank(self, query, candidates, top_k=5):
        assert query == "creator microphone"
        return [candidates[0], candidates[2]]


def test_search_keeps_relevant_items_and_reports_order_state():
    request = SearchRequest(
        "creator microphone",
        ["USB microphone with stand", "camera tripod", "pop filter"],
        OrderContext("ORD-1042", "packing", True),
    )
    result = rerank_order_search(request, FakeClient())
    assert result["results"] == ["USB microphone with stand", "pop filter"]
    assert result["order_update"] == "Order ORD-1042: packing; Receipt ready"
