---
id: PL-B53Y
title: docket's front-matter fold takes an indented line opening with # for a comment before it takes it for a continuation, so a quoted value carried onto such a line is read short with its opening quote kept and nothing reported, a comment line inside a plain value does not end it, and a blank line inside a value folds to a space where YAML folds a newline, against the README's exactly-as-YAML promise; latent
priority: P3
effort: M
status: done
classes: defect
feature: front-matter-round-trip
milestone: v0.5.29
touches: subprojects/docket/src/docket/model.py, subprojects/docket/README.md, subprojects/docket/tests/test_model.py, tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
closed: 2026-10-18
pr: 1597
payoff: a quoted or comment-interrupted front-matter value is read as YAML reads it or refused by name, rather than stored short with nothing reported
verify: grep -q 'def test_a_quoted_value_continued_on_a_hash_led_line_is_read_whole' subprojects/docket/tests/test_model.py && grep -q 'def test_a_comment_line_inside_a_plain_value_is_not_folded_over' subprojects/docket/tests/test_model.py
reenters: PL-HXJY
---

**Problem.** docket's front-matter fold takes an indented line opening with # for a comment before it takes it for a continuation, so a quoted value carried onto such a line is read short with its opening quote kept and nothing reported, a comment line inside a plain value does not end it, and a blank line inside a value folds to a space where YAML folds a newline, against the README's exactly-as-YAML promise; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.model`. `_fold`, the one reader of where a front-matter value ends,
skips a line whose first non-blank character is `#` before it asks whether the
line continues the value above. `subprojects/docket/README.md` says an indented
line continues a value exactly as YAML folds a plain scalar, and that a quoted
value is unquoted; in YAML 1.2.2 a `#` inside a double-quoted scalar is content
(§ 7.3.1), and a comment line ends a plain scalar (§ 6.6, § 7.3.3).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against PyYAML:

```text
title: "Fixed in
  #1377 at last"

title: Fixed in
# a comment
  1377 at last
```

The first read as `"Fixed in`, its opening quote kept, with
`unread_front_matter_lines` and `repeated_front_matter_keys` both empty and
`parse_item` agreeing, so nothing is reported; PyYAML reads `Fixed in #1377 at
last`. The second read as `Fixed in 1377 at last`, where PyYAML refuses the
mapping, the scalar having ended at the comment. And a quoted value with a
blank line inside it folds to one space where PyYAML keeps a newline. A plain
value carried onto a `#`-led line reads `Fixed in` in both, the control. Latent:
no tracked front matter carries a quoted value onto a second line or holds a
line opening with `#`.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: the first form reads
`"Fixed in` with no unread line and no repeated key, the second
`Fixed in 1377 at last`, and `title: "a` over a blank line and `  b"` reads
`a b`; PyYAML 6.0 reads `Fixed in #1377 at last`, refuses the second, and
reads `a\nb`.

**Why it matters.** A title or reason written this way is stored short with
nothing said, and every reader of the item reads the short form.

**Generator check.** Not a member of `PL-R417`. It reads the item front-matter
value grammar, `PL-HXJY`'s fact, in the one reader itself, as `PL-LNDJ` did.
`PL-HXJY` is closed with a `spent` verdict; the comment test dates from
2026-08-24, so this is stock its sweep did not reach rather than new inflow. Filed
2026-10-06, after `PL-HXJY` closed (2026-10-05), it is still a post-close
instance of that head's fact, one of two with `PL-1R9S`; a third would read as
a fix that did not hold (2026-10-11 triage).

**Done when.** `_fold` takes an indented line for a continuation before it
takes it for a comment while a quoted value is open, ends a plain value at a
comment line or declines it by name, and folds a blank line as YAML does or the
README stops promising it, each pinned by a test.

**Closed 2026-10-18.** `_fold` now ends a plain value at a comment line and
reports an indented line after it as unread, and folds a `#`-led line into a
quoted value that is still open (`_quote_open`). A blank line inside a value
still folds to a space; the README now says so as a stated departure from
YAML rather than promising YAML's reading. One fixture in
`tests/unit/test_doc_check.py` placed a comment line inside a plain field to
pin doc_check's decline of it; that case can no longer arise, so it was
removed and the decline's wording now names a blank or unread line only.
