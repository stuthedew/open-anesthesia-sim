---
id: PL-P00H
title: docket's picks.bold_lead names a Required-scope entry from roadmap.list_entries' whole entry joined into one line, so an entry that does not open with a closed bold lead is named in docket picks' build line by a nested item's or a later paragraph's bold run, by a first sentence run past its paragraph's end, or by a ** pair a blank line splits; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket's picks.bold_lead names a Required-scope entry from roadmap.list_entries' whole entry joined into one line, so an entry that does not open with a closed bold lead is named in docket picks' build line by a nested item's or a later paragraph's bold run, by a first sentence run past its paragraph's end, or by a ** pair a blank line splits; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`subprojects/docket/src/docket/picks.py`. `roadmap.list_entries` hands `picks`
each `Required scope` entry as one line, its later paragraphs and nested lists
joined on with spaces, as documented there and widened by `PL-YSMD`.
`bold_lead` takes the first bold pair in that text (`_BOLD_LEAD_RE`), or, where
there is none, the text up to the first full stop and space. Both cross the
blank line or nested-list start where the entry's lead paragraph ends
(CommonMark 0.31.2 § 4.8, § 5.2), and emphasis pairs only inside one
paragraph's inline content (§ 6.2).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
through `wave`, `picks` and `format_picks`, against markdown-it-py 4.2.0 in
CommonMark mode. Three entries of a gate milestone's `Required scope`:

```text
- The View contract and its two classes (queue item PL-F1F1):
  - **Data views**, which read the run.
  - **Control views**, which change it.
- Keep the layout model free of Qt (queue item PL-F2F2)

  It is pure Python. Nothing in it imports Qt.
- **The adapter (queue item PL-F3F3), one module.

  The only importer of QSplitter.** Nothing else.
```

`docket picks` names them `Data views`, `Keep the layout model free of Qt
(queue item PL-F2F2) It is pure Python`, and `The adapter (queue item PL-F3F3),
one module. The only importer of QSplitter`. markdown-it reads the first lead
paragraph as holding no strong text (`Data views` is a nested item's), ends the
second at its blank line, and reads the third's two `**` runs as literal, since
the pair straddles a blank line. Latent: over all 75 `Required scope` entries in
`ROADMAP.md`, `bold_lead` gives the same name over the joined text as over the
lead paragraph alone. Only the name a build line prints goes wrong; the entry
number is right.

**Generator check.** A member of `PL-R417`: a reader reads past the end of the
statement it names, the entry's lead paragraph, into the blocks the entry holds
after it. The function arrived 2026-10-04 in `#1345` (`PL-G2HP`), after the
head was recorded, so it is inflow rather than stock the earlier sweeps missed.

**Done when.** `bold_lead` reads the entry's lead paragraph alone, for example
from a `ScopeEntry` field that `roadmap.list_entry_lines` fills through
`docket.markdown.read`, and `PL-R417`'s guard gains a `picks, ` case for each
of the three forms above, failing on today's reader.
