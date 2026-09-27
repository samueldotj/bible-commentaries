"""Write data/kjv-versification.json from the KJV USFM in the site repository.

SWORD modules with Versification=KJV index one entry per verse in this order,
so the reader needs the number of verses in every chapter.

    python tools/make_versification.py ../tamilscripture.com
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "tamilscripture.com")
    books_toml = (site / "data/books.toml").read_text(encoding="utf-8")
    codes = re.findall(r'^code = "([0-9A-Z]{3})"', books_toml, flags=re.M)
    usfm = {p.name[3:6]: p for p in (site / "data/versions/kjv").glob("*.usfm")}

    books = []
    for code in codes:
        chapters: list[int] = []
        for line in usfm[code].read_text(encoding="utf-8").splitlines():
            if m := re.match(r"\\c (\d+)", line):
                assert int(m[1]) == len(chapters) + 1, (code, line)
                chapters.append(0)
            for v in re.findall(r"\\v (\d+)", line):
                chapters[-1] = max(chapters[-1], int(v))
        books.append({"code": code, "verses": chapters})

    assert len(books) == 66
    out = ROOT / "data/kjv-versification.json"
    out.parent.mkdir(exist_ok=True)
    lines = [json.dumps(b, separators=(",", ":")) for b in books]
    out.write_text("[\n" + ",\n".join(lines) + "\n]\n", encoding="utf-8", newline="\n")
    ot = sum(sum(b["verses"]) for b in books[:39])
    nt = sum(sum(b["verses"]) for b in books[39:])
    print(f"wrote {out.relative_to(ROOT)}: OT {ot} verses, NT {nt} verses")


if __name__ == "__main__":
    main()
