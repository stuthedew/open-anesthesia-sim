---
id: PL-KKHD
title: The owner's arm rule for read holds lives only in the Projects trial's instructions: arm on green unless the change reaches src/, tests/, docs/MODEL.md, README.md or arming.py, while bin/docket arm, CLAUDE.md and docs/maintainer.md hold every change outside the store unarmed for his read
priority: P2
effort: M
status: done
classes: defect, infra
feature: owner-rules-in-repo
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_claims.py, docs/maintainer.md, CLAUDE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) and not safety or science; the Projects trial began on 2026-09-25, so the problem was not present at the freeze, and nothing on the frozen list names it
added: 2026-10-03
closed: 2026-10-03
pr: 1320
payoff: every session holds for the owner's read only a change to the simulator paths or arming.py, and arms any other on green, as his rule asks
verify: grep -q 'def test_a_change_outside_the_owners_read_list_arms_on_green' subprojects/docket/tests/test_cli.py
---

**Problem.** The owner's arm rule for read holds lives only in the Projects trial's instructions: arm on green unless the change reaches src/, tests/, docs/MODEL.md, README.md or arming.py, while bin/docket arm, CLAUDE.md and docs/maintainer.md hold every change outside the store unarmed for his read

**What the owner's rule says, and where it is written.** The Projects trial's
instructions (Project settings > Memory > Project instructions), as this
project's threads receive them on 2026-10-03:

> `hold` naming a claim: the work is unfinished, so finish it or yield it. Any
> other `hold` that raises no specific question for me is armed on green, with
> the hold's reason in your report. The exception is a pull request that
> changes src/, tests/ outside subprojects/, docs/MODEL.md,
> src/anesthesia_sim/data/, README.md or
> subprojects/docket/src/docket/arming.py: leave it unarmed and ask me to read
> it, and I answer "Merge it".

`PL-NZC0`'s copy of the same instructions, taken on 2026-09-25, reads "let
`bin/docket arm` decide arming", so the rule changed after that date, and in the
instructions only. Its kind is unrecorded: nothing says whether the owner wrote
it or ratified a coordinator's draft.

**Where the repository says otherwise.** `bin/docket arm` answers `hold` for any
path outside `docs/items/`, `docs/pr-bodies/` and `subprojects/docket/`
(`arming.arms_on_green`), and prints `arming.READ_ASK`, the ask for the owner's
read. `CLAUDE.md` § "The queue, and how the project owner works" says of that
answer "`hold`: leave it unarmed", and `docs/maintainer.md` § "Read a simulator
change before you arm it" says "A session leaves a held pull request unarmed"
(project owner, 2026-09-25, ratified, `PL-SQTR`, built by `PL-K6B2`). The
owner's rule narrows his read to the paths that section reads "most closely",
plus `arming.py`.

**Why it matters.** A session outside the Project reads only the repository, so
it holds a change to `ROADMAP.md`, `CLAUDE.md`, `tools/`, `.claude/` or
`.github/` for a read the owner has said he does not want, and a Project thread
gets two answers to one question. Both happened on 2026-10-03: `#1298` (the
Gate 2 design round) met the hold on `docs/dead-ends.md` and armed under the
Project's rule, while `#1308` (`PL-D388`'s `ROADMAP.md` paragraph) followed
`arm` and `CLAUDE.md`, disarmed and asked for a read until the coordinator
relayed the rule.

**Recommendation: write the owner's list where `arm` reads it.** `arming.py`
gains the list as the set of paths held for the owner's read, beside `TOOLING`
and `GATE`, and `arm` prints `READ_ASK` only for a change reaching it. Any other
path outside the store arms on green, and the answer names it, so the report
carries the hold's reason as the rule asks. Whether a change "raises a specific
question" stays the session's judgment, so the answer says so as advice rather
than deciding it, and `CLAUDE.md`'s bullet takes one clause for that case,
naming what it replaces. `docs/maintainer.md`'s section is rewritten to the
rule. This is the carrier `PL-8XQS` chose for the review ask's summary: the
rule printed at the moment it is acted on, for every session alike. The build
changes `arming.py`, so its own pull request is held for the owner's read under
either rule.

