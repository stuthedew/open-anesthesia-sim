---
id: PL-HTHC
title: docket's config.load reads a list setting of the wrong type as its default and coerces a non-string scalar with str(), where its docstring promises that a malformed config fails to parse, so a setting that looks applied is silently not; latent
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_config.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
payoff: a mistyped or misspelt docket.toml setting stops the run by name instead of silently falling back to a default that looks applied
verify: grep -q 'def test_a_list_setting_of_the_wrong_type_is_rejected_rather_than_defaulted' subprojects/docket/tests/test_config.py && grep -q 'def test_an_unknown_key_in_the_docket_table_is_rejected' subprojects/docket/tests/test_config.py
---

**Problem.** docket's config.load reads a list setting of the wrong type as its default and coerces a non-string scalar with str(), where its docstring promises that a malformed config fails to parse, so a setting that looks applied is silently not; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`docket.config`. `load` reads `docket.toml` through `tomllib`, then hands each
list setting to `_tuple`, which returns the default for anything but a list of
strings, and each scalar to `str()` or `int()`. Its docstring says a malformed
config is reported by failing to parse rather than by being silently ignored,
since a setting that looks applied but is not is worse than one never written.
`_date` keeps that promise and raises; `_tuple` and the `str()` reads do not.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15, with
a scratch `docket.toml`:

```text
[docket]
instruction_paths = "CLAUDE.md"
protected_paths = ["src/anesthesia_sim/core", 1]
workflow_paths = "tools"
```

`load` returned the empty default for all three, with nothing raised. A second
file setting `check_command = ["make", "check"]` gave the string
`['make', 'check']` as the command, and a misspelt `workflow_path` key was
ignored. Latent: every list setting in the tracked `docket.toml` is a list of
strings, and it holds no key `load` does not read.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: the scratch file above gave
`()` for all three list settings and the string `"['make', 'check']"` for
`check_command`, with a misspelt `workflow_path` ignored and nothing raised.
The tracked `docket.toml` still holds no unknown key and no list that is not
all strings.

**Why it matters.** `docket.toml` decides which paths are protected, which are
apparatus and which command proves a branch. A setting that silently falls
back to its empty default switches the matching guard off while the file
reads as though it were on.

**Generator check.** Not a member of `PL-R417`: the value is read whole by
`tomllib`, and the fault is what `load` does with it. Not `PL-F66M`, which is
the normalizing of two path settings. The fact misread
is the type each `docket.toml` setting takes; no head's `misread:` states it
and no other open item reads it, so a one-off (2026-10-11 triage).

**Done when.** `load` raises naming the key for a list setting that is not a
list of strings, a scalar of the wrong type and an unknown key in the docket
table, as `_date` does for a date, each pinned by a test.
