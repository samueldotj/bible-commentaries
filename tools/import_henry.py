"""Import Matthew Henry from the SWORD MHC module into en/henry/.

SWORD files Henry's text under verse keys, but not always where it belongs. A
"preverse" block before a section may hold the volume preface, the book's
introduction, the first chapter's introduction, or a whole earlier section.
So each entry is read as a stream of events (headings, introductions,
paragraphs) and units are built from the stream:

  <title type="x-ms">          the book; what follows is its introduction
  <title type="x-s2">          a preface heading inside the book's introduction
  <div type="introduction">    the chapter's introduction
  <title type="x-s3">          a section; its range comes from the verse numbers
                               in the KJV passage that follows (dropped)

    python tools/import_henry.py
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refs import osis_to_id  # noqa: E402
from sword import ROOT, read_module, versification  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

TOKEN = re.compile(r"<title[^>]*>.*?</title>|<note[^>]*>.*?</note>|<reference[^>]*>.*?</reference>|<[^>]+>|[^<]+", re.S)


def clean(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r" +([,.;:?!)])", r"\1", text)
    return text.strip()


class Stream:
    """Events from one entry: ("title", type, text), ("intro", "start"|"end"), ("para", text, refs, verses)."""

    def __init__(self) -> None:
        self.events: list[tuple] = []
        self.buf: list[str] = []
        self.refs: list[dict] = []
        self.supers: list[int] = []

    def flush(self) -> None:
        text = clean("".join(self.buf))
        if text:
            self.events.append(("para", text, self.refs, self.supers))
        self.buf, self.refs, self.supers = [], [], []

    def feed(self, markup: str, stats: Counter) -> list[tuple]:
        for tok in TOKEN.findall(markup):
            if tok.startswith("<title"):
                self.flush()
                kind = re.search(r'type="([^"]*)"', tok)
                text = clean(re.sub(r"<[^>]+>", "", tok))
                self.events.append(("title", kind[1] if kind else "", text))
            elif tok.startswith("<note"):
                stats["footnotes kept as a paragraph"] += 1
                self.flush()
                self.events.append(("para", clean(re.sub(r"<[^>]+>", "", tok)), [], []))
            elif tok.startswith("<reference"):
                inner = clean(re.sub(r"<[^>]+>", "", tok))
                osis = re.search(r'osisRef="([^"]*)"', tok)
                for rid in osis_to_id(osis[1]) if osis else []:
                    self.refs.append({"text": inner, "ref": rid})
                self.buf.append(inner)
            elif tok.startswith("<div") and 'type="introduction"' in tok:
                self.flush()
                self.events.append(("intro", "start" if "sID=" in tok else "end"))
            elif tok.startswith("<div") and 'type="x-p"' in tok and "sID=" in tok:
                self.flush()
            elif tok.startswith("<div") and 'type="x-p"' in tok:
                self.flush()
            elif tok.startswith("<l ") and "eID=" in tok:
                self.buf.append("\n")
            elif tok.startswith("<lg") and "eID=" in tok:
                self.flush()
            elif tok.startswith('<hi type="super">'):
                self.buf.append("\x00")  # the next text is a verse number
            elif tok.startswith("<"):
                continue
            else:
                if self.buf and self.buf[-1] == "\x00":
                    self.buf.pop()
                    m = re.match(r"\s*(\d+)", tok)
                    if m:
                        self.supers.append(int(m[1]))
                self.buf.append(tok)
        self.flush()
        return self.events


def main() -> None:
    last = {(b["code"], c): n for b in versification() for c, n in enumerate(b["verses"], 1)}
    _, entries = read_module(ROOT / "cache/sword/MHC")
    stats: Counter = Counter()
    units: dict[str, Unit] = {}
    order: list[str] = []

    def unit(rng: str, kind: str, title: str | None = None) -> Unit:
        if rng in units:
            stats[f"text added to an existing {kind} unit"] += 1
            if title and not units[rng].title:
                units[rng].title = title
            return units[rng]
        units[rng] = Unit(rng, kind, title=title)
        order.append(rng)
        return units[rng]

    # The stream runs on across entries within a book: an entry often begins with
    # the end of the previous section's comment.
    current: Unit | None = None
    mode = None  # "book", "book-heading", "intro", "section"
    pending_title: str | None = None
    book = None
    for e in entries:
        if e.book != book:
            book, current, mode, pending_title = e.book, None, None, None
        if not e.verse and e.chapter and mode != "book":
            current, mode = None, None  # a chapter entry starts afresh
        events = Stream().feed(e.text, stats)

        for ev in events:
            if ev[0] == "title":
                _, kind, text = ev
                if kind == "x-ms":
                    current, mode = unit(e.book, "book", title=text), "book"
                elif kind in ("x-s2", "main") and mode == "book" and current is not None:
                    current.paragraphs.append(Para(text, heading=True))
                elif kind == "x-s3" and mode == "book":
                    # Inside the book's introduction: a heading there, unless a KJV passage follows.
                    pending_title, mode = text, "book-heading"
                elif kind == "x-s3":
                    pending_title, current, mode = text, None, "section"
                elif current is not None:
                    current.paragraphs.append(Para(text, heading=True))
                else:
                    pending_title = text
                    stats[f"title {kind} before any unit"] += 1
                continue
            if ev[0] == "intro":
                if ev[1] == "start":
                    chapter = e.chapter or 1
                    current, mode = unit(f"{e.book}.{chapter}", "chapter"), "intro"
                else:
                    current, mode = None, None
                continue

            _, text, refs, supers = ev
            if mode == "book-heading" and not supers and current is not None:
                current.paragraphs.append(Para(pending_title, heading=True))
                pending_title, mode = None, "book"
            elif mode == "book-heading":
                current, mode = None, "section"
            if supers or (mode == "section" and current is None and re.match(r"\d+ ", text)):
                # The KJV passage: gives the section's verses; the text itself is dropped.
                nums = supers or [int(re.match(r"(\d+)", text)[1])]
                chapter = e.chapter
                lo, hi = min(nums), max(max(nums), min(nums))
                if e.verse and e.verse_end > hi and lo == e.verse:
                    hi = e.verse_end
                hi = min(hi, last[(e.book, chapter)])
                rng = f"{e.book}.{chapter}.{lo}" + (f"-{hi}" if hi > lo else "")
                current, mode = unit(rng, "passage", title=pending_title), "section"
                pending_title = None
                stats["kjv passages dropped"] += 1
                continue
            if current is None:
                if mode == "book":
                    current = unit(e.book, "book")
                elif e.verse:
                    current = unit(e.range_id, "passage", title=pending_title)
                    pending_title = None
                    stats["section without a passage (keyed by its entry)"] += 1
                else:
                    current = unit(f"{e.book}.{e.chapter}" if e.chapter else e.book, "chapter" if e.chapter else "book")
            current.paragraphs.append(Para(text, refs))

    all_units = [units[r] for r in order if units[r].paragraphs]
    stats["units with no text (dropped)"] = len(order) - len(all_units)

    covered: Counter = Counter()
    for u in all_units:
        if u.kind == "passage":
            b, c, vs = u.range.split(".")
            lo, _, hi = vs.partition("-")
            for v in range(int(lo), int(hi or lo) + 1):
                covered[(b, int(c), v)] += 1
    stats["verses in two passage units"] = sum(1 for n in covered.values() if n > 1)
    stats["verses in no passage unit"] = sum(n for n in last.values()) - len(covered)
    problems = check("henry", all_units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write("henry", all_units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
