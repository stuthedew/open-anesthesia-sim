---
id: PL-YPLM
title: fixture_id_check reads three forms beside its joins wrongly - _front_matter_joins finds a front matter's edges itself so a closing marker with trailing space is no close and a document-end marker is one, _opens_a_node takes a comma or bracket ending a plain scalar's text for a node opener, and scan_text reads .claude/settings.json raw so a JSON-escaped line continuation is not decoded - and a malformed fixture id is misread; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: fixture_id_check reads a front matter's edges, a quoted scalar's start and a settings.json hook command as their formats do, so a malformed id there is neither missed nor falsely reported
verify: grep -q 'def test_the_front_matter_joins_find_its_edges_through_docket' tests/unit/test_fixture_id_check.py && grep -q 'def test_a_comma_ending_a_plain_scalar_opens_no_quoted_scalar' tests/unit/test_fixture_id_check.py && grep -q 'def test_a_settings_json_hook_command_is_read_decoded' tests/unit/test_fixture_id_check.py
---

**Problem.** fixture_id_check reads three forms beside its joins wrongly - _front_matter_joins finds a front matter's edges itself so a closing marker with trailing space is no close and a document-end marker is one, _opens_a_node takes a comma or bracket ending a plain scalar's text for a node opener, and scan_text reads .claude/settings.json raw so a JSON-escaped line continuation is not decoded - and a malformed fixture id is misread; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
the larger `tools/` checks.

- `_front_matter_joins` accepts only an exact `---` line as the close and also
  closes on `...`, where `docket.frontmatter.opens` and `closing` are the
  shared reader of a front matter's edges; a front matter closed by `---`
  with a trailing space gets no joins, so its id is read short where PyYAML
  reads it whole.
- `_opens_a_node` treats `,`, `[`, `{`, `-` or `?` at the end of a plain
  scalar's text as opening a node in block context, so the value below is
  joined as a double-quoted scalar, where PyYAML 6.0.3 keeps the backslash:

```text
description: one, "PL-K7QX\
  Z"
```

- `scan_text` reads `.claude/settings.json` as text, so a hook command whose
  JSON string holds an escaped backslash-newline, which bash would join, is
  read with the escape undecoded.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3 and `json`. Latent: no front matter under
`.claude/` closes with trailing space or `...`, none ends a plain scalar this
way, and no hook command holds the escape.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: a front matter closed by
`--- ` or cut by `...` reports `PL-K7Q` where PyYAML reads `PL-K7QX`; the
comma form reports `PL-K7QXZ` where PyYAML reads `PL-K7QX\ Z`; and a
`settings.json` hook command holding `\\\n` before `Z` reports nothing where
bash joins `PL-K7QXZ`. None of the three forms stands in `.claude/`.

**A fourth form, found 2026-10-12 by `PL-5DZ8`'s closing sweep.** `_opens_a_node` sees an anchor or tag ahead of the quote as no node opener, so `description: &a "PL-K7\` followed by `  QX"` is not joined and `PL-K7` is reported, where `docket.frontmatter._node_start` skips the anchor and reads a quoted scalar. The Done-when's "place a double-quoted scalar only where YAML opens one" covers it.

**Why it matters.** Each form either hides a malformed id from the check or
reports a well-formed one as malformed, and the first keeps a second reading
of a front matter's edges beside `docket.frontmatter`'s, free to drift from it.

**Generator check.** Not members of `PL-R417`: an edge marker, a node
indicator and a JSON escape are each read within one line. `PL-S4JL` holds the
continued forms. The first form, a front matter's edges
found again beside `docket.frontmatter.opens` and `closing`, is an instance of
`PL-KGYT`'s fact, which spelling of a repeated predicate is the answer, filed
after that head closed (2026-10-01); `PL-74T0` holds that cluster's
post-close count (2026-10-11 triage).

**Done when.** The joins find the front matter through `docket.frontmatter`,
place a double-quoted scalar only where YAML opens one, and read
`.claude/settings.json` through `json`; a test pins each form.
