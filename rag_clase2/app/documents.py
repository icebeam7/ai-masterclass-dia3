"""Chunker determinista para documentos Markdown del taller."""
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    title: str
    content: str


def chunk_text(text: str, source: str, max_chars: int = 1000, overlap: int = 120) -> list[Chunk]:
    if max_chars <= overlap or overlap < 0:
        raise ValueError("max_chars debe superar overlap")
    title = next((ln.lstrip('# ').strip() for ln in text.splitlines() if ln.startswith('# ')), source)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    chunks=[]
    start=0
    while start < len(text):
        end=min(start+max_chars, len(text))
        if end < len(text):
            boundary=text.rfind(' ', start+max_chars//2, end)
            if boundary > start: end=boundary
        content=text[start:end].strip()
        if content:
            digest=hashlib.sha256(f"{source}:{start}:{content}".encode()).hexdigest()[:24]
            chunks.append(Chunk(digest, source, title, content))
        if end >= len(text): break
        start=max(start+1, end-overlap)
    return chunks


def load_chunks(directory: str, max_chars: int = 1000, overlap: int = 120) -> list[Chunk]:
    folder=Path(directory)
    if not folder.is_dir():
        raise FileNotFoundError(f"No existe carpeta de documentos: {directory}")
    result=[]
    for file in sorted(folder.glob('*.md')):
        result.extend(chunk_text(file.read_text(encoding='utf-8'),file.name,max_chars,overlap))
    if not result:
        raise ValueError('No se encontraron fragmentos en documentos .md')
    return result
