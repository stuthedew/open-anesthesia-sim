---
id: PL-KT0H
title: doc_check's LINK_RE takes no line ending after a link's destination, nor a title or an angle-bracket destination at all, so a link whose ) or title follows on the next line is never checked and its missing target passes; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1358
payoff: a link with a title, an angle-bracket destination or its closing parenthesis on the next line is checked like any other, so its broken target fails make check
verify: grep -qF '"links, a destination' tests/unit/test_doc_check.py && grep -qF '"links, an angle-bracket destination' tests/unit/test_doc_check.py
---

**Problem.** doc_check's LINK_RE takes no line ending after a link's destination, nor a title or an angle-bracket destination at all, so a link whose ) or title follows on the next line is never checked and its missing target passes; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 6.3: whitespace, including up to one line ending, may follow a link's destination before its title or `)`. `[the notes](docs/missing.md` over `)`, and the same with its title on the next line, give `LINK_RE` nothing where markdown-it-py 4.2.0 reads `docs/missing.md`, so `check_citations` never reports the missing file. A title on the destination's own line and a `<...>` destination are missed too; neither is a continuation, but the reading is the same pattern's. Latent: the documents' 17 relative links agree with markdown-it.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `LINK_RE` finds no link in "[the notes](docs/missing.md" over ")" or in `[the notes](docs/missing.md "Title")`, and reads `<docs/missing.md>` with its brackets as the target of an angle-bracket destination.

**Why it matters.** `check_citations` holds each relative link's target to the tree, and a link it never reads is a broken link `make check` passes; GitHub renders all three forms as links, so the miss shows only when a reader follows one.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `LINK_RE` reads a destination as CommonMark 0.31.2 § 6.3 does - an angle-bracket destination without its brackets, an optional title in quotes or parentheses, and whitespace holding at most one line ending around them - and `check_citations` holds that target to the tree; `links, ...` cases in `CONTINUED_STATEMENTS` pin each form.