**One point for the build to put to the owner first.** The list arms changes to
`.github/workflows/` and `.claude/hooks/` on green, and `update-armed.yml` and
`direct-merge-guard.sh` decide merges as much as `arming.py` does; `PL-WW0Q`
makes the same point about the modules `arm` reads its answer through. Ask
whether they join the list, rather than adding them on his behalf.

**Generator check.** A member of `PL-PDVF`: the fact is the owner's current
rule for sessions, held in the Projects trial's instructions and not in the
repository, as `PL-8XQS` and `PL-F23S` found for two other rules.

**Done when.** `bin/docket arm` holds for the owner's read a change reaching
`src/`, `tests/` outside `subprojects/`, `docs/MODEL.md`,
`src/anesthesia_sim/data/`, `README.md` or `arming.py`, and arms on green any
other change outside the store, naming those paths in its answer; tests in
`subprojects/docket/tests/test_cli.py` hold both answers; and
`docs/maintainer.md` states the rule.

**Built 2026-10-03, in `PL-PDVF`'s pull request.** `arming.READ_PATHS` holds the
owner's list as he spelt it - `src/`, `tests/` (the root's; the docket
package's own tests arm with the tooling), `docs/MODEL.md`,
`src/anesthesia_sim/data/`, `README.md` - with `arming.GATE` beside it.
`arming.waits_on_read` answers for a path, `arming.arms_on_green` is its
negation and takes the path alone now, and `arming.outside_the_store` names
what an `arm` answer reports. `arm` holds for a claim, a path on the list or
the gate, prints the list in every answer, and under `arm` names each path
outside `docs/items/`, `subprojects/docket/` and `docs/pr-bodies/` with the
owner's rule of 2026-10-03, so the report carries the hold's old reason;
whether the change raises a question for him stays the session's call, and
the answer says so. `test_a_change_outside_the_owners_read_list_arms_on_green`
and `test_arm_holds_for_a_read_a_path_on_the_owners_read_list` in
`subprojects/docket/tests/test_cli.py` hold both answers,
`test_the_owners_read_list_is_spelt_as_the_owner_spelt_it` the list, and
`subprojects/docket/tests/test_claims.py`'s two predicate tests the rest.
`CLAUDE.md`'s `hold` clause and `docs/maintainer.md` § "Read a simulator change
before you arm it" state the rule.

**What it reopens.** `ROADMAP.md` and `docs/WORKING_NOTES.md` arm on green
now. `PL-0JGZ` (project owner, 2026-09-26, ratified, over widening `arm` to
treat them as queue records) had kept `arm` holding them, because the roadmap
is where the owner sets direction; his list of 2026-10-03 is the later word
and names neither, so the build followed the list. That is the ratified
decision reopened on ordinary evidence, and it is put to him in the review
ask rather than decided here.

**Decision needed.** Should `.github/workflows/` and `.claude/hooks/` join the
read list?

**Recommendation:** yes, both directories whole. `update-armed.yml`,
`tag-release.yml` and `direct-merge-guard.sh` decide what merges and what is
tagged, which is the reason `arming.py` is on the list, and under the list as
written a change to any of them arms itself on green, so the one file the
owner holds for a read can be loosened from beside it. The cost is a read on
each change to them: 51 commits touched the two directories in the fourteen
days to 2026-10-03, most in the Bash-guard burst of 2026-09-26, and the rate
since 2026-09-30 is about one a day. Not added on his behalf: the list is his,
and the build keeps it as he spelt it.

**Answered 2026-10-03: yes, both** (project owner, 2026-10-03, ratified, over
leaving them armed on green), "Agree with recs" in the project chat at
23:22Z on the two recommendations put there, and built in `#1320`:
`arming.READ_PATHS` holds `.github/workflows/` and `.claude/hooks/` whole, so
`.github/CODEOWNERS` and `.claude/settings.json` arm. The same answer settles
the reopening above: `ROADMAP.md` and `docs/WORKING_NOTES.md` stay arming on
green (project owner, 2026-10-03, ratified, over holding them as `PL-0JGZ`
had), recorded there too.

