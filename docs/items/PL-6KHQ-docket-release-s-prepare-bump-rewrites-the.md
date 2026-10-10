---
id: PL-6KHQ
title: docket release's prepare_bump rewrites the first line shaped like a version key in pyproject.toml, which can be a line inside a TOML multi-line string ahead of the real key, and its read-back passes when the requested version equals the declared one - the resume of an interrupted cut - so a string value is silently changed; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket release's prepare_bump rewrites the first line shaped like a version key in pyproject.toml, which can be a line inside a TOML multi-line string ahead of the real key, and its read-back passes when the requested version equals the declared one - the resume of an interrupted cut - so a string value is silently changed; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.release`. `prepare_bump` substitutes the
first match of `VERSION_RE`, a pattern anchored on a physical line, then reads
the result back through `version_in` (`tomllib`). A TOML 1.0 multi-line basic
string continues a value across lines, so a line inside one can match the
pattern. The read-back refuses every such case but one: `below_current` lets
the declared version through, for resuming a cut interrupted after its bump,
and there the rewritten line inside the string passes.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `tomllib`, with target `0.2.0`:

```text
[project]
name = "x"
description = """
version = "0.1.0"
"""
version = "0.2.0"
```

`prepare_bump` accepts and the description's line becomes `version = "0.2.0"`;
`tomllib` reads the description changed and the version not. With target
`0.3.0` the same input is refused by name. Latent: in `pyproject.toml` the
first such line is the real key, and no multi-line string holds one.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-3DD9`'s fix left.

**Done when.** The bump rewrites the line `tomllib` says holds the project's
version - the key's own line - and refuses where it cannot place it; a test
pins the form above.
