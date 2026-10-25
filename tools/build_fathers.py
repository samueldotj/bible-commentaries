"""When and where each author quoted in the Early Church Fathers lived, from Wikidata.

`data/fathers.toml` says which Wikidata item each author in en/ecf/ is, and
which city to show when Wikidata's own is not the one the author is known by
(the editorial part). This script asks Wikidata (CC0) for the rest: the years,
the city's name, its modern country and its coordinates, so that no date or
place here is typed from memory. It writes `data/fathers.json`, which
`tools/publish.py` puts on each quotation.

    python tools/build_fathers.py search       # find items for authors not yet in fathers.toml
    python tools/build_fathers.py find Antioch # candidate items for a city, for a `place`
    python tools/build_fathers.py              # write data/fathers.json

`search` adds what it finds with `checked = false`; read the report, correct
the wrong ones, and set `checked = true`. The build uses unchecked entries too,
so a search result reaches the site only through a review of this file.
"""

from __future__ import annotations

import json
import re
import sys
import time
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "data" / "fathers.toml"
OUT = ROOT / "data" / "fathers.json"
API = "https://www.wikidata.org/w/api.php"
UA = {"User-Agent": "tamilscripture-commentary/0.1 (https://www.tamilscripture.com)"}
CIRCA = "Q5727902"
HUMAN = "Q5"
# Words in a Wikidata description that mark an item as one of ours: a church
# writer, a council, an early text.
CHURCHY = re.compile(r"saint|bishop|theolog|church|monk|pope|father|writer|priest|abbot|martyr|ascetic|hermit|"
                     r"patriarch|historian|poet|council|synod|text|apocryph|pseudepigraph|epistle|treatise|liturgy|"
                     r"hymn|deacon|presbyter|scholar|philosoph|apolog|exeget|homil|desert|mystic|heresiarch|gnostic", re.I)


def get(params: dict) -> dict:
    url = f"{API}?{urllib.parse.urlencode({**params, 'format': 'json'})}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as fh:
                return json.load(fh)
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    return {}


def entities(ids) -> dict:
    """Wikidata id → labels, descriptions, claims and the English Wikipedia title."""
    out: dict = {}
    ids = [i for i in dict.fromkeys(ids) if i]
    for i in range(0, len(ids), 40):
        out.update(get({"action": "wbgetentities", "ids": "|".join(ids[i:i + 40]),
                        "props": "labels|descriptions|claims|sitelinks", "languages": "en",
                        "sitefilter": "enwiki"}).get("entities", {}))
        time.sleep(0.2)
    return out


def label(e: dict) -> str | None:
    return e.get("labels", {}).get("en", {}).get("value")


def description(e: dict) -> str:
    return e.get("descriptions", {}).get("en", {}).get("value", "")


def statements(e: dict, prop: str) -> list[dict]:
    """A property's statements, the preferred ones only when there are any, and
    never the deprecated ones."""
    ss = [s for s in e.get("claims", {}).get(prop, []) if s.get("rank") != "deprecated" and s["mainsnak"].get("datavalue")]
    best = [s for s in ss if s.get("rank") == "preferred"]
    return best or ss


def claim_ids(e: dict, prop: str, current: bool = False) -> list[str]:
    """Item values; with `current`, only those with no end time (a city's
    country now, not the empire it once lay in)."""
    out = []
    for s in statements(e, prop):
        if current and "P582" in s.get("qualifiers", {}):
            continue
        v = s["mainsnak"]["datavalue"]["value"]
        if isinstance(v, dict) and "id" in v:
            out.append(v["id"])
    return out


def coord(e: dict) -> tuple[float, float] | None:
    for s in statements(e, "P625"):
        v = s["mainsnak"]["datavalue"]["value"]
        return round(v["latitude"], 4), round(v["longitude"], 4)
    return None


def date(e: dict, prop: str) -> dict | None:
    """The first dated statement: {year, precision, circa}. Year is negative BCE."""
    for s in statements(e, prop):
        v = s["mainsnak"]["datavalue"]["value"]
        if not isinstance(v, dict) or "time" not in v:
            continue
        m = re.match(r"([+-])(\d+)-", v["time"])
        if not m:
            continue
        circa = any(q.get("datavalue", {}).get("value", {}).get("id") == CIRCA
                    for q in s.get("qualifiers", {}).get("P1480", []))
        year = int(m.group(2)) * (-1 if m.group(1) == "-" else 1)
        return {"year": year, "precision": v.get("precision", 9), "circa": circa}
    return None


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def century(d: dict) -> int:
    """Wikidata gives a century as a year inside it (or its last year)."""
    y = abs(d["year"])
    return (y - 1) // 100 + 1 if y % 100 == 0 else y // 100 + 1


