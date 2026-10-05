---
id: PL-WJM4
title: cmd_withdraw's docstring says the write replaces one line, but with_front_matter_value replaces the key's line and every continuation _fold gives it; latent
priority: P3
effort: S
status: done
classes: docs, defect
feature: front-matter-round-trip
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1363
payoff: a session reading cmd_withdraw is told the true extent of what a withdrawal rewrites, so nobody trusts a one-line diff a wrapped recurrences value does not give, or narrows the write to match and orphans the tail
verify: ! grep -qF 'replaces one line' subprojects/docket/src/docket/cli.py && ! grep -qF 'whose diff is *one* line' subprojects/docket/src/docket/model.py
---

**Problem.** cmd_withdraw's docstring says the write replaces one line, but with_front_matter_value replaces the key's line and every continuation _fold gives it; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`cli.py`:1663-1666 describes the `recurrences:` withdrawal as a one-line replace; the write goes through `with_front_matter_value`, which replaces the key line and its folded continuations. A docstring that no longer says what the code does.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, in a scratch store run with `--items` and `--no-git`, an item whose `recurrences:` wraps onto an indented second line (`2026-10-02 PL-B1C2,` then `2026-10-03 PL-D3D3`): `bin/docket withdraw PL-K7QX PL-D3D3 --because PL-F4F4` exited 0, and `diff` against the file as it was showed `6,7c6`, both lines replaced by the one line `recurrences: 2026-10-02 PL-B1C2, 2026-10-03 PL-D3D3 withdrawn 2026-10-04 PL-F4F4`, where `cmd_withdraw`'s docstring says "the write here replaces one line and cannot disturb another".

**Why it matters.** The docstring is the stated contract of the one command that edits a recorded value in place, and "replaces one line" is the reason it gives for writing past an unknown key, so a reader weighing a withdrawal on a wrapped value, or reviewing its diff, is promised a smaller edit than the code makes. The code is the side that is right: replacing the folded lines whole is deliberate since `PL-JD4L`, and `with_front_matter_value`'s own comment says a field spread over several lines "is replaced whole rather than left with an orphaned tail". A session that made the code match the docstring would bring that orphaned tail back.

**Generator check.** An instance of `PL-9HD1`'s fact, the item front-matter value grammar: where a field's value ends and which spellings it may take, filed after that head closed on 2026-09-21. The docstring states a value's extent as one line where `_fold` gives it continuations. One of three such instances, with `PL-0779` and `PL-LNDJ`, recorded under `PL-HXJY` as a generator whose fix did not hold.

**Done when.** `cmd_withdraw`'s docstring states the write's extent as `_fold` gives it, the field's own line and every indented continuation folded into it, and no longer says it replaces one line; `with_front_matter_value`'s own docstring in `model.py`, which makes the same claim as "an edit whose diff is *one* line" (found at triage, 2026-10-04), says the same; both `! grep -qF` clauses of `verify:` pass, and nothing in the command's behaviour changes. A docstring correction, so no test is owed.
