"""Import Matthew Poole from the BibleSupport e-Sword module into en/poole/.

Text comes from the e-Sword 11 edition (.cmti, HTML). The Greek and Hebrew
Poole typed in the OLB fonts survive only in the RTF edition (.cmtx), where
they are font runs ("\\f1 anwyen"). The Greek runs are converted to Greek
letters and put back in place of the Latin letters in the HTML edition. The Hebrew
runs do not follow a consistent key, so each becomes "[Hebrew]"; Poole
usually writes the transliteration beside it ("vya ish").

A chapter's first verse opens with its heading ("ISAIAH CHAPTER 1", "PSALM 23"),
then for a Psalm "THE ARGUMENT", then the chapter's outline; these become the
chapter's introduction. Each note starts with the words it explains in bold:
"<b>The vision,</b> or, the visions; ...".

    python tools/import_poole.py
"""

from __future__ import annotations

import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from esword import html_text, paragraphs, read_module  # noqa: E402
from sword import ROOT, versification  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

HTML = ROOT / "cache/esword/matthew_pool_commentary.cmti"
RTF = ROOT / "cache/esword/Matthew Pool Commentary.cmtx"

GREEK = dict(zip("abgdezhyiklmnxoprsvtufcqwABGDEZHYIKLMNXOPRSTUFCQW",
                 "αβγδεζηθικλμνξοπρσςτυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"))
FONT = re.compile(r"\{\\f(\d+)[^ ;]* ([^;]+);\}")
CHAPTER_HEAD = re.compile(r"\s*<b>\s*(?:[1-3] )?[A-Z][A-Z .]*(?:CHAPTER|PSALM)\s+\d+\s*</b>\s*$|\s*<b>\s*PSALM\s+\d+\s*</b>\s*$")
LEMMA = re.compile(r"\s*(?:Ver\.\s*(\d+)[^.<]*\.\s*)?<b>(.*?)</b>\s*", re.S)


def greek(run: str) -> str:
    return "".join(GREEK.get(c, c) for c in run)


def rtf_runs() -> dict[tuple[int, int, int], list[tuple[str, str]]]:
    """(book, chapter, verse) -> [("grk"|"heb", run)] in order, from the RTF edition."""
    db = sqlite3.connect(f"file:{RTF}?mode=ro", uri=True)
    out: dict[tuple[int, int, int], list[tuple[str, str]]] = defaultdict(list)
    for b, c, v, t in db.execute("select Book, ChapterBegin, VerseBegin, Comments from Verses"):
        if not t or "OLB" not in t:
            continue
        fonts = {f: name for f, name in FONT.findall(t)}
        kinds = {f: "grk" if "Grk" in n else "heb" for f, n in fonts.items() if "OLB" in n}
        if not kinds:
            continue
        for m in re.finditer(r"\\f(%s) ?([^\\{}]+)" % "|".join(kinds), t):
            run = m[2].strip()
            if run:
                out[(b, c, v)].append((kinds[m[1]], run))
    return out


def put_back(texts: list[str], runs: list[tuple[str, str]], stats: Counter) -> list[str]:
    """Replace each run, in order, at its next whole-word occurrence."""
    texts = list(texts)
    i, pos = 0, 0
    for kind, run in runs:
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(run) + r"(?![A-Za-z])")
        for j in range(i, len(texts)):
            m = pat.search(texts[j], pos if j == i else 0)
            if m:
                new = greek(run) if kind == "grk" else "[Hebrew]"
                texts[j] = texts[j][: m.start()] + new + texts[j][m.end():]
                i, pos = j, m.start() + len(new)
                stats[f"{kind} runs put back"] += 1
                break
        else:
            stats[f"{kind} runs not found in the HTML"] += 1
    return texts


def is_outline(markup: str, book: str, chapter: int) -> bool:
    if re.match(r"\s*<ref>", markup) or re.search(r"<p[^>]*margin-left|^\s*$", markup):
        return True
    plain = html_text(markup)[0]
    if re.match(r"\s*<b>", markup):
        return False
    return bool(re.search(r"<ref>[1-3]?[A-Z][a-z]{1,2}[ _]%d:" % chapter, markup)) and len(plain) < 900


