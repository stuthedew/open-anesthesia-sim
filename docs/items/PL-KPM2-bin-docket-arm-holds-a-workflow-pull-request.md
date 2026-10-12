---
id: PL-KPM2
title: bin/docket arm holds a workflow pull request for the owner's read where it changes .github/workflows/, .claude/hooks/ or docket's shell.py, though the owner said on 2026-10-12 that workflow items need no merge confirmation
priority: P2
effort: S
status: done
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_claims.py, CLAUDE.md, docs/maintainer.md, docs/apparatus.md
added: 2026-10-12
closed: 2026-10-12
pr: 1432
payoff: a workflow pull request merges on green CI without waiting for the owner's merge word, as he asked on 2026-10-12, while a change a learner or clinician could see still waits for his read
verify: grep -q 'def test_arm_arms_a_workflow_path_the_owner_released_on_green' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket arm holds a workflow pull request for the owner's read where it changes .github/workflows/, .claude/hooks/ or docket's shell.py, though the owner said on 2026-10-12 that workflow items need no merge confirmation

**The owner's rule** (project owner, 2026-10-12): "don't need to ask me for
merge confirmation for workflow items", written in the Projects trial's project
chat at 02:34Z and relayed to this thread by its coordinator. His own words, so
a specified decision. It reopens two ratified ones: `.github/workflows/` and
`.claude/hooks/` joining the read list (2026-10-03, `PL-KKHD`), and docket's
lexer joining it (2026-10-10, `PL-JNYL`). Every other path on the list is a
product path, where a wrong clinical value could reach the screen, besides the
gate itself.

**Scope, read as the coordinator read it.** Workflow items means docket's
workflow lane. A product change keeps its hold, and so does a change crossing
both lanes, which holds by its product path whatever else it changes. So the
three workflow paths leave `READ_PATHS`, and nothing else does.

**Asked, with a recommendation** (2026-10-12, open): whether `arming.py`
itself, `GATE`, stays held. **Recommendation: keep it held.** It decides which
pull requests wait for the owner, and it has been held since 2026-09-25 so that
the gate cannot loosen itself (`PL-SQTR`): armed on green, a workflow pull
request could drop `src/` or `docs/MODEL.md` from the list and merge unread. It
changed twice in the week to 2026-10-12, so the hold costs him little. Built on
the recommendation until he answers; the pull request writing this rule changes
`arming.py` and merges on his 2026-10-12 message either way.

**Not `PL-XTBF`.** `docket new` matched this capture to it on the two paths
they share. That item asks how a repair push treats a pull request the owner
has armed, a different question, so no recurrence was recorded.

**Why it matters.** Every hold the owner does not want costs him a merge word
and stalls the work until he gives it: on 2026-10-12, `PL-0CJC`'s pull request
was to be held for a read of `shell.py` alone. A rule stated in chat that no
session's tools carry is followed only by the sessions that read the chat.

**Generator check.** None: the hold applied the owner's rules of 2026-10-03 and
2026-10-10 as written, and his rule of 2026-10-12 changes them. No reader
misread a fact, and no other item shares the cause.

**Done when.** `bin/docket arm` answers `arm` for a branch whose paths outside
the store lie under `.github/workflows/` or `.claude/hooks/` or are docket's
`shell.py`, and still holds for every product path, and for `arming.py` as the
owner's answer above decides; `arming.py`'s decision record, `CLAUDE.md`'s
arming bullet and `docs/maintainer.md` § "Read a simulator change before you
arm it" say so; a test pins each released path arming on green.

**Done 2026-10-12** (`#1432`). `arming.READ_PATHS` keeps the five simulator
paths: `.github/workflows/`, `.claude/hooks/` and docket's lexer left it, so
`bin/docket arm` answers `arm` for a branch changing them and nothing on the
list, and a branch crossing both lanes holds by its product path alone.
`arming.py` itself stays held on the recommendation above until the owner
answers. `LEXER` and its pin went with the lexer's hold, since nothing reads the
constant now. `arming.py`'s decision record, `CLAUDE.md`'s arming bullet,
`docs/maintainer.md` § "Read a simulator change before you arm it" and
`docs/apparatus.md`'s hooks paragraph say so. Pinned by
`test_arm_arms_a_workflow_path_the_owner_released_on_green` in
`subprojects/docket/tests/test_cli.py`, three paths, each red on `main`'s gate
and each holding beside a product path; the read list's spelling test and
`test_claims.py`'s arm assertions turned with the list.
