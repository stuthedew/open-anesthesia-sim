---
id: PL-3YRT
title: .claude/rules/apparatus-standard.md's paths: match none of the 35 apparatus tests under tests/unit/, so the apparatus test bar its section on tests states never loads when a session opens one
status: untriaged
feature: apparatus-test-bar
touches: .claude/rules/apparatus-standard.md
added: 2026-09-27
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