def fmt(d: dict, ad: bool = False) -> str:
    """One date as the site shows it: "c. 347", "4th century", "20 BC"."""
    if d["precision"] <= 7:
        return f"{ordinal(century(d))} century" + (" BC" if d["year"] < 0 else "")
    y = d["year"]
    text = f"{-y} BC" if y < 0 else (f"AD {y}" if ad else str(y))
    return ("c. " if d["circa"] or d["precision"] == 8 else "") + text


def lived(e: dict) -> str | None:
    born, died = date(e, "P569"), date(e, "P570")
    # Wikidata sometimes holds dates that contradict each other (born 100,
    # died 99); then only the death is kept, as in the site's build-church.py.
    if born and died and born["year"] >= died["year"]:
        born = None
    if born and died:
        if born["precision"] <= 7 and died["precision"] <= 7:
            a, b = century(born), century(died)
            return f"{ordinal(a)} century" if a == b else f"{ordinal(a)}–{ordinal(b)} century"
        return f"{fmt(born)}–{fmt(died, ad=born['year'] < 0 < died['year'])}"
    if died:
        return f"died {fmt(died)}" if died["precision"] > 7 else fmt(died)
    if born:
        return f"born {fmt(born)}" if born["precision"] > 7 else fmt(born)
    for prop in ("P1317", "P2031"):  # floruit, start of work period
        d = date(e, prop)
        if d:
            return f"fl. {fmt(d)}" if d["precision"] > 7 else fmt(d)
    for prop in ("P585", "P580", "P571", "P577"):  # a council's date, a text's writing
        d = date(e, prop)
        if d:
            return fmt(d)
    return None


def year_of(e: dict) -> int | None:
    """One year in the author's life, for the atlas's timeline: the death, else
    the floruit, else the date of a council or a text, else the birth."""
    for prop in ("P570", "P1317", "P2031", "P585", "P580", "P571", "P577", "P569"):
        d = date(e, prop)
        if d:
            if d["precision"] <= 7:  # the middle of the century
                c = century(d)
                return (c * 100 - 50) * (-1 if d["year"] < 0 else 1)
            return d["year"]
    return None


def module_authors() -> dict[str, int]:
    """Every author in en/ecf/, without the module's notes in parentheses, by
    how many quotations name them."""
    counts: dict[str, int] = {}
    for path in (ROOT / "en" / "ecf").glob("*/*.json"):
        for u in json.loads(path.read_text(encoding="utf-8"))["units"]:
            seen = set()
            for p in u["paragraphs"]:
                if p.get("author") and p.get("quote") not in seen:
                    seen.add(p.get("quote"))
                    name = base_name(p["author"])
                    counts[name] = counts.get(name, 0) + 1
    return counts


def base_name(author: str) -> str:
    """"Origen of Alexandria (is referenced above by Jerome (AD 420))" → "Origen of Alexandria"."""
    return author.split(" (")[0].strip()


def read_roster() -> dict[str, dict]:
    if not ROSTER.exists():
        return {}
    return tomllib.loads(ROSTER.read_text(encoding="utf-8")).get("author", {})


def toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def write_roster(roster: dict[str, dict], counts: dict[str, int]) -> None:
    lines = [
        "# The authors quoted in the Early Church Fathers commentary, and the Wikidata",
        "# item for each. `tools/build_fathers.py` takes their years, city, modern",
        "# country and coordinates from Wikidata into data/fathers.json; nothing",
        "# datable is typed here.",
        "#",
        "#   wikidata = the author's item (or a council's, a text's)",
        "#   place    = the item of the city to show, when Wikidata's work location",
        "#              or place of death is not the one the author is known by",
        "#              (\"none\" when Wikidata's is misleading and there is no better)",
        "#   name     = the author's right name, when the module gives a wrong one",
        "#   none     = why there is no item (an anonymous or pseudonymous writer)",
        "#   checked  = false until someone has confirmed the item is the right one",
        "#",
        "# Ordered by how often the module quotes the author.",
        "",
    ]
    for name in sorted(roster, key=lambda n: (-counts.get(n, 0), n)):
        a = roster[name]
        lines.append(f"[author.{toml_str(name)}]")
        for k in ("wikidata", "place", "name", "none"):
            if a.get(k):
                lines.append(f"{k} = {toml_str(a[k])}")
        if "checked" in a:
            lines.append(f"checked = {'true' if a['checked'] else 'false'}")
        if a.get("note"):
            lines.append(f"# {a['note']}")
        lines.append("")
    ROSTER.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def score(name: str, e: dict) -> int:
    s = 0
    years = [d["year"] for p in ("P569", "P570", "P1317", "P2031", "P571", "P577", "P585") if (d := date(e, p))]
    if years:
        s += 3 if min(years) <= 1100 else -6
    if HUMAN in claim_ids(e, "P31"):
        s += 1
    if CHURCHY.search(description(e)):
        s += 2
    if (label(e) or "").lower() == name.lower():
        s += 1
    return s


