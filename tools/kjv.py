"""The KJV text from the site repository, for checking verse keys.

Geneva's module repeats the KJV verse before its notes, so each entry can be checked
against the verse it is keyed to, and re-keyed when it is misplaced.
"""

from __future__ import annotations

import re
from pathlib import Path

from sword import ROOT

SITE = ROOT.parent / "tamilscripture.com"


def normalize(text: str) -> str:
    """Letters and digits only, lower case, so spacing, hyphens and punctuation don't matter."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def verses(site: Path = SITE) -> dict[str, str]:
    """Verse id (`JHN.3.16`) to plain KJV text."""
    out: dict[str, str] = {}
    for path in sorted((site / "data/versions/kjv").glob("*.usfm")):
        book = path.name[3:6]
        chapter = 0
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\\f .*?\\f\*|\\x .*?\\x\*", "", text, flags=re.S)
        text = re.sub(r'\|[a-z]+="[^"]*"', "", text)  # word attributes: LORD|strong="H3068"
        text = text.replace("¶", " ")
        for m in re.finditer(r"\\c (\d+)|\\v (\d+) ([^\\]*(?:\\(?!c |v )[^\\]*)*)", text):
            if m[1]:
                chapter = int(m[1])
                continue
            body = re.sub(r"\\\+?[a-z]+\d*\*?", " ", m[3])
            out[f"{book}.{chapter}.{m[2]}"] = " ".join(body.split())
    return out
