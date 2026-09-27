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
