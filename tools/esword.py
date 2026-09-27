"""Read e-Sword 11 commentary modules (.cmti, SQLite with HTML).

Tables: Details(Title, Abbreviation, Information, Version),
BookCommentary(Book, Comments), ChapterCommentary(Book, Chapter, Comments) and
VerseCommentary(Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd, Comments).
Books are numbered 1-66 in the usual Protestant order.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sword import Entry, versification


def read_module(path: Path) -> tuple[dict[str, str], list[Entry]]:
    codes = [b["code"] for b in versification()]
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    title, abbr, info, version = db.execute("select Title, Abbreviation, Information, Version from Details").fetchone()
    details = {"Title": title, "Abbreviation": abbr, "Information": info or "", "Version": str(version)}

    entries: list[Entry] = []
    for book, text in db.execute("select Book, Comments from BookCommentary order by Book"):
        if text and text.strip():
            entries.append(Entry(codes[book - 1], 0, 0, 0, text))
    for book, ch, text in db.execute("select Book, Chapter, Comments from ChapterCommentary order by Book, Chapter"):
        if text and text.strip():
            entries.append(Entry(codes[book - 1], ch, 0, 0, text))
    rows = db.execute(
        "select Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd, Comments from VerseCommentary"
        " order by Book, ChapterBegin, VerseBegin"
    )
    for book, cb, vb, ce, ve, text in rows:
        if not (text and text.strip()):
            continue
        if ce != cb:
            raise ValueError(f"{path.name}: comment spans chapters {book} {cb}:{vb}-{ce}:{ve}")
        entries.append(Entry(codes[book - 1], cb, vb, max(ve, vb), text))
    return details, entries
