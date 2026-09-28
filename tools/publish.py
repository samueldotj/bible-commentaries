"""Publish the commentaries for tamilscripture.com: build the site's JSON, upload it to R2.

    python tools/publish.py build            # dist/commentary/{version}/, no network
    python tools/publish.py upload --dry-run  # what would be uploaded
    python tools/publish.py upload            # new version's files, then latest.json

What the site reads, under the public base URL (e.g. https://cdn.tamilscripture.com):

    commentary/latest.json                          {"version": "3f2a…", "published": "…"}  (5-minute cache)
    commentary/{version}/index.json                 the sources, and the chapters each one covers
    commentary/{version}/{source}/{BOOK}/{ch}.json  one chapter of one commentary (intro.json: the book's)

The version is a hash of every file under it, so files under a version never
change (cached for a year), and publishing new text is a new version plus a new
latest.json; the site needs no deploy. A chapter file is the English from en/
with any Tamil draft (ta/, ta-ecf/) merged in as "ta" on each paragraph, as the
site's dictionary articles have it.

R2 credentials, as for the site's audio (tools/audio): R2_ACCOUNT_ID,
R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY from the environment, or from
.env.audio in the site repository next to this one. R2_COMMENTARY_BUCKET names
the bucket (default: the audio bucket, ts-audio) and R2_COMMENTARY_PREFIX the
folder in it (default: commentary).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sword import ROOT, versification  # noqa: E402

DIST = ROOT / "dist" / "commentary"
SITE = ROOT.parent / "tamilscripture.com"
IMMUTABLE = "public, max-age=31536000, immutable"
LATEST = "public, max-age=300"

# What the site shows about each commentary. `licence` and `attribution` appear
# beside the text; the Tamil drafts of the public-domain ones are CC BY.
SOURCES = [
    {"id": "henry", "name": "Matthew Henry", "short": "M. Henry", "year": "1706",
     "title": "Commentary on the Whole Bible",
     "desc_ta": "பக்திக்குரிய விளக்கம், பகுதி பகுதியாக", "desc_en": "Devotional, section by section",
     "licence": "Public domain", "attribution": "Matthew Henry, Commentary on the Whole Bible (1708–1710); text from CCEL via the SWORD Project"},
    {"id": "calvin", "name": "John Calvin", "short": "Calvin", "year": "1540–1564",
     "title": "Commentaries",
     "desc_ta": "சீர்திருத்த விளக்கம், வசனம் வசனமாக", "desc_en": "Reformation exposition, verse by verse",
     "licence": "Public domain", "attribution": "John Calvin, Commentaries, tr. Calvin Translation Society (1843–1855); text from CCEL"},
    {"id": "geneva", "name": "Geneva Bible notes", "short": "Geneva", "year": "1599",
     "title": "Geneva Bible marginal notes",
     "desc_ta": "சுருக்கமான ஓரக் குறிப்புகள்", "desc_en": "Short marginal notes",
     "licence": "Public domain", "attribution": "Geneva Bible notes (1599); text from the SWORD Project"},
    {"id": "poole", "name": "Matthew Poole", "short": "Poole", "year": "1685",
     "title": "Annotations upon the Holy Bible",
     "desc_ta": "சொல் சொல்லாகக் குறிப்புகள்", "desc_en": "Notes on the words of each verse",
     "licence": "Public domain", "attribution": "Matthew Poole, Annotations upon the Holy Bible (1683–1685); e-Sword module by BibleSupport.com"},
    {"id": "trapp", "name": "John Trapp", "short": "Trapp", "year": "1656",
     "title": "A Commentary upon the Old and New Testaments",
     "desc_ta": "சுருக்கமும் சுவையுமான குறிப்புகள்", "desc_en": "Pithy notes, rich in illustration",
     "licence": "Public domain", "attribution": "John Trapp, Commentary (1647–1656), ed. Webster and Martin; e-Sword module by BibleSupport.com"},
    {"id": "ecf", "name": "Early Church Fathers", "short": "Fathers", "year": "100–1000",
     "title": "Early Church Fathers Commentary",
     "desc_ta": "திருச்சபைப் பிதாக்களின் மேற்கோள்கள்", "desc_en": "Quotations from the church fathers",
     "licence": "Free to copy, share and distribute for personal and ministry purposes",
     "attribution": "Early Church Fathers Commentary, compiled by SermonIndex.net"},
]
DRAFT_FOLDERS = ("ta", "ta-ecf")


def book_order() -> dict[str, int]:
    return {b["code"]: i for i, b in enumerate(versification())}


def drafts_for(source: str, book: str, name: str) -> dict[str, dict]:
    """Tamil drafts of one chapter file, by unit id."""
    for folder in DRAFT_FOLDERS:
        p = ROOT / folder / source / book / name
        if p.exists():
            return {u["id"]: u for u in json.loads(p.read_text(encoding="utf-8"))["units"]}
    return {}


def chapter_doc(path: Path) -> dict:
    """The site's file for one chapter: the English units, Tamil merged in where a
    current draft exists (its source_hash matches the English)."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    ta = drafts_for(doc["source"], doc["book"], path.name)
    units = []
    for u in doc["units"]:
        d = ta.get(u["id"])
        current = d is not None and d.get("source_hash") == u.get("hash")
        u = {k: v for k, v in u.items() if k != "hash"}
        if current:
            by_id = {p["id"]: p for p in d.get("paragraphs", [])}
            for p in u["paragraphs"]:
                if p["id"] in by_id:
                    p["ta"] = by_id[p["id"]]["text"]
                    if by_id[p["id"]].get("anchor"):
                        p["anchor_ta"] = by_id[p["id"]]["anchor"]
                    p["ta_source"] = "draft"
            if d.get("title"):
                u["title_ta"] = d["title"]
        units.append(u)
    return {"source": doc["source"], "book": doc["book"], "chapter": doc["chapter"], "units": units}


