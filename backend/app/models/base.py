"""公共 Mixin 与工具函数。"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Uuid


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UUIDMixin:
    """UUID 主键。"""

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)


class CreatedAtMixin:
    """仅创建时间。"""

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class TimestampMixin:
    """创建时间 + 更新时间。"""

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
