# Roadmap

The work is done in stages, so the size of the data and the translation cost
grow one commentary at a time. Geneva and Matthew Henry go first: Geneva
because it is small, and Henry because readers are most likely to want it.

## 0. Repository ✅

- [x] Create this repository, separate from tamilscripture.com, so the site
  repository stays small and its deploys are not slowed.
- [x] README and roadmap.

## 1. Survey the sources

- [x] Geneva, Henry and Calvin: CrossWire modules downloaded, read with
  `tools/sword.py` and counted (`sources/survey.md`).
- [x] Henry comes from CrossWire `MHC` (public domain, prepared from CCEL),
  so e-Sword is no longer needed for Henry.
- [x] Calvin: the CrossWire module lacks the comment on each verse in
  Psalms, Zechariah, Malachi and 1–2 Timothy–Titus, so CCEL's 45 ThML volumes
  were downloaded and read with `tools/ccel.py` instead.
- [ ] Geneva: find notes for Judges, Jonah and Philemon, which are missing
  from the module, and identify who modernised the spelling.
- [x] Poole and Trapp: the owner downloaded the BibleSupport modules; read
  with `tools/esword.py` and counted.
- [x] Poole: the Greek typed in the OLB font is converted from the RTF
  edition; the Hebrew runs are marked `[Hebrew]`.
- [x] Trapp: Jude was filed under Judges 1, and is re-keyed on import.
- [ ] Poole and Trapp: check BibleSupport's terms of use.
- [x] Early Church Fathers: the owner provided the SermonIndex module; read
  with `tools/esword.py` and counted.
- [x] Early Church Fathers: SermonIndex's compilation is free to copy, share
  and distribute for personal and ministry purposes (owner, 2026-09-27). Used
  under those terms; its Tamil drafts go in their own folder, `ta-ecf/`.
- [ ] Gill: set aside for now.

## 2. Import the English

- [x] The English format (`en/README.md`): one file per chapter, units
  keyed by verse range, plain-text paragraphs with ids and references.
- [x] Geneva (`tools/import_geneva.py`): 14,583 units. Misplaced entries
  are re-keyed by their KJV verse text.
- [x] Henry (`tools/import_henry.py`): 5,484 units. Each section's range is
  read from its KJV passage, and every verse is covered.
- [ ] Clean-up rules for each source: Henry's italic verse quotes, Gill's
  transliterated Hebrew, Trapp's Latin, Calvin's own translation of each
  passage, and book and chapter introductions.
- [x] Checks: every range parses, stays inside the book's chapters and
  verses, no unit or paragraph is empty, and no markup is left.
- [x] Calvin (`tools/import_calvin.py`): 13,724 units, with Calvin's
  Arguments and prefaces, and the editors' footnotes as footnote paragraphs.
- [x] Poole (`tools/import_poole.py`): 27,136 units, with chapter outlines,
  lemmas, and Greek put back.
- [x] Trapp (`tools/import_trapp.py`): 27,595 units, re-keyed by verse text.
- [ ] Early Church Fathers.

## 3. Translation tool

In `tools/translate` of the site repository:

- [x] `translate commentary status | show | run`, reading `en/` here and
  writing drafts to `ta/{source}/{BOOK}/{chapter}.json` (`ta-ecf/` for the
  Early Church Fathers). Design: `docs/feature_commentary_translation.md` in
  the site repository.
- [x] A commentary prompt:
  - the IRV text of the verses explained and of other verses cited;
  - IRV wording where the commentator quotes the verse, but his point kept
    where it rests on his own Bible's wording;
  - anchors given as the IRV's words for the phrase;
  - references as Tamil book name and chapter:verse, from the import's ids;
  - archaic English in present-day formal Tamil; the theology not softened;
  - Latin, Greek and Hebrew kept, with a Tamil rendering in brackets.
- [x] Checks: anchors, references, footnote markers, `[Hebrew]`; Latin is
  not flagged as untranslated English; no length check on footnotes.
- [ ] A first run against the API (a few units), before the pilot.

## 4. Pilot

- [ ] About 40 units across all the commentaries, including the hardest
  English (Trapp, the Early Church Fathers).
- [ ] Compare Claude Sonnet 5 and Claude Opus 5.5 in the blind review, and
  choose the model.
- [ ] Cost: under $20.

## 5. Stage 1: Geneva and Matthew Henry

- [ ] Full batch run and a repair batch.
- [ ] Commit the drafts to `ta/`.

## 6. Publish

- [ ] A build in this repository that writes one JSON file per chapter.
- [ ] Upload to R2 under `commentary/{hash}/`, where the hash is taken from
  the commentary data rather than the site build. Unchanged commentary is
  then never uploaded again.
- [ ] A GitHub Actions workflow here that builds and uploads when commentary
  changes, without deploying the site.
- [ ] Site integration in tamilscripture.com. The page design is the
  owner's.

## 7. Corrections

- [ ] `commentary:` correction targets in the site's community review.
- [ ] Export accepted corrections into `overrides/` here, as the dictionary
  export does for the site repository.

## 8. Later stages

- [ ] Stage 2: Calvin.
- [ ] Stage 3: Poole and Trapp.
- [ ] Stage 4: the Early Church Fathers.
- [ ] Gill, if it is taken up again.

## Estimated cost

These are Message Batches prices, based on the dictionary run (about $100
per million English words on Claude Sonnet 5, and about 2.2 times that on
Claude Opus 5). The word counts are measured where the survey has been
run, and estimated for Gill.

| Commentary | English words | Sonnet 5 | Opus 5 |
|---|---|---|---|
| Geneva | 0.39M (imported) | ~$40 | ~$90 |
| Matthew Henry | 6.47M (imported) | ~$650 | ~$1,420 |
| Calvin | 7.01M (imported, with 15,490 footnotes) | ~$700 | ~$1,540 |
| Poole | 3.42M (imported, with lemmas) | ~$340 | ~$750 |
| Trapp | 3.40M (imported, with lemmas) | ~$340 | ~$750 |
| Early Church Fathers | 13.42M (measured) | ~$1,340 | ~$2,950 |
| **Total without Gill** | **34.1M** | **~$3,400** | **~$7,500** |
| Gill, set aside | ~7M (estimate) | ~$700 | ~$1,500 |

Not in the figures above:
- Calvin: the translation tables and front matter left out of the import.
  (His editors' footnotes are in the Calvin figure; the owner decided on
  2026-09-27 that they are translated.)
- The Early Church Fathers: 0.58M words of author and source lines, which
  need translating only once per author and per work.

## Open questions

- The licence of the Tamil drafts. The dictionary's drafts of public-domain
  sources are CC BY.
- How to present the Early Church Fathers to the site's Reformed readers.
- Who modernised the spelling of the Geneva notes in the SWORD module. The
  lettered and numbered notes match the 1599 edition.
- Calvin's translation tables: left out of the import for now.
- Latin, Greek and Hebrew quotations (Trapp's and Calvin's footnotes): kept
  as written with a Tamil rendering in brackets, to be confirmed in the pilot.
