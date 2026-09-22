---
id: PL-44DG
title: measure_resident undercounts the true per-session resident payload by 4,794 characters: the SessionStart digest and the docket skill description are resent every turn and counted by nothing
priority: P2
effort: S
status: done
classes: defect
feature: instruction-staleness-audit
milestone: v0.5.3
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/resident-instructions.md
added: 2026-09-21
closed: 2026-09-21
pr: 885
payoff: the one gauge the project consults about resident size stops being 7.2% low
verify: uv run pytest tests/unit/test_doc_check.py -k 'digest or skill or hook' -q
---

**Problem.** measure_resident undercounts the true per-session resident payload by 4,794 characters: the SessionStart digest and the docket skill description are resent every turn and counted by nothing

**Measured 2026-09-21.** `tools/doc_check.py`'s `measure_resident` counts
`CLAUDE.md` plus every `.claude/rules/*.md` carrying no `paths:` frontmatter,
and reports 66,773 characters on `origin/main`. That is not what a session
actually carries. Two payloads reach every session at launch and are resent on
every turn, and nothing counts either:

| Payload | Characters | Counted by |
| --- | --- | --- |
| SessionStart digest (`.claude/hooks/docket-digest.sh`) | 4,169 | nothing |
| `docket` skill description frontmatter | 625 | nothing |
| **Undercount** | **4,794** | — |

True per-session resident payload is therefore **71,567**, and the reported
figure is **7.2% low**.

**Why it matters.** The growth advisory in `check_resident_instructions` is the
one gauge the project consults when it asks whether the resident set is a
problem, and `docs/resident-instructions.md` is the ledger written against its
numbers. A gauge that is 7% wrong is a defect whether or not anyone acts on the
reading — and the digest is the half that *grows on its own*, since it carries
the dead-ends list (1,376 characters today) and scales with the store. It is the
one component of resident cost that can rise without any edit to an instruction
file, so it is precisely the part a size gauge most needs to see.

**Independent of the rest of `instruction-staleness-audit`.** Grouped with it
because the same session measured all three, not because it is blocked on
either. Worth doing on its own terms.

**Scope note.** `_measure` deliberately drops a rules file carrying `paths:`,
and that stays — this adds two payloads it never considered, rather than
reopening which rules files count. `PL-JQVB` already established that a skill's
resident cost is invisible here; this closes the measurement half of it.

**Done when.** `measure_resident` counts the SessionStart digest output and the
skill description frontmatter, the reported resident total matches what a
session actually carries, and a test pins the digest contribution so a change to
the hook cannot silently drop out of the count.
