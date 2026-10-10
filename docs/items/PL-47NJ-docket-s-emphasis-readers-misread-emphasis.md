---
id: PL-47NJ
title: docket's emphasis readers misread emphasis inside one statement - checks' _marks_recommendation takes a multiplication's asterisks for emphasis, _heading_words matches a heading by prefix, _sections pairs an unclosed heading's opener with a run that cannot close it, _labels reads no heading inside a list item, and picks.bold_lead takes asterisks inside a code span - so a missing recommendation, a missing section or a bold lead is read wrongly; latent
status: untriaged
added: 2026-10-10
---

**Problem.** docket's emphasis readers misread emphasis inside one statement - checks' _marks_recommendation takes a multiplication's asterisks for emphasis, _heading_words matches a heading by prefix, _sections pairs an unclosed heading's opener with a run that cannot close it, _labels reads no heading inside a list item, and picks.bold_lead takes asterisks inside a code span - so a missing recommendation, a missing section or a bold lead is read wrongly; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`docket.checks` and of docket's cli, picks and
trend modules. CommonMark 0.31.2 § 6.2 decides which delimiter runs open and
close emphasis (left- and right-flanking), and § 6.1 makes a code span's
content literal:

```text
The cost is 2 * 3 and we recommend nothing x * y here.
**Problems with the dose** ...        **Done whenever** ...
**Done when. The suite
passes and **foo** is bar.
**Decision needed.** Which?

- ## Answers 2026-10-01

  Take A.
- **`a ** b`** lead
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `_marks_recommendation` returns true on the first (no
`_NOT_EMPHASIS`, which `_labels` applies); `_heading_words` opens the
`**Problem.**` and `**Done when.**` sections on the second; `_sections` takes
the run before `foo` for the heading's closer, where CommonMark leaves the
opener literal; `_answered_beneath` finds no answer label in the fourth, where
the same heading at the top level is one (the README says a heading is one as
CommonMark reads it); `bold_lead` stops inside the code span. Latent: no
answer on today's store changes.

**Generator check.** Not a member of `PL-R417`: each reads the right
statement and pairs emphasis wrongly inside it. The `_sections` form is the
remainder of closed `PL-M890` within a statement.

**Done when.** Each reader pairs emphasis by § 6.2's flanking rules over the
statement's text with code spans blanked, matches a heading word whole, and
reads headings inside containers; a test pins each form above.
