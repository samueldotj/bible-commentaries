"""Survey the SWORD modules in cache/sword: coverage, units and English words.

Words are counted in the commentator's own text only. Bible text that a
module repeats (the KJV verse in Geneva, the KJV passage heading each section
in Henry) is left out, and Calvin's editors' footnotes and his parallel Latin
translations are counted separately, because they may not be translated.

    python tools/survey.py > survey.md
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ccel  # noqa: E402
import esword  # noqa: E402
from sword import ROOT, Entry, read_module, versification  # noqa: E402

TAG = re.compile(r"<[^>]+>")
PARA = re.compile(r'<div sID="[^"]*" type="x-p"/>(.*?)<div eID="[^"]*" type="x-p"/>', re.S)


def words(markup: str) -> int:
    return len(TAG.sub(" ", markup).split())


def geneva(e: Entry) -> dict[str, int]:
    # "verse text<br /> (a) note (b) note"
    _, _, notes = e.text.partition("<br />")
    return {"comment": words(notes)}


def henry(e: Entry) -> dict[str, int]:
    comment = passage = 0
    for p in PARA.findall(e.text):
        if '<hi type="super">' in p:
            passage += words(p)
        else:
            comment += words(p)
    return {"comment": comment, "kjv passage (dropped)": passage}


def calvin(e: Entry) -> dict[str, int]:
    text = e.text
    notes = sum(words(n) for n in re.findall(r"<note.*?</note>", text, re.S))
    text = re.sub(r"<note.*?</note>", " ", text, flags=re.S)
    tables = sum(words(t) for t in re.findall(r"<table.*?</table>", text, re.S))
    text = re.sub(r"<table.*?</table>", " ", text, flags=re.S)
    return {"comment": words(text), "editors' notes": notes, "translation tables": tables}


def poole(e: Entry) -> dict[str, int]:
    return {"comment": words(e.text)}


P = re.compile(r"<p[^>]*>(.*?)</p>", re.S)


def trapp(e: Entry) -> dict[str, int]:
    # <p>1 KJV verse</p><p>Ver. 1. <b>words</b>] comment {a}</p><p><i>{a}</i> Latin source</p>
    counts = {"comment": 0, "kjv verse (dropped)": 0, "footnotes": 0}
    for p in P.findall(e.text):
        if re.match(r"\s*\d+\s", p):
            counts["kjv verse (dropped)"] += words(p)
        elif re.match(r"\s*<i>\{\w+\}</i>", p):
            counts["footnotes"] += words(p)
        else:
            counts["comment"] += words(p)
    return counts


FATHERS: dict[str, int] = defaultdict(int)


def ecf(e: Entry) -> dict[str, int]:
    # <p><b>Father</b>: quotation<br/><i>— Source work</i></p>, several per verse
    counts = {"comment": 0, "attributions": 0}
    for p in P.findall(e.text):
        name = re.match(r"\s*<b>(.*?)</b>", p)
        if name:
            FATHERS[re.sub(r"\s*\(\(.*", "", name[1]).strip()] += 1
        attr = "".join(re.findall(r"^\s*<b>.*?</b>|<i>\s*— .*?</i>\s*$", p, re.S))
        counts["attributions"] += words(attr)
        counts["comment"] += words(p) - words(attr)
    return counts


MODULES = {
    "geneva": ("sword/Geneva", geneva),
    "henry": ("sword/MHC", henry),
    "calvin": ("ccel", calvin),
    "poole": ("esword/matthew_pool_commentary.cmti", poole),
    "trapp": ("esword/trapp_john_-_complete_commentary_ot_nt.cmti", trapp),
    "ecf": ("esword/Early Church Fathers Commentary.cmti", ecf),
}


UNKEYED: dict[str, str] = {}


def load(path: Path):
    if path.name == "ccel":
        entries, unkeyed = ccel.read_all(path, [b["code"] for b in versification()])
        UNKEYED["ccel"] = unkeyed
        return {"Version": "ThML", "SwordVersionDate": "45 volumes"}, entries
    if path.suffix == ".cmti":
        details, entries = esword.read_module(path)
        return {"Version": details["Version"], "SwordVersionDate": details["Title"]}, entries
    return read_module(path)


def covered_verses(entries: list[Entry]) -> dict[str, set[tuple[int, int]]]:
    out: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for e in entries:
        if e.verse:
            for v in range(e.verse, e.verse_end + 1):
                out[e.book].add((e.chapter, v))
    return out


def main() -> None:
    books = versification()
    print("# Source survey\n")
    print("Written by `python tools/survey.py > sources/survey.md`. Words are the")
    print("commentator's own text; repeated Bible text is not counted.\n")
    for sid, (module, rule) in MODULES.items():
        path = ROOT / "cache" / module
        if not path.exists():
            print(f"## {sid}\n\nNot downloaded: `cache/{module}`\n")
            continue
        conf, entries = load(path)
        totals: dict[str, int] = defaultdict(int)
        per_book: dict[str, int] = defaultdict(int)
        kinds: dict[str, int] = defaultdict(int)
        longest = max(entries, key=lambda e: rule(e)["comment"])
        for e in entries:
            counts = rule(e)
            for k, n in counts.items():
                totals[k] += n
            per_book[e.book] += counts["comment"]
            kinds["book intro" if not e.chapter else "chapter intro" if not e.verse else "verse" if e.verse == e.verse_end else "range"] += 1
        cov = covered_verses(entries)

        print(f"## {sid} ({module} {conf.get('Version')}, {conf.get('SwordVersionDate')})\n")
        print(f"- Units: {len(entries):,} ({', '.join(f'{k} {v:,}' for k, v in sorted(kinds.items()))})")
        for k, n in totals.items():
            print(f"- Words, {k}: {n:,}")
        if path.name in UNKEYED:
            print(f"- Words outside any comment (prefaces, arguments, translation tables, indexes): {words(UNKEYED[path.name]):,}")
        print(f"- Longest unit: {longest.range_id}, {rule(longest)['comment']:,} words")
        print("\n| Book | Verses with a comment | Words |\n|---|---|---|")
        for b in books:
            total = sum(b["verses"])
            n = len(cov.get(b["code"], ()))
            if n or per_book.get(b["code"]):
                print(f"| {b['code']} | {n:,} of {total:,} ({100 * n // total}%) | {per_book[b['code']]:,} |")
        missing = [b["code"] for b in books if not per_book.get(b["code"])]
        print(f"\nNo comment at all: {', '.join(missing) or 'none'}\n")
        if sid == "ecf":
            top = sorted(FATHERS.items(), key=lambda kv: -kv[1])
            print(f"{len(top)} authors. Most quoted: " + ", ".join(f"{k} ({v:,})" for k, v in top[:15]) + "\n")


if __name__ == "__main__":
    main()
