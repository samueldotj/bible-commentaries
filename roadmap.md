# Roadmap

The work is done in stages, so the size of the data and the translation cost
grow one commentary at a time. Geneva and Matthew Henry go first: Geneva
because it is small, and Henry because readers are most likely to want it.

## 0. Repository ✅

- [x] Create this repository, separate from tamilscripture.com, so the site
  repository stays small and its deploys are not slowed.
- [x] README and roadmap.

## 1. Survey the sources

- [ ] Download each module and record its origin, checksum and terms in
  `sources/{id}/SOURCE.md`.
- [ ] Check e-Sword's terms for taking text out of its own modules (Henry,
  Gill). If they do not allow it, take Henry from CCEL and find another
  edition of Gill.
- [ ] Inspect each module's schema: the e-Sword `VerseCommentary` table and
  its RTF or HTML, and SWORD OSIS entries.
- [ ] Count the English words in each commentary, and replace the estimates
  below with exact figures.

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

These estimates are Message Batches prices, based on the dictionary run
(about $100 per million English words on Claude Sonnet 5, and about 2.2
times that on Claude Opus 5). They are ±30% until step 1 counts the words.

| Commentary | English words | Sonnet 5 | Opus 5 |
|---|---|---|---|
| Geneva | ~0.3M | ~$25 | ~$60 |
| Matthew Henry | ~4M | ~$350 | ~$800 |
| Calvin | ~5M | ~$450 | ~$1,000 |
| Poole | ~3M | ~$270 | ~$600 |
| Trapp | ~2.5M | ~$225 | ~$500 |
| Gill | ~7M | ~$600 | ~$1,400 |
| **Total** | **~22M** | **~$1,900** | **~$4,300** |

## Open questions

- The licence of the Tamil drafts. The dictionary's drafts of public-domain
  sources are CC BY.
- Whether e-Sword's terms allow taking the Henry and Gill text.
- Which edition of the Geneva notes the SWORD module holds, and whether it
  is the 1599 edition.
