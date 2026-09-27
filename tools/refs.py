"""Scripture references to site verse ids (`JHN.3.16`, `JHN.3.16-18`, `PSA.23`).

A range across chapters is written `JHN.3.36-4.2`. The site's own ids stop
within one chapter, so it must treat that form separately.
"""

from __future__ import annotations

import re

from ccel import OSIS
from sword import versification

CODES = [b["code"] for b in versification()]
FROM_OSIS = dict(zip(OSIS, CODES))

# Book abbreviations in the Geneva module's <scripRef> elements.
GENEVA = {
    "Ge": "GEN", "Ex": "EXO", "Le": "LEV", "Nu": "NUM", "De": "DEU", "Jos": "JOS", "Jud": "JDG", "Ru": "RUT",
    "1Sa": "1SA", "2Sa": "2SA", "2sa": "2SA", "1Ki": "1KI", "2Ki": "2KI", "1Ch": "1CH", "2Ch": "2CH",
    "Ezr": "EZR", "Ne": "NEH", "Neh": "NEH", "Es": "EST", "Job": "JOB", "Ps": "PSA", "Pr": "PRO", "Ec": "ECC",
    "So": "SNG", "Is": "ISA", "Isa": "ISA", "Jer": "JER", "La": "LAM", "Eze": "EZK", "Da": "DAN", "Dan": "DAN",
    "Ho": "HOS", "Joe": "JOL", "Joel": "JOL", "Am": "AMO", "Ob": "OBA", "Jon": "JON", "Mic": "MIC", "Na": "NAM",
    "Ha": "HAB", "Hab": "HAB", "Zep": "ZEP", "Hag": "HAG", "Zec": "ZEC", "Mal": "MAL",
    "Mt": "MAT", "Mr": "MRK", "Lu": "LUK", "Joh": "JHN", "Ac": "ACT", "Ro": "ROM", "Rom": "ROM",
    "1Co": "1CO", "2Co": "2CO", "Ga": "GAL", "Gal": "GAL", "Eph": "EPH", "Php": "PHP", "Col": "COL",
    "1Th": "1TH", "2Th": "2TH", "1Ti": "1TI", "2Ti": "2TI", "Tit": "TIT", "Phm": "PHM", "He": "HEB",
    "Heb": "HEB", "Jas": "JAS", "1Pe": "1PE", "2Pe": "2PE", "1Jo": "1JN", "2Jo": "2JN", "3Jo": "3JN",
    "Jude": "JUD", "Re": "REV", "Rev": "REV",
}


def osis_to_id(osis_ref: str) -> list[str]:
    """`Gen.1.14-Gen.1.19` -> `GEN.1.14-19`; several refs are separated by spaces."""
    out = []
    for one in osis_ref.split():
        one = one.removeprefix("Bible:")
        start, _, end = one.partition("-")
        s = start.split(".")
        if s[0] not in FROM_OSIS:
            continue
        rid = ".".join([FROM_OSIS[s[0]], *s[1:]])
        if end:
            e = end.split(".")
            if len(s) == 3 and len(e) == 3 and e[:2] == s[:2]:
                rid += f"-{e[2]}"
            elif len(s) == 3 and len(e) == 3 and e[0] == s[0]:
                rid += f"-{e[1]}.{e[2]}"
            elif len(s) == 2 and len(e) == 2 and e[0] == s[0]:
                rid += f"-{e[1]}"
        out.append(rid)
    return out


def geneva_to_ids(text: str) -> list[str]:
    """`Ex 12:14,21:6, De 15:17` -> [`EXO.12.14`, `EXO.21.6`, `DEU.15.17`]; `Nu 12:7,8` -> two verses."""
    out: list[str] = []
    book = chapter = None
    for part in re.split(r"[;,]\s*", text.strip()):
        m = re.fullmatch(r"(?:([1-3]?[A-Za-z]+)\s+)?(?:(\d+):)?(\d+)(?:-(\d+))?", part.strip())
        if not m:
            continue
        if m[1]:
            book = GENEVA.get(m[1])
        if m[2]:
            chapter = m[2]
        if not (book and chapter):
            continue
        out.append(f"{book}.{chapter}.{m[3]}" + (f"-{m[4]}" if m[4] else ""))
    return out
