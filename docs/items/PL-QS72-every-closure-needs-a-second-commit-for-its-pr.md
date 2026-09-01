---
id: PL-QS72
title: Every closure needs a second commit for its pr:, because the number does not exist when CLAUDE.md requires the closure to be committed - derive it from the squash-merge subject instead
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_checks.py
added: 2026-09-01
closed: 2026-09-01
commit: b07d059
pr: 151
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_vcs.py && grep -q 'recoverable from its merge commit' subprojects/docket/src/docket/checks.py
---

**Problem.** Two rules that are each right on their own make a follow-up
commit unavoidable for every closure. `CLAUDE.md` requires the closure to
travel in the same commit as its work (`PL-P5S0`: a merge arriving between the
two took the work and left the item open, with `main` carrying the fix while a
debt gate still counted it). `_check_closures` requires a `pr` once that
closure stands on the default base (`PL-HVX9`: without it there is no way back
from a closure to the work that made it). The number does not exist until the
work is pushed and the pull request opened, so no session can satisfy both in
one commit.

Observed twice in one session, on `PL-5QKT` and then on `PL-JWXF`: each merge
turned `bin/docket check` red against `origin/main` and cost a second commit,
and in both cases a second pull request, because nothing else was outstanding.

**Why it matters.** `main` going red is the loudest signal this project has,
and it now fires on the successful completion of every item. A signal that
means "an item finished normally" trains sessions to treat a red store check
as routine, which is the opposite of what it is for. The cost is one extra
commit and often one extra pull request per item, against seventy-three open
items.

**Where.** The number is already in the subject GitHub writes for a squash
merge - `PL-JWXF Scope the selects-no-test advisory ... (#148)` - and
`vcs.PR_SUBJECT_RE` already parses that shape for `merged_pull_requests`,
while `vcs._leading_ids` already reads the ids a subject opens with.
`closures_on_base` is where the two meet: it already walks the closures in
question, so it can report the number each one's merge commit names alongside
whether the closure landed. `checks._check_closures` then splits on whether
the provenance is actually lost.

**Done when.** A closure whose merge commit names its pull request is an
advisory that says which number to record, not an error. A closure whose
number cannot be derived stays an error, because that is provenance genuinely
lost. `make check` stays green through a normal merge.

**Not a backfill.** All 115 closed items already carry a `pr`, checked while
writing this, so nothing here has a backlog to clear and no command is added
to clear one. The advisory is transient by construction: it appears when a
closure merges and disappears when the field is written.

**Its `verify:` pairs two files' suites with a `grep`**, not a `-k`, per
`PL-5QKT`. Run before being written down: it exits 1 on the `grep`, having
collected and passed both suites.

**Worked 2026-09-01.** `closures_on_base` already walked the closures in
question, so it now also returns which pull request each landed one's own
merge commit names, from a single history read taken only when something
landed. Both parsers already existed - `PR_SUBJECT_RE` for the number in
trailing parentheses, `_leading_ids` for the run of ids a subject opens with -
so one merge closing two items answers for both, and the newest commit naming
an id wins over the capture that filed it. `_check_closures` then splits:
recoverable number is an advisory naming the exact line to write, no commit
naming one stays the error it was.

**The workaround proposed in #150 was wrong and is not what shipped.** Pushing
the work, opening the pull request, then adding `pr:` before the merge reopens
the window `PL-P5S0` closed: the merge can arrive between the two pushes,
taking the work and stranding the closure. The whole point of this item is
that the closure need not be split at all - it travels with its work, the item
lands with an empty `pr`, and the advisory names the number afterwards.
`.claude/skills/docket/SKILL.md` says so explicitly rather than leaving the
order to judgment.

**`PL-B1C2` replaced `PL-A1B2` in the test data of both suites.** The id
alphabet excludes vowels, so `PL-A1B2` cannot be parsed as an item id - it was
inert wherever it was only compared as a string, and silently unmatched the
moment it reached `_leading_ids`, which is how it was found.

**No backfill, by measurement.** All 115 closed items already carried a `pr`,
so no command was added to write one in bulk: the advisory is transient by
construction and a one-off migration is the case the deterministic-tooling
gate excludes.
