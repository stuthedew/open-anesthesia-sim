---
id: PL-ZPDM
title: vcs.tags and vcs.changed_items answer with a bare frozenset, so a git that does not answer is indistinguishable from a repository with no tags and a branch that changed nothing
priority: P2
effort: M
status: done
classes: defect
feature: git-silence-channel
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, tools/doc_check.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-22
pr: 892
verify: uv run pytest "subprojects/docket/tests/test_vcs_silence.py::test_one_silenced_git_call_never_leaves_a_read_looking_clean[tags]" "subprojects/docket/tests/test_vcs_silence.py::test_one_silenced_git_call_never_leaves_a_read_looking_clean[changed_items]"
---

**Problem.** vcs.tags and vcs.changed_items answer with a bare frozenset, so a git that does not answer is indistinguishable from a repository with no tags and a branch that changed nothing

**Found building `PL-Q9Z1`'s failure channel, 2026-09-19, and narrowed the same
day.** Every other public read in `subprojects/docket/src/docket/vcs.py` now
wraps its runner in `_Silences` and reports an unanswered call as `declined`.
These two cannot: `frozenset()` is the whole answer, and it is what a silence
and an empty repository both produce.

`subprojects/docket/tests/test_vcs_silence.py` holds them by asserting the
breach - each still loses a finding to a silence, and says nothing - so the gap
is a running test rather than a marker excusing one, and it fails the day this
closes.

**`default_base` was in this item's first title and is not this item.**
`PL-73P0` had already been filed for it by `PL-BHVM`'s own session, with the
wider case: the base is the one input whose wrongness cannot be seen in any
answer downstream of it, because every downstream answer is *about* that base.
That is a stronger argument than this one and it keeps the read.

**Why it matters, read from the two call sites rather than in general.** A silence
returning `frozenset()` is not a wrong answer a caller can question - it is the
right *shape* of answer, carrying a fact the caller has no way to doubt, and the
two callers act on opposite halves of that:

- `tags` reaches `cli.py:1365` as `is_untagged(current, tags(root))`. An empty set
  makes every version untagged, so `bin/docket release` prints the untagged
  warning and returns 1. The cut is refused - the safe direction - but the
  operator is told a specific and possibly false fact about the repository, and
  the remedy it implies is to push a tag that may already exist.
- `changed_items` reaches `cli.py:309`, scoping a `--verify` run to the items a
  branch changed. An empty set means the scoped run checks nothing and says
  nothing, which is the permissive direction. The comment directly above it
  promises the opposite - both reads "under-report where that base cannot be
  resolved rather than guessing - a scoped run then checks nothing and says so" -
  and that promise is kept for an unresolvable base and broken for a silent diff.

**The pattern is already one call away.** `vcs.py:4204-4207` runs the *private*
`_changed_items` inside a `_Silences` wrapper and returns
`RecordReport(declined=run.reason)` when it comes back empty. The public read is
the bare one.

**Done when** a caller can tell "no tags" from "git would not say", and
`test_vcs_silence.py` moves the two out of `GAPS` and into `SWEPT`.

**Found at triage, 2026-09-19: the fixture claims three gaps for this item, not
two.** `subprojects/docket/tests/test_vcs_silence.py` carries `known_gap="PL-ZPDM"`
on `tags` (line 343), `changed_items` (line 348) **and `default_base`** (line
350). The paragraph above disowns the third - `default_base` is `PL-73P0`'s, on
the stronger argument that the base is the one input whose wrongness cannot be
seen in any answer downstream of it. So closing this item moves two of the three
entries, and the third needs its `known_gap` re-pointed at `PL-73P0` by whoever
reaches it first. Left as found rather than corrected here: a triage pass sets
fields, and re-attributing another item's gap is that item's work.

**Closed 2026-09-22.** `tags` answers with a `TagSet` (`names`, `declined`) and
`changed_items` with a `ChangedItems` (`identifiers`, `declined`), both wrapping
their runner in `_Silences` like every other public read in the module. Both are
in `test_vcs_silence.py`'s sweep now; `default_base`'s entry is re-pointed at
`PL-73P0`, which the paragraph above had already disowned it to.

**The brief had the `tags` caller's direction backwards, and the real direction
is the permissive one.** It read the silence as refusing the cut - "the safe
direction" - on the reasoning that an empty set makes every version untagged.
`release.is_untagged` returns `False` for an empty set and has since the gate was
written (`c9285084`, 2026-08-30, `PL-J3ZK`): a project holding no tags is held to
nothing, because a tool that started refusing releases in a project that never
tags would be teaching a practice rather than holding one. So a silence was not a
refusal that named a possibly false fact - it was free passage, on the one gate
that exists because the gap it guards cannot be repaired afterwards. The claim
was wrong when written rather than gone stale; nothing about the code moved
between 2026-09-19 and this close.

**What each of the three callers does now.**

- `cmd_release` refuses on `declined`, through `_unreadable_tags_refusal` rather
  than `_untagged_warning`: that message names a specific fact - this version
  carries no tag - which is exactly what has not been established, and sends the
  operator to push a tag that may already exist. A dry run is still allowed
  through with the message, as it is for a genuinely untagged release, and
  `--no-git` remains the escape hatch for a checkout with no git to ask.
- `cmd_check` declines the `verify:` replay whole - `LandedReport(declined=...)`,
  so the headline counts it unchecked - instead of scoping it to an empty set and
  reporting a clean run. The call site's comment had promised "a scoped run then
  checks nothing and says so"; the saying-so half was the part missing.
- `doc_check.check_tags` keeps its silence, which its own docstring argues for: a
  check that fails on how somebody fetched the repository is a check that gets
  switched off. The behaviour is unchanged and is now a decision the code states
  rather than the accident of one empty set covering two cases.

**One exit code is worth recording, because it decides which cases this reaches.**
Inside a repository, `git diff --name-only <base>...HEAD` exits **128** for a base
that does not resolve, so a shallow CI clone whose base ref was never fetched now
declines rather than replaying nothing. Outside a repository the same command
exits **1** - "error: Could not access" - which `_run_git` reads as git answering
no, so `test_verify_base_narrows_the_replay_to_what_the_branch_changed` still
drives the narrowing rather than the decline. `git tag --list` outside a
repository exits 128, which is what the release-refusal test is built on.
