# bible-commentaries

Public-domain Bible commentaries, keyed by verse, with Tamil translations, for
[tamilscripture.com](https://tamilscripture.com).

This repository holds the working data: the English text taken from each
commentary, the Tamil drafts, and the corrections accepted by reviewers. The
site repository (`tamilscripture.com`) never stores this data. A build in this
repository writes one JSON file per chapter and uploads it to Cloudflare R2,
and the site reads those files from the CDN.

See [roadmap.md](roadmap.md) for the plan and its current state.

## Commentaries

| Id | Work | Date | Coverage | Source module |
|---|---|---|---|---|
| `geneva` | Geneva Bible marginal notes | 1599 | Whole Bible | CrossWire SWORD `Geneva` |
| `henry` | Matthew Henry, *Commentary on the Whole Bible* | 1708–1710 | Whole Bible | CrossWire SWORD `MHC` |
| `calvin` | John Calvin, *Commentaries* (Calvin Translation Society) | 1840s–50s | Most books, but not Judges–Esther, Job, Proverbs–Song, 2–3 John or Revelation | CCEL ThML, 45 volumes |
| `poole` | Matthew Poole, *English Annotations on the Holy Bible* | 1683–1685 | Whole Bible (Poole up to Isaiah 58, finished by colleagues) | BibleSupport e-Sword `.cmtx` |
| `trapp` | John Trapp, *A Commentary or Exposition upon All the Books of the Old and New Testament* | 1647–1656 | Whole Bible | BibleSupport e-Sword `.cmtx` |
| `gill` | John Gill, *Exposition of the Whole Bible* | 1746–1763 | Whole Bible | e-Sword |

All six texts are in the public domain. The digital editions were prepared
by others, so each source's folder records where its module came from and
on what terms, before any of its text is committed. See
`sources/{id}/SOURCE.md` and the word counts in
[sources/survey.md](sources/survey.md).

## Tools

- `tools/make_versification.py` writes `data/kjv-versification.json`, the
  verse counts of the KJV, from the site repository.
- `tools/sword.py` reads compressed SWORD commentary modules (zCom, zCom4).
- `tools/esword.py` reads e-Sword 11 commentary modules (`.cmti`).
- `tools/survey.py` writes `sources/survey.md`.

## Layout

```
sources/{id}/SOURCE.md     where the module came from, its checksum, and the terms it is offered under
sources/{id}/LICENSE       licence of the text as committed here
en/{id}/{BOOK}/{ch}.json   English text, one file per chapter
ta/{id}/{BOOK}/{ch}.json   Tamil drafts, one file per chapter
overrides/{id}/...         corrections accepted by reviewers on the site
```

The module files themselves (`.cmtx`, `.cmti`, SWORD zips) are not
committed. `SOURCE.md` gives the download location and checksum, and a
fetch script puts them under `cache/`, which git ignores.

## Identifiers

Identifiers follow tamilscripture.com, so references work the same in both
repositories.

- **Books:** the USFM codes in `data/books.toml` of the site repository
  (`GEN`, `JHN`, `SNG`, ...).
- **Comment unit:** a verse range such as `JHN.3.16` or `JHN.3.16-18`, or `JHN.3`
  for a chapter introduction and `JHN` for a book introduction.
- **Paragraph:** `{id}/{range}#p{n}-{hash8}`, e.g.
  `henry/JHN.3.16-18#p2-4f2a9c1b`, where `hash8` is the FNV-1a hash of the
  English paragraph. This is the same scheme as dictionary articles, so a
  Tamil draft is marked stale when the English under it changes.

## Translation

The Tamil drafts are made by the translation tool in the site repository
(`tools/translate`), extended to handle commentary. It uses the same
theological glossary, reviewed Tamil names and IRV book names as the
dictionary translation, and the same Message Batches workflow. Drafts are
shown on the site as drafts until reviewers correct or accept them.
