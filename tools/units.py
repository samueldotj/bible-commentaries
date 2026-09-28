"""The English files: units of comment, their paragraphs, ids, checks and writing.

en/{source}/{BOOK}/{chapter}.json holds one chapter's units, and
en/{source}/{BOOK}/intro.json the book's own introduction:

{
  "source": "henry", "book": "JHN", "chapter": 3,
  "units": [
    {"id": "henry/JHN.3.1-21", "range": "JHN.3.1-21", "kind": "passage",
     "title": "Christ's Interview with Nicodemus.", "hash": "4f2a9c1b",
     "paragraphs": [{"id": "henry/JHN.3.1-21#p1-0c1d2e3f", "text": "...",
                     "refs": [{"text": "Mal. ii. 7", "ref": "MAL.2.7"}]}]}
  ]
}

kind is "book", "chapter" or "passage". A paragraph may also carry "heading": true,
a footnote has "footnote": true and "label" (its marker, which stays in the text as "{a}"),
"verse" is the verse a paragraph is on inside a longer unit, and "anchor" holds the words of the
verse a paragraph explains (Geneva's notes, the lemmas of Poole, Trapp and Calvin).
Paragraph ids follow the site's articles: {unit id}#p{n}-{fnv8 of the text}.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from sword import ROOT, versification

MAX_CHARS = 900  # a longer paragraph is cut at sentence ends
TARGET_CHARS = 700


def fnv8(s: str) -> str:
    """64-bit FNV-1a, first 8 hex digits; the same as the site's `articles::fnv8`."""
    h = 0xCBF29CE484222325
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{h:016x}"[:8]


@dataclass
class Para:
    text: str
    refs: list[dict] = field(default_factory=list)
    heading: bool = False
    label: str | None = None
    anchor: str | None = None
    verse: int | None = None
    footnote: bool = False
    extra: dict = field(default_factory=dict)  # source-specific fields, on every piece (ECF: author, work, quote)


@dataclass
class Unit:
    range: str
    kind: str
    title: str | None = None
    paragraphs: list[Para] = field(default_factory=list)

    @property
    def book(self) -> str:
        return self.range.split(".")[0]

    @property
    def chapter(self) -> int:
        parts = self.range.split(".")
        return int(parts[1].split("-")[0]) if len(parts) > 1 else 0

    @property
    def first_verse(self) -> int:
        parts = self.range.split(".")
        return int(parts[2].split("-")[0]) if len(parts) > 2 else 0


def ends_in_abbreviation(s: str) -> bool:
    words = s.rstrip().split()
    if not words:
        return False
    word = words[-1].rstrip(".?!")
    letters = word.lstrip("\"'([“‘")
    return "." in letters or sum(c.isalpha() for c in letters) <= 4


def split_long(text: str) -> list[str]:
    """Cut a paragraph over MAX_CHARS at sentence ends into about TARGET_CHARS, as the site does."""
    if len(text) <= MAX_CHARS:
        return [text]
    out: list[str] = []
    para = ""
    sentence = ""
    for i, c in enumerate(text):
        sentence += c
        nxt = text[i + 1] if i + 1 < len(text) else None
        after = text[i + 2] if i + 2 < len(text) else None
        if (
            c in ".?!"
            and (nxt is None or nxt.isspace())
            and not ends_in_abbreviation(sentence)
            and (after is None or after.isupper() or after in "\"“(")
        ):
            if len(para) + len(sentence) > TARGET_CHARS and para:
                out.append(para.strip())
                para = ""
            para += sentence
            sentence = ""
    para += sentence
    if para.strip():
        out.append(para.strip())
    return [piece for p in out for piece in split_hard(p)]


def split_hard(text: str) -> list[str]:
    """A piece still over twice MAX_CHARS (one long sentence, a list): cut at line breaks, then at "; "."""
    if len(text) <= 2 * MAX_CHARS:
        return [text]
    for sep in ("\n", "; "):
        parts = text.split(sep)
        if len(parts) == 1:
            continue
        out: list[str] = []
        cur = ""
        for i, part in enumerate(parts):
            piece = part + (sep.strip() if sep != "\n" and i < len(parts) - 1 else "")
            if cur and len(cur) + len(piece) > TARGET_CHARS:
                out.append(cur.strip())
                cur = ""
            cur += (" " if cur and sep != "\n" else "\n" if cur else "") + piece
        if cur.strip():
            out.append(cur.strip())
        return [q for p in out for q in split_hard(p)] if len(out) > 1 else out
    return [text]


