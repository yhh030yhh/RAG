# SmartCMS —— 基于 RAG 的智能内容管理系统

一个前后端分离的轻量级 AI 知识库问答系统（全栈学习项目）。

- **前端**：React 19 + TypeScript + Vite + Ant Design
- **后端**：FastAPI + SQLAlchemy 2.x + Pydantic v2
- **RAG**：文档解析（PDF/TXT/MD）→ 文本分块 → Embedding 向量化 → 向量检索 → DeepSeek 生成回答
- **存储**：开发期 SQLite（内存余弦检索），生产 PostgreSQL + pgvector

## 功能

- 管理员登录（JWT + Argon2id）
- 文章 / 分类 / 标签管理（含发布、归档、分页、搜索）
- 知识库文档上传、解析、分块、向量化、重新索引
- RAG 智能问答（引用来源、多轮对话、SSE 流式）
- 检索调试界面（查看 Query 向量、Top-K 命中、相似度分数、最终回答）

## 目录结构

```
smartcms/
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/     # 路由层
│   │   ├── core/       # 配置、数据库、安全
│   │   ├── models/     # SQLAlchemy 模型（9 张表）
│   │   ├── schemas/    # Pydantic 校验
│   │   ├── services/   # 业务逻辑
│   │   └── rag/        # RAG：parser / splitter / embedding / retrieval / llm / prompt / pipeline
│   ├── migrations/     # Alembic 迁移
│   └── tests/          # pytest 测试
├── frontend/           # React 前端
├── storage/            # 上传文件（运行时生成，已 gitignore）
└── docker-compose.yml  # 生产部署
```

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 初始化数据库（二选一）
alembic upgrade head        # 推荐：版本化迁移
# 或直接启动，应用会自动建表

uvicorn app.main:app --reload
```

启动后自动创建管理员（默认 `admin` / `admin123`，可用环境变量修改）。

### 2. 前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

前端已配置代理，`/api` 请求转发到 `http://localhost:8000`。

## 配置（`backend/.env`）

复制 `backend/.env.example` 为 `backend/.env` 后按需修改：

| 变量 | 说明 |
|---|---|
| `DATABASE_URL` | 默认 SQLite；生产改为 `postgresql+psycopg://...` |
| `SECRET_KEY` | JWT 密钥，生产必改 |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 管理员初始化账号 |
| `LLM_PROVIDER` | `deepseek`（真实）或 `fake`（离线占位） |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `EMBEDDING_PROVIDER` | `cloud`（云端）或 `fake`（离线测试） |
| `EMBEDDING_API_KEY` / `EMBEDDING_BASE_URL` / `EMBEDDING_MODEL` | 云端 Embedding（默认硅基流动 BGE-M3，兼容 DashScope） |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` / `TOP_K` / `SIMILARITY_THRESHOLD` | RAG 参数 |

**离线跑通全流程**（无任何 Key）：把 `LLM_PROVIDER` 和 `EMBEDDING_PROVIDER` 都设为 `fake`。

**接入真实模型**：
- DeepSeek：在 [DeepSeek 开放平台](https://platform.deepseek.com) 获取 Key，填入 `DEEPSEEK_API_KEY`。
- Embedding：推荐硅基流动 `BAAI/bge-m3`（1024 维），或阿里 DashScope `text-embedding-v3`，填入对应 Key/地址/模型。

## 数据库与向量存储

模型统一用 SQLAlchemy 编写，向量列通过 `EmbeddingVectorType` 跨方言适配：

- **SQLite（开发）**：向量存 JSON，检索时内存计算余弦相似度。
- **PostgreSQL + pgvector（生产）**：向量用 `VECTOR(1024)`，检索走 `<=>` 余弦算子。

迁移由 Alembic 管理；切换生产库时执行 `alembic upgrade head` 即可（迁移中的向量类型同样按方言适配）。

## 测试

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

覆盖认证、CMS CRUD、文档处理、向量检索、问答与来源引用、健康检查。

## Docker 部署

```bash
# 项目根目录，需已安装 Docker
docker compose up --build
```

- 前端 Nginx：`http://localhost:5173`
- 后端 API：`http://localhost:8000`
- PostgreSQL + pgvector：`localhost:5432`

生产环境请通过环境变量传入 `DEEPSEEK_API_KEY`、`EMBEDDING_API_KEY` 等密钥。

## 核心 API（前缀 `/api/v1`）

| 模块 | 端点 |
|---|---|
| 认证 | `POST /auth/login`、`GET /auth/me`、`PUT /auth/password` |
| 文章 | `GET/POST /articles`、`GET/PUT/DELETE /articles/{id}`、`POST /articles/{id}/publish`、`/archive` |
| 分类 | `GET/POST /categories`、`PUT/DELETE /categories/{id}` |
| 标签 | `GET/POST /tags`、`DELETE /tags/{id}` |
| 知识库 | `POST /documents/upload`、`GET/DELETE /documents/{id}`、`POST /documents/{id}/reindex`、`GET /documents/{id}/chunks` |
| 问答 | `POST /chat/sessions`、`POST /chat/sessions/{id}/messages`（支持 `?stream=true` SSE）、`GET .../messages` |
| 调试 | `POST /rag/retrieve`、`GET /rag/health` |

## RAG 流程

```
上传文档 → 文件校验 → 保存 → 解析(PyMuPDF/TXT/MD) → 文本清洗 → 递归分块
→ Embedding(BGE-M3 云端) → 向量入库 → (用户提问 → Query 向量化 → 余弦检索
→ Top-K → 阈值过滤 → 构建 Prompt → DeepSeek 生成 → 返回答案 + 来源)
```

设计说明：RAG 链路采用手写的轻量实现（httpx + PyMuPDF + 自写分块器），而非 LangChain 高级封装，以便清晰理解每步调用链路；Embedding/LLM 均走 OpenAI 兼容接口，可插拔替换。
