"""Read CCEL ThML commentaries (Calvin's calcom01-45.xml).

A comment begins at an empty <scripCom osisRef="Bible:Ps.2.1" type="Commentary"/>
marker and runs to the next marker, or to the next <div1>/<div2> heading,
which starts a new section with its translation table. Text outside any comment
(prefaces, arguments, translation tables, indexes) is returned separately.
A comment is keyed to the verse of its marker; its range runs to the verse before the
next marker in the same chapter.
"""

from __future__ import annotations

import re
from pathlib import Path

from sword import Entry

OSIS = (
    "Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song "
    "Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal "
    "Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas "
    "1Pet 2Pet 1John 2John 3John Jude Rev"
).split()

MARK = re.compile(r'<scripCom[^>]*osisRef="Bible:([1-3]?[A-Za-z]+)\.(\d+)(?:\.(\d+))?[^"]*"[^>]*/>')
SECTION = re.compile(r"<div[12][ >]")


def read_volume(path: Path, codes: list[str]) -> tuple[list[Entry], str]:
    """Comments keyed by verse, and the text that belongs to no comment."""
    text = path.read_text(encoding="utf-8", errors="replace")
    head_end = text.find("</ThML.head>")
    if head_end < 0:
        raise ValueError(f"{path.name}: no </ThML.head>")
    body = text[head_end:]
    to_code = dict(zip(OSIS, codes))
    marks = list(MARK.finditer(body))
    entries: list[Entry] = []
    unkeyed = [body[: marks[0].start()] if marks else body]
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        cut = SECTION.search(body, m.end(), end)
        stop = cut.start() if cut else end
        unkeyed.append(body[stop:end])
        book, chapter, verse = to_code[m[1]], int(m[2]), int(m[3] or 0)
        entries.append(Entry(book, chapter, verse, verse, body[m.end() : stop]))
    for a, b in zip(entries, entries[1:]):
        if a.verse and a.book == b.book and a.chapter == b.chapter and b.verse > a.verse:
            a.verse_end = b.verse - 1
    return entries, "".join(unkeyed)


def read_all(folder: Path, codes: list[str]) -> tuple[list[Entry], str]:
    entries: list[Entry] = []
    unkeyed: list[str] = []
    for path in sorted(folder.glob("calcom*.xml")):
        e, u = read_volume(path, codes)
        entries += e
        unkeyed.append(u)
    return entries, "".join(unkeyed)
