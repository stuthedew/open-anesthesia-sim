---
id: PL-38HD
title: Cut v0.5.6 from the twelve items finished since v0.5.5: the in-flight guards stop guessing who holds an item, and verify's assertion check reads parsed statements rather than lines, with nothing in the simulator moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.7
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
closed: 2026-09-23
pr: 931
payoff: the twelve items finished since v0.5.5 ship under their own number and stop being re-offered in every session digest, and a release that moves nothing a learner can reach says so by tree identity rather than by assertion
verify: grep -q "^version = \"0.5.6\"" pyproject.toml
---

**Problem.** Cut v0.5.6 from the twelve items finished since v0.5.5: the in-flight guards stop guessing who holds an item, and verify's assertion check reads parsed statements rather than lines, with nothing in the simulator moving

Twelve items have closed since v0.5.5 and are re-offered in every session
digest. None completes a feature - seven advance partway: `carrier-detection`,
`parallel-sessions`, `verify-false-reject`, `gate-list-integrity`, `ci-cost`,
`pr-body-integrity` and `release-process` - and seven are Gate 2 entries
(`PL-0HPV`, `PL-3QM9`, `PL-4W2L`, `PL-7TVT`, `PL-HX5C`, `PL-N2PP`, `PL-WFFX`),
which stands at 39 of 185 cleared at this cut: 29 at v0.5.5, these seven, and
`PL-XQGH`, `PL-CNJH` and `PL-2DTK`, dropped by `PL-4W2L`'s decision. None is a
milestone, and every number above this one is spent - `bin/docket wave`
reserves 0.6.0, 0.7.0, 0.8.0 and 0.9.0 - so this is a patch on § "Versioning
decision"'s test rather than a capability boundary.

## What this release contains, by tree object

| Object | v0.5.5 | cut | |
| --- | --- | --- | --- |
| `src/` | `37b0a4c` | `37b0a4c` | identical - `core/`, `data/` and `app/` with it |
| `tests/reference/` | `a184830` | `a184830` | identical |
| `docs/MODEL.md` | `148686b` | `148686b` | identical |
| `README.md` | `9938368` | `9938368` | identical |
| `.github/` | `27c67f3` | `27c67f3` | identical |

So nothing a learner can reach moves, read off tree identity alone. The diff
against the v0.5.5 tag outside `docs/items/` and this cut's own files is the
queue tool and what describes it: `subprojects/docket/` (source and tests), `tools/open_pull_requests.py`
and its test, `.claude/skills/docket/modes/` `start.md`, `close-out.md` and
`release.md`, `docket.toml`, `docs/ARCHITECTURE.md` and `ROADMAP.md`.

`.github/` differs from the `da3c951` v0.5.5's row names because that row was
measured at its cut and `#920` then rewrote two comments in `quality.yml`
before the tag. `git diff da3c951 27c67f3` is comment lines only.

## The theme

Six items are one question answered wrongly six ways - who holds an item:
`PL-3QM9` and `PL-7TVT` (an age that was a calendar date, and "do not start
these again" resting on it), `PL-N2PP` and `PL-HX5C` (work nobody had pushed,
closed by the empty-commit start rule), `PL-8FJK` and `PL-3W3P` (a queue-only
commit read by where it wrote rather than what it did). `PL-4W2L` rebuilds
`verify`'s assertion check at the statement altitude, and `PL-0HPV` puts the
scoped verify replay into `make check`. The rest are `PL-RFHH`, `PL-WFFX`,
`PL-BYN2`, and `PL-3XWZ`, the v0.5.5 cut, which closes here because a cut
cannot stamp itself. The baseline section in `ROADMAP.md` is written around
that rather than around the class labels.

## v0.5.5's tag span

`#920` (`PL-0HPV`) and `#921` (`PL-WFFX`) closed their items after v0.5.5's cut
was taken and before its tag, so `git describe --contains` resolves them to
v0.5.5 while this release's notes describe them. v0.5.5's notes take the
`### also inside this tag's span` pointer in this cut, now that the release it
names exists. Probed before writing it with a local `v0.5.6` tag on the cut
commit, deleted afterwards: `tools/doc_check.py` asked for exactly the two
lines written, and `make check` would otherwise have failed on `main` the
moment the v0.5.6 tag was pushed. `#919` (`PL-7TVT`'s start rule) and `#922`
(`PL-4W2L`'s decision) merged in the same window but closed no item that
shipped, so the check asks nothing of them; the baseline section names both.

## Shipped as cut

`list_sessions` at the cut showed four sibling sessions running, each on item
work - `PL-J6HP`, `PL-R808`, `PL-9RFP` and `PL-NGBM` - and none holding a
cut. `bin/docket flight` reported no ref carrying one, `v0.5.5` was tagged on
its release commit `c903f738`, and `bin/docket release` fetched and did not
refuse. The mechanical half was pushed first, as `39235c6e`, so a second cut
from any session is refused from that push on.

**`#930` merged after the cut** (`PL-NGBM`, `PL-M6FY`, `PL-3T2Q`: one
`Invocation` per `bin/docket` command, so `--no-git` asks git nothing), touching
only `subprojects/docket/` and item files, so every tree-identity claim above
holds at the tag. `origin/main` was merged into this branch at the project
owner's request on 2026-09-23 ("refresh main"), cleanly. It ships as cut: the
three are described in the next release, and v0.5.6's notes take the
`### also inside this tag's span` pointer at that cut, which nothing prompts
until the next tag is pushed (`PL-JLYG`).

Anything merging between this cut and the tag sits inside the `v0.5.6` tag
without being named in its notes and takes the pointer under the next release,
on `PL-V065`'s ratified precedent (project owner, 2026-09-21). This item
closes here and ships under the next release - a cut cannot stamp itself.

**Done when.** `pyproject.toml` reads 0.5.6, `docs/releases/v0.5.6.md` holds
the notes, `docs/releases/v0.5.5.md` carries its tag-span pointer,
`ROADMAP.md` carries the version-table row with the `current baseline` mark
moved onto it and a baseline section, `make check` is green, and the tag is
run by the project owner on the merge commit.
