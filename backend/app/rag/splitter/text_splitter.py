"""递归字符分块：优先保留段落/换行/句子结构，带重叠。"""
import re


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80,
    chars_per_token: float = 4.0,
) -> list[str]:
    """将文本切分为带重叠的 chunk。

    参数为 token 数，内部按 ``chars_per_token`` 估算为字符数。
    """
    chunk_chars = max(int(chunk_size * chars_per_token), 1)
    overlap_chars = max(int(overlap * chars_per_token), 0)

    # 1. 原子切分：段落 -> 换行 -> 句子
    segments: list[str] = []
    for para in re.split(r"\n{2,}", text):
        for line in re.split(r"\n", para):
            for sent in re.split(r"(?<=[。！？!?；;.])", line):
                s = sent.strip()
                if s:
                    segments.append(s)

    # 2. 超长段硬切
    atomic: list[str] = []
    step = max(chunk_chars - overlap_chars, 1)
    for seg in segments:
        if len(seg) <= chunk_chars:
            atomic.append(seg)
        else:
            for i in range(0, len(seg), step):
                atomic.append(seg[i : i + chunk_chars])

    # 3. 合并为带重叠的 chunk
    chunks: list[str] = []
    cur = ""
    for seg in atomic:
        if len(cur) + len(seg) + 1 <= chunk_chars:
            cur = f"{cur} {seg}" if cur else seg
        else:
            if cur:
                chunks.append(cur)
            if overlap_chars and len(cur) > overlap_chars:
                cur = cur[-overlap_chars:] + " " + seg
            else:
                cur = seg
    if cur.strip():
        chunks.append(cur)

    return [c.strip() for c in chunks if c.strip()]
