---
id: PL-6KHQ
title: docket release's prepare_bump rewrites the first line shaped like a version key in pyproject.toml, which can be a line inside a TOML multi-line string ahead of the real key, and its read-back passes when the requested version equals the declared one - the resume of an interrupted cut - so a string value is silently changed; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1436
payoff: Resuming an interrupted release cut can never silently rewrite a string value in pyproject.toml.
verify: grep -q 'def test_a_resumed_bump_leaves_a_version_line_inside_a_multi_line_string_alone' subprojects/docket/tests/test_release.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16,
against `tomllib`: with target `0.2.0` `prepare_bump` accepts and the
description reads `version = "0.2.0"` back; with `0.3.0` it refuses by name;
`below_current` returns empty for `0.2.0` over `0.2.0`, which is what lets the
resume through. Still latent: `pyproject.toml`'s one version line is the real
key, and the file holds no multi-line string.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-3DD9`'s fix left. Latent, so an ordinary item under the head's spent
ruling (re-checked 2026-10-11).

**Why it matters.** The resume of an interrupted cut is the run nobody reads
the diff of closely, and the rewrite lands in the project file every release
ships, so a value inside a string would change silently and go out with the
tag. The read-back exists to refuse a bump its one line cannot make, and in
this one case it passes.

**Done when.** The bump rewrites the line `tomllib` says holds the project's
version - the key's own line - and refuses where it cannot place it; a test
pins the form above.
