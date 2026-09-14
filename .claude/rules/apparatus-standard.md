---
paths:
  - "/subprojects/docket/**"
  - "/tools/**"
  - "/.claude/**"
  - "/.github/**"
  - "/docs/worker.md"
---

# The bar for the workflow apparatus

`CLAUDE.md` § "Proactive expert review and domain best practices" splits this
repository into two standards and names the paths on each side. This is the
apparatus half, and it loads only on those paths.

That scoping is the point rather than a convenience. Applied to `src/`,
`tests/`, `docs/MODEL.md` or `README.md`, every sentence below is wrong — they
are held to the opposite standard, and one that argues for *more* investment,
not less. While this text was resident a session quoted it as the bar for
comment quality in `src/` and reached the wrong answer confidently, citing the
right file (`PL-6SBB`). A session that never opens an apparatus path now never
loads it.

The apparatus is held to **working reliably and staying streamlined**.
Reliability and the functionality it actually needs are the outcome;
"streamlined" describes how that gets built, never a ceiling on it. What to cut
is bloat — duplicated logic, an option nobody sets, prose restating what a
command already prints, a mechanism larger than its job because it was written
badly — and never function or robustness, which is the trade a size target
invites and this one refuses.

It is scaffolding, not product; nobody evaluating this project will read it.
Polishing it past sufficient is the most common way this project wastes a
session. Where the two standards compete for a session, the simulator wins.

## What a test on this side is for

A test here exists to keep the apparatus working, and a wrong answer costs a
session rather than a patient. So the bar is the one the simulator's standard
refuses: a test here earns its place if its **absence would let a real defect
through**. A script's own rule, the failure path it reports on, and the input
that once broke it are worth pinning; a getter, a constructor, or the standard
library's own behaviour are not. That is the whole bar, and nothing stricter
applies to the fifteen apparatus tests under `tests/unit/` or to
`subprojects/docket/tests/`.

**It does not reach a test that imports the product package.** That test is the
simulator's, and `CLAUDE.md`'s safety-critical standard asks of it what the
paragraph above does not: boundary, invalid-input, pathological-input and
regression tests, and validation against published reference cases or
independently calculated test vectors. The line is mechanical rather than a
judgment made per file — `tools/workflow_paths_check.py` decides it by exactly
that import, on the rule that "A test file under `tests/` is apparatus when it
does not import the product package, and product when it does."

## The floor: an answer has to be true, or has to say it could not answer

"Working reliably" is the outcome; this is the one property of it that refuses
things, and the paragraphs above deliberately did not state one (`PL-WGXJ`).
**What this apparatus tells a session must be true, or must say what it could
not read.** Handing over a partial reading as a complete one is the violation,
because at the point of use the two are indistinguishable.

It binds the **answer-giving surface** rather than the path list at the top of
this file: `bin/docket`'s output, the session-start digest, what a check
reports, and what an item brief claims about the tree. A formatter, a fixture,
a Makefile target has no answer to get wrong and stays under the paragraph
above with nothing extra asked of it. Scoping the floor to everything would
refuse nothing in particular, which is the defect it exists to remove arriving
one level up.

**Why this property and not another: it is the failure this apparatus actually
has.** Of the 41 open apparatus-only `defect` items on 2026-09-14, about 35
describe a command, check or brief handing a session a confident answer that is
wrong or incomplete — a reading of their titles rather than a script's count,
so treat it as an order of magnitude and not a statistic. `docket next` hid
eight startable items behind annotation commits (`PL-X3WZ`); `check --items`
reports a clean store as 112 errors (`PL-K5PW`); a verify replay reports green
rather than declining to answer (`PL-T7VS`). What is left is cleanups, renames
and design debt.

**And the consequence does not stay inside the apparatus.** `docket check` is
what pins `safety`- and `science`-classed work to `P1`. A class misspelt as
`safey` matched no rule, so work a clinician could be misled by stayed seatable
in the bottom band while the check reported zero errors (`PL-MVC2`). The
apparatus decides which safety work a session is offered, so a silent wrong
answer here defers that work without anyone having decided to.

Writing the floor down costs nothing because the code already holds to it:
`FlightReport.unreadable`, `PullRequestHistory.declined` and `doc_check`'s
`Report.declined` all exist so that what went unread travels with the answer
instead of being rounded off. The floor is the rule those three are instances
of.

**It is not the specialist standard arriving by another door.** It asks for no
polish, no coverage target, no abstraction, no prose. A five-line script that
prints the right answer clears it; a well-factored, well-tested mechanism that
quietly answers from a partial read does not.
