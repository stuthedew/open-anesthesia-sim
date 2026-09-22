---
id: PL-T5K1
title: Report the dated assertions in the instruction set that are past a staleness threshold, as a grooming advisory
priority: P2
effort: M
status: done
classes: infra
feature: instruction-staleness-audit
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests, docket.toml
added: 2026-09-21
closed: 2026-09-21
pr: 883
payoff: the assertion that quietly goes wrong at month eighteen reaches a reader instead of being obeyed
verify: uv run pytest subprojects/docket/tests/test_instructions.py subprojects/docket/tests/test_checks.py -k 'instruction or staleness or dated_assertion or re_dating or oldest_first' -q
---

**Problem.** Report the dated assertions in the instruction set that are past a staleness threshold, as a grooming advisory

The instruction set asserts facts about a world that changes — network policy,
tool behavior, what a check catches, which agent is running — and nothing
expires any of them. `PL-BSYZ` stated an egress refusal measured 2026-09-04 as
a standing fact, so it would have told sessions not to retry doi.org the moment
the policy opened; `PL-GDB0` records three current-state facts written as
permanent rules in a single session. Both were caught by the project owner
rather than by any gate, and `.claude/rules/expert-review.md` says why no gate
will ever catch the judgment half: "It fails quietly. A wrongly permanent
sentence trips no check and never can, because altitude is judgment rather than
a fact about the tree."

**Why it matters.** This is the failure mode that outlives a size problem. A
rule that is long costs attention; a rule that was true in 2026 and is false in
2029 gets *obeyed*. Every gauge the project currently has measures size, so this
is invisible to all of them. The two instances so far were both fast failures
caught personally; the one nobody catches is the assertion that quietly goes
wrong at month eighteen, which is precisely what the project owner asked to
automate (2026-09-21): "I won't notice, or might too late when everything is
going wrong for a bit."

**What is automatable, and what is not.** The decidable half is *which*
assertions are due for re-checking — arithmetic on dates, no judgment. Whether
an aged assertion is still true stays human, per `CLAUDE.md` § "Prefer
deterministic tooling": do not script the judgment.

**Measured 2026-09-21, so the implementing session need not re-derive it.**
74 dated assertions across 17 instruction files (16 in `CLAUDE.md`, 11 in
`.claude/rules/citing-sources.md`, the rest across the rules and the `docket`
skill's modes). Every one is under 30 days old, because the project is 30 days
old. Only **4 external URLs** exist in the whole instruction set, so URL
liveness checking buys nothing and is explicitly out of scope.

**Design.** A grooming advisory, not a `make check` error. The pattern already
exists and is tested: `subprojects/docket/src/docket/checks.py` carries
day-thresholded advisories with a config knob (`untriaged_stale_days: int = 14`)
and `_check_stale_open_threads`. This is a third one beside them. It fires on
`make docket`, where a reader already has hygiene in hand — never on `make
check`, which is edit-triggered and would be noise.

**The advisory must be able to reach zero**, which is the constraint that
shapes it. `checks.py` warns in its own comments that an advisory which "could
not reach zero" costs the *next* advisory its reader. A raw age list can never
reach zero, since every assertion ages. Discharge is re-verify-and-re-date,
which resets the age and drops the entry. Cap the report at the 5 oldest so it
stays actionable however large the set grows.

**Known limitation, recorded so it is not rediscovered as a defect.** Age is a
proxy for staleness, not staleness. A dated *record* — "project owner ratified
X on this date" — never goes stale; a measured *environmental* fact does. Early
precision will be mediocre, and the right narrowing should be learned from the
first firing rather than guessed now. This audit would not have caught either
`PL-BSYZ` or `PL-GDB0`: both were filed within days. It targets the slow
failure, not the fast one.

**Done when.** `make docket` names the dated assertions past the threshold,
newest-first and capped, in a form a reader can discharge by re-verifying and
re-dating; and the advisory reads as zero on a tree where nothing is past it.
