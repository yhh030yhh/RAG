"""通用工具函数。"""
import re


def slugify(text: str) -> str:
    """将标题转为 URL 友好的 slug，支持中文。"""
    text = text.strip().lower()
    # 非（字母数字下划线 或 中文字符）替换为 '-'
    text = re.sub(r"[^\w一-鿿]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "article"


def unique_slug(base: str, exists) -> str:
    """在 base 已存在时追加序号，直到唯一。"""
    slug = base
    n = 2
    while exists(slug):
        slug = f"{base}-{n}"
        n += 1
    return slug
