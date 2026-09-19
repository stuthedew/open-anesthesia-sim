---
id: PL-R5VS
title: Cut v0.4.31 from the 12 finished items since v0.4.30: the release that completes model-capability-routing and recommendation-rationale
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-19
payoff: the twelve items finished since v0.4.30 stop being twelve unshipped files and get a milestone: stamp saying where they shipped, and the next cut stops being blocked behind this one
verify: grep -q '^version = "0.4.31"' pyproject.toml && test -f docs/releases/v0.4.31.md && grep -q '^## Current baseline: v0.4.31' ROADMAP.md
---

**Problem.** Cut v0.4.31 from the 12 finished items since v0.4.30: the release that completes model-capability-routing and recommendation-rationale

**Asked for by the project owner, 2026-09-19** ("cut new version"). Twelve
finished items stand unshipped since `v0.4.30` (`bin/docket release --dry-run`),
and they complete two features: `model-capability-routing` and
`recommendation-rationale`.

**Why this number.** The mechanical guess is `0.4.31` and nothing contests it.
`bin/docket wave` reports `0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0` as reserved by
`ROADMAP.md`, so no minor number is free, and a patch is what the content
warrants - measured by tree object rather than read off the diff:

- `git diff --stat v0.4.30..origin/main -- src/` reports **one** file changed,
  `core/matrix_exponential.py`, 9 insertions and 5 deletions, and the whole of
  it is inside the module docstring: `PL-5MT4`'s correction of a DOI that
  carried a spurious trailing `10` and the re-dating of the provenance note
  beside it. No executable line moved.
- `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.30` and here,
  so no stored scientific value moved.
- `tests/reference/` resolves to `fcb3eca` at both, so every
  published-reference expected value is byte-identical and still met.

**Both release refusals were checked rather than assumed.** `v0.4.30` is tagged
on `origin` at `fe32c6f` (`git ls-remote --tags origin`), which peels to the
merge commit of `#730`, so the refusal-on-untagged-predecessor does not bind.
And `bin/docket release --dry-run` fetches before it answers and named no
unmerged ref carrying a cut, so no second session is mid-release.

**The cadence's no-interim-release rule was checked, and this release does
carry a gate entry.** `PL-7DMJ` (the alveolar water-vapour simplification) is
a Gate 1 frozen entry - added 2026-09-19, `science`-classed, and present as a
list bullet inside `ROADMAP.md` § "v0.5.0 - the case you can branch" -> "Debt
gate: the frozen list", checked against the list itself rather than against a
count. The other eleven appear in that section nowhere or only under the later
§ "Declined to Gate 2 on the refilling-queue ground", which is not the frozen
list.

So the check that cleared `v0.4.30` does not clear this one, and the question
is whether § "The cadence"'s "no interim release is cut partway through
clearing" refuses the cut. It does not, on the project's own recorded practice:
**159 of the 175 frozen entries already carry a `milestone:` stamp from a
`v0.4.x` patch**, spread across `v0.4.5` through `v0.4.29`, and `v0.4.29`'s own
release notes describe its predecessor in as many words - "a patch on the
`v0.4.x` track carrying one Gate 1 entry". The `v0.4.x` row records that the
track "freezes no gate and takes no section of its own" and "promises no
particular patch number", which is what makes the two compatible: the sentence
refuses giving *the gate* a version, and the continuously-cut patch track is
not that. This release ships one such entry, as `v0.4.24`, `v0.4.25`, `v0.4.28`
and `v0.4.29` each did.

**Not fixed here, and not this release's to fix.** `main` is red on
`bin/docket check --verify`: `PL-8GQW` (push the `v0.4.30` tag) is an open item
whose `verify:` command already passes, because the owner pushed the tag after
the item was filed. `#736` closes it and is open and unmerged. `PL-8GQW` is not
among the twelve, so it is out of this cut's scope and ships in whichever patch
follows its merge.

**Why it matters.** `bin/docket release` refuses to cut a release while the
previous one is untagged, so an unshipped run of finished work compounds: the
next cut cannot start until this one is tagged, and the items stay unstamped
with no `milestone:` recording where they shipped. The release notes are also
the only place the twelve are read as two completed features rather than as
twelve files.

**Done when.** `pyproject.toml` reads `0.4.31`, `uv.lock` agrees,
`docs/releases/v0.4.31.md` exists, `ROADMAP.md` carries a `v0.4.31`
version-table row with the `current baseline` mark moved onto it and a baseline
section saying what the release was for, and `make check` passes. The tag itself
is the project owner's to push and is outstanding until they confirm it.
