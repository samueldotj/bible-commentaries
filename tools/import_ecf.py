"""Import the Early Church Fathers Commentary (SermonIndex) into en/ecf/.

Each verse gathers quotations from the fathers. A quotation is one or more
<p>: the first opens with the father's name in bold ("<b>Augustine of Hippo
((as quoted by Aquinas, AD 1274))</b>: ..."), the last ends with the work
quoted ("<br/><i>— Tractates on John 11</i>"). Every paragraph carries its
quotation's author, work and number (`quote`), so the site can group them;
"as quoted by Aquinas, AD 1274" is kept as `via`.

    python tools/import_ecf.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from esword import html_text, read_module  # noqa: E402
from sword import ROOT, versification  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

MODULE = ROOT / "cache/esword/Early Church Fathers Commentary.cmti"
AUTHOR = re.compile(r"\s*<b>(.*?)</b>\s*:?\s*", re.S)
WORK = re.compile(r"(?:<br\s*/?>)?\s*<i>\s*—\s*(.*?)</i>\s*$", re.S)
VIA = re.compile(r"\s*\(\((.*?)\)\)\s*$")


def main() -> None:
    last = {b["code"]: b["verses"] for b in versification()}
    _, entries = read_module(MODULE)
    stats: Counter = Counter()
    units: dict[str, Unit] = {}
    for e in entries:
        paras: list[Para] = []
        pending: list[Para] = []  # paragraphs of the quotation being read
        author = via = None
        quote = 0
        for markup in re.findall(r"<p[^>]*>(.*?)</p>", e.text, re.S):
            if m := AUTHOR.match(markup):
                if pending:  # the last quotation had no work line
                    stats["quotations without a work"] += 1
                    paras += pending
                    pending = []
                name = re.sub(r"<[^>]+>", "", m[1]).strip()
                v = VIA.search(name)
                author, via = (VIA.sub("", name).strip(), v[1].strip()) if v else (name, None)
                quote += 1
                markup = markup[m.end():]
            work = None
            if w := WORK.search(markup):
                work = html_text(w[1])[0]
                markup = markup[: w.start()]
            text, refs = html_text(markup)
            if text:
                extra = {"author": author, "quote": quote} if author else {}
                if via:
                    extra["via"] = via
                pending.append(Para(text, refs, extra=extra))
            if work is not None:
                for p in pending:
                    p.extra["work"] = work
                paras += pending
                pending = []
                stats["quotations"] += 1
        paras += pending
        if not paras:
            stats["entries with no text"] += 1
            continue
        chapters = last.get(e.book, [])
        if e.chapter > len(chapters) or e.verse_end > chapters[e.chapter - 1]:
            stats["outside the Protestant canon (Daniel 13-14: Susanna, Bel), dropped"] += 1
            continue
        units[e.range_id] = Unit(e.range_id, "passage", paragraphs=paras)

    all_units = list(units.values())
    problems = check("ecf", all_units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write("ecf", all_units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
