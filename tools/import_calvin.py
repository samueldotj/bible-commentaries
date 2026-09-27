"""Import Calvin's commentaries from CCEL's ThML volumes into en/calvin/.

Comments are read by tools/ccel.py: each begins at a <scripCom> marker and is
keyed to its verse, covering the verses up to the next marker in the chapter;
a marker without a verse (a Psalm's argument) is the chapter's introduction.

A paragraph that begins "<b>2.</b> <i>He came to Jesus by night.</i>" is on verse 2
and explains those words; they are kept as its verse and anchor. The editors'
footnotes (<note n="55">) become footnote paragraphs, marked {55} in the text.
Translation tables are left out. Each book's Argument, found in the volume's
front matter or at the head of the book before its first comment, is the
book's introduction; dedications, translators' prefaces and title pages are
not imported.

    python tools/import_calvin.py
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ccel import MARK, OSIS  # noqa: E402
import ccel  # noqa: E402
from refs import osis_to_id  # noqa: E402
from sword import ROOT, versification  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

CACHE = ROOT / "cache/ccel"
NOTE = re.compile(r"<note\b[^>]*?(?:\bn=\"([^\"]*)\")?[^>]*>(.*?)</note>", re.S)
TABLE = re.compile(r"<table\b.*?</table>", re.S)
P = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)
LEMMA = re.compile(r"\s*(?:<a\b[^>]*/>\s*)*(?:<b>\s*(\d+)\s*\.?\s*</b>\s*\.?\s*|(\d+)\s*\.\s*)?<i>(.*?)</i>\s*", re.S)
HEADING = re.compile(r"(?:PSALM|CHAPTER|LECTURE)\s+[\dIVXLC]+\.?|[A-Z][A-Z .,’']{2,60}\.?")


def plain(markup: str) -> tuple[str, list[dict]]:
    refs = []
    for m in re.finditer(r"<scripRef\b[^>]*>(.*?)</scripRef>", markup, re.S):
        osis = re.search(r'osisRef="([^"]*)"', m[0])
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", m[1])).split())
        for rid in osis_to_id(osis[1]) if osis else []:
            refs.append({"text": text, "ref": rid})
    markup = re.sub(r"\s+", " ", markup)  # line breaks in the XML are not breaks in the text
    text = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", markup)))
    text = re.sub(r"[ \t\r\f\v ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text).strip()
    text = re.sub(r" +([,.;:?!)])", r"\1", text)
    return text, refs


def comment_paras(markup: str, stats: Counter) -> list[Para]:
    """Paragraphs of one comment, each followed by the footnotes marked in it."""
    stats["translation-table words left out"] += len(re.sub(r"<[^>]+>", " ", " ".join(TABLE.findall(markup))).split())
    markup = TABLE.sub(" ", markup)
    notes: dict[str, str] = {}

    def mark(m: re.Match) -> str:
        n = m[1] or str(len(notes) + 1)
        notes[n] = m[2]
        return f" {{{n}}}"

    markup = NOTE.sub(mark, markup)
    out: list[Para] = []
    for p in P.findall(markup) or [markup]:
        verse = anchor = None
        if m := LEMMA.match(p):
            lemma = plain(m[3])[0].rstrip(",;:. ")
            rest = p[m.end():]
            if lemma and plain(rest)[0].lstrip(",;:. ") and len(lemma) < 300:
                verse = int(m[1] or m[2]) if (m[1] or m[2]) else None
                anchor = lemma
                p = rest
                stats["paragraphs with a lemma"] += 1
        text, refs = plain(p)
        if anchor:
            text = text.lstrip(",;:. ")
        if text and not out and HEADING.fullmatch(text):
            stats["headings dropped (PSALM 23.)"] += 1
            continue
        if text:
            out.append(Para(text, refs, anchor=anchor, verse=verse))
        for n in re.findall(r"\{(\w+)\}", text):
            if n in notes:
                note_text, note_refs = plain(" ".join(P.findall(notes[n])) or notes[n])
                if note_text:
                    out.append(Para(note_text, note_refs, label=n, footnote=True))
                    stats["footnotes"] += 1
                del notes[n]
    for n, body in notes.items():  # a note outside any <p>
        text, refs = plain(body)
        if text:
            out.append(Para(text, refs, label=n, footnote=True))
            stats["footnotes"] += 1
    return out


def book_arguments(path: Path, codes: list[str], stats: Counter) -> list[tuple[str, str, str]]:
    """(book, title, markup) for each Argument in a volume."""
    text = path.read_text(encoding="utf-8", errors="replace")
    to_code = dict(zip(OSIS, codes))
    out = []
    divs = list(re.finditer(r'<div1\b[^>]*>', text))
    for i, d in enumerate(divs):
        attrs = d[0]
        kind = re.search(r'type="([^"]*)"', attrs)
        title = re.search(r'title="([^"]*)"', attrs)
        kind, title = (kind[1] if kind else ""), (title[1] if title else "")
        end = divs[i + 1].start() if i + 1 < len(divs) else len(text)
        region = text[d.end():end]
        first = MARK.search(region)
        head = region[: first.start()] if first else region
        opening = " ".join(re.sub(r"<[^>]+>", "", x).strip() for x in P.findall(region[:3000])[:3]).upper()
        is_argument = kind.lower() == "front" and (
            re.search(r"ARGUMENT|CALVIN[’']S PREFACE|AUTHOR[’']S PREFACE|PREFACE OF JOHN CALVIN|PREFACE TO THE PROPHET", opening)
            or re.search(r"argument|calvin's preface", title, re.I)
        )
        is_book_head = kind.lower() == "book" and first is not None
        if is_argument and not re.search(r"argument|preface", title, re.I):
            title = "The Author's Preface" if "PREFACE" in opening else "The Argument"
        if not (is_argument or is_book_head):
            continue
        nxt = MARK.search(text, d.end())
        if not nxt or len(re.sub(r"<[^>]+>", " ", TABLE.sub(" ", head)).split()) < 40:
            continue
        # The Harmony of the Evangelists' Argument is on all three Gospels; it goes with Matthew.
        book = "MAT" if "Matthew, Mark, Luke" in text[:3000] else to_code[nxt[1]]
        out.append((book, title, head))
        stats["book arguments"] += 1
    return out


def main() -> None:
    codes = [b["code"] for b in versification()]
    stats: Counter = Counter()
    units: dict[str, Unit] = {}

    def add(rng: str, kind: str, paras: list[Para], title: str | None = None) -> None:
        if not paras:
            stats["empty comments"] += 1
            return
        if rng in units:
            units[rng].paragraphs += paras
            stats[f"text added to an existing {kind} unit"] += 1
        else:
            units[rng] = Unit(rng, kind, title=title, paragraphs=paras)

    for path in sorted(CACHE.glob("calcom*.xml")):
        entries, _ = ccel.read_volume(path, codes)
        for e in entries:
            paras = comment_paras(e.text, stats)
            if e.verse:
                add(e.range_id, "passage", paras)
            else:
                add(f"{e.book}.{e.chapter}", "chapter", paras)
        for book, title, markup in book_arguments(path, codes, stats):
            add(book, "book", comment_paras(markup, stats), title=title)

    all_units = list(units.values())
    problems = check("calvin", all_units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write("calvin", all_units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
