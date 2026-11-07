"""跨方言向量类型：PostgreSQL 用 pgvector VECTOR，SQLite 用 JSON。"""
from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


class EmbeddingVectorType(TypeDecorator):
    """向量列类型。

    - PostgreSQL：`VECTOR(dim)`
    - 其它（SQLite）：`JSON`（float 列表）

    读取结果统一归一化为 ``list[float]``。
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector

                return dialect.type_descriptor(Vector(settings.EMBEDDING_DIM))
            except ImportError:  # 未安装 pgvector 时回退为 JSON
                return dialect.type_descriptor(JSON())
        return dialect.type_descriptor(JSON())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if hasattr(value, "tolist"):  # numpy 数组 -> list
            value = value.tolist()
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value
