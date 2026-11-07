def _upload_doc(client, h, tmp_path, name="rag.md", content=None):
    content = content or "Retrieval-Augmented Generation enhances LLMs by retrieving relevant documents from a knowledge base."
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    with open(p, "rb") as f:
        return client.post(
            "/api/v1/documents/upload",
            headers=h,
            files={"file": (name, f, "text/markdown")},
        ).json()


def test_document_processing_and_chunks(client, auth_headers, tmp_path):
    h = auth_headers
    doc = _upload_doc(client, h, tmp_path)
    st = client.get(f"/api/v1/documents/{doc['id']}/status", headers=h).json()
    assert st["status"] == "COMPLETED"
    assert st["chunk_count"] >= 1

    chunks = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=h).json()
    assert len(chunks) >= 1
    assert chunks[0]["content"]


def test_retrieve_debug(client, auth_headers, tmp_path):
    h = auth_headers
    _upload_doc(client, h, tmp_path)
    r = client.post("/api/v1/rag/retrieve", headers=h, json={"question": "What is RAG?", "top_k": 3}).json()
    assert r["query_embedding_dim"] == 1024
    assert len(r["hits"]) >= 1


def test_chat_answer_with_sources(client, auth_headers, tmp_path):
    h = auth_headers
    _upload_doc(client, h, tmp_path)
    sess = client.post("/api/v1/chat/sessions", headers=h, json={}).json()
    ans = client.post(
        f"/api/v1/chat/sessions/{sess['id']}/messages",
        headers=h,
        json={"content": "What is RAG?"},
    ).json()
    assert ans["role"] == "assistant"
    assert ans["content"]
    # 命中知识库时应返回来源
    assert isinstance(ans["sources"], list)
    assert len(ans["sources"]) >= 1


def test_rag_health(client, auth_headers):
    r = client.get("/api/v1/rag/health", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["embedding_configured"] is True
