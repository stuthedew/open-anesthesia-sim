---
id: PL-B5VM
title: "main is red on PL-S5YM's non-discriminating verify: an unrelated merge added a test whose name contains 'covered', flipping 'pytest -k covered' to passing while the item's own work is untouched"
priority: P2
effort: S
status: done
classes: defect, infra
feature: queue-hygiene
milestone: v0.4.26
touches: docs/items
added: 2026-09-15
closed: 2026-09-15
pr: 598
verify: test -z "$(grep -h '^verify:' docs/items/PL-S5YM-*.md | grep -- '-k covered')"
---

**Problem.** `main` was red. Quality run #1985 on `7ba6108e` failed with one
error: `PL-S5YM is open but its verify: command already passes (1 of 147
checked)`.

**The chain, established rather than guessed.**

1. `PL-S5YM`'s command was `uv run pytest tests/unit/test_doc_check.py -k
   covered`, written when the item was captured (`4e0da215`). It was honest
   then: `-k covered` matched no test, pytest exited 5, the command failed —
   which is what an open item's command must do.
2. #593 (`PL-MXSL`, `PL-F933`, commit `7ba6108e`) added
   `test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered` —
   a test about citations a `.gitignore` covers, with nothing whatever to do
   with `TreeMap.covered_dirs`, the bare-directory branch `PL-S5YM` is about.
3. `-k` matched it on the substring "covered". The command began passing, and
   the whole-store replay read that as work landed without its item being
   closed.

None of `PL-S5YM`'s work had been done: `covered_dirs` appears in
`tools/doc_check.py` and nowhere in `tests/unit/test_doc_check.py`. Confirmed
by collecting the selection — `-k covered` picks exactly one test, and it is
the unrelated one.

**Why it matters, and why `main` is the only place it showed.**
`.github/workflows/quality.yml` runs `bin/docket check --verify --verify-base`
on a pull request, scoped to the items that branch changed, and the unscoped
`bin/docket check --verify` only on push to `main`. #593 changed neither
`PL-S5YM` nor any file it declares, so no pull request could have replayed it.
The breakage was invisible until it was already on the default branch, which
is the case the session-start digest's red-main line exists to surface — no
pull request will show it, and nobody owns it.

It also defeats the guarantee the replay stands for, in the direction that
matters. `docket verify` would ACCEPT a branch that did none of `PL-S5YM`'s
work, and the store would assert an item was finished when its subject was
untouched. That is `.claude/rules/apparatus-standard.md`'s floor exactly: what
the apparatus tells a session must be true.

**Fixed by** rewriting `PL-S5YM`'s `verify:` to key on both halves of its own
"Done when" rather than on a test name: `tests/unit/test_doc_check.py` must
name `covered_dirs`, which only that item's work puts there, and
`docs/ARCHITECTURE.md` must no longer carry the "no tree draws one today"
clause the item exists to replace. Run against the tree as found, it fails, as
an open item's must. `PL-S5YM` itself carries the account, so the next session
to open it is not left to re-derive why its command changed.

**The class, counted and captured rather than fixed here.** Four other open
items rest on a bare `pytest -k SUBSTRING` that any future unrelated test name
can satisfy — `PL-10MX`, `PL-8JY7`, `PL-GVC0`, `PL-LWMS`; a fifth, `PL-L4YG`,
also greps for a specific `def test_...` and is anchored. `PL-Q8RQ` carries
that, including the observation that whether a command can discriminate at all
is decidable enough for `docket check` to refuse the shape.

**Done when.** No open item's `verify:` is `-k covered`, which the command
above reads, and `main`'s next whole-store replay is green.
