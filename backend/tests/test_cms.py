def test_category_crud(client, auth_headers):
    h = auth_headers
    c = client.post("/api/v1/categories", headers=h, json={"name": "技术", "description": "技术类"}).json()
    assert c["name"] == "技术"

    lst = client.get("/api/v1/categories", headers=h).json()
    assert any(x["id"] == c["id"] for x in lst)

    u = client.put(f"/api/v1/categories/{c['id']}", headers=h, json={"name": "改名", "description": "d"}).json()
    assert u["name"] == "改名"

    assert client.delete(f"/api/v1/categories/{c['id']}", headers=h).status_code == 204


def test_tag_create_and_delete(client, auth_headers):
    h = auth_headers
    t = client.post("/api/v1/tags", headers=h, json={"name": "RAG"}).json()
    assert t["name"] == "RAG"
    assert client.delete(f"/api/v1/tags/{t['id']}", headers=h).status_code == 204


def test_article_full_flow(client, auth_headers):
    h = auth_headers
    cat = client.post("/api/v1/categories", headers=h, json={"name": "AI"}).json()
    tag = client.post("/api/v1/tags", headers=h, json={"name": "检索"}).json()

    art = client.post(
        "/api/v1/articles",
        headers=h,
        json={
            "title": "RAG 入门指南",
            "content": "检索增强生成技术。",
            "category_id": cat["id"],
            "tag_ids": [tag["id"]],
        },
    ).json()
    assert art["status"] == "DRAFT"
    assert art["tags"][0]["name"] == "检索"
    assert art["category"]["name"] == "AI"

    pub = client.post(f"/api/v1/articles/{art['id']}/publish", headers=h).json()
    assert pub["status"] == "PUBLISHED"
    assert pub["published_at"] is not None

    # 中文搜索
    s = client.get("/api/v1/articles", headers=h, params={"search": "入门"}).json()
    assert s["total"] >= 1

    assert client.delete(f"/api/v1/articles/{art['id']}", headers=h).status_code == 204
