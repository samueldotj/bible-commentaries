"""Read compressed SWORD commentary modules (ModDrv zCom and zCom4).

A module has, for each testament, three files:

  {ot,nt}.bzs  block index: offset, compressed size, uncompressed size (3 x u32)
  {ot,nt}.bzv  entry index: block, offset in the block, size
               (u32 u32 u16 for zCom, u32 u32 u32 for zCom4)
  {ot,nt}.bzz  zlib-compressed blocks

The entry index has one slot per KJV position, in this order: the module
heading, the testament heading, then for each book its introduction, and for
each chapter its introduction followed by its verses. A comment that covers
several verses is stored once, and the other verses link to it with the same
block, offset and size.
"""

from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Entry:
    book: str
    chapter: int  # 0 for a book introduction
    verse: int  # 0 for a chapter introduction
    verse_end: int  # last verse of a linked range; same as verse otherwise
    text: str

    @property
    def range_id(self) -> str:
        if self.chapter == 0:
            return self.book
        if self.verse == 0:
            return f"{self.book}.{self.chapter}"
        if self.verse_end == self.verse:
            return f"{self.book}.{self.chapter}.{self.verse}"
        return f"{self.book}.{self.chapter}.{self.verse}-{self.verse_end}"


def versification() -> list[dict]:
    return json.loads((ROOT / "data/kjv-versification.json").read_text(encoding="utf-8"))


def slots(books: list[dict]):
    """(book, chapter, verse) for every index slot after the two headings."""
    for b in books:
        yield b["code"], 0, 0
        for c, n in enumerate(b["verses"], 1):
            yield b["code"], c, 0
            for v in range(1, n + 1):
                yield b["code"], c, v


def read_testament(data_dir: Path, testament: str, books: list[dict], wide: bool):
    bzs = (data_dir / f"{testament}.bzs").read_bytes()
    bzv = (data_dir / f"{testament}.bzv").read_bytes()
    bzz = (data_dir / f"{testament}.bzz").read_bytes()

    blocks = [struct.unpack_from("<III", bzs, i) for i in range(0, len(bzs), 12)]
    cache: dict[int, bytes] = {}

    def block(n: int) -> bytes:
        if n not in cache:
            off, size, _ = blocks[n]
            cache[n] = zlib.decompress(bzz[off : off + size])
        return cache[n]

    fmt, width = ("<III", 12) if wide else ("<IIH", 10)
    index = [struct.unpack_from(fmt, bzv, i) for i in range(0, len(bzv), width)]
    positions = list(slots(books))
    if len(index) != len(positions) + 2:
        raise ValueError(f"{testament}: {len(index)} index slots, expected {len(positions) + 2}")

    entries: list[Entry] = []
    last_key = None
    for (book, chapter, verse), key in zip(positions, index[2:]):
        if key[2] == 0:
            last_key = None
            continue
        if verse > 0 and key == last_key and entries[-1].book == book and entries[-1].chapter == chapter:
            entries[-1].verse_end = verse
            continue
        n, off, size = key
        text = block(n)[off : off + size].decode("utf-8", errors="replace")
        entries.append(Entry(book, chapter, verse, verse, text))
        last_key = key if verse > 0 else None
    return entries


def read_module(module_dir: Path) -> tuple[dict[str, str], list[Entry]]:
    """Read a SWORD module unpacked from its CrossWire zip."""
    conf_path = next((module_dir / "mods.d").glob("*.conf"))
    conf: dict[str, str] = {}
    for line in conf_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            conf.setdefault(k.strip(), v.strip())
    driver = conf["ModDrv"].lower()
    if driver not in ("zcom", "zcom4"):
        raise ValueError(f"unsupported driver {conf['ModDrv']}")
    data_dir = module_dir / conf["DataPath"].lstrip("./")
    books = versification()
    entries = read_testament(data_dir, "ot", books[:39], driver == "zcom4")
    entries += read_testament(data_dir, "nt", books[39:], driver == "zcom4")
    return conf, entries
