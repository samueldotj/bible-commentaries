# C. H. Spurgeon, The Treasury of David

**Module:** CrossWire SWORD `TDavid`, "C. H. Spurgeon's Treasury of David", version 2.1, 2022-06-05
(ModDrv zCom4, OSIS markup, KJV versification, BlockType BOOK). Only the Psalms.

**Download:** <https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/TDavid.zip>, 4,956,285 bytes,
SHA-256 `d0081cba094f399ceb95f372e13068a4d76814de4529bc6794eab0f2ed6e89cc`. Unpacked into
`cache/sword/TDavid/`.

**Terms:** `DistributionLicense=Public Domain`. The About text: "This seven volume "magnum opus", by
Charles H. Spurgeon, was first published in weekly installments over a twenty-year span in the London
Metropolitan Tabernacle's periodical, The Sword and the Trowel. ... It is now in the public domain."
`TextSource=http://archive.spurgeon.org/treasury/`. Published 1869–1885; Spurgeon died in 1892.

## What is in it

The module files each psalm whole under its first verse, after an empty chapter entry. Headings
(`<title type="x-s">`) divide it into Spurgeon's sections. Word counts are for all 150 psalms:

| Section | Words | What it is |
|---|---|---|
| Overview, with Title, Division (and Author, Subject for Psalm 119) | 0.15M | Spurgeon's introduction to the psalm |
| Exposition | 0.62M | Spurgeon's comment, verse by verse: "Verse 1.", "Ver. 1.", "Verses 1, 2." |
| Explanatory Notes and Quaint Sayings | 1.25M | quotations from about 1,700 writers, each ending with its author and work |
| Hints to the Village Preacher | 0.12M | sermon outlines on the verses |
| Works upon the ... Psalm | small | lists of books on the psalm, in 29 psalms |

- Psalm 119 repeats Exposition and Notes for each verse. Each stanza opens with an introduction
  labelled with its eight verses ("Verses 17-24").
- The module has no exposition of Psalm 119:1. Its first Exposition heading is at verse 2, although
  `History_2.1` says Psalm 119 was restored.
- A note's author and work are in italics after it ("*John Hull, B.D., in "Lectures on
  Lamentations,"* 1617."). In Psalm 119 they are in roman type ("... Thomas Manton.").
- Notes often run on inside one paragraph, each opening with its own italic label ("*Whole Psalm.*").
- 7,104 references, as `<reference osisRef="Matt.15.13">`.

## Import (`tools/import_spurgeon.py`)

- 2,486 units, 38,113 paragraphs, 2,056,787 words:
  - `spurgeon/PSA`: the preface;
  - `spurgeon/PSA.23` (150): the overview and its kin, then the notes and hints on the whole psalm;
  - `spurgeon/PSA.23.1` (2,335): the exposition of a verse, or of the verses Spurgeon grouped, then the
    notes and hints on those verses. A note or hint on a verse with no exposition of its own gets a
    unit of its own (33).
- Every paragraph has `section`: `overview`, `exposition`, `notes` or `hints`. A heading opens the
  notes and the hints in each unit ("Explanatory Notes and Quaint Sayings", "Hints to the Village
  Preacher").
- The verse label leaves the text for `verse` (and `verse_end` for a range). The italic words of the
  verse after it go to `anchor` (7,751), as with Calvin.
- A note's author and work leave the text for `author` and `work`, and `quote` numbers the notes of a
  unit, as with the Early Church Fathers. 8,289 notes have an author (1,111 of them in roman type in
  Psalm 119), and 171 cite only a work. A short
  closing line in italics is taken as an author only when it reads as a name (capitalised words,
  initials, degrees, particles, a year). Otherwise it stays in the text, so a verse quoted in italics
  at the end of a note is not lost. Some of the 1,700 names keep extra words ("Robert Leighton, D.D.,
  Archbishop of Glasgow"), and about 30 are wrong.
- A heading inside the notes ("TITLE.", for notes on the psalm's title) stays in the notes.
- Dropped: the 29 "Works upon the ... Psalm" book lists and 175 page markers in Psalm 119 ("Psalms
  119:2\*", "Continued...See ...").
- Verses in no passage unit: 59:15, 106:27, 106:38, 106:41 (Spurgeon groups or skips them) and 119:1
  (missing from the module).
- Per psalm, the import keeps 98–102% of the module's words. The difference is the labels, headings
  and page markers.
