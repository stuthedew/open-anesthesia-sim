---
id: PL-3WFF
title: Review the 6 regular expressions in src/anesthesia_sim/ that tools/regex_baseline.py lets stand without a reason, and replace each one a parser or string method does better or write its reason beside it
status: untriaged
feature: regex-review
added: 2026-11-03
---

**Problem.** Review the 6 regular expressions in src/anesthesia_sim/ that tools/regex_baseline.py lets stand without a reason, and replace each one a parser or string method does better or write its reason beside it

`PL-7JYV` stops a session before it writes a regular expression with no
written reason, and lets the calls the tree already held stand in
`tools/regex_baseline.py`. Six of those are under `src/`, one module-level
`re.compile` in each of these files:

- `src/anesthesia_sim/app/agent_cost.py`
- `src/anesthesia_sim/app/currency_code.py`
- `src/anesthesia_sim/app/preferences.py`
- `src/anesthesia_sim/app/view_registry.py`
- `src/anesthesia_sim/layout/run_identity.py`
- `src/anesthesia_sim/layout/tree.py`

**Why it matters.** These are the simulator's own, held to the specialist
standard, and a pattern that reads a format it does not parse holds only until
the first case it was not written for. None of the six had a recorded reason.

**Approach.** For each pattern, ask the questions `tools/regex_check.py`'s
`GUIDANCE` prints: what it must recognise, whether a module or the standard
library already reads that format, and whether a string method does it. Then
replace it, with a test of text it must accept and text it must refuse, or keep
it with a `# regex:` comment giving the reason. Either way, lower or delete its
entry in `tools/regex_baseline.py` in the same commit.

**Done when.** No entry under `src/` is left in `tools/regex_baseline.py`.

**Checked 2026-11-03.** The "Regex usage code review" session reviewed all
six and recommends keeping each one. Each is a whole-value check where outside
input enters, run with `fullmatch` and ASCII ranges such as `[0-9]`, because
`\d` matches any Unicode digit and `$` matches before a trailing newline. Each
already has a comment above it giving its reason, but without the `regex:`
tag. A standard-library parser alone accepts too much: `date.fromisoformat`
returns a date for `"20080305"` on Python 3.13, which this session confirmed,
and the review reports that `Decimal` accepts `1e3`, `NaN` and `1_000`.

So the work is small:

1. Start each existing comment with `regex:`.
2. Fix one comment. `src/anesthesia_sim/layout/run_identity.py` calls the
   session token "a version 4 UUID", but 32 zeros match `_SESSION_TOKEN`, and
   `uuid.UUID(hex="0" * 32).version` is `None`, which this session confirmed.
   The refusal message already states the real rule, 32 lowercase hexadecimal
   digits.
3. Decide two smaller points the review raised. `_VERSION` in
   `src/anesthesia_sim/app/view_registry.py` accepts leading zeros, which
   Semantic Versioning 2.0.0 item 2 forbids, though developers write that
   value in code. `_CURRENCY_CODE_PATTERN` checks only the shape, so an
   unassigned code such as `QQQ` passes, which is acceptable for a label.
