---
id: PL-9GBS
title: Check whether make release and tools/doc_check.py say they could not answer on a shallow clone: the v0.6.19 cut on a shallow thread checkout asked for no pointer lines in v0.6.18's notes, and after git fetch --unshallow doc_check named #2103 and #2118 as inside v0.6.18's tag span
priority: P2
effort: S
status: done
classes: defect
feature: release-process
touches: tools/doc_check.py, subprojects/docket/src/docket/release.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2340
payoff: a release cut on a shallow clone says it could not read the history instead of leaving out pointer lines without a word
tests: tests/unit/test_doc_check.py::test_a_truncated_clone_with_no_finding_still_says_it_could_not_walk_its_spans
---

**Problem.** Check whether make release and tools/doc_check.py say they could not answer on a shallow clone: the v0.6.19 cut on a shallow thread checkout asked for no pointer lines in v0.6.18's notes, and after git fetch --unshallow doc_check named #2103 and #2118 as inside v0.6.18's tag span

**Why it matters.** A release cut on a shallow clone may leave out pointer lines that the release notes owe, with no warning. A tool that cannot read history must say so rather than answer as if the history were empty.

**Done when.** The answer is recorded here with its date: whether `make release` and `tools/doc_check.py` each report that they could not read the tag span on a shallow clone. Where one does not, a test shows it now says so.

**Generator check.** The fact is whether the local history is deep enough to answer. `PL-Z1ZT` (a prediction count taken on a shallow clone) is a second reader of it, and is in flight elsewhere; if a third appears, the fact is a generator.

**Answered 2026-11-27.** `make release` runs `bin/docket release`, which writes the new release's notes and reads no tag span, so it never asks for pointer lines and has nothing to decline. The pointer lines are asked for by `tools/doc_check.py`'s `check_tag_span_covers_its_notes`, which `make check` runs after the cut. On a shallow clone that check declined only when it found a short span. A closure whose commit is past the clone's boundary is in no span the clone can walk, so the check found nothing and said nothing. That is how the v0.6.19 cut asked for no pointer line in v0.6.18's notes, and how #2103 and #2118 surfaced only after `git fetch --unshallow`.

**Done 2026-11-27.** The check now declines on any shallow clone, and on any checkout whose completeness git cannot report, whether or not it found something. The decline says that a closure older than the clone's history may be missing from its notes unseen, and that `git fetch --unshallow --tags` makes the question answerable. The old comment justified declining only with a finding by `check_tags`'s reasoning, that a clone which has fetched its tags can answer. That holds for `check_tags`, whose question is which tags exist, and not here: a shallow clone stays shallow after `git fetch --tags`, so it still cannot walk the spans.

**Regression.** `tests/unit/test_doc_check.py::test_a_truncated_clone_with_no_finding_still_says_it_could_not_walk_its_spans` clones a tagged history two commits deep, so the clone holds neither closure of the older span. It fails against `tools/doc_check.py` at `8f404cfa`, where the clone reports no error and no decline.

**Documents checked:** `check_tag_span_covers_its_notes`'s docstring and the comment above the decline, both updated; the docstring of `test_a_truncated_clone_declines_instead_of_reporting_a_span_it_cannot_walk`, which named the old reasoning and now does not; `.claude/skills/docket/modes/release.md` and `ROADMAP.md` § "Tags", neither of which mentions a shallow clone; `docs/apparatus.md`'s line for `doc_check.py`, which is still true.
