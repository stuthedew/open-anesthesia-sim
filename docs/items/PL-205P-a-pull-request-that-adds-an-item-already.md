---
id: PL-205P
title: A pull request that ADDS an item already passing its verify: goes green while the same check on main fails immediately, so the scoped replay's scope appears to exclude newly added items - twice now this has reddened main for four commits
status: untriaged
added: 2026-09-20
---

**Problem.** A pull request that ADDS an item already passing its verify: goes green while the same check on main fails immediately, so the scoped replay's scope appears to exclude newly added items - twice now this has reddened main for four commits

**Measured 2026-09-20.** Same check name, same content, opposite verdicts,
seventeen seconds apart in the merge:

| ref | what ran | `checks` |
| --- | --- | ---: |
| `2aebe030` - `#744`'s head, pre-merge | scoped replay (`--verify-base origin/main`) | **success** |
| `4bfcf00b` - `#744`'s merge commit on `main` | whole-store replay (`--verify`) | **failure** |

The error on `main` was `PL-66Z5 is open but its verify: command already
passes (1 of 193 checked)`. **`PL-66Z5` was introduced by `#744` itself**,
recovered off a stranded branch already at `status: ready` and already carrying
a `verify:` that passed on arrival - `git show
4bfcf00b:docs/items/PL-66Z5-*.md` shows both fields. So the branch created the
file the error is about, and the scoped replay that is supposed to cover "items
this branch changed" passed anyway.

**Hypothesis, not yet confirmed: an item the branch *adds* is not in the scoped
replay's scope.** `--verify-base origin/main` computes scope by diffing against
the base, where the file does not exist. That would make a newly added item
invisible at pull-request time in exactly the case where it is most likely to
be wrong - an item arriving from a recovery, a capture or a triage pass, which
nobody has run the command for. Confirm against
`subprojects/docket/src/docket/` before building anything; the number to beat
is how many open items entered the store already passing.

**Why it matters, and why it is not merely a gap.** This is `CLAUDE.md`'s first
compounding-friction test as stated - a check passes while the guarantee it
stands for is void. The pull-request check is the one anybody looks at; `main`'s
own run is watched by nobody, so both times this has happened it was found by
accident:

- **After `v0.4.31`**, four commits red while `ruff`, `mypy` and all 3243 tests
  were green. `ROADMAP.md`'s v0.4.31 baseline section records it: "Pull requests
  run the *scoped* replay, which is why no pull request showed it."
- **From `#744` to `#749`**, four commits red again - `#744`, `#745`, `#747`
  (the `v0.4.32` release) and `#748`. Found only because a session happened to
  read `main`'s run while refreshing for a closing block.

Twice is a pattern, and the cost is not the red itself but that **a release was
cut on a red `main` and nobody could have known**: `#747` carries `v0.4.32`.

**Two candidate fixes, and the cheap one may be enough.** Either the scoped
replay counts added item files as in scope - which is the bug if the hypothesis
holds, and costs one command in the scope computation - or the whole-store
replay also runs on `pull_request`, which CI measured at 147.7s against 1116.2s
serially and is affordable, but is the blunt answer. Prefer the first; measure
before choosing.

**Done when.** A pull request that adds an item whose `verify:` already passes
fails its own `checks` job, with a test driving that case, so the failure lands
on the branch rather than on `main`.
