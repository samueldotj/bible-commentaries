# Matthew Henry, Commentary on the Whole Bible

**Module:** CrossWire SWORD `MHC`, "Matthew Henry's Complete Commentary on the Whole Bible", version 2.2,
2022-08-29 (ModDrv zCom4, OSIS 2.1.1 markup, KJV versification)

**Download:** <https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/MHC.zip>, 15,195,123 bytes,
SHA-256 `6bcb936873ca144e317805e5c1677940fd86e2403f7c14517752e44f25c8882b`

**Terms:** `DistributionLicense=Public Domain`. The About text says: "Public Domain--Copy Freely. This text was
prepared from the Christian Classics Ethereal Library ... Thanks also to Logos Research, Inc. for providing
CCEL with their text".

Because this module comes from CrossWire, we do not need e-Sword's copy of Henry.

## What is in it

- 5,504 entries:
  - 66 book introductions
  - 1,189 chapter introductions
  - 4,249 sections, each commenting on one verse or a range of verses (e.g. `JHN.3.1-21`)
- Every book has comment on 100% of its verses.
- 5,226,551 words of comment.
- Each section opens with a heading (`<title type="x-s3">`), then the KJV text of the passage, with
  verse numbers as `<hi type="super">`. That KJV text (822,583 words) is dropped. The site shows the IRV.
- Paragraphs are `<div type="x-p">` milestones. Henry's quotations of the verse are
  `<hi type="italic">`, and references are `<reference osisRef="Mal.2.7">`.

## Notes for the import and translation

- Sections are long. The longest is `MAT.24.4-31` at 13,436 words, and `JHN.3.1-21` is about 13,000.
  They will be translated in parts, as the dictionary does with long articles.
- Henry's outline numbering (I., 1., (1.)) is part of the text and must be kept.
- References are written in Henry's style ("Mal. ii. 7") and linked by `osisRef`. The Tamil should
  cite them from the `osisRef`, not from the Roman numerals.

## Import (`tools/import_henry.py`)

- 5,484 units, 60,189 paragraphs, 6,465,790 words:
  - 61 book introductions (with the volume prefaces);
  - 1,170 chapter introductions;
  - 4,253 sections.
- The survey counted 5.23M words, but only the text inside paragraph markers. The import keeps all of
  Henry's text.
- **Where SWORD puts the text.** Text is often not under its own verse key:
  - a "preverse" block may hold the volume preface, the book's introduction, the first chapter's
    introduction, or a whole earlier section (Joshua 18:1 sits before 18:2);
  - an entry often begins with the end of the previous section's comment (the comment on Genesis
    19:15–23 is at the start of the 19:24 entry).

  So the importer reads each book as one stream. Each section's range comes from the verse numbers
  in its KJV passage, which is then dropped.
- Every verse of the Bible is in a section. Two verses are in two sections, as Henry divided them:
  Jeremiah 46:12 and Jude 15.
- The 32 footnotes are kept as paragraphs.
- Henry's outline numbering (I., 1., (1.)) stays in the text.
- 73,000 references keep Henry's wording ("Mal. ii. 7") with their verse id.
