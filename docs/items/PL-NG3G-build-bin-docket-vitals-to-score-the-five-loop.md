---
id: PL-NG3G
title: Build bin/docket vitals to score the five loop-trial readouts, in the shape the v0.3.0 trial argued for
priority: P2
effort: M
status: ready
classes: infra, session-cost
feature: planning-cadence
touches: subprojects/docket/, docs/items/
added: 2026-09-02
verify: bin/docket vitals --base v0.2.8 && python3 -m pytest subprojects/docket/tests/test_vitals.py
---

**Problem.** `PL-SZ56` pre-registered five readouts and deliberately did not
build a command for them: "Building `bin/docket vitals` to measure whether the
project is overbuilding workflow apparatus would be the failure mode under
test arriving through the door marked measurement", and `CLAUDE.md`'s gate for
new tooling is whether it will genuinely run again — "which the v0.3.0 run is
the evidence for, not a prediction to act on now". The run has happened. It is
the evidence, and it came out in favour.

**Why it matters, with the arithmetic.** Scoring the five readouts by hand for
the v0.3.0 close-out took most of a session, and readout 2 was scored three
different ways before a defensible number was settled on — see `PL-40PL`.
Gates 1, 2 and 3 each want the same five readouts, so the rule is settled once
here and read three more times. That is the `CLAUDE.md` test for moving work
out of the model: the answer is deterministic, it comes from the tree, and it
recurs.

The stronger reason is not cost. A readout scored by hand is scored by whoever
is holding the session, against a protocol written in prose, after the outcome
is known — which is the exact failure `PL-SZ56` exists to prevent, and which
it had to mitigate twice mid-run (readouts 3 and 4 were both amended while the
trial ran). A command states its rule where a reviewer can read it and answers
identically every run, which is the determinism and auditability the
safety-critical standard asks for, arriving free.

**What it computes, and what it refuses to.** Four of the five readouts are
decidable from the tree and belong in code:

1. *Product against apparatus churn* — `git diff --shortstat <base>..<head>`
   over the two path sets. It must carry the partition `PL-C8MV` identifies,
   with apparatus tests counted as apparatus, and print both scorings rather
   than picking one.
2. *Net queue change* — intake and closures over the window. This needs the
   counting rule `PL-40PL` has to write down first; that item is this one's
   prerequisite, not a duplicate of it. Cross-check the answer against the
   open-count delta, which is an independent route to the same number and
   caught an off-by-one during the v0.3.0 scoring.
3. *Stranded items* — `bin/docket stranded` already answers, and must report
   how many refs it could read, per `PL-21GS`.
4. *Digest self-reported blindness* — whether the "N refs could not be
   compared" line fires.

**Readout 3 is not computed, and that is the design.** Whether a defect was
*caused* by an entry is the judgment half. `PL-SZ56`'s first attempt to
mechanize it — file overlap between an item's `touches` and a closed entry's
changes — returned seven hits, none of them causal, because `docs/MODEL.md`
and `simulation_view.py` appear in most items' `touches` and the date fields
are day-granular. A tool that guesses at causation is worse than no tool,
because its output looks authoritative and is not. `vitals` should print the
*candidate* set and the evidence a human needs — defect-classed items filed in
the window, which closed entries they name, and whether each reproduces at the
entry's merge and not its parent — and then stop, leaving the call and its
reasoning to the close-out.

**Where.** `subprojects/docket/src/docket/`, as a subcommand alongside
`stranded` and `wave`, with `--base` defaulting to the last tag. Standard
library only, per `CLAUDE.md`, so it runs from a bare checkout.

**Not before the readouts' rules are settled.** `PL-40PL` (readout 2 names no
command and its t=0 will not reproduce) has to answer first, or this command
hard-codes the ambiguity instead of removing it. Readout 3's causal rule
should likewise be frozen before v0.4.0 opens rather than amended while it
runs, which is what happened to it in v0.3.0.

**Done when.** `bin/docket vitals --base <tag>` prints the four computed
readouts with their thresholds and a pass/fail each, prints readout 3's
candidate set without scoring it, names the confounds each reading carries,
and has tests covering a window with no intake, a window where apparatus leads
product, and a stranded branch that is live rather than abandoned.
