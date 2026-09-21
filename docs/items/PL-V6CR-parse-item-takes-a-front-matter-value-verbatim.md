---
id: PL-V6CR
title: parse_item takes a front-matter value verbatim to end of line, so a title quoted the way YAML requires for an embedded colon keeps its quote characters and every reader prints them
priority: P3
effort: S
status: done
classes: defect
milestone: v0.5.0
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
added: 2026-09-21
closed: 2026-09-21
pr: 826
payoff: a front-matter value quoted the way YAML requires reads as the string the author meant, so 56 titles stop printing their quotes and 3 verify: commands become runnable instead of exiting 127
verify: uv run pytest subprojects/docket/tests/test_model.py -q -k "quote or verbatim"
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

**Closed 2026-09-21 under `PL-9HD1`**, with `PL-5B39` and `PL-FX0K`.

**The first of the two answers was taken - strip in `parse_item` - and the
second was not needed.** Stripping costs no churn: 56 titles and 3 `verify:`
commands read correctly with no file edited, where refusing at `docket check`
would have opened 59 errors against items already written. The cost this brief
named, that a title genuinely opening and closing with a quote can no longer be
expressed, is still one no item has ever wanted.

**What the measurement added to the case.** 3 of the 59 are `verify:` fields,
not titles, and a `verify:` is handed to a shell: it reads the quoted form as a
single word and exits 127 having run nothing. That is `PL-MZH2` exactly, which
was repaired by hand on `PL-D9H6` in `#138` - and three more arrived afterwards,
because the hand repair left the reader that produced it untouched. So this was
never only cosmetic.

**And the strip is narrower than "surrounded by quotes".** `PL-XF5V`'s `payoff:`
opens with a quoted phrase and runs on past its closing quote; the rule only
unquotes where the pair closes at the last character, which leaves that value
verbatim. `''` inside a single-quoted scalar collapses, which two titles here
need. Inside a double-quoted scalar, only a backslash before a quote or another
backslash escapes - turning a backslash-n into a newline would invent a
character the file does not hold.
