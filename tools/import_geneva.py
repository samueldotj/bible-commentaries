"""Import the Geneva notes from the SWORD module into en/geneva/.

Each entry is the KJV verse with note markers ({a}, {1}), then the notes:
"(a) ... (b) ...". The first verse of a book also carries "The Argument".
Some entries sit under the wrong key (the last verse of a chapter stored at the
next chapter's first slot), so each is checked against the KJV and re-keyed by
its verse text.

    python tools/import_geneva.py
"""

from __future__ import annotations

import difflib
import html
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kjv import normalize, verses  # noqa: E402
from refs import geneva_to_ids  # noqa: E402
from sword import ROOT, read_module, versification  # noqa: E402
from units import Para, Unit, check, split_long, write  # noqa: E402

MARKER = re.compile(r"\{(\w{1,2})\}")
REF = re.compile(r"<scripRef>(.*?)</scripRef>", re.S)


def plain(markup: str) -> tuple[str, list[dict]]:
    refs = []
    for m in REF.finditer(markup):
        text = " ".join(m[1].split())
        for rid in geneva_to_ids(text):
            refs.append({"text": text, "ref": rid})
    text = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", " ", markup)))
    text = re.sub(r"\s+([,.;:?!)])", r"\1", " ".join(text.split()))
    return text, refs


def anchor(verse: str, label: str) -> str | None:
    """The words after the marker, up to the next marker or punctuation, at most six words."""
    m = re.search(r"\{" + re.escape(label) + r"\}\s*(.*)", verse)
    if not m:
        return None
    rest = MARKER.split(m[1])[0]
    rest = re.split(r"[,;:.?!()]", rest)[0].replace("[", "").replace("]", "")
    words = rest.split()[:6]
    return " ".join(words) or None


NOTE_START = re.compile(r"(?:^|(?<=\s))[({](\w{1,2})[)}]\s")


def split_notes(notes: str, labels: list[str], stats: Counter) -> list[tuple[str | None, str]]:
    """(label, text) pairs. A note starts with its label, "(a)", or "{a}" in a few entries."""
    out: list[tuple[str | None, str]] = []
    starts = list(NOTE_START.finditer(notes))
    stats["note label with no marker in the verse"] += sum(1 for m in starts if m[1] not in labels)
    if not starts:
        if notes.strip():
            stats["notes without a label"] += 1
            out.append((None, notes.strip()))
        return out
    if notes[: starts[0].start()].strip():
        stats["text before the first note"] += 1
        out.append((None, notes[: starts[0].start()].strip()))
    for i, m in enumerate(starts):
        stop = starts[i + 1].start() if i + 1 < len(starts) else len(notes)
        text = notes[m.end() : stop].strip()
        if text:
            out.append((m[1], text))
        else:
            stats["empty note"] += 1
    found = {m[1] for m in starts}
    stats["marker without a note"] += sum(1 for x in labels if x not in found)
    return out


def main() -> None:
    kjv = verses()
    by_text: dict[str, list[str]] = defaultdict(list)
    for vid, t in kjv.items():
        by_text[normalize(t)].append(vid)

    last_verse = {(b["code"], c): n for b in versification() for c, n in enumerate(b["verses"], 1)}
    _, entries = read_module(ROOT / "cache/sword/Geneva")
    stats: Counter = Counter()
    units: dict[str, Unit] = {}

    for e in entries:
        raw = e.text
        labels = MARKER.findall(raw.split("<br")[0])
        if "<br" in raw:
            head, _, rest = raw.partition("<br />")
        else:
            first = min((raw.find(f"({x})") for x in labels if f"({x})" in raw), default=-1)
            head, rest = (raw[:first], raw[first:]) if first > 0 else (raw, "")
            stats["notes without <br />"] += 1
        labels = MARKER.findall(head)
        verse_plain = normalize(re.sub(r"\{\w+\}|<[^>]+>|\[|\]", "", head))

        # Which verse is this really?
        own = f"{e.book}.{e.chapter}.{e.verse}"
        rng = e.range_id if e.verse else None
        def like(vid: str) -> float:
            return difflib.SequenceMatcher(None, verse_plain, normalize(kjv.get(vid, ""))).ratio()

        if not (e.verse and like(own) > 0.85):
            hits = by_text.get(verse_plain)
            # The usual misplacement: the previous chapter's last verse, in modernised wording.
            prev = e.chapter - 1
            prev_last = f"{e.book}.{prev}.{last_verse.get((e.book, prev), 0)}" if prev > 0 else ""
            if hits:
                rng = hits[0]
                stats["re-keyed by verse text"] += 1
            elif prev_last and like(prev_last) > 0.7 and like(prev_last) > like(own):
                rng = prev_last
                stats["re-keyed to the previous chapter's last verse"] += 1
            elif e.verse:
                stats["verse text does not match (kept its key)"] += 1
            else:
                stats["chapter entry with no matching verse (dropped)"] += 1
                continue
        book = rng.split(".")[0]

        notes = ""
        for part in rest.split("<br />"):
            text, refs = plain(part)
            if not text:
                continue
            if text.startswith("The Argument"):
                body = re.sub(r"^The Argument\s*[-—–:]?\s*", "", text)
                u = units.setdefault(book, Unit(book, "book", title="The Argument"))
                u.paragraphs += [Para(p, [r for r in refs if r["text"] in p]) for p in split_long(body)]
                stats["arguments"] += 1
            else:
                notes += " " + part

        if not notes.strip():
            stats["verse with no notes"] += 1
            continue
        paras = []
        for label, text_markup in split_notes(notes, labels, stats):
            text, refs = plain(text_markup)
            paras.append(Para(text, refs, label=label, anchor=anchor(head, label) if label else None))
        stats["notes"] += len(paras)
        if rng in units:
            existing = {p.text for p in units[rng].paragraphs}
            new = [p for p in paras if p.text not in existing]
            units[rng].paragraphs += new
            stats["merged into a verse already present"] += 1
        else:
            units[rng] = Unit(rng, "passage", paragraphs=paras)

    problems = check("geneva", list(units.values()))
    for p in problems:
        print("PROBLEM", p)
    counts = write("geneva", list(units.values()))
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
