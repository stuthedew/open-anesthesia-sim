---
id: PL-HTHC
title: docket's config.load reads a list setting of the wrong type as its default and coerces a non-string scalar with str(), where its docstring promises that a malformed config fails to parse, so a setting that looks applied is silently not; latent
status: untriaged
added: 2026-10-06
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

**Generator check.** Not a member of `PL-R417`: the value is read whole by
`tomllib`, and the fault is what `load` does with it. Not `PL-F66M`, which is
the normalizing of two path settings.

**Done when.** `load` raises naming the key for a list setting that is not a
list of strings, a scalar of the wrong type and an unknown key in the docket
table, as `_date` does for a date, each pinned by a test.
