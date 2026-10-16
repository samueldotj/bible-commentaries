"""Import Spurgeon's Treasury of David from the SWORD TDavid module into en/spurgeon/.

The module files a whole psalm under its first verse. Inside, headings
(<title type="x-s">) divide it into Spurgeon's sections:

  OVERVIEW, TITLE, DIVISION, ...      the psalm's introduction
  EXPOSITION                          Spurgeon's comment, "Verse 1." / "Ver. 1." / "Verses 1, 2."
  EXPLANATORY NOTES AND QUAINT SAYINGS  quotations from other writers, each ending
                                      with its author and work in italics
  HINTS TO THE VILLAGE PREACHER       sermon outlines on the verses
  WORKS UPON THE ... PSALM            lists of books (dropped)

Psalm 119 repeats EXPOSITION and NOTES for each verse. Units:

  spurgeon/PSA          the preface
  spurgeon/PSA.23       the overview and its kin, then the notes and hints on the whole psalm
  spurgeon/PSA.23.1     the exposition of a verse (or of the verses it groups),
                        then the notes and hints on those verses

Every paragraph has "section": overview, exposition, notes or hints, and a heading
opens the notes and the hints in each unit. A note's author and work are taken
out of its text into "author" and "work", with "quote" numbering the notes of a
unit, as the Early Church Fathers are. The verse label is taken out of the text
into "verse" ("verse_end" for a range), and the italic words of the verse that
follow it into "anchor", as Calvin's are.

    python tools/import_spurgeon.py
"""

from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refs import osis_to_id  # noqa: E402
from sword import ROOT, read_module, versification  # noqa: E402
from units import Para, Unit, check, write  # noqa: E402

SOURCE = "spurgeon"
TITLE = re.compile(r'<title type="x-s">(.*?)</title>', re.S)
TOKEN = re.compile(r"<reference[^>]*>.*?</reference>|<[^>]+>|[^<]+", re.S)
I0, I1 = "\x01", "\x02"  # italic start and end, until the label and anchor are found

# Heading → section; anything else in the introduction stays as a heading of its own.
SECTIONS = [
    ("EXPOSITION", "exposition"),
    ("EXPLANATORY NOTES AND QUAINT SAYINGS", "notes"),
    ("NOTES RELATING TO THE PSALM AS A WHOLE", "notes"),
    ("HINTS TO THE VILLAGE PREACHER", "hints"),
    ("HINTS TO PREACHERS", "hints"),
]
HEADINGS = {"notes": "Explanatory Notes and Quaint Sayings", "hints": "Hints to the Village Preacher"}
LABEL = re.compile(
    rf"^\s*(?:{I0}\s*)?(Whole Psalm|Verses?|Ver\.?|Vers\.)\s*"
    rf"(\d+(?:\s*(?:[-–,&]|and|to)\s*\d+)*)?\s*\.?\s*(?:{I1})?\s*"
)
ATTRIBUTION = re.compile(rf"\s*{I0}([^{I0}{I1}]+){I1}\s*,?\s*(\d{{4}}[^.]*\.?|\([^)]*\d{{4}}[^)]*\)\.?)?\s*$")
INLINE_LABEL = re.compile(r'<hi type="(?:italic|bold)">\s*(?:Whole Psalm|Verses?|Ver\.?)\s*[\d,\-– and]*\.?\s*</hi>')
PARTICLES = {"of", "in", "the", "de", "du", "van", "von", "der", "and", "à", "a", "le", "la", "from", "on", "upon", "by", "st", "an"}
NOTE_LABEL = re.compile(r"^(?:[A-Z][a-z]+(?: [A-Z][a-z]+)?)[.:] ")  # "Eulogium.", "Alphabetical Arrangement."
JUNK = re.compile(r"^(Psalms? \d+:\d+\*?|Continued\.\.\..*)$")


def clean(text: str) -> str:
    text = html.unescape(text).replace(" ", " ")
    text = re.sub(r"\s*•\s*$", "", text, flags=re.M)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r" +([,.;:?!)])", r"\1", text)
    return text.strip()


