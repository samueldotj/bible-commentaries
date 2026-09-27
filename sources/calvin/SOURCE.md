# John Calvin, Commentaries

## Source: CCEL ThML, 45 volumes

**Where:** `https://ccel.org/ccel/calvin/calcom01.xml` to `calcom45.xml`, downloaded 2026-09-27 (71 MB). The
SHA-256 of each volume is in [SHA256SUMS](SHA256SUMS).

**Terms:** each volume's header gives `<DC.Rights>Public Domain</DC.Rights>`. The files also carry the
comment `Copyright Christian Classics Ethereal Library`, which applies to CCEL's electronic edition. The
translation is the Calvin Translation Society's (Edinburgh, 1840s–1850s).

**Read with:** `tools/ccel.py`.

## What is in it

A comment begins at an empty `<scripCom osisRef="Bible:Ps.2.1" type="Commentary"/>` marker and runs to
the next marker, or to the next `<div1>`/`<div2>` heading. Each comment is keyed to one verse. It is taken
to cover the verses up to the next marker in the same chapter, since Calvin often takes several verses
together.

- 14,052 comments:
  - 591 at chapter level (e.g. the argument of a Psalm);
  - 2,356 covering a range of verses;
  - 11,105 on a single verse.
- 6,335,578 words of Calvin's comment.
- Not counted as comment:
  - 783,192 words of footnotes by the Calvin Translation Society editors (`<note>`), often quoting
    Calvin's French or Latin;
  - 284,393 words in translation tables inside comments;
  - 1,514,072 words outside any comment: prefaces, dedications, arguments, the translation tables that
    open each section (Calvin's own version beside the English, or Leo Juda's beside Calvin's), and
    indexes.
- Volume titles (from `DC.Title`):
  - 1–2 Genesis; 3–6 Harmony of the Law; 7 Joshua; 8–12 Psalms; 13–16 Isaiah;
    17–21 Jeremiah and Lamentations; 22–23 Ezekiel; 24–25 Daniel; 26–30 the Minor Prophets;
  - 31–33 Harmony of the Gospels (Matthew, Mark, Luke); 34–35 John; 36–37 Acts; then Romans to the
    Catholic Epistles.

## What Calvin wrote, and how it is keyed

- No comment on Judges–Esther, Job, Proverbs, Ecclesiastes, Song of Songs, 2–3 John or Revelation.
- **Ezekiel** covers chapters 1–20 only (37% of verses).
- **Harmony of the Law** (Exodus–Deuteronomy) is arranged by subject. A comment is keyed to one verse,
  but may discuss parallel passages in other books.
- **Harmony of the Gospels:** a comment is keyed to the Gospel of its marker, mostly Matthew and Luke.
  Mark has comment on 13% of its verses, because its parallels are discussed under Matthew. The site may
  need to show a Matthew comment for its parallel in Mark.

## Not used: CrossWire `CalvinCommentaries`

The CrossWire module was also surveyed:
- version 1.1, 2022-08-01, SHA-256 `df66fc8c03537499ad006d069481d2c95b600887cdbd6ce75ec5d264b573192a`;
- converted from CCEL by Luke Plant.

It lacks the comment on each verse in Psalms, Zechariah, Malachi, 1–2 Timothy and Titus: those books
have only chapter arguments and translation tables. For example, it has 115,220 words for Psalms against
763,597 in CCEL.
