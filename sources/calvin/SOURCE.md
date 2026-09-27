# John Calvin, Commentaries

## Surveyed: CrossWire `CalvinCommentaries` (not to be used)

**Module:** CrossWire SWORD `CalvinCommentaries`, version 1.1, 2022-08-01 (ModDrv zCom, OSIS markup, KJV
versification). It was converted from CCEL by Luke Plant.

**Download:** <https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/CalvinCommentaries.zip>,
20,897,508 bytes, SHA-256 `df66fc8c03537499ad006d069481d2c95b600887cdbd6ce75ec5d264b573192a`

**Terms:** `DistributionLicense=Public Domain`, text from <http://www.ccel.org/>.

### What is in it

- 11,063 entries across 48 books.
- 5,455,135 words of Calvin's comment, plus two other kinds of text:
  - 676,448 words of footnotes by the Calvin Translation Society editors (`<note>`), often quoting
    Calvin's French or Latin;
  - 771,401 words in translation tables (`<table>`), which set Calvin's Latin version beside the English,
    or Leo Juda's version beside Calvin's in Genesis.

### Why it is not usable

**Several books hold only chapter headings and translations, not the comment on each verse.** In these
books each chapter is a single entry of a few thousand characters: the chapter argument and the
translation table.

| Book | Words in the module | Expected (rough estimate from the printed volumes) |
|---|---|---|
| Psalms | 115,220 | Five volumes, over a million words |
| Zechariah | 10,874 | About 150,000 |
| Malachi | 3,118 | About 50,000 |
| 1 Timothy | 4,256 | About 45,000 |
| 2 Timothy | 1,379 | About 30,000 |
| Titus | 1,901 | About 15,000 |

Haggai (28,985 words, 39% of verses) and Zephaniah (75%) may also be incomplete.

## Recommended source: CCEL ThML, one file per volume

- **Where:** `https://ccel.org/ccel/calvin/calcom01.xml` to `calcom45.xml` (45 volumes; `calcom46` does
  not exist).
- **Terms:** each file's header gives `<DC.Rights>Public Domain</DC.Rights>`. The file also carries a
  comment, `Copyright Christian Classics Ethereal Library`, which applies to CCEL's electronic
  edition. To be checked before the text is committed.
- **Structure:** each comment is marked with a
  `<scripCom osisRef="Bible:Ps.1.1" parsed="|Ps|1|1|0|0" type="Commentary"/>`, followed by a
  `<div class="Commentary">`. This keys it by verse directly, the same way the SWORD module was built.

## What Calvin wrote

Calvin did not comment on Judges–Esther, Job, Proverbs, Ecclesiastes, Song of Songs, 2–3 John or Revelation.
Other books need care:

- Ezekiel covers chapters 1–20 only.
- Mark and Luke are mostly inside the *Harmony of the Evangelists*.
- Exodus–Deuteronomy are arranged by subject in the *Harmony of the Law*, so one comment can cover
  verses scattered across several books.