def main() -> None:
    codes = [b["code"] for b in versification()]
    number = {c: i + 1 for i, c in enumerate(codes)}
    runs = rtf_runs()
    _, entries = read_module(HTML)
    # read_module drops the <p style> attributes' context we need, so re-read the raw rows for styles
    stats: Counter = Counter()
    units: dict[str, Unit] = {}

    def add(rng: str, kind: str, paras: list[Para], title: str | None = None) -> None:
        if not paras:
            return
        if rng in units:
            units[rng].paragraphs += paras
            stats[f"text added to an existing {kind} unit"] += 1
        else:
            units[rng] = Unit(rng, kind, title=title, paragraphs=paras)

    for e in entries:
        raw = re.findall(r"<p[^>]*>.*?</p>|[^<]+(?:<(?!p[ >])[^<]*)*", e.text, re.S)
        # Drop the placeholder, and the KJV's subscriptions to the epistles ("<<The second epistle ...>>").
        raw = [
            r for r in raw
            if html_text(r)[0] and "No text from Poole on this verse" not in r
            and not re.fullmatch(r"<<.*>>", html_text(r)[0], re.S)
        ]
        if not raw:
            stats["no text from Poole"] += 1
            continue
        inner = [re.sub(r"^<p[^>]*>|</p>$", "", r, flags=re.S) for r in raw]
        styled = [bool(re.match(r"<p[^>]*(margin-left|font-weight)", r)) for r in raw]
        texts = [html_text(x) for x in inner]
        key = (number[e.book], e.chapter, e.verse)
        if e.verse and key in runs:
            fixed = put_back([t for t, _ in texts], runs[key], stats)
            texts = [(f, r) for f, (_, r) in zip(fixed, texts)]

        if not e.chapter:  # the book's introduction
            paras, title = [], None
            for (text, refs), sty in zip(texts, styled):
                if title is None and sty:
                    title = text.rstrip(".")
                    continue
                paras.append(Para(text, refs, heading=sty and len(text) < 80))
            add(e.book, "book", paras, title)
            continue
        if not e.verse:
            add(f"{e.book}.{e.chapter}", "chapter", [Para(t, r) for t, r in texts])
            continue

        # A chapter's first verse: heading, argument, outline, then the notes.
        start = 0
        if CHAPTER_HEAD.match(inner[0]):
            intro: list[Para] = []
            argument = False
            start = 1
            prev_outline = False
            for k in range(1, len(inner)):
                text, refs = texts[k]
                if re.fullmatch(r"\s*<b>\s*THE ARGUMENT\.?\s*</b>\s*", inner[k]):
                    intro.append(Para("THE ARGUMENT", heading=True))
                    argument, prev_outline = True, False
                elif is_outline(inner[k], e.book, e.chapter) or (styled[k] and not re.match(r"\s*<b>", inner[k])):
                    # Outline lines wrap into several <p>s; one not starting with a reference continues the last.
                    if prev_outline and not re.match(r"\s*<ref>", inner[k]) and styled[k] and intro:
                        intro[-1].text += " " + text
                        intro[-1].refs += refs
                    else:
                        intro.append(Para(text, refs))
                    prev_outline, argument = True, False
                elif argument:
                    intro.append(Para(text, refs))
                else:
                    break
                start = k + 1
            add(f"{e.book}.{e.chapter}", "chapter", intro)
            stats["chapter introductions"] += 1

        notes: list[Para] = []
        for k in range(start, len(inner)):
            text, refs = texts[k]
            verse = anchor = None
            if m := LEMMA.match(inner[k]):
                lemma = html_text(m[2])[0]
                rest = text[text.find(lemma) + len(lemma):] if lemma in text else ""
                if lemma and rest.lstrip(",;:. ") and len(lemma) < 200:
                    anchor = lemma.rstrip(",;:. ")
                    verse = int(m[1]) if m[1] else None
                    text = rest.lstrip(",;:. ")
                    stats["notes with a lemma"] += 1
            if text.strip():
                notes.append(Para(text, refs, anchor=anchor, verse=verse))
        if len(notes) == 1 and notes[0].text.startswith("See Poole on"):
            stats["cross-references (See Poole on ...)"] += 1
        add(e.range_id, "passage", notes)

    all_units = list(units.values())
    problems = check("poole", all_units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write("poole", all_units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
