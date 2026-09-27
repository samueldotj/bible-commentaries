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
- [ ] Calvin: the CrossWire module lacks the comment on each verse in
  Psalms, Zechariah, Malachi and 1–2 Timothy–Titus. Download CCEL's 45 ThML
  volumes instead, then survey them.
- [ ] Geneva: find notes for Judges, Jonah and Philemon, which are missing
  from the module, and identify who modernised the spelling.
- [ ] Poole and Trapp: owner downloads the BibleSupport modules (an account
  is needed). Then survey their e-Sword `VerseCommentary` table.
- [ ] Gill: owner downloads it inside e-Sword, and records e-Sword's terms.

## 2. Import the English

- [ ] A converter from each module into `en/{id}/{BOOK}/{ch}.json`: verse
  ranges, plain-text paragraphs, and headings kept.
- [ ] Clean-up rules for each source: Henry's italic verse quotes, Gill's
  transliterated Hebrew, Trapp's Latin, Calvin's own translation of each
  passage, and book and chapter introductions.
- [ ] Checks: every range parses, stays inside the book's chapters and
  verses, and no unit is empty.
- [ ] Import Geneva and Henry.

## 3. Translation tool

In `tools/translate` of the site repository:

- [ ] A commentary input type next to dictionary articles, reading from this
  repository.
- [ ] A commentary prompt:
  - send the IRV text of the verses commented on;
  - use IRV wording where the commentator quotes the verse, but translate
    his point where it rests on the English wording;
  - keep Calvin's own translation of each passage as his;
  - translate archaic English into modern Tamil;
  - do not soften or update the theology.
- [ ] Checks: allow Latin, Greek and Hebrew quotations, and tune the length
  ratio.

## 4. Pilot

- [ ] About 40 units across all six commentaries, including the hardest
  English (Trapp, Gill).
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
- [ ] Stage 3: Poole, Trapp and Gill.

## Estimated cost

These are Message Batches prices, based on the dictionary run (about $100
per million English words on Claude Sonnet 5, and about 2.2 times that on
Claude Opus 5). The word counts are measured where the survey has been
run, and estimated elsewhere.

| Commentary | English words | Sonnet 5 | Opus 5 |
|---|---|---|---|
| Geneva | 0.41M (measured) | ~$40 | ~$90 |
| Matthew Henry | 5.23M (measured) | ~$520 | ~$1,150 |
| Calvin | ~7M (5.46M measured in an incomplete module) | ~$700 | ~$1,500 |
| Poole | ~3M (estimate) | ~$300 | ~$650 |
| Trapp | ~2.5M (estimate) | ~$250 | ~$550 |
| Gill | ~7M (estimate) | ~$700 | ~$1,500 |
| **Total** | **~25M** | **~$2,500** | **~$5,400** |

Calvin also has 0.68M words of footnotes by his English editors, and 0.77M
words of translation tables, mostly Latin. Whether to translate them is an
open question; they are not in the figures above.

## Open questions

- The licence of the Tamil drafts. The dictionary's drafts of public-domain
  sources are CC BY.
- Whether e-Sword's terms allow taking the Gill text.
- Who modernised the spelling of the Geneva notes in the SWORD module. The
  lettered and numbered notes match the 1599 edition.
- Whether Calvin's editors' footnotes and his Latin translation tables are
  translated, shown in English, or left out.
