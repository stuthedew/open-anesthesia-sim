---
id: PL-HVX9
title: "The scaffolding standard says 'staying small', which reads as a size cap rather than a bar on bloat"
priority: P3
effort: S
status: done
classes: session-cost, infra
feature: worker-instructions
milestone: v0.2.8
touches: CLAUDE.md
added: 2026-09-01
closed: 2026-09-01
commit: 22c4851
pr: 143
verify: python3 tools/doc_check.py check && grep -qF 'staying streamlined' CLAUDE.md
---

**Problem.** `CLAUDE.md`'s "Two standards, deliberately unequal" paragraph holds
the workflow apparatus — `subprojects/docket/`, `tools/`, `.claude/`,
`docs/worker.md`, and `CLAUDE.md` itself — to *working reliably and staying
small*. "Small" names a size, and a size is a thing a session can hit by
removing function. Nothing in the paragraph says which half wins when they
pull apart, so a session reading it can conclude that a feature `docket`
genuinely needs, or a guard that makes a command reliable, is the thing to
give up. That is the opposite of what the standard is for.

**Why it matters.** The project owner's stated intent (2026-09-01) is that
functionality and reliability are the desired outcome, and that leanness is
about *how* the thing is written — the concern is a subproject ballooning
because the code is poor, not one growing because the job grew. "Streamlined"
carries that; "small" does not. The wording is load-bearing rather than
cosmetic, because this paragraph is resident in every session and is the only
place the scaffolding standard is stated: it is what a session applies when
deciding whether to add a flag, split a module, or leave a rough edge in
`docket`. A standard that can be satisfied by deleting needed behavior is a
standard that will eventually be satisfied that way.

It also mis-cues the direction of the risk. Bloat here has a specific cause —
duplicated logic, an option nobody sets, prose restating what a command
already prints, a mechanism larger than its job because it was written
badly. Those are the things to cut, and naming them is more actionable than
naming a size.

**Where.** `CLAUDE.md`, the "Two standards, deliberately unequal" paragraph
under "Proactive expert review and domain best practices" (one paragraph;
the phrase is *working reliably and staying small*). `subprojects/docket/README.md`
states no size principle of its own — grep finds "small" there only in "a small
front-matter block", which is descriptive — so the guiding principle lives in
`CLAUDE.md` alone and that is the only file the change touches.

**Not a size metric.** The obvious follow-on — a check that measures
`subprojects/docket/` and fails on growth — would rebuild the size cap this
item removes, in a form that cannot be argued with. `tools/doc_check.py`'s
`check_resident_instructions` is deliberately advisory for the same reason
(`PL-H7XN`): it reports growth so the routing question gets asked, and decides
nothing. Whether a mechanism is bigger than its job is judgment, which
`CLAUDE.md`'s own "do not script the judgment" rule keeps out of a script.

**Done when.** The paragraph states reliability and needed functionality as the
outcome, names bloat rather than size as what to cut, and says explicitly that
function and robustness are not what gets traded away for leanness. `make check`
passes; its resident-instruction advisory will report the growth, which is
expected for a change that adds a clause to a resident file.
