---
id: PL-S4JL
title: fixture_id_check's two new joins misread a continued form each - _fence_joins drops the last line of a shell fence its list item or block quote closes, and _front_matter_joins reads a quote opening a plain or block scalar's continuation line as a double-quoted scalar and joins its backslash-newline - so a malformed fixture id is missed; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/src/docket/fences.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/tests/test_fences.py, subprojects/docket/tests/test_frontmatter_reference.py, docs/items/PL-YPLM-fixture-id-check-reads-three-forms-beside-its.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1435
payoff: a malformed id carried across a container-closed shell fence or a quote-led scalar continuation line is reported rather than missed
verify: grep -q 'def test_a_fence_its_container_closes_is_joined_to_its_last_line' tests/unit/test_fixture_id_check.py && grep -q 'def test_a_quote_opening_a_continuation_line_joins_nothing' tests/unit/test_fixture_id_check.py
---

**Problem.** fixture_id_check's two new joins misread a continued form each - _fence_joins drops the last line of a shell fence its list item or block quote closes, and _front_matter_joins reads a quote opening a plain or block scalar's continuation line as a double-quoted scalar and joins its backslash-newline - so a malformed fixture id is missed; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
the larger `tools/` checks. `scan_text` reads each
`.md` file under `.claude/` through `_joined`, new in `#1390`:

- `_fence_joins` joins a shell fence's lines with `docket.shell.joined_text`
  over `range(block.start + 1, block.end)`. `docket.fences.Block.end` is the
  closing fence line where the fence closes itself, and the last content line
  where its container ends first (its docstring says so; CommonMark 0.31.2
  § 4.5, § 5.2), so that line never reaches the join (POSIX XCU § 2.2.1).
- `_front_matter_joins` with `_opens_a_node` takes any quote at a line's start
  for a double-quoted scalar and removes the backslash-newline inside it, which
  YAML 1.2.2 does only in a double-quoted scalar (§ 7.3.1). A quote opening a
  plain scalar's continuation line (§ 7.3.3) or a block scalar's content line
  (§ 8.1) is text, and the backslash stays.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0 and cmark-gfm 0.29 (fence content ending
in the joined line), bash 5.2.21 and dash (both print the joined id), and
PyYAML 6.0.3 and ruamel.yaml 0.19.1 (which keep the backslash):

```text
- item2

  ```bash
  echo PL-K7QX\
  Z
not indented

---
name: x
description: Use it for the queue
  "see PL-K7Q\
  X"
---
```

The fence's malformed id is not reported, though the same fence closed by its
own marker is; the front matter is joined to a well-formed id, so the
malformed one YAML reads goes unreported, and a `description: >` block scalar
reads the same. Latent: `.claude/` holds 17 shell fences, none closed by its
container, and 12 front matters, none with an indented line opening with a
quote.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `scan_text` reports nothing
for the container-closed fence and `PL-K7QXZ` for the same fence closed by its
own marker, and nothing for the plain-continuation and `description: >`
front matters, where PyYAML 6.0 keeps the backslash. `.claude/` still holds 17
shell fences, none container-closed, and 12 front matters, none with a
quote-led indented line.

**Why it matters.** fixture_id_check is what keeps a malformed id out of the
documents sessions read and copy from, and each form here hides one from it
while the check passes.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names. The code is new in `#1390`: the gap closed `PL-HKR5`'s fix left. Latent, so an ordinary item under that head's `spent` verdict: found live in a tracked file, it reopens `PL-R417` (2026-10-11 triage).

**Done when.** A container-closed fence's last line is joined, and a front
matter's backslash-newline is removed only inside a double-quoted scalar
`docket.frontmatter` places; a test pins each form above.