def pieces(markup: str) -> list[tuple[str, list[dict]]]:
    """A section's paragraphs as (text with italic marks, refs). A list or a
    poem is its own piece, its lines joined with "\\n"."""
    out: list[tuple[str, list[dict]]] = []
    buf: list[str] = []
    refs: list[dict] = []
    # Notes often run on in one paragraph, each opening with its label: start a piece there.
    markup = INLINE_LABEL.sub(r'<div type="x-p"/>\g<0>', markup)

    def flush() -> None:
        nonlocal buf, refs
        text = clean("".join(buf))
        if text.replace(I0, "").replace(I1, "").strip():
            out.append((text, refs))
        buf, refs = [], []

    for tok in TOKEN.findall(markup):
        if tok.startswith("<reference"):
            inner = clean(re.sub(r"<[^>]+>", "", tok))
            osis = re.search(r'osisRef="([^"]*)"', tok)
            for rid in osis_to_id(osis[1]) if osis else []:
                refs.append({"text": inner, "ref": rid})
            buf.append(inner)
        elif re.match(r'<div [^>]*type="x-p"', tok) or tok in ("<list>", "</list>") or tok.startswith("<lg"):
            flush()
        elif tok.startswith("</item>") or (tok.startswith("<l ") and "eID=" in tok):
            buf.append("\n")
        elif tok == '<hi type="italic">':
            buf.append(I0)
        elif tok == "</hi>":
            # Close an italic run if one is open; bold runs leave no mark.
            text = "".join(buf)
            if text.rfind(I0) > text.rfind(I1):
                buf.append(I1)
        elif tok.startswith("<"):
            continue
        else:
            buf.append(tok)
    flush()
    return out


def plain(text: str) -> str:
    return clean(text.replace(I0, "").replace(I1, ""))


BOUNDARY = re.compile(r"[.?!][\"”’]?\s+")


def name_like(s: str, min_words: int = 1) -> bool:
    """A writer's name as Spurgeon cites it: capitalised words, initials, degrees, particles,
    a year, and quoted titles ("J. R. Macduff, D.D., in "The Shepherd and his Flock," 1866")."""
    words = re.sub(r"[\"“][^\"”]*[\"”]?", " ", s).replace(",", " ").split()
    if not min_words <= len(words) <= 14 or len(s) > 160:
        return False
    if words[-1].strip(".").lower() in PARTICLES:
        return False
    for w in words:
        core = w.strip("().;:'’")
        if not core or core.lower().removesuffix("'s") in PARTICLES or core == "&":
            continue
        if re.fullmatch(r"\d{4}(-\d{4})?\.?|([A-Z]\.)+[A-Za-z]*\.?|[A-Z]\.?", core):
            continue
        if not core[0].isupper() or core.isupper() and len(core) > 4:  # "LORD": a verse, not a name
            return False
    return True


def name_tail(text: str, min_words: int) -> int | None:
    """Where a name that ends the text begins: the leftmost sentence end after which
    everything is name-like, so "... fly, run, march. E.W. Hengstenberg" gives "E.W. Hengstenberg"."""
    start = None
    for m in reversed(list(BOUNDARY.finditer(text))):
        if name_like(text[m.end():].rstrip(" ."), min_words):
            start = m.end()
        elif start is not None:
            break
    return start


def plain_attribution(text: str) -> tuple[str, str] | None:
    """Psalm 119 sets a note's author in roman type: "... frame of his heart. Thomas Manton."
    Two words at least, so that a closing "Amen." is not taken for an author."""
    if not text.endswith("."):
        return None
    k = name_tail(text, 2)
    return (text[:k].rstrip(), text[k:].strip()) if k is not None else None


def citation(body: str, cite: str, year: str) -> tuple[str, str, str] | None:
    """A note's text, author and work from the italic (or roman) line that ends it:
    'John Hull, B.D., in "Lectures on Lamentations,"' 1617, 'Samuel Smith's "Chiefe Shepheard,"',
    'Thomas Scott, in' + '"Plain Commentary"' (the name in roman before the title),
    "Condensed from a Sermon by Edward Payson". None when it is not a citation (a verse in italics)."""
    cite = re.sub(r"^From\s+", "", cite.strip(" ,—-"))
    # The italics sometimes begin inside the note: "... desires. Thomas Watson".
    if not name_like(cite.rstrip(" .")) and (k := name_tail(cite, 1)) is not None:
        body, cite = f"{body} {cite[:k].strip()}".strip(), cite[k:]
    work_first = None
    if m := re.match(r"(?:Condensed |Abridged )?from (.*?),? by ([A-Z].*)$", cite, re.I):
        work_first, cite = m[1], m[2]
    elif m := re.match(r"(?:the )?(French|German|Latin|Dutch|Italian) of (.*)$", cite):
        work_first, cite = f"from the {m[1]}", m[2]
    # Only the work in italics: the author is at the end of the roman text.
    if re.match(r"(?:in|on|dans)\b|[\"“]", cite):
        title = re.sub(r"^(?:in|on|dans)\.?,?\s+", "", cite)
        if not name_like(re.sub(r"[\"“”,.]", " ", title)):  # a verse in quotes, not a title
            return None
        m = re.search(r"([A-Z][\w.' -]{2,60}?)(?:,? (?:in|on)\.?,?|'s),?\s*$", body)
        before = body[: m.start(1)].rstrip() if m else ""
        if m and (not before or before[-1] in ".?!\"”’") and name_like(m[1].rstrip(" .,")):
            body, cite = before, f"{m[1].rstrip(' ,')} in {title}"
        else:
            return body.strip(), "", ", ".join(x for x in (title.strip(' ,."“”'), year.strip(" .")) if x)
    if not re.search(r"\b[A-Z]\.[A-Z]\.$", cite):  # keep the stop of "D.D."
        cite = cite.rstrip(" .")
    if not year and (y := re.search(r",?\s*\(?(\d{4})\)?\.?$", cite)):
        cite, year = cite[: y.start()], y[1]
    m = re.match(r"(.*?)(?:,? in\.?,? |'s |, on )(.*)", cite)
    who, work = (m[1], m[2]) if m else (cite, "")
    who = who.strip(" ,—-")
    if not name_like(who):
        return None
    work = ", ".join(x for x in (work_first, work.strip(' ,."“”'), year.strip(" .")) if x)
    if not re.search(r"\b[A-Z]\.[A-Z]\.?$", who):
        who = who.rstrip(" .,")
    elif not who.endswith("."):
        who += "."
    return body.strip(), who, work


