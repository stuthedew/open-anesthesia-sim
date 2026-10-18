---
id: PL-3YRT
title: .claude/rules/apparatus-standard.md's paths: match none of the 35 apparatus tests under tests/unit/, so the apparatus test bar its section on tests states never loads when a session opens one
priority: P3
effort: M
status: done
classes: docs, infra
feature: apparatus-test-bar
milestone: v0.5.28
touches: .claude/rules/apparatus-standard.md, .claude/rules/where-new-code-goes.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
closed: 2026-10-18
pr: 1556
payoff: a session editing an apparatus test under tests/unit/ is told which bar it is held to, instead of applying the simulator's by default
verify: grep -qF 'apparatus-standard.md' .claude/rules/where-new-code-goes.md
---

**Problem.** .claude/rules/apparatus-standard.md's paths: match none of the 35 apparatus tests under tests/unit/, so the apparatus test bar its section on tests states never loads when a session opens one

**Evidence, 2026-09-27, at `553522c6`.** The rule's frontmatter is
`/subprojects/docket/**`, `/tools/**`, `/.claude/**`, `/.github/**` and
`/docs/worker.md`. Its section "What a test on this side is for" addresses
"the fifteen apparatus tests under `tests/unit/`", which `docket.toml`'s
`workflow_paths` now lists 35 of by name. None of them is under any of those
globs, so opening one loads the simulator's rules and not this one. The bar
the section states - a test earns its place if its absence would let a real
defect through - reaches `subprojects/docket/tests/` and never `tests/unit/`.
`PL-N6Y0`, which wrote the section, did not consider loading. `PL-FDMJ`
(ready) assumes the opposite ("named in `docket.toml`'s `workflow_paths`,
which counts them apparatus"). No item filed it; found by this session's
verification of `PL-8ZGY` (a subagent sweep, confirmed against the file).

**Related, not the same.** `PL-NB45` is the section's stale *count*; this is
its *scope*. The same edit can close both, since both are that one section,
but fixing the count leaves the rule unloaded. `docket new` matched this
capture to `PL-NB45` and wrote a recurrence there; that match was wrong, and
it was discarded uncommitted because `#1199` rewrites `PL-NB45`.

**Not decided here.** Listing 35 test paths in a rule's `paths:` would be a
fifth carrier of the apparatus set, which is `PL-8ZGY`'s generator (the lane
partition's hand-kept carriers). So the fix is either a glob that selects
those tests, which their names do not permit today, or moving the test bar
somewhere that loads for them. That choice belongs with `PL-8ZGY`'s design
round.

**Why it matters.** The bar in "What a test on this side is for" never loads
for the 35 apparatus tests under `tests/unit/`, so a session editing one applies
the simulator's bar instead. That is the safe direction to be wrong in -
`PL-21RC`'s reading of the same gap for `docs/maintainer.md` - so `P3`.

**Decision needed.** Where the apparatus tests get their bar from, now that
`PL-8ZGY` closed recording this as related rather than taking it into its design
round. **Recommended: move them into a directory of their own under
`tests/`**, which one glob in the rule's `paths:` and one `workflow_paths`
entry can each name, replacing the 35-file list rather than adding a fifth
carrier of it. Not `tools/tests/`: `tools/` is held to the 3.11 floor and these
tests run under 3.14. It moves 35 files and changes what `make check` and CI
collect, so it is a refactor to weigh, not a session's call alone.

**Done when.** Opening any test under `tests/` loads a rule that says which
bar it is held to - by the import rule `tools/workflow_paths_check.py` and
`docket.arming` apply, not by a list - and points the apparatus side at
`.claude/rules/apparatus-standard.md` § "What a test on this side is for"; and
that section says it reaches `tests/unit/` by that pointer.

**Generator check.** An instance of `PL-G424`'s fact (a scope carrier restating
the apparatus set): the gap `PL-21RC` names for `docs/maintainer.md`, one set of
files later. `PL-8ZGY` records it as related, not a member.

**Decided** (2026-10-12, in the first batched design round, a session's call):
no move; one pointer where the tests already load a rule. Counted against
`origin/main` at 919ad967: 42 test files under `tests/unit/` import no
`anesthesia_sim` (the 35 above was the count on 2026-09-27), and 74 open items
cite at least one of them, 80 citations in all. A move would turn every one of
those into a path `tools/doc_check.py`'s `check_citations` holds a live brief
to, so the moving pull request would carry 74 brief repairs beside
`docket.toml`, `tools/workflow_paths_check.py`, `arming.py`'s test rule and the
`Makefile` - for a `P3` gap whose failure direction is the safe one. That
number refutes the recommendation above, under
`.claude/rules/expert-review.md` § "Count what undoing it would cost, before
taking the cheaper route".

The cheapest carrier that loads for these files already exists:
`.claude/rules/where-new-code-goes.md` has `/tests/**` in its `paths:` and is,
by its own design, a file of pointers. One paragraph there says that which bar
a test under `tests/` is held to is the import rule
`tools/workflow_paths_check.py` and `docket.arming` already apply - importing
`anesthesia_sim`, the simulator's standard in `CLAUDE.md`; importing none of
it, `.claude/rules/apparatus-standard.md` § "What a test on this side is for",
which does not load on this path by itself - and restates neither bar.
`apparatus-standard.md`'s section then says it reaches `tests/unit/` by that
pointer rather than by its own `paths:`. No fifth carrier of the set, no file
moves, and the rule the section states finally loads where it is needed. It
repairs a rule that never loads for the files it governs - a defect in what
exists - so the pause on new workflow mechanisms does not hold it.
