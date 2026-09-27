# John Trapp, A Commentary or Exposition upon All the Books of the Old and New Testament

**Module:** "John Trapp's Complete Commentary, OT and NT" (abbreviation `Trapp`), an e-Sword module
"Formatted for e-Sword by: www.BibleSupport.com". The owner downloaded both editions on 2026-09-27 from
<http://www.biblesupport.com/e-sword-downloads/file/7101-trapp-john-complete-commentary-5-vols/>.

| File | Format | Bytes | SHA-256 |
|---|---|---|---|
| `trapp_john_-_complete_commentary_ot_nt.cmti` | e-Sword 11 (HTML), Details version 4 | 60,605,440 | `fb2a266e46b89b18e299c61759385a3ab628a980208deac5c9d72052244c807f` |
| `Trapp, John - Complete Commentary OT NT.cmtx` | e-Sword 9–10 (RTF), Details version 1 | 37,846,016 | `635e617ccbaac55f55076775e0f91d688564273d489ad38aedac149de484c82e` |

**Edition:** The `Details` table says: "Reprinted from the author's last edition. Edited by W. Webster and
Hugh Martin", in five volumes (Genesis–2 Chronicles, Ezra–Psalms, Proverbs–Daniel, Hosea–Malachi,
Matthew–Revelation). That is the 1860s reprint, and it is in the public domain.

**Terms:** The module states none. Still to find: whether BibleSupport's terms of use say anything about
module text.

## What is in it

- 27,606 entries, keyed to verses; 67 of them cover a range.
- 4,237,211 words of comment.
- Not counted as comment:
  - 188,237 words of KJV verse text, which is dropped;
  - 14,991 words of footnotes.
- Each entry opens with the KJV verse (`<p>1 There was a man...</p>`), then Trapp's notes, each headed
  with its words (`Ver. 1. <b>A ruler of the Jews</b>]`).
- Footnote markers `{a}` point to footnotes at the end, which are mostly his Latin and Greek sources.
- Greek is Unicode in `<grk><span lang="el-GR">`, and Latin is in `<i>`.

## Problems

- ~~No comment on Jude.~~ e-Sword book 65 has no rows, but Jude's comment is filed under Judges 1. See
  the import below.
- Some books have comment on fewer verses: Numbers 36%, 1 Chronicles 42%, Deuteronomy 64%. This may be
  Trapp's own selection. To be checked against the printed volumes.

## Import (`tools/import_trapp.py`)

- 27,595 units, 63,344 paragraphs, 3,203,109 words, plus about 0.2M words of lemmas.
- The survey's 4.24M counted the Old Testament's KJV verses ("Exo 1:1 And these...") as comment. The
  import drops all 27,874 KJV verse paragraphs.
- **Jude is not missing.** Its 25 verses were filed under Judges 1:1–25. Each entry is checked against
  the KJV by its verse text, and 141 were re-keyed, all of Jude among them. The second Luke 2:1 entry
  is 2:2.
- 44,401 notes keep their lemma ("Ver. 1. **A ruler of the Jews**]") as `anchor`.
- 1,005 footnotes of Latin and Greek sources, marked `{a}` in the note.