def verses(spec: str | None, last: int) -> tuple[int, int] | None:
    nums = [int(n) for n in re.findall(r"\d+", spec or "")]
    nums = [n for n in nums if 1 <= n <= last]
    return (min(nums), max(nums)) if nums else None


def split_sections(text: str, stats: Counter) -> list[tuple[str, str | None, str]]:
    """(section, heading or None, markup) in order."""
    parts = TITLE.split(text)
    out = [("overview", None, parts[0])]
    for raw, body in zip(parts[1::2], parts[2::2]):
        name = clean(re.sub(r"<[^>]+>", "", raw))
        name = re.sub(r"^Psalms? \d+\s*", "", name).strip()
        section, rest = None, ""
        for prefix, sec in SECTIONS:
            if name.upper().startswith(prefix):
                section = sec
                rest = re.sub(r"^\s*" + r"\s+".join(map(re.escape, prefix.split())) + r"\.?", "",
                              re.sub(r"^\s*Psalms? \d+\s*", "", raw), count=1)
                break
        if section is None and re.match(r"WORKS? UPON", name, re.I):
            stats["book lists dropped (WORKS UPON THE ... PSALM)"] += 1
            continue
        if section is None and out[-1][0] != "overview":
            # "TITLE." inside the notes (notes on the psalm's title): still the notes.
            out.append((out[-1][0], None, body))
            continue
        if section is None:
            heading = None if name.upper() in ("OVERVIEW", "") else name.rstrip(".").title()
            out.append(("overview", heading, body))
            continue
        rest = re.sub(r"^\s*\(([^)]*)\)\s*", r"\1 ", rest)  # "EXPOSITION (The Reader is referred ...)"
        out.append((section, None, rest + " <div type=\"x-p\"/> " + body))
    return out


