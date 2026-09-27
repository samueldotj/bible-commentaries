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
  - Geneva notes carry `label` (`a`, `1`) and `anchor`: the KJV words the note explains, taken from
    where the marker stands in the verse.
- **`refs`:** the references in a paragraph.
  - `text` is written as the commentator wrote it ("Mal. ii. 7", "Ro 3:31"), so the translator can
    find it.
  - `ref` is the verse id. A range across chapters is written `JHN.3.36-4.2`.
- **Not included:** the KJV text that the modules repeat (Henry's passage before each section,
  Geneva's verse before its notes). The site shows the IRV.
