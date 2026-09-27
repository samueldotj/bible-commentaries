# English text

One JSON file per chapter: `en/{source}/{BOOK}/{chapter}.json`. A book's own
introduction is in `en/{source}/{BOOK}/intro.json`. These files are written
by `tools/import_{source}.py` from the modules in `cache/`, so edit the
importer, not the files.

```json
{
 "source": "henry", "book": "JHN", "chapter": 3,
 "units": [
  {"id": "henry/JHN.3.1-21", "range": "JHN.3.1-21", "kind": "passage",
   "title": "Christ's Interview with Nicodemus.", "hash": "3b0c9a1e",
   "paragraphs": [
    {"id": "henry/JHN.3.1-21#p1-9f19f8ba", "text": "We found, in the close of the foregoing chapter, ..."},
    {"id": "henry/JHN.3.1-21#p5-1c2d3e4f", "text": "... Mal. ii. 7 ...",
     "refs": [{"text": "Mal. ii. 7", "ref": "MAL.2.7"}]}
   ]}
 ]
}
```

- **Unit:** one comment.
  - `kind` is `book` (an introduction or the Geneva "Argument"), `chapter` (a chapter's
    introduction) or `passage`.
  - `range` uses the site's verse ids: `JHN`, `JHN.3`, `JHN.3.16`, `JHN.3.1-21`.
  - `hash` is FNV-1a of all the unit's English, so a Tamil draft can tell when the English under it
    has changed.
- **Paragraph:** a piece of plain text, with no markup.
  - `id` is `{unit id}#p{n}-{fnv8 of the text}`, as the site's dictionary articles use.
  - A paragraph over 900 characters is cut at sentence ends into about 700, as the site does. A
    very long sentence or list is cut at line breaks or semicolons.
  - Poetry keeps its line breaks as `\n`.
  - `heading: true` marks a heading inside a unit.
  - `anchor` holds the words of the verse that a paragraph explains:
    - Geneva: the KJV words where the note's marker stands;
    - Poole: the bold words that open a note ("**The vision,**");
    - Trapp: the words before the `]` ("Ver. 1. **A ruler of the Jews**]");
    - Calvin: the italic words after the verse number ("**2.** *He came to Jesus by night.*").

    They are the old English wording of the verse. The site can print them before the paragraph,
    and the translation should use the IRV's wording.
  - `verse` is the verse a paragraph is on, when it differs from the unit's first verse or the unit
    covers several.
  - `label` is a Geneva note's letter or number (`a`, `1`), or a footnote's marker.
  - `footnote: true` marks a footnote: Calvin's editors' notes, or Trapp's Latin and Greek sources.
    Its marker stays in the text it belongs to, as `{55}` or `{a}`, and the footnote follows that
    paragraph.
- **`refs`:** the references in a paragraph.
  - `text` is written as the commentator wrote it ("Mal. ii. 7", "Ro 3:31"), so the translator can
    find it.
  - `ref` is the verse id. A range across chapters is written `JHN.3.36-4.2`.
- **Not included:**
  - the KJV text that the modules repeat (Henry's passage before each section, Geneva's and Trapp's
    verse before their notes, the KJV's closing lines to the epistles) — the site shows the IRV;
  - Calvin's translation tables (0.29M words);
  - Poole's "No text from Poole on this verse" placeholders.
