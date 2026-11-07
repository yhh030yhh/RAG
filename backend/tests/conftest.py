"""测试配置：在导入应用前注入离线 fake 提供者与隔离的临时数据库。"""
import os
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="smartcms-test-").replace("\\", "/")

os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
os.environ["STORAGE_DIR"] = _TMP_DIR
os.environ["EMBEDDING_PROVIDER"] = "fake"
os.environ["LLM_PROVIDER"] = "fake"
os.environ["SIMILARITY_THRESHOLD"] = "0"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-bytes-long-ok"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    tok = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}
