---
id: PL-W7WL
title: bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it
status: untriaged
added: 2026-09-20
---

**Problem.** bin/docket release writes the notes before bin/docket record can backfill pr:, so an item merged just before a cut gets a notes line with no pull request number and the cut cannot be regenerated to add it

**Observed 2026-09-20, cutting v0.4.32 (`PL-V3GD`).** `PL-TGFY` merged as #745
minutes before the cut, so it carried no `pr:` when `make release
VERSION=0.4.32` generated `docs/releases/v0.4.32.md`. Its notes line shipped as

```
- PL-TGFY PL-Z34C is a frozen gate entry ... so the gate holds an entry nothing can clear
```

while its five siblings all carry `— #742`, `— #743`, `— #739`, `— #740` and
`— #744`. `bin/docket record` then wrote `pr: 745` onto the item correctly, but
the notes were already on disk and `bin/docket release --dry-run` answers
`Nothing to release: no finished work since 0.4.32`, so there is no supported
way to regenerate them. The line was corrected by hand on that branch.

**The documented procedure is what produces it.** The `docket` skill's release
mode, and `PL-V3GD`'s own brief, both order the steps `make release` first and
`bin/docket record` second. That order is right for everything else — `record`
wants the merge on the base — but it guarantees this outcome for any item that
merged between the previous cut and this one without its number being
backfilled first.

**Why it matters.** The notes are the permanent record of what shipped where,
and `pr:` is how a reader gets from a released item back to the change that
made it. A missing number is not wrong, but it is unrecoverable through the
tool: the one command that would rewrite the line refuses, correctly, because
re-cutting a shipped release is what leaves two sets of notes disagreeing about
the same items (`PL-1MKQ`'s territory).

**Two candidate fixes, and the cheap one looks right.** Either `bin/docket
release` runs the same backfill `bin/docket record` does before it writes the
notes — it already fetches, so the information is in hand — or the documented
order is swapped so `record` runs first. The first is better: it removes the
failure rather than asking every future cut to remember, which is `CLAUDE.md`'s
preference for deterministic tooling over a rule a session has to hold.

**Done when.** A cut whose finished set includes an item that merged without a
`pr:` still writes that item's pull request number into the release notes, with
a test driving that case.
