---
id: PL-QFFF
title: tools/dead_ends.py's ENTRY pattern does not match docs/dead-ends.md line 74, whose bold title is followed by a parenthetical before its dash, so the session-start digest drops that dead end with nothing reported and shows 10 of the 11
priority: P2
effort: S
status: ready
classes: defect
touches: tools/dead_ends.py, tests/unit/test_dead_ends.py, docs/dead-ends.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: every session starts with the whole dead-ends record, and an entry the tool cannot read fails make check instead of vanishing from the digest
verify: grep -q 'def test_an_entry_the_pattern_cannot_read_is_refused' tests/unit/test_dead_ends.py
---

**Problem.** tools/dead_ends.py's ENTRY pattern does not match docs/dead-ends.md line 74, whose bold title is followed by a parenthetical before its dash, so the session-start digest drops that dead end with nothing reported and shows 10 of the 11

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`).** Line 74 opens `- **Detecting duplicate captures by shared cited referents** (item ids, shas, ...) — refuted 2026-09-16`, and the digest of this session listed ten dead ends without it. Not a `PL-R417` member: the entry is on one line, and the fault is which shapes the pattern admits, not where the entry ends.

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`python3 -c "import sys; sys.path.insert(0, 'tools'); import dead_ends as d; t = d.DEAD_ENDS.read_text(); b = d._bullets(t, []); print(len(b), len(d.entries(t)), [n for n, _, j in b if not d.ENTRY.match(j)], d.check(t))"`
printed `11 10 [74] []`: eleven bullets open like an entry, ten are entries,
the one on line 74 is dropped, and `check` finds nothing.
`python3 tools/dead_ends.py check` exits 0 and `emit` prints ten. So the tool
does not report a bullet it fails to parse: `entries` keeps what `ENTRY`
matches and discards the rest, and `check` refuses only a bullet spanning two
lines, so a one-line bullet that `OPENING` matches and `ENTRY` does not goes
unreported, though the comment on `OPENING` says such a bullet cannot leave
the digest unreported. `ENTRY` is unchanged since `#527` (2026-09-13) and
line 74 dates from `#607` (2026-09-15), so this dead end has never reached a
digest.

**Why it matters.** Every session since 2026-09-15 has started without the
refutation of detecting duplicate captures by shared cited referents, which
fired on 84% of open items when `PL-85NT` measured it. The digest is the only
route by which a dead end is in context at the moment a session re-proposes
it; the module docstring's own case is that nothing else would prompt a
session to look. The drop hides the entry from the rest of the tool as well:
its `PL-85NT` is never checked as an id, and `budget` reads 2,460 emitted
bytes where the eleven entries emit 2,864, both under the 3,200-byte nudge
band, so admitting it trips no budget test. No test sees the drop:
`test_emit_prints_the_header_and_every_entry` counts against `entries` itself.

**Done when.** `python3 tools/dead_ends.py emit` prints all eleven entries,
line 74's among them, whether `ENTRY` admits an aside between the title and
its dash or the entry is rewritten to the shape `ENTRY` reads; and `check`
refuses, naming its line, any bullet that `OPENING` matches and `ENTRY` cannot
read, pinned by `test_an_entry_the_pattern_cannot_read_is_refused` in
`tests/unit/test_dead_ends.py`. The shipped file is then held by the `check`
run `test_the_script_runs_under_a_bare_interpreter` already makes.

**Generator check.** A re-entry of `PL-F5B9` (closed 2026-10-04, `#1352`):
the same defect, an entry dropped from the digest with nothing reported, which
that fix should have covered, since the `OPENING` it added carries a comment
saying no such bullet can leave the digest unreported. Its cause was a wrapped
entry, which made it a `PL-R417` member; line 74 sits on one physical line, so
this is not that head's fact. The fact misread is which bullets of
`docs/dead-ends.md` are entries: the tool holds two readings of it, `OPENING`,
which the wrap refusal reads, and `ENTRY`, which `emit`, `budget` and the id
check read, and nothing reports where they disagree. No head's `misread:`
states it.
