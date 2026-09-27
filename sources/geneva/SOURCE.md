# Geneva Bible notes

**Module:** CrossWire SWORD `Geneva`, "Geneva Bible Translation Notes", version 1.1, 2001-11-28
(ModDrv zCom, ThML markup)

**Download:** <https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/Geneva.zip>, 1,680,224 bytes,
SHA-256 `188d4806f837444e16dc7fb53341bb654d89f67e740a32e31c864ddbf1175e7f`

**Terms:** The notes were printed in 1599 and are in the public domain. The module's `.conf` has no
`DistributionLicense` field and does not say who prepared the text.

## What is in it

- 14,713 entries, keyed to verses. There are 18 chapter-level entries, and these hold book "Arguments".
- 414,323 words of notes.
- Each entry is the KJV verse, then `<br />`, then the notes. The verse text marks where each note is
  anchored with `{a}` or `{1}`, and the notes follow as `(a) ...`. The two sequences look like the
  1599 edition: letters for the marginal notes, numbers for the notes Laurence Tomson took from Beza.
- The spelling is modernised ("As an unformed lump and without any creature in it"), and the modernisation is not credited to anyone.
- Scripture references are `<scripRef>` elements with abbreviated references (`2Co 1:19`).

## Problems

- **No notes at all for Judges, Jonah or Philemon.** The 1599 edition has notes on these books, so the
  module dropped them.
- The verse text is the KJV, not the Geneva text, so the site should show the IRV verse and use the
  `{a}` anchors only to place the notes.

## To decide

- Who modernised the spelling, and whether this can be confirmed as the 1599 edition.
- Where to get notes for Judges, Jonah and Philemon.

## Import (`tools/import_geneva.py`)

- 14,583 units and 18,395 notes, 394,322 words:
  - 14,548 verses with notes;
  - 35 book Arguments.
- **Misplaced entries.** 148 entries hold the previous chapter's last verse in the slot of the next
  chapter's first verse. For example, the `GEN.15.1` slot holds Genesis 14:24 and its notes. They are
  re-keyed by comparing their verse text with the KJV in the site repository: 138 exactly and 10 by
  close wording. In every case the notes were already present at the right verse. **So any notes the
  edition has on those 148 first verses (Genesis 15:1, for example) are missing from the module.** To
  check against a printed or scanned 1599 edition.
- 58 entries have KJV text that differs from the site's KJV (modernised: "sixty" for "threescore"). They keep
  their key.
- Each note is split on its label, `(a)` or `{a}` in a few entries. Its `anchor` is taken from where the
  marker stands in the verse. 93 labels have no marker in the verse, so those notes have no anchor.
- Left as they are:
  - 8 notes without a label: cross-references like `See Geneva "Isa 13:1"`, two source typos
    (`(q You that...`), and Junius's chronology at Revelation 1:1;
  - one note of 3,157 characters.
