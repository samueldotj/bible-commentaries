"""Import John Trapp from the BibleSupport e-Sword module into en/trapp/.

Each entry is the KJV verse ("1 There was a man..." or "Exo 1:1 And these..."),
which is dropped, then Trapp's notes, each on a phrase of the verse:
"Ver. 1. <b>A ruler of the Jews</b>] Either a chieftain...". Footnotes giving his
Latin and Greek sources follow as "<i>{a}</i> ...", marked {a} in the note.

Some entries are misfiled (Jude's comment sits under Judges 1:19-25), so each
entry's KJV verse is checked against the KJV and the entry re-keyed by it.

    python tools/import_trapp.py
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from esword import html_text, paragraphs, read_module  # noqa: E402
from kjv import normalize, verses  # noqa: E402
from sword import ROOT  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

MODULE = ROOT / "cache/esword/trapp_john_-_complete_commentary_ot_nt.cmti"
KJV_VERSE = re.compile(r"\s*(?:\d+|[1-3]?[A-Z][a-z]{1,2} \d+:\d+)\s+\S")
LEMMA = re.compile(r"\s*(?:Ver\.\s*(\d+)[^.<]*\.\s*)?<b>(.*?)</b>\s*\]\s*", re.S)
VER = re.compile(r"\s*Ver\.\s*(\d+)[^.<]*\.\s*")
FOOTNOTE = re.compile(r"\s*(?:<i>)?\s*\{(\w{1,2})\}\s*(?:</i>)?\s*")


def verse_text(markup: str) -> str:
    """The KJV verse without its number or reference, normalised for comparing."""
    text = html_text(markup)[0]
    text = re.sub(r"^\s*(?:\d+|[1-3]?[A-Z][a-z]{1,2} \d+:\d+)\s+", "", text)
    return normalize(re.sub(r"<<.*?>>|\[|\]", "", text))


def main() -> None:
    kjv = verses()
    by_text: dict[str, list[str]] = defaultdict(list)
    by_number: dict[str, list[str]] = defaultdict(list)
    for vid, text in kjv.items():
        by_text[normalize(text)].append(vid)
        by_number[vid.rsplit(".", 1)[1]].append(vid)
    _, entries = read_module(MODULE)
    stats: Counter = Counter()
    units: dict[str, Unit] = {}
    for e in entries:
        paras = paragraphs(e.text)
        leading = []
        while paras and KJV_VERSE.match(html_text(paras[0])[0]) and not paras[0].lstrip().startswith("Ver."):
            leading.append(paras.pop(0))
        stats["kjv verse paragraphs dropped"] += len(leading)

        rng = e.range_id
        if leading:
            said = verse_text(leading[0])
            own = f"{e.book}.{e.chapter}.{e.verse}"

            def like(vid: str) -> float:
                return difflib.SequenceMatcher(None, said, normalize(kjv.get(vid, ""))).ratio()

            if like(own) < 0.8:
                hits = by_text.get(said) or [
                    max(by_number[str(e.verse)], key=like, default=None)
                ]
                if hits[0] and like(hits[0]) >= 0.8:
                    rng = hits[0]
                    stats["re-keyed by verse text"] += 1
                else:
                    stats["verse text does not match (kept its key)"] += 1
        out: list[Para] = []
        for markup in paras:
            if re.fullmatch(r"<<.*>>", html_text(markup)[0], re.S):
                stats["kjv subscriptions dropped"] += 1
                continue
            if m := FOOTNOTE.match(markup):
                text, refs = html_text(markup[m.end():])
                if text:
                    out.append(Para(text, refs, label=m[1], footnote=True))
                    stats["footnotes"] += 1
                continue
            verse = anchor = None
            if m := LEMMA.match(markup):
                verse = int(m[1]) if m[1] else None
                anchor = html_text(m[2])[0].rstrip(",;: ") or None
                markup = markup[m.end():]
                stats["notes with a lemma"] += 1
            elif m := VER.match(markup):
                verse = int(m[1])
                markup = markup[m.end():]
            text, refs = html_text(markup)
            if not text:
                if anchor:
                    stats["lemma with no note"] += 1
                continue
            out.append(Para(text, refs, anchor=anchor, verse=verse if verse and verse != e.verse or e.verse_end > e.verse else None))
        if not out:
            stats["entries with nothing but the verse"] += 1
            continue
        if rng in units:
            stats["merged into a verse already present"] += 1
            units[rng].paragraphs += out
        else:
            units[rng] = Unit(rng, "passage", paragraphs=out)

    units = list(units.values())
    problems = check("trapp", units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write("trapp", units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
