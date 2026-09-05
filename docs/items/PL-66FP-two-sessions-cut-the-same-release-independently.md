---
id: PL-66FP
title: Two sessions cut the same release independently: docket release has no in-flight guard, so a second session bumps the version and writes notes for a version already on main
priority: P2
effort: M
status: done
classes: infra
feature: parallel-sessions
milestone: v0.4.0
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-05
pr: 323
verify: uv run pytest subprojects/docket/tests/test_release.py subprojects/docket/tests/test_vcs.py subprojects/docket/tests/test_cli.py -q && grep -q 'def test_a_release_another_branch_is_already_cutting_is_refused' subprojects/docket/tests/test_cli.py
---

**Problem.** Two sessions cut the same release independently: docket release has no in-flight guard, so a second session bumps the version and writes notes for a version already on main

**Why it matters.** A release is the widest write in the repository -
`pyproject.toml`, `uv.lock`, `ROADMAP.md`, a new `docs/releases/` file and a
`milestone:` stamp on every item going out - and it is the one change no guard
watches. Two of them cannot both land: the second is resolved by discarding a
whole session's work, which is what happened to v0.3.7 and what nearly
happened again to v0.3.9 the same day.

**Where.** `subprojects/docket/src/docket/release.py` decides,
`subprojects/docket/src/docket/vcs.py` reads git, `cli.py` wires the refusal
into `cmd_release`; `subprojects/docket/README.md` and
`.claude/skills/docket/SKILL.md` say what the refusal means.

**Done when.** `bin/docket release` fetches, then refuses to cut either a
version the default branch already holds or a release an unmerged ref is
already carrying, naming the evidence and the way out of each; the digest
says the same instead of offering a release; and the tests prove both against
a real checkout rather than a stubbed one.

**Decided 2026-09-05 (project owner).** Both halves, and the fetch. The
base-only check the item sketched would not have caught either race, for the
reason recorded below.

**Observed 2026-09-04.** Two sessions cut v0.3.7 within the same hour. One
merged as #301 with seven items plus `PL-DR1Z`; the other reached #302 with the
same seven minus `PL-DR1Z`, having bumped `pyproject.toml`, relocked `uv.lock`,
written `docs/releases/v0.3.7.md`, stamped seven items with `milestone: v0.3.7`,
added a version-table row and written a whole `## Current baseline: v0.3.7`
section. All of it duplicate. Resolving the merge meant taking `origin/main`'s
side of both conflicted files, after which `git diff origin/main` was empty and
#302 had nothing left to merge.

**Why the existing guards did not fire.** Every in-flight guard this project
has matches a `PL-` id - `docket flight`, `show`, `next`, `concurrent`, the
digest, `branch_id_check`. A release cut carries no item id by design:
`branch_id_check` prints "a release commit, which owes no id". So the one piece
of work that writes to `pyproject.toml`, `uv.lock`, `ROADMAP.md` and a new
`docs/releases/` file - the most collision-prone change in the repository -
is the only one no guard can see. `PL-CP74` closed exactly this hole for
unfiled housekeeping; a release is the same shape and was not covered.

**Where a check could go.** `bin/docket release` already refuses to cut while
the previous release is untagged. The same command could refuse, or warn, when
the version it is about to write already exists on the default base - readable
from `git show origin/<base>:pyproject.toml` or from `docs/releases/`, and
needing no network beyond the fetch a session has already done. Whether it
should be a refusal or an advisory is the open question: a session cutting a
release deliberately after a failed attempt would trip a refusal.

**Cost.** One session's release work, and a merge that had to be resolved by
discarding it. Nothing was lost from `main`, because the better cut won.


**Observed again 2026-09-04, while this item was being worked.** Two sessions
had a v0.3.9 release prepared within the hour: one archived
(`claude/pl-cg7j-ofg95t`, "confirm 0.3.9 as version") and one running, whose
branch `claude/simulated-time-step-count-575qso` carries `Release v0.3.9: the
chart's cost, the reader's choice, and a run that repeats` and pull request
#320. **The check this item asks for would not have fired on either**, because
v0.3.9 was not on `origin/main` at the time and still is not. That is the
limit of a base-only check, and it is not incidental: the loser of the v0.3.7
race cut from a checkout that did not yet hold `PL-DR1Z` (merged 11:26, eight
minutes before the winning release merged at 11:34), so `origin/main` said
0.3.6 in its checkout whenever it looked.

**What the base cannot see, a ref can.** Measured against this repository's
refs on 2026-09-04, one `git diff --name-only origin/main...<ref> --
docs/releases/` per unmerged ref named
`origin/claude/simulated-time-step-count-575qso -> docs/releases/v0.3.9.md`
and nothing else - three unmerged refs, one hit, no false positives. It needs
a fetch to be current, which `bin/docket release` does not do today.

**Built.** `release.already_released` decides the landed half from the base's
notes listing and version field, supplied by `vcs.released_on_base`;
`vcs.cuts_in_flight` reads the unmerged half from the refs, subtracting the
notes the base already holds - without that subtraction the branch whose
v0.3.9 release had merged twenty minutes earlier was still listed, because a
squash merge leaves the ref unlanded by `_work_already_on_base`'s test.
`cmd_release` fetches, then refuses on either, and marks a ref `HEAD`
contains as this checkout's own rather than a rival. The digest's
`Releasable:` line carries the same answer in place of the offer, computed
only where a release is being offered, since that is where the duplicate
starts.