def search(name: str) -> list[str]:
    hits = get({"action": "wbsearchentities", "search": name, "language": "en", "type": "item", "limit": 7})
    time.sleep(0.2)
    return [h["id"] for h in hits.get("search", [])]


def cmd_search() -> None:
    counts = module_authors()
    roster = read_roster()
    todo = [n for n in counts if n not in roster]
    print(f"{len(todo)} authors to look up")
    for name in todo:
        ids = search(name)
        if not ids and " of " in name:  # "Haymo of Halberstadt" → "Haymo"
            ids = search(name.split(" of ")[0])
        ent = entities(ids)
        ranked = sorted(((score(name, ent.get(i, {})), i) for i in ids), key=lambda t: -t[0])
        if ranked and ranked[0][0] >= 3:
            q = ranked[0][1]
            e = ent[q]
            roster[name] = {"wikidata": q, "checked": False,
                            "note": f"{label(e)}: {description(e)} ({lived(e) or 'undated'})"}
        else:
            roster[name] = {"none": "not found on Wikidata", "checked": False}
        print(f"  {name}: {roster[name].get('wikidata') or '—'}  {roster[name].get('note', '')}")
    write_roster(roster, counts)


def cmd_find(query: str) -> None:
    ids = search(query)
    ent = entities(ids)
    for i in ids:
        e = ent.get(i, {})
        print(f"{i}  {label(e)}: {description(e)}  {coord(e) or 'no coordinates'}")


def place_of(e: dict, override: str | None) -> str | None:
    """The city to show: the roster's, else the work location, else the place of
    death, else (for a council or a text) its location."""
    if override:
        return None if override == "none" else override
    for prop in ("P937", "P20", "P276", "P291"):
        ids = claim_ids(e, prop)
        if ids:
            return ids[0]
    return None


def cmd_build() -> None:
    counts = module_authors()
    roster = read_roster()
    missing = [n for n in counts if n not in roster]
    if missing:
        print(f"{len(missing)} authors are not in {ROSTER.name}; run `search` first: {missing[:5]}")
    ent = entities(a["wikidata"] for a in roster.values() if a.get("wikidata"))
    places = {n: place_of(ent.get(a.get("wikidata", ""), {}), a.get("place")) for n, a in roster.items()}
    ent.update(entities(q for q in places.values() if q and q not in ent))
    countries = {q: (claim_ids(ent[q], "P17", current=True) or [None])[0] for q in set(places.values()) if q in ent}
    ent.update(entities(c for c in countries.values() if c and c not in ent))

    out: dict = {"_comment": "Written by tools/build_fathers.py from data/fathers.toml and Wikidata (CC0); do not edit."}
    for name in sorted(roster):
        a = roster[name]
        e = ent.get(a.get("wikidata", ""), {})
        row: dict = {}
        if a.get("name"):
            row["name"] = a["name"]
        if e and (when := lived(e)):
            row["lived"] = when
            row["year"] = year_of(e)
        q = places[name]
        pe = ent.get(q or "", {})
        if pe and label(pe):
            city, country = label(pe), label(ent.get(countries.get(q) or "", {}))
            row["place"] = city if not country or country == city or country in city else f"{city}, {country}"
            if c := coord(pe):
                row["lat"], row["lon"] = c
        if a.get("wikidata"):
            row["wikidata"] = a["wikidata"]
        if row:
            out[name] = row
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    rows = [r for k, r in out.items() if not k.startswith("_")]
    print(f"fathers.json: {len(rows)} authors · {sum('lived' in r for r in rows)} dated · "
          f"{sum('place' in r for r in rows)} placed · {sum('lat' in r for r in rows)} on the map")


def main() -> None:
    if sys.argv[1:2] == ["search"]:
        cmd_search()
    elif sys.argv[1:2] == ["find"]:
        cmd_find(" ".join(sys.argv[2:]))
    else:
        cmd_build()


if __name__ == "__main__":
    main()
