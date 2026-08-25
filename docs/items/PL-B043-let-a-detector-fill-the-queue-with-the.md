---
id: PL-B043
title: Let a detector fill the queue with the mechanical findings nobody thinks to file
status: dropped
added: 2026-08-25
closed: 2026-08-25
reason: the findings named are invariants, not queue items; superseded by four checks filed separately, since a detector that files work is the wrong response to a condition whose steady state is zero
---

**Problem.** A category of real, valuable work is invisible to the queue
because nobody has an idea that produces it. The untested guards surfaced only
because a coverage report was run; PL-69J3's ten inert `noqa` directives
surfaced only because `ruff --select RUF100` was run; PL-JL24 surfaced only
because a hash was orphaned in front of someone.

**Why it matters.** Findings enumerable by a command are exactly the findings
provable by a command, which makes them the natural supply for the delegation
tier — though the value does not depend on delegation.

**Where.** `tools/`, `subprojects/docket/`, `pyproject.toml`.

**Decided.** Dropped as framed. The candidates were measured against the
current tree first:

| Candidate | Findings today |
| --- | --- |
| Open items declaring no `touches` | 0 of 36 open |
| Unreachable recorded `commit:` hashes | 0 of 32 |
| Inert `noqa` directives | unchecked — `RUF100` is not in ruff's `select` |
| Uncovered `raise`/`except` branches | no gate; `core-guard-coverage` is doing this by hand, 7 of 9 |
| Dangling documentation citations | already done by `tools/doc_check.py` |

Three of the five are at zero, and for a specific reason: each was found once,
filed, and fixed. The historical rate is not a stream but one-off discoveries,
already harvested.

That reframes the item. **These are not queue items; they are invariants.** A
condition that should be zero, is zero, and was non-zero once is a regression
guard — which is what `doc_check.py` already is: its package-map and
provenance checks report nothing on almost every run, and their value is that
`weight_kg` cannot silently leave the provenance table a second time.

So the decision the item asked for — whether a detector *files* items or
merely *reports* them — is answered with neither: **it gates.** If a
condition's steady state is zero, a filing machine files nothing; and when a
condition does break, an item that waits in a queue is strictly slower and
lossier than a red `make check` that stops the commit which broke it, with the
cause attached.

This also passes the item's own scope-discipline test more strongly than
either option offered. The test was whether the output would be worth having
if no cheap model ever ran it. A gate's output is worth having precisely
because no model runs it.

On the second question — one tool or several — neither. No new tool. Each
subject already has a home, and the one-script-per-subject precedent is best
honoured by not creating a script where the subject is already owned.

**What is left undone, honestly.** The item's underlying observation survives
and is not addressed by any of this: nobody sits down and thinks "I should
file an item about untested capacity guards." Gating handles the enumerable
cases and does nothing for the next category nobody has thought of, which no
detector can, because an unknown unknown is not enumerable. That remains a
periodic sweep with a fresh lens — a session practice, not a tool. Building
something that claimed to automate it would be the homework machine this item
warned against.

**Done when.** Closed by this decision; successors filed.
