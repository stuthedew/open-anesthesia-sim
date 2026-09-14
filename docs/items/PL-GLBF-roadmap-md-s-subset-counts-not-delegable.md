---
id: PL-GLBF
title: ROADMAP.md's subset counts - not-delegable, entries reaching into src/ - are still hand-maintained and unchecked
priority: P3
effort: S
classes: defect, docs
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_not_delegable_subset_count' tests/unit/test_doc_check.py
status: done
closed: 2026-09-13
added: 2026-09-01
---

**Problem.** PL-H8MQ made every count of a frozen list's *size* checkable, and
removed the prose restatements a checker cannot safely read. What it did not
touch are the counts of a *subset* of a list, which state a property of the
entries rather than the list's length. Live examples, all hand-maintained:

- "**Seven entries are marked `not-delegable`,**" in the v0.2.8 section
- "The two entries that change repository configuration rather than the tree"
- "Three entries reach into `src/`" in the definition of done

**Why it matters.** Each goes stale the next time an entry with that property
is admitted or closed, and none of them fails anything. The same failure PL-H8MQ
describes, one level down: on 2026-09-01 the v0.3.0 section still said its
contents were "the fourteen listed under Debt gate" when the list had held
twenty since six entries were added — a reader would have thought the release
shipped fourteen items. That one was found by hand while working PL-H8MQ, not
by a check.

**Where.** `ROADMAP.md`; `tools/doc_check.py`'s `check_gate_counts`, which
already has the entries parsed and reports at the right granularity.

