# Matthew Poole, English Annotations on the Holy Bible

**Module:** "Matthew Poole's Commentary" (abbreviation `Poole`), an e-Sword module formatted by
BibleSupport. The owner downloaded both editions on 2026-09-27 from
<http://www.biblesupport.com/e-sword-downloads/file/772-matthew-poole-commentarycmtxexe/>.

| File | Format | Bytes | SHA-256 |
|---|---|---|---|
| `matthew_pool_commentary.cmti` | e-Sword 11 (HTML), Details version 4 | 48,290,816 | `49adf6ef6b907ec1fc30bb43411dfae657af3ab441c58fc2d7e8a8f5d944e8be` |
| `Matthew Pool Commentary.cmtx` | e-Sword 9–10 (RTF), Details version 2 | 34,975,744 | `22f3bfbccaf716922c4ec495a7714e8ea504ba4f658307caacf68daa2cd137bc` |

**Terms:** Poole's *Annotations* were printed in 1683–1685 and are in the public domain. The module's
`Details` table holds Poole's preface (5,534 words) but no statement about the electronic text, and does
not name the edition it was typed from. Still to find: whether BibleSupport's terms of use say anything
about module text.

## What is in it

- One row for every KJV verse (31,092), plus 64 book introductions and 2 chapter entries.
- 3,525,757 words, all commentary. There is no Bible text to drop.
- Each chapter's outline ("JOHN CHAPTER 3" and a list of passages) sits at the top of the chapter's
  first verse. The import should split it off as a chapter introduction.
- HTML tags: `<p>`, `<b>` (the words being explained), `<i>`, and `<ref>` (references written as
  `Joh 1:49`).

## Greek and Hebrew

Poole's Greek and Hebrew were typed in the OLB Greek and Hebrew fonts, which use Latin keys. For example,
`anwyen` is ἄνωθεν.

- In the RTF edition these runs keep their font (`\f1 anwyen\f0`): 992 runs in 619 entries (OLBGrk in
  562 entries, OLBHeb in 83).
- In the HTML edition the font is lost, so they read as nonsense Latin letters.

The import should read the RTF edition, or take the Greek and Hebrew runs from it, and convert them to
Unicode.

## Import (`tools/import_poole.py`)

- 27,136 units, 75,440 paragraphs, 3,200,161 words, plus about 0.22M words of lemmas:
  - 63 book introductions ("THE ARGUMENT");
  - 1,050 chapter introductions: heading, Psalm argument and title, and the chapter's outline;
  - 26,023 verses.
- 4,924 entries that are only "No text from Poole on this verse" are dropped.
- 50,767 notes open with the words they explain in bold, which are kept as `anchor`.
- **Greek and Hebrew:** all 992 font runs in the RTF edition were found in the HTML text and put back:
  - 882 Greek runs, converted from the OLB key (`anwyen` → ανωθεν);
  - 110 Hebrew runs, which became `[Hebrew]` because the key is not consistent. Poole usually gives
    the transliteration beside them.
