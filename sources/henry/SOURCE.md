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
