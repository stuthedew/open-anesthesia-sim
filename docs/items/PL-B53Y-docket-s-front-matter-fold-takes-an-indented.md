---
id: PL-B53Y
title: docket's front-matter fold takes an indented line opening with # for a comment before it takes it for a continuation, so a quoted value carried onto such a line is read short with its opening quote kept and nothing reported, a comment line inside a plain value does not end it, and a blank line inside a value folds to a space where YAML folds a newline, against the README's exactly-as-YAML promise; latent
status: untriaged
feature: front-matter-round-trip
added: 2026-10-06
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

**Why it matters.** A title or reason written this way is stored short with
nothing said, and every reader of the item reads the short form.

**Generator check.** Not a member of `PL-R417`. It reads the item front-matter
value grammar, `PL-HXJY`'s fact, in the one reader itself, as `PL-LNDJ` did.
`PL-HXJY` is closed with a `spent` verdict; the comment test dates from
2026-08-24, so this is stock its sweep did not reach rather than new inflow.

**Done when.** `_fold` takes an indented line for a continuation before it
takes it for a comment while a quoted value is open, ends a plain value at a
comment line or declines it by name, and folds a blank line as YAML does or the
README stops promising it, each pinned by a test.
