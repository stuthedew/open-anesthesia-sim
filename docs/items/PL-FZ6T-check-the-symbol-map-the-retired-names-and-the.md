---
id: PL-FZ6T
title: Check the symbol map, the retired names and the partition-coefficient rule, so core/ cannot drift back off the domain
priority: P2
effort: M
status: blocked
blocked-by: PL-H46J
classes: infra
feature: core-domain-language
touches: tools, tests/unit
added: 2026-09-03
verify: uv run pytest tests/unit/ && grep -rq 'def test_symbol_code_cell_must_resolve' tests/unit/
---

**Problem.** Everything planned-milestone item 29 establishes is prose the
moment it lands. A later session adding a compartment, an accessor or a
coefficient has nothing telling it the convention exists.

**Why it matters.** `CLAUDE.md` asks for the decidable half of any mechanism to
be moved into code that runs free forever rather than re-derived at full context
in every session, and `tools/doc_check.py` is the project's worked example of
where that line falls: it decides whether a cited path exists, never whether the
sentence around it is still true. The same split applies cleanly here.

**Three rules, all decidable.** Standard library only, so a hook or a bare
checkout can run them; wired into `make check`.

1. **Every Code cell in `docs/MODEL.md` § "Symbols" resolves.** Parse the table,
   parse `core/` with `ast`, and assert each `ClassName.accessor` names a real
   attribute, property or field on that class. Cells reading `—` are accepted
   and must carry the sentence saying why. This is what stops `PL-H46J`'s map
   rotting.
2. **The retired names never reappear in `core/`.** After `PL-9SH6`,
   `concentration_fraction` and the `circuit_`-stuttered form are gone; a closed
   vocabulary check keeps them gone.
3. **A partition-coefficient identifier names both phases, in order.** Any name
   matching `*partition_coefficient` must match
   `<phase>_<phase>_partition_coefficient` with both phases drawn from a
   declared set. This is the rule `PL-212V` establishes, and it is worth
   enforcing precisely because the literature does not hold a convention — Baker
   and Farmery name one symbol "tissue-gas", "tissue-blood" and "blood tissue"
   within a single chapter, so a reader cannot fall back on recall.

**A fourth was considered and is not worth building.** A unit-suffix check over
every float-valued name in `core/` passes today — the suffixes are already
near-universal — so it would be a pure ratchet. That is not disqualifying on its
own, since it stays silent until violated. It is left out because the closed
suffix vocabulary would need maintaining against every legitimate new kind, and
`CLAUDE.md` is explicit that where the benefit is unclear the answer is no.
Reconsider if a suffix regression is ever actually observed.

**What must not be scripted.** Whether a name is the one a reader who knows the
domain would guess. That is the judgment half, it is the whole point of the
pass, and a tool that guessed at it would be worse than no tool because its
output would look authoritative. The three rules above are all mechanical:
resolvable, absent, well-formed.

**Where.** A new `tools/` script, or three rules added to `tools/doc_check.py`
if they sit naturally beside its existing checks — decide by whether the AST
parse of `core/` fits there without distorting it. Tests in
`tests/unit/`, one per rule, each with a fixture that violates it.

**Blocked on `PL-H46J`** (the Symbols Code column) and `PL-9SH6` (the accessor
rename), because rules 1 and 2 have nothing to check until those land. Rule 3
could be built against `PL-212V` alone if it turns out to be worth splitting.

**Done when.** The three rules run in `make check`, each has a unit test that
fails when its rule is violated, all three pass against the tree, and each
states its rule in a message a reader can act on without opening the script.