def refs_in(text: str, refs: list[dict]) -> list[dict]:
    """The references whose text falls in this piece of a split paragraph."""
    return [r for r in refs if r["text"] in text]


def unit_json(source: str, u: Unit) -> dict:
    uid = f"{source}/{u.range}"
    paras = []
    n = 0
    for p in u.paragraphs:
        # A Geneva note is kept whole with its label; anything else long is cut.
        pieces = [p.text] if p.heading or (p.label and not p.footnote) else split_long(p.text)
        for i, piece in enumerate(pieces):
            n += 1
            d: dict = {"id": f"{uid}#p{n}-{fnv8(piece)}", "text": piece}
            if p.heading:
                d["heading"] = True
            if p.footnote:
                d["footnote"] = True
            if p.label and i == 0:
                d["label"] = p.label
            if p.verse and i == 0:
                d["verse"] = p.verse
            if p.anchor and i == 0:
                d["anchor"] = p.anchor
            d.update(p.extra)
            r = refs_in(piece, p.refs) if len(pieces) > 1 else p.refs
            if r:
                d["refs"] = r
            paras.append(d)
    english = "\n".join(([u.title] if u.title else []) + [p["text"] for p in paras])
    out = {"id": uid, "range": u.range, "kind": u.kind}
    if u.title:
        out["title"] = u.title
    out["hash"] = fnv8(english)
    out["paragraphs"] = paras
    return out


def check(source: str, units: list[Unit]) -> list[str]:
    """Problems that stop the import: bad ranges, empty units, duplicate ids."""
    books = {b["code"]: b["verses"] for b in versification()}
    problems = []
    seen: set[str] = set()
    for u in units:
        m = re.fullmatch(r"([1-3A-Z]{3})(?:\.(\d+)(?:\.(\d+)(?:-(\d+))?)?)?", u.range)
        if not m or m[1] not in books:
            problems.append(f"{u.range}: not a range")
            continue
        chapters = books[m[1]]
        if m[2] and not 1 <= int(m[2]) <= len(chapters):
            problems.append(f"{u.range}: no such chapter")
            continue
        if m[3]:
            last = chapters[int(m[2]) - 1]
            start, end = int(m[3]), int(m[4] or m[3])
            if not 1 <= start <= end <= last:
                problems.append(f"{u.range}: verses outside 1-{last}")
        if not u.paragraphs or not any(p.text.strip() for p in u.paragraphs):
            problems.append(f"{u.range}: empty")
        if any(not p.text.strip() for p in u.paragraphs):
            problems.append(f"{u.range}: an empty paragraph")
        if any(re.search(r"<[a-zA-Z/][^>]*>", p.text) for p in u.paragraphs):
            problems.append(f"{u.range}: markup left in the text")
        if u.range in seen:
            problems.append(f"{u.range}: two units with this range")
        seen.add(u.range)
    return problems


def write(source: str, units: list[Unit]) -> dict[str, int]:
    """Write en/{source}/, replacing what is there. Returns counts for the report."""
    out_dir = ROOT / "en" / source
    if out_dir.exists():
        for f in out_dir.glob("*/*.json"):
            f.unlink()
    order = {b["code"]: i for i, b in enumerate(versification())}
    units = sorted(units, key=lambda u: (order[u.book], u.chapter, u.first_verse, u.kind != "chapter"))
    files: dict[tuple[str, int], list[dict]] = {}
    for u in units:
        files.setdefault((u.book, u.chapter), []).append(unit_json(source, u))
    paragraphs = words = 0
    for (book, chapter), us in files.items():
        path = out_dir / book / ("intro.json" if chapter == 0 else f"{chapter}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = {"source": source, "book": book, "chapter": chapter, "units": us}
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        for u in us:
            paragraphs += len(u["paragraphs"])
            words += sum(len(p["text"].split()) for p in u["paragraphs"]) + len((u.get("title") or "").split())
    return {"files": len(files), "units": len(units), "paragraphs": paragraphs, "words": words}