def build() -> tuple[str, Path]:
    """Write dist/commentary/{version}/; return the version and its folder."""
    order = book_order()
    files: dict[str, bytes] = {}
    chapters: dict[str, dict[str, list[int]]] = {}
    for s in SOURCES:
        src_dir = ROOT / "en" / s["id"]
        if not src_dir.exists():
            continue
        cover: dict[str, list[int]] = {}
        for path in sorted(src_dir.glob("*/*.json"), key=lambda p: (order[p.parent.name], 0 if p.stem == "intro" else int(p.stem))):
            doc = chapter_doc(path)
            rel = f"{s['id']}/{path.parent.name}/{path.name}"
            files[rel] = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            cover.setdefault(path.parent.name, []).append(0 if path.stem == "intro" else int(path.stem))
        chapters[s["id"]] = cover
    index = {"sources": [s for s in SOURCES if s["id"] in chapters], "chapters": chapters}
    files["index.json"] = json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode())
        h.update(hashlib.sha256(files[rel]).digest())
    version = h.hexdigest()[:12]

    out = DIST / version
    if out.exists():
        shutil.rmtree(out)
    for rel, data in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (DIST / "latest.json").write_text(json.dumps({"version": version, "published": datetime.now(timezone.utc)
                                                  .isoformat(timespec="seconds")}) + "\n", encoding="utf-8")
    size = sum(len(b) for b in files.values())
    print(f"version {version}: {len(files):,} files, {size / 1e6:.0f} MB, in {out.relative_to(ROOT)}")
    return version, out


def env() -> dict[str, str]:
    e: dict[str, str] = {}
    dotenv = SITE / ".env.audio"
    if dotenv.exists():
        for line in dotenv.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                e[k.strip()] = v.strip().strip('"').strip("'")
    e.update({k: v for k, v in os.environ.items() if k.startswith("R2_")})
    missing = [k for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY") if not e.get(k)]
    if missing:
        raise SystemExit(f"set {', '.join(missing)} in the environment or in {dotenv}")
    return e


def s3_client(e: dict[str, str]):
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        raise SystemExit("boto3 is not installed: pip install boto3")
    return boto3.client(
        "s3", endpoint_url=f"https://{e['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=e["R2_ACCESS_KEY_ID"], aws_secret_access_key=e["R2_SECRET_ACCESS_KEY"],
        region_name="auto", config=Config(retries={"max_attempts": 5, "mode": "standard"}, max_pool_connections=32),
    )


def upload(dry_run: bool, jobs: int) -> int:
    version, folder = build()
    e = env()
    bucket = e.get("R2_COMMENTARY_BUCKET") or e.get("R2_BUCKET") or "ts-audio"
    prefix = e.get("R2_COMMENTARY_PREFIX", "commentary").strip("/")
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    print(f"{len(files):,} files to s3://{bucket}/{prefix}/{version}/, then {prefix}/latest.json")
    if dry_run:
        return 0
    s3 = s3_client(e)

    def put(p: Path, key: str, cache: str) -> None:
        s3.put_object(Bucket=bucket, Key=key, Body=p.read_bytes(), ContentType="application/json; charset=utf-8",
                      CacheControl=cache)

    done = 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(put, p, f"{prefix}/{version}/{p.relative_to(folder).as_posix()}", IMMUTABLE) for p in files]
        for f in as_completed(futures):
            f.result()
            done += 1
            if done % 1000 == 0:
                print(f"  {done:,}/{len(files):,}", flush=True)
    put(DIST / "latest.json", f"{prefix}/latest.json", LATEST)
    print(f"published version {version}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["build", "upload"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--jobs", type=int, default=24)
    a = ap.parse_args()
    if a.action == "build":
        build()
        return 0
    return upload(a.dry_run, a.jobs)


if __name__ == "__main__":
    sys.exit(main())
