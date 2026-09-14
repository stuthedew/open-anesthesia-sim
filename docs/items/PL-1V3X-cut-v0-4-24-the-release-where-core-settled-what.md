---
id: PL-1V3X
title: "Cut v0.4.24: the release where core/ settled what its dimensionless numbers are called"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 565
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.24"' pyproject.toml && test -f docs/releases/v0.4.24.md
---

**Problem.** Cut v0.4.24: the release where core/ settled what its dimensionless numbers are called

**Ten finished items since v0.4.23**, offered and approved by the project owner
on 2026-09-14. `v0.4.23` was confirmed tagged on the remote at `7dd1a03` before
the cut, so `bin/docket release`'s refusal-on-untagged-predecessor did not
apply, and `main`'s own quality run #1906 on `4b4f80d` was confirmed green
first - the run that proved `main` had recovered from the `PL-6TQH` store error.
`list_sessions` showed no live session carrying a cut and none asking for one.

**A patch, and the version policy is why.** `ROADMAP.md` § "Versioning
decision" picks the number for the capability boundary a release crosses, and
this crosses none: the only behavioral change is a render-loop cache that makes
an unchanged frame cheaper. `bin/docket wave` puts the project between numbered
steps on `v0.4.x` with Gate 1 next, so `0.4.24` is the patch-track successor.

**What the release does not touch, measured rather than asserted.** A release
that renames the scientific core's vocabulary is exactly the one in which a
value could move unnoticed, so the claim is made on tree objects and executable
lines rather than on the diff's prose:

- `tests/reference/` resolves to `42ce3b2` at both `v0.4.23` and here - every
  published-reference expected value byte-identical, and still met by the suite.
- `src/anesthesia_sim/data/` resolves to `6960c78` at both, unmoved now across
  three releases.
- Eleven files under `src/` change and **no numeric literal in executable code
  does**: every changed line carrying a number is a docstring or a comment, and
  the only executable changes in the display layer are `NewType` annotations,
  which erase at runtime.

**What is in this commit.** `make release VERSION=0.4.24` wrote the bump,
`docs/releases/v0.4.24.md`, the `milestone:` stamps and the relocked `uv.lock`.
Written by hand, which it does not generate:

- the `v0.4.24` version-table row, and `v0.4.23` demoted from current baseline;
- the "Current baseline: v0.4.24" section, in four subsections.

Nothing cited § "Current baseline: v0.4.23", checked before the rename and
confirmed by `make check` after - the breakage `PL-MHYG` caused at the previous
cut did not recur.

**One thing rides this item's id rather than taking one of its own.**
`bin/docket record` wrote the seven `pr` numbers the base was owed: `PL-1PSX`
to #563, and `PL-6KNM`, `PL-6TQH`, `PL-BDNB`, `PL-BQ46`, `PL-KL2Q`, `PL-XP6W`
to #561.

**After the merge.** The tag is the project owner's to push; this environment
cannot push a tag ref (`PL-N936`), and attempting it fails convincingly rather
than loudly.

