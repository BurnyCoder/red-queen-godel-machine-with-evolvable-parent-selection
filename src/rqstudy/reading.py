"""Token-aware full manuscript access with fixed, cached reading of every chunk."""

from __future__ import annotations

import functools
import urllib.request
from pathlib import Path

from tokenizers import Tokenizer
from .data import digest

TOKENIZER_URL = "https://huggingface.co/Qwen/Qwen3.5-4B/resolve/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/tokenizer.json"
TOKENIZER_HASH = "5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42"
READ = "Extract specific research questions, methods, evidence, flaws and limitations from this manuscript passage. Use compact factual notes. Preserve important numbers. Omit publication status and decisions."


@functools.lru_cache(maxsize=3)
def tokenizer(project: Path):
    path = project / ".private" / "data" / "tokenizer.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(TOKENIZER_URL, timeout=90) as stream:
            raw = stream.read()
        if digest(raw) != TOKENIZER_HASH:
            raise ValueError("Tokenizer download hash mismatch")
        path.write_bytes(raw)
    if digest(path.read_bytes()) != TOKENIZER_HASH:
        raise ValueError("Tokenizer hash mismatch")
    return Tokenizer.from_file(str(path))


def chunks(text: str, size: int, codec) -> list[str]:
    """Slice original Unicode by token offsets, covering all characters exactly once."""
    encoded = codec.encode(text, add_special_tokens=False)
    if len(encoded.ids) <= size:
        return [text]
    cuts = sorted(
        {
            0,
            len(text),
            *(encoded.offsets[i][0] for i in range(size, len(encoded.ids), size)),
        }
    )
    return [text[a:b] for a, b in zip(cuts, cuts[1:]) if b > a]


def read_paper(broker, event: str, text: str):
    """Include every source passage; recursively compress exceptionally long notes."""
    codec = tokenizer(broker.project)
    # Reserve room for evolved instructions, the review schema and output tokens.
    limit = max(512, broker.ctx - 4096) if broker.ctx > 4096 else 2048
    sections = chunks(text, limit, codec)
    metadata = dict(
        route="direct" if len(sections) == 1 else "section",
        chunks=len(sections),
        chars=len(text),
        covered=sum(map(len, sections)),
        sha256=digest(text),
    )
    if len(sections) == 1:
        return text, metadata
    layer = 0
    while len(sections) > 1:
        notes = [
            broker.ask(f"{event}/read/{layer}/{i}", "reader", READ, part, 192)
            for i, part in enumerate(sections)
        ]
        merged = "\n\n".join(notes)
        if not merged.strip():
            raise ValueError("Empty reading notes")
        sections = chunks(merged, limit, codec)
        layer += 1
    return sections[0], metadata