def main() -> None:
    last = {c: n for c, n in enumerate(next(b for b in versification() if b["code"] == "PSA")["verses"], 1)}
    _, entries = read_module(ROOT / "cache/sword/TDavid")
    stats: Counter = Counter()
    all_units: list[Unit] = []

    preface = Unit("PSA", "book")
    for e in entries:
        if e.chapter == 0:
            for text, refs in pieces(e.text):
                if plain(text) == "Preface":
                    preface.paragraphs.append(Para("Preface", heading=True, extra={"section": "overview"}))
                else:
                    preface.paragraphs.append(Para(plain(text), refs, extra={"section": "overview"}))
    all_units.append(preface)

    for n in range(1, 151):
        text = "".join(e.text for e in entries if e.chapter == n)
        intro = Unit(f"PSA.{n}", "chapter")
        passages: dict[str, Unit] = {}
        spans: list[tuple[int, int, str]] = []
        # Paragraphs collected per unit and section, put in order at the end.
        collected: dict[str, dict[str, list[Para]]] = {}

        def add(unit: Unit, section: str, p: Para) -> None:
            collected.setdefault(unit.range, {}).setdefault(section, []).append(p)

        def unit_for(lo: int, hi: int, create: bool) -> Unit:
            for a, b, rng in spans:
                if a <= lo <= b:
                    return passages[rng]
            rng = f"PSA.{n}.{lo}" + (f"-{hi}" if hi > lo and create else "")
            if not create:
                rng = f"PSA.{n}.{lo}"
                stats[f"notes or hints on a verse with no exposition (unit of its own)"] += 1
                hi = lo
            passages[rng] = Unit(rng, "passage")
            spans.append((lo, hi, rng))
            return passages[rng]

        for section, heading, markup in split_sections(text, stats):
            current: Unit = intro
            if heading:
                add(intro, "overview", Para(heading, heading=True))
            pending: list[Para] = []  # paragraphs of the note being read
            for raw, refs in pieces(markup):
                if JUNK.match(plain(raw)):
                    stats["page markers dropped (Psalms 119:2*, Continued...)"] += 1
                    continue
                if section != "overview" and re.fullmatch(r"\W*", plain(raw)):
                    continue
                p = Para("", refs)
                m = LABEL.match(raw)
                if section == "notes" and pending and (m or NOTE_LABEL.match(plain(raw))):
                    # A new note begins: the one before had no author.
                    for q in pending:
                        stats["note paragraphs without an author"] += 1
                        add(current, "notes", q)
                    pending = []
                if m and section != "overview":
                    if m[1] == "Whole Psalm":
                        current = intro
                    else:
                        span = verses(m[2], last[n])
                        if span is None:
                            stats["verse labels without a verse of the psalm"] += 1
                        else:
                            if section == "exposition" and n == 119 and span[1] > span[0]:
                                # A stanza's introduction ("Verses 17-24") sits with its first verse.
                                current = unit_for(span[0], span[0], create=True)
                            elif section == "exposition":
                                existing = next((passages[r] for a, b, r in spans if a == span[0]), None)
                                current = existing or unit_for(span[0], span[1], create=True)
                            else:
                                current = unit_for(span[0], span[1], create=False)
                            p.verse = span[0]
                            if span[1] > span[0]:
                                p.extra["verse_end"] = span[1]
                    raw = raw[m.end():]
                    a = re.match(rf"\s*{I0}([^{I0}{I1}]+){I1}\s*", raw)
                    if a and len(a[1]) < 200:
                        p.anchor = plain(a[1]).strip(" \"“”‘’'.,;:")
                        raw = raw[a.end():]
                        stats["anchors"] += 1
                elif section == "exposition" and current is intro and spans:
                    current = passages[spans[-1][2]]
                if section == "notes":
                    at = ATTRIBUTION.search(raw)
                    found = None
                    if at and len(at[1]) < 160 and plain(raw[: at.start()]):
                        found = plain(raw[: at.start()]), plain(at[1]), (at[2] or "")
                    elif pa := plain_attribution(plain(raw)):
                        found = pa[0], pa[1], ""
                        stats["authors in roman type (Psalm 119)"] += 1
                    if found and (cited := citation(*found)):
                        body, who, work = cited
                        if not who:
                            stats["notes citing only a work"] += 1
                        p.text = body
                        pending.append(p)
                        quote = sum(1 for q in collected.get(current.range, {}).get("notes", []) if q.extra.get("author")) + 1
                        for q in pending:
                            q.extra["quote"] = quote
                            if who:
                                q.extra["author"] = who
                            if work:
                                q.extra["work"] = work
                        stats["notes with an author"] += 1
                        for q in pending:
                            add(current, "notes", q)
                        pending = []
                        continue
                    p.text = plain(raw)
                    if p.text:
                        pending.append(p)
                    continue
                p.text = plain(raw)
                if p.text:
                    add(current, section, p)
            for q in pending:
                stats["note paragraphs without an author"] += 1
                add(current, "notes", q)

        for u in [intro, *sorted(passages.values(), key=lambda u: u.first_verse)]:
            got = collected.get(u.range, {})
            for section in ("overview", "exposition", "notes", "hints"):
                paras = got.get(section, [])
                if not paras:
                    continue
                if section in HEADINGS:
                    u.paragraphs.append(Para(HEADINGS[section], heading=True))
                    u.paragraphs[-1].extra["section"] = section
                for p in paras:
                    p.extra["section"] = section
                    u.paragraphs.append(p)
            if u.paragraphs:
                all_units.append(u)
                stats[f"{u.kind} units"] += 1
            else:
                stats["units with no text (dropped)"] += 1

    covered = Counter()
    for u in all_units:
        if u.kind == "passage":
            _, c, vs = u.range.split(".")
            lo, _, hi = vs.partition("-")
            for v in range(int(lo), int(hi or lo) + 1):
                covered[(int(c), v)] += 1
    missing = [f"{c}:{v}" for c in last for v in range(1, last[c] + 1) if (c, v) not in covered]
    stats["verses in no passage unit"] = len(missing)
    print("verses in no passage unit:", " ".join(missing))
    stats["verses in two passage units"] = sum(1 for k in covered.values() if k > 1)
    problems = check(SOURCE, all_units)
    for p in problems[:40]:
        print("PROBLEM", p)
    counts = write(SOURCE, all_units)
    for k, v in sorted(stats.items()):
        print(f"{k}: {v:,}")
    print(", ".join(f"{k} {v:,}" for k, v in counts.items()))
    if problems:
        print(f"{len(problems)} problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