**Approach.** The `not-delegable` count is the one worth doing first, because
it is decidable without judgment: `docket` reads `not-delegable:` off each
item, so the count is a query over the entries the gate already names. The
other two describe what an entry's *work* touches, which no field records —
those are either left to the reader (and then the number should come out of
the prose, per PL-H8MQ's rule) or need a field that does not exist yet. Decide
which before writing anything: a check that guesses the judgment half is worse
than no check.

**Done when.** A subset count in `ROADMAP.md` either fails `make check` when it
disagrees with the items, or has been removed from the prose because nothing
can decide it.

**Triaged 2026-09-01 to `needs-decision`, not to `ready`.** The fields are
filled in - `P3`, `defect`/`docs`, `dev-tooling`, beside `PL-H8MQ`, whose work
this continues - but the item cannot be started, because its own **Approach.**
names a decision that has to come first and this triage pass deliberately did
not make it.

**Decision needed.** Whether the two counts that describe an entry's *work* -
"the two entries that change repository configuration" and "three entries reach
into `src/`" - come out of `ROADMAP.md`'s prose, or whether an item gains a
field recording what its work touches so a checker can decide them. The
`not-delegable` count needs no decision and is checkable either way.

Stated at length: the `not-delegable`
count is a query over fields `docket` already reads and can simply be checked.
The other two - "the two entries that change repository configuration" and
"three entries reach into `src/`" - describe what an entry's *work* touches,
which no field records. So either those two numbers come out of the prose (per
`PL-H8MQ`'s rule that a count nothing can decide should not be written down),
or an item gains a field that records what its work touches at that
granularity, which is a larger change and one that would need filling in
across the gate.

No `verify:` yet, and that is correct rather than missing: the command depends
on which answer is taken, and `docket check` owes one only at `ready`.

## Decided 2026-09-13: build the one decidable count, and record why the other two are neither checked nor removed

**The decision asked which of two — the counts come out of the prose, or an item
gains a field. The measured answer is neither, and the third option is better
than both.**

### The premise this brief rests on is wrong, and the field it asks for exists

The brief says the two work-describing counts "describe what an entry's *work*
touches, which no field records". `touches:` records exactly that, on 208 of 236
open items (88%). So the question is not whether to add a field — it is whether
the field already there can decide these counts. **It cannot, and the proof is
this item's own example.**

`ROADMAP.md:827` says "Three entries reach into `src/` and `tests/`", naming
PL-020, PL-ZN0N and PL-69J3. By `touches:`:

| entry | `touches:` reaches `src/` or `tests/` |
| --- | --- |
| PL-020 | yes — `src/anesthesia_sim/py.typed`, `tests/unit/test_bootstrap.py` |
| **PL-ZN0N** | **no — `pyproject.toml` and nothing else** |
| PL-69J3 | yes — `simulation_view.py` and four `tests/` files |

A checker over `touches:` computes **2** and the prose says **3**, and the prose
is right. The two fields answer different questions: `touches:` records the files
an item is *expected to change*, while the definition-of-done sentence records
the scope an item is *permitted to reach* — PL-ZN0N may "add, remove or annotate
`noqa` directives", which live in `src/`, without that being a file it plans to
edit. A check built on the near-miss field would fail a correct sentence, which
is `CLAUDE.md`'s own warning: "a tool that guesses at the judgment half is worse
than no tool, because its output looks authoritative and is not."

The second count fails for a different reason. "The two entries that change
repository configuration rather than the tree" — PL-J786 and PL-S4M2 — both
carry an **empty** `touches:`, which is correct for them. But 28 open items also
carry an empty `touches:` because nobody filled it in, so emptiness conflates
"changes nothing in the tree" with "unmeasured" and can decide nothing.

### And they cannot go stale, because the list they describe is closed

The brief's harm model is that each count "goes stale the next time an entry
with that property is admitted or closed". All three live examples are in the
**v0.2.8** section — a `Completed` release. Every id the three counts name was
checked today:

PL-J786 `dropped`; PL-S4M2, PL-8HJ2, PL-ZQ9C, PL-1Q3S, PL-H7XN, PL-CMCB,
PL-020, PL-ZN0N, PL-69J3 all `done`, every one stamped `milestone: v0.2.8`.

Ten of ten closed, on a frozen list, in a shipped release. Nothing will ever be
admitted to it or closed out of it again, so the staleness these counts were
filed for has a probability of zero. `PL-H8MQ`'s rule — a count nothing can
decide should not be written down — is aimed at a number that can *drift*.
Deleting correct history from a shipped release's section to satisfy a rule
about live ones is a loss, not a tidy-up.

### So the work is the one count that is genuinely decidable

`ROADMAP.md:723`, "**Seven entries are marked `not-delegable`**", is a query
over a field `docket` already reads, on a list `check_gate_counts` already
parses. It needs no judgment, it is the count this brief itself identified as
the one worth doing first, and — unlike the other two — the same check keeps
working on every future section, which is where the risk actually lives.

Scope, and nothing beyond it:

1. Extend `tools/doc_check.py`'s `check_gate_counts` to verify a
   `**N entries are marked `not-delegable`**` sentence against the items the
   section's frozen list names.
2. Record in `ROADMAP.md`, beside the two counts left unchecked, that they are
   deliberately not checkable and why — the `touches:`/permitted-scope mismatch
   above — so this is not rediscovered and re-filed a third time.

**Effort stays `S`.** One check against an existing parse, plus two sentences.

### Left for the owner, and it is not this item's to take

The same *shape* recurs about fifteen times in the **live** sections — Gate 1's
declines and v0.5.1's dispositions — and those lists are still growing, so
unlike v0.2.8's they genuinely can drift. Sampling them shows three kinds, and
they do not want one answer: some are decidable from `classes:` ("Four further
`safety`/`science` items"), some from `blocked-by:` ("Four are waiting on the
port"), and a good number are already anchored in time ("Eleven more from the
2026-09-12 triage pass"), which is a record of what a pass found on a date and
cannot go stale for the same reason a shipped section cannot.

Whether that is worth a second pass is a scoping call rather than a defect, and
it is deliberately not folded in here: doing so would turn an `S` item about
three dead numbers into an open-ended audit of the roadmap's live prose.

## Built 2026-09-13

`tools/doc_check.py`'s `check_gate_counts` now holds a
`**N entries are marked \`not-delegable\`**` sentence to the items the section's
frozen list names, and `ROADMAP.md`'s Definition of done for v0.2.8 records why
its two neighbours are left to the reader. The `not-delegable` count is entries
rather than ids, matching every other count the function checks.

**Two failure directions were closed that the decision did not name**, both
found by writing the tests rather than by reading the code:

- `read_items` answers `[]` for a store directory that is not there, so a
  truncated checkout would have read as "no entry is withheld" and failed the
  sentence by exactly its own size. `_read_store` asks whether the directory
  exists rather than inferring it from the result, and returns `None`, which
  the check turns into a `declined` line.
- A frozen entry naming an id the store does not hold would have read as "not
  withheld", failing a correct sentence and naming the prose as the fault.
  Nothing else in `doc_check.py` reports that state, so `_withheld_entries`
  returns `None` and the check declines instead.

Proven by watching it fail first: `ROADMAP.md:848` edited from `Seven` to
`Eight` reports `says 8 ... but 7 of them hold an item carrying that field`,
and reverting clears it.
