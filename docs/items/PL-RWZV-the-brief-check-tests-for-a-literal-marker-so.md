---
id: PL-RWZV
title: The brief check tests for a literal marker, so an elaborated heading fails and an empty one passes
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-08-31
closed: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_stub_above_a_real_brief_does_not_satisfy_the_check' subprojects/docket/tests/test_checks.py
---

**Problem.** `checks.py` tests brief completeness with `marker not in
item.body` against the literal strings in `REQUIRED_BRIEF` plus
`**Done when.**`. Substring presence is the whole test, so it is wrong in both
directions:

- **An elaborated heading fails.** `PL-921W` was captured with `**Why it
  matters, and why it is not new.**`, which is a better heading than the bare
  one and reads as the required section to any human. `docket check` reported
  `brief is missing **Why it matters.**` and the heading had to be flattened
  to satisfy it (done 2026-08-31, during triage).
- **An empty heading passes.** The same file carried a stub block - `**Problem.**`
  echoing the title, then `**Why it matters.**`, `**Where.**` and `**Done
  when.**` with nothing under any of them - above its real brief. Had the stub
  been all there was, triaging the item to `ready` would have passed the check
  with three empty sections.

**Why it matters.** The check exists so that an item reaching `ready` can be
worked by someone who was not there when it was captured. Presence of a string
is a proxy for that, and it is a weak one in the direction that matters: it
rejects good briefs on wording while accepting empty ones on structure. The
first cost is paid in edits to prose that was already right; the second is
paid by whoever picks up an item with nothing under its headings.

**Where.** `subprojects/docket/src/docket/checks.py` - `REQUIRED_BRIEF` and
the loop at the top of `_check_item_fields`, and `test_checks.py` beside it.

**Approach.** Keep the marker literal and cheap; change what counts as
present. Match a heading at the start of a line by its opening words
(`**Why it matters`) rather than by the whole string, and require some
non-whitespace text between it and the next `**`-opened heading. That stays
decidable, needs no regex over prose, and is the `CLAUDE.md` line exactly: it
decides whether a section has content, never whether the content is any good.

**Not urgent, and worth saying why.** One elaborated heading has been rejected
and no empty-section item has reached `ready` - the stub above was caught by a
reader, not by the check. This is a small tax with a small hole beside it, not
a live failure.

**Done when.** A heading whose opening words match a required marker satisfies
the check however it continues; a required section with no text under it does
not; and tests cover both, including the two real cases above.

**Triaged 2026-08-31, in the session that found it.** P3, `infra`,
`dev-tooling`. The `verify:` command keys on `heading` rather than `brief`:
`-k brief` already selects a passing test today and would prove nothing.

**Admitted to v0.2.8's frozen list, 2026-09-01, under the scope test,**
reversing the "not urgent" reading above rather than disputing it. Urgency is
not the test; a misfire in machinery the goal names is, and this is a `docket
check` misfire like `PL-5YK8`, on the gate that decides whether an item may
reach `ready`. The empty-section half stopped being hypothetical on 2026-09-01:
`PL-K2ZK` and `PL-W1LN` were both captured with the four-heading stub above
their real briefs, and both would have passed this check at `ready` had the
stub been all they carried. The stubs were removed by hand during that triage.

**Worked 2026-09-01.** The approach the brief proposed, with two things it did
not specify decided here.

*The first matching heading is the one judged.* This file was itself the
empty-section case - four headings echoing the format, empty, above the real
brief, at `ready` - so the rule had to say which occurrence it reads. "Any
occurrence with text under it" would have passed exactly this shape, which is
the hole rather than the fix; "all occurrences" would reject a brief that
legitimately returns to a heading later. The stub was deleted in this commit,
and `test_a_stub_above_a_real_brief_does_not_satisfy_the_check` holds the
shape so it cannot come back. The three other files carrying it - `PL-8MZN`
and `PL-V5XM` dropped, `PL-WFJ9` done - sit outside `OPEN_STATUSES` and the
check never reads them.

*An empty section and a missing one are now two messages, not one.* The fix
for each is different - write the section, against add the heading - and a
single "brief is missing" line naming both would send a reader to the wrong
one. `_section_text` returns `None` for absent and `""` for present-but-empty
to keep the two distinguishable at the call site.

*Validated against the store before it was written.* The rule was prototyped
over all 241 item files first: it flags this file's two empty sections and
nothing else, and reports nothing newly missing, so no existing brief is
rejected by the change. The `verify:` command was replaced at the same time -
it was a bare `-k heading`, which selected no test and exited 5 both before
and after the work.
