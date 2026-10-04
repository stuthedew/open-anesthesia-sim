---
id: PL-N7LK
title: Four apparatus documents wrap a spaced hyphen to a line start, so CommonMark renders a clause as a list item: docs/WORKING_NOTES.md:912, docs/maintainer.md:240, subprojects/docket/README.md:369 and .claude/skills/docket/modes/close-out.md:293 (the PL-DSMK shape outside ROADMAP.md; twelve such lines across six documents suggest a doc_check rule that a list may not interrupt a paragraph, captured rather than built while the generator pause holds)
priority: P3
effort: S
status: ready
classes: docs, defect
feature: prose-renders-as-written
touches: docs/WORKING_NOTES.md, docs/maintainer.md, subprojects/docket/README.md, .claude/skills/docket/modes/close-out.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: docs/maintainer.md's statement of which pull requests wait for the owner's read, and three other passages, render as the single statements they are instead of a paragraph cut short and a stray bullet
verify: ! grep -qE '^ *- which was settled on fit' docs/WORKING_NOTES.md && ! grep -qE '^ *- (or .\.github/workflows/|the paths where a wrong clinical value)' docs/maintainer.md && ! grep -qE '^ *- and by the time the discussion becomes' subprojects/docket/README.md && ! grep -qE '^ *- (that per-run holder widgets|read as obviously true)' .claude/skills/docket/modes/close-out.md
---

**Problem.** Four apparatus documents wrap a spaced hyphen to a line start, so CommonMark renders a clause as a list item: docs/WORKING_NOTES.md:912, docs/maintainer.md:240, subprojects/docket/README.md:369 and .claude/skills/docket/modes/close-out.md:293 (the PL-DSMK shape outside ROADMAP.md; twelve such lines across six documents suggest a doc_check rule that a list may not interrupt a paragraph, captured rather than built while the generator pause holds)

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`uv run --no-project --with markdown-it-py==4.2.0 markdown-it docs/WORKING_NOTES.md docs/maintainer.md subprojects/docket/README.md .claude/skills/docket/modes/close-out.md | grep -E '^<li>(which was settled|or <code>.github|and by the time|that per-run)'`
prints four list items, one per document, opening "which was settled on
fit", "or `.github/workflows/`, `.claude/hooks/` and", "and by the time the
discussion becomes implementation" and "that per-run holder widgets": each a
one-item list opened on the line after a paragraph's last line, the first and
last nested inside the list entry or numbered step they sit in. A scan of
every tracked Markdown file outside `docs/items/` with markdown-it-py for a
list opening that way finds 36: these four, `PL-T4FK`'s line in
`docs/MODEL.md`, and 31 that are lists by intent (19 in `docs/pr-bodies/`,
ten in the YAML front matter of `.claude/rules/` files, and one each in
`docs/worker.md` and `docs/releases/v0.5.9.md`). With `ROADMAP.md`'s fixed in
`#1343`, these five are the only ones left, and a rule that a list may not
interrupt a paragraph would have to tell the other 31 apart.

**Why it matters.** Each passage renders as a paragraph that stops short and
a bullet that opens on a conjunction. The costly one is `docs/maintainer.md`
§ "Read a simulator change before you arm it", the owner's statement of which
pull requests `bin/docket arm` holds for their read: rendered, the paragraph
ends at "the paths where a wrong clinical value could reach the screen", and
`.github/workflows/`, `.claude/hooks/`, `arming.py` and the account of how a
held pull request is merged follow as a bullet beginning "or". Sessions read
the raw text, where the dash reads as written, and none of the four splits a
quoted citation, so no check misreads them today; the cost falls on the page
the owner reads.

**Done when.** Every spaced hyphen in the four passages, both of a bracketing
pair where there are two, sits mid-line or at the end of a line: the "numpy,
and it is already decided" entry in `docs/WORKING_NOTES.md`, the paragraph
opening "`bin/docket arm` holds a pull request for your read" in
`docs/maintainer.md`, the paragraph opening "It was fifty lines of bash" in
`subprojects/docket/README.md`, and the "Make one of the sceptics run the
claim" step in `.claude/skills/docket/modes/close-out.md`. The `markdown-it`
command above then prints nothing.

**Generator check.** A member of `PL-R417` by its fact, where one statement
ends in a format that continues statements across lines, met here by a writer
rather than a reader: a Markdown paragraph runs on across physical lines until
a line opening with a list marker ends it, and each of these wraps took that
line for a continuation. With `PL-DSMK` (done) and `PL-T4FK` it is three items
on the head's fact, so it belongs to that head rather than to a new one. It is
not added to `PL-R417`'s `root-cause-of:` here, because #1353's branch holds
that file. No check holds the fact for a writer; `PL-LNNL` is the one that
would.
