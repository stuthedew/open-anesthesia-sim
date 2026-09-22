---
id: PL-Q8RQ
title: Four open items' verify commands rest on a bare 'pytest -k SUBSTRING', which any unrelated test name can satisfy: PL-S5YM turned main red exactly this way, and whether a command can discriminate at all is decidable enough for docket check to refuse it
priority: P2
effort: M
status: ready
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_config.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, docket.toml
added: 2026-09-15
payoff: a new verify: command can no longer rest on a pytest -k name, so an open item's check cannot start passing because an unrelated test happens to share the name - the way PL-S5YM turned main red
verify: grep -q 'def test_a_bare_k_selector_is_refused' subprojects/docket/tests/test_checks.py
---

**Problem.** Four open items' verify commands rest on a bare 'pytest -k SUBSTRING', which any unrelated test name can satisfy: PL-S5YM turned main red exactly this way, and whether a command can discriminate at all is decidable enough for docket check to refuse it

**Why it matters.** A bare `pytest -k SUBSTRING` does not fail when no test
carries the name. It *selects nothing*, collects nothing and exits 5 - non-zero,
so it reads as a command correctly failing before the work, and it goes on
reading that way afterwards unless some test happens to match. It also
specifies only that *some* test somewhere comes to be called `SUBSTRING`, never
that any behavior holds, so it is a bet on a name rather than a specification.

`PL-S5YM` turned `main` red in exactly this way: its `-k covered` selector
began matching a test that a merge added. The blast radius is on record - three
sessions diagnosed that red `main` independently inside four minutes and opened
three pull requests for it (`PL-99YZ`). Four open items carry the same shape
today, so this is live rather than historical, and the skill already documents
the replacement (the whole file's suite paired with a `grep` for the test the
work adds, which exits 1 as an ordinary failure).

**Done when.** `bin/docket check` refuses a `verify:` command whose only
selector is a bare `-k`, grandfathered from a date in `docket.toml` the way
`verify_required_from` and `verify_required_at_close_from` already are. The
grandfathering is load-bearing rather than politeness: without it the four open
instances fail `make check` the moment the rule lands, which forces exactly the
campaign the `docket` skill refuses - "each is repaired as its item is
started", because a command written away from its work is how every wrong one
in this store came to exist. A test pins both the refusal and the
grandfathering.

**Re-pointed by `PL-6TP8`, 2026-09-19.** The contract's first obligation on a
command - its failure before the work is an evaluation, an ordinary exit 1 and
never pytest's 5 - is the rule this item makes mechanical, and the check is
still wanted as briefed, grandfathering included. Population today: `PL-10MX`,
`PL-GVC0` and `PL-8JY7` at `ready`, `PL-LWMS` at `blocked`.
