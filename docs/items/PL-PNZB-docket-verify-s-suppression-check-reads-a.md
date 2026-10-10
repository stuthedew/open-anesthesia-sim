---
id: PL-PNZB
title: docket verify's suppression check reads a configuration file's diff one physical line at a time, so a TOML array or multi-line string rewrapped with no change is refused as an added suppression, a suppression split by a line-ending backslash or moved between two keys' continued values passes, and a configparser continuation behaves the same; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** docket verify's suppression check reads a configuration file's diff one physical line at a time, so a TOML array or multi-line string rewrapped with no change is refused as an added suppression, a suppression split by a line-ending backslash or moved between two keys' continued values passes, and a configparser continuation behaves the same; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.verify`. `added_suppressions` reads every
changed file the logical-line reader does not - a `.toml`, `.cfg` or `.ini` -
through `_net_line_changes`' added lines, cancelled per file, and
`is_suppression_line` judges each. Its docstring calls a configuration file
one where no token can wrap. TOML 1.0 continues an array across lines and
trims a line-ending backslash with the whitespace after it inside a
multi-line basic string; `configparser` takes an indented line for the key
above it. The check is `no suppression added`, which `--self` never relaxes.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `tomllib` and `configparser`, on scratch repositories:

```text
A. addopts = ["-p", "no:xfail"]   reflowed to one element per line
B. addopts = """-p no:cacheprovider -p no:x\
     fail"""
C. "no:xfail", moved from the markers = [ array to the addopts = [ array
D. an .ini continuation re-indented from four spaces to two
E. an .ini continuation moved from markers = to addopts =
```

A and D are refused as an added suppression where the value is unchanged; B,
C and E pass where `addopts` gains `no:xfail`. The Python half, read through
logical lines, gets both directions right. Latent: no line in the six tracked
`.toml` files matches the suppression pattern, no `.cfg` or `.ini` is tracked,
and `pyproject.toml` and `docket.toml` hold eleven multi-line arrays.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-CFWP`'s fix left.

**Done when.** A configuration file's suppressions are compared as values the
format's own reader gives (`tomllib`, `configparser`) on both sides, or the
file is declined by name; a test pins each form above.
