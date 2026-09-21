---
id: PL-V6CR
title: parse_item takes a front-matter value verbatim to end of line, so a title quoted the way YAML requires for an embedded colon keeps its quote characters and every reader prints them
status: untriaged
added: 2026-09-21
---

**Problem.** parse_item takes a front-matter value verbatim to end of line, so a title quoted the way YAML requires for an embedded colon keeps its quote characters and every reader prints them

**Hit on 2026-09-20 while triaging, and repaired in `#812`'s second commit.**
Three of the six items triaged there carry a colon in their title -
`PL-FKN7`, `PL-R17Y`, `PL-RS3Z`. Writing their front matter by hand I quoted
them the way YAML requires, `title: "The branch's presentation_requested
wiring is untested: every branch test reads the controller, none reads the
display"`. `parse_item` is not a YAML reader: it takes the rest of the line,
so the quote characters became the first and last characters of the title.

`bin/docket feature branch-display-tests` then printed them quoted, which is
how it was caught - by reading the output for a reply, not by any check.
`ad9da30` stripped them.

**Why it is worth an item rather than the one-line fix it already got.** The
store answered confidently and wrongly, which is the failure
`.claude/rules/apparatus-standard.md`'s floor names, and nothing in `docket
check` can see it: a title with quotes in it is a valid title. The next
session to hand-write a front-matter value with a colon in it - a title, a
`payoff`, a `reason` - makes the same mistake for the same reason, because
quoting is the correct instinct everywhere else.

Two candidate answers, and they are not exclusive:

- **Strip a surrounding matched quote pair in `parse_item`**, which makes the
  YAML instinct harmless. Costs: a title that genuinely opens and closes with
  a quote character can no longer be expressed, which no item has ever wanted.
- **Refuse it in `docket check`**, so a quoted value is an error naming the
  field rather than a silently wrong string. Costs nothing and catches the
  `reason`/`payoff` cases the first answer would also fix.

The second is the cheaper to get right and the first is the kinder to use.
`PL-5B39` is the neighbouring defect - `parse_item` truncating a multi-line
value at its first line - and whoever takes either should read both, since
both are the same reader being less of a parser than its callers assume.

**Done when.** A front-matter value written with surrounding quotes either
parses to the unquoted string or fails `bin/docket check` naming the field,
and a test under `subprojects/docket/tests/` holds whichever way it settles.
