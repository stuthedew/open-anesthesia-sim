---
id: PL-YPLM
title: fixture_id_check reads three forms beside its joins wrongly - _front_matter_joins finds a front matter's edges itself so a closing marker with trailing space is no close and a document-end marker is one, _opens_a_node takes a comma or bracket ending a plain scalar's text for a node opener, and scan_text reads .claude/settings.json raw so a JSON-escaped line continuation is not decoded - and a malformed fixture id is misread; latent
status: untriaged
added: 2026-10-10
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

**Generator check.** Not members of `PL-R417`: an edge marker, a node
indicator and a JSON escape are each read within one line. `PL-S4JL` holds the
continued forms.

**Done when.** The joins find the front matter through `docket.frontmatter`,
place a double-quoted scalar only where YAML opens one, and read
`.claude/settings.json` through `json`; a test pins each form.
