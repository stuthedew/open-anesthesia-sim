---
id: PL-PNZB
title: docket verify's suppression check reads a configuration file's diff one physical line at a time, so a TOML array or multi-line string rewrapped with no change is refused as an added suppression, a suppression split by a line-ending backslash or moved between two keys' continued values passes, and a configparser continuation behaves the same; latent
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: a TOML or ini value reflowed without change no longer refuses a close-out, and a suppression continued across lines or moved between keys no longer passes verify as none added
verify: grep -q 'def test_a_configuration_suppression_is_compared_as_its_formats_reader_reads_it' subprojects/docket/tests/test_verify.py
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`: form A, `addopts =
["-p", "no:xfail"]` reflowed to one element per line in a scratch
`pyproject.toml`, gives `found=('"no:xfail",',)`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-CFWP`'s fix left.

**Why it matters.** `no suppression added` is a check `verify --self` never
relaxes, so its false refusal blocks a correct close-out, and its false pass
lets a disabled plugin or marker through while the report reads `none`.
Latent: no tracked configuration value holds the suppression pattern today.

**Done when.** A configuration file's suppressions are compared as values the
format's own reader gives (`tomllib`, `configparser`) on both sides, or the
file is declined by name; a test pins each form above.
