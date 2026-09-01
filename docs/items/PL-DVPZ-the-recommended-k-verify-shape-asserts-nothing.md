---
id: PL-DVPZ
title: The recommended -k verify shape asserts nothing until the work lands, so 19 of 34 open items carry a command that proves nothing today
priority: P2
effort: S
status: done
classes: docs, infra
feature: delegation
milestone: v0.2.8
touches: .claude/skills/docket/SKILL.md
added: 2026-09-01
closed: 2026-09-01
commit: 800b133
pr: 153
verify: python3 tools/doc_check.py check && grep -qF 'never a bare `-k`' .claude/skills/docket/SKILL.md
---

**Problem.** `.claude/skills/docket/SKILL.md` offers three shapes to copy, and
the middle one - `uv run pytest tests/unit/test_simulation_view.py -k halted` -
selects no test until the work names one to match. `PL-5QKT` measured the
result: 19 of 34 open items carry a command in that shape, every one of them
exiting 5 with nothing collected. The recommended shape is the defect.

**Why it matters.** Exit 5 is not exit 0, so such a command reads to every
reader of an exit status as one that correctly fails, which is why the state
went unnoticed until it was measured. `-k` also matches a *name*, so what the
command specifies is that some test somewhere comes to be called `halted` -
not that any behavior holds. Two known instances of the failure that follows:
`PL-D2GW`, whose `-k gate` matched nothing before the work and nothing after
it, and `PL-JWXF`'s own command in this session, which passed only once its
target string was made contiguous in the source.

The third row already solves the same problem for documentation, and solves
it correctly: `doc_check.py check` runs something that exists and passes
today, and the `grep` is the half that fails until the work exists. The test
row should be built the same way and is not.

**Where.** The table and the paragraphs around it in
`.claude/skills/docket/SKILL.md`. Measured against a scratch file rather than
recalled:

| Shape | Before the work | Reads as |
| --- | --- | --- |
| `pytest <file> -k no_such_name` | 5 | a command that correctly fails |
| `pytest <file>::test_no_such` | 4 | a usage error, same as a typo'd path |
| `pytest <file>` | 0 | already passing, proves nothing |
| `pytest <file> && grep -q 'def test_no_such' <file>` | 1 | an ordinary failure |

The last is the one to recommend. It exits 1, the code a failing test gives,
so nothing has to read a special case; the pytest half runs the file's whole
suite and proves it healthy, which `-k` never did; and the `grep` names the
exact test the work must add, which makes the command a specification rather
than a bet on a name.

**Done when.** The skill recommends the paired shape for a test-adding item
and says outright that a bare `-k` is not acceptable, with the exit codes that
make the difference legible.

**No new check, deliberately.** `PL-5QKT` and `PL-JWXF` already built the
runtime one: `docket check` runs every open item's command and raises an
advisory for those selecting no test among the items `next` is about to offer.
A static rule reading the same `-k` out of the item file would be a second
advisory saying the same thing, and the cost of a duplicate advisory is the
next advisory, which gets read the same way.

**The 19 existing commands are not rewritten here.** The skill's own rule is
that a command written away from the work is how every wrong one came to
exist, so each is repaired when its item is started - which is exactly when
the advisory names it.

**Its `verify:` pairs `doc_check` with a `grep`**, the shape this item is
about. Run before being written down: it exits 1 on the `grep`.

**Worked 2026-09-01.** The middle table row becomes `uv run pytest
tests/unit/test_simulation_view.py && grep -q 'def test_halted'
tests/unit/test_simulation_view.py`, and the rule is stated in the heading
rather than left to be inferred from an example. The exit-code table above it
is the reason, and it was measured against a scratch file rather than recalled
- exit 4 for a `::` node id was the one that would have been guessed wrong.

The last two rows are now named as the *same* shape, which is the point worth
carrying: something that runs and passes today, paired with a `grep` for what
the work adds, each half doing a different job. The documentation row already
worked that way; the test row now does too.

**No check was added**, and the reasoning is recorded above rather than left
implicit: the runtime advisory from `PL-5QKT`, scoped by `PL-JWXF`, already
names exactly these commands at exactly the moment somebody can act on one. A
static rule reading the same `-k` from the item file would say the same thing
twice, and a duplicate advisory costs the next advisory rather than itself.
