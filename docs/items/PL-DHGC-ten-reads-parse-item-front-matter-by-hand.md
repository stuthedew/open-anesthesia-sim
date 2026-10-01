---
id: PL-DHGC
title: Ten reads parse item front matter by hand instead of through docket.model, and one is wrong today: item_reads looks for status: done in a file's first 400 characters, so it reads 20 of 1,624 closed items as open; the others are generator_check's own parser, open-status set, list splits and a closure count that misses dropped, item_reads's --- split, and model's own parser restating FIELD_ORDER and LIST_FIELDS
priority: P2
effort: M
status: ready
classes: defect
feature: read-facts-through-docket
touches: tools/item_reads.py, tools/generator_check.py, subprojects/docket/src/docket/model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: item_reads stops reading closed items as open and generator_check counts a dropped member as closed, because both read front matter through docket.model
verify: ! grep -qF 'CLOSED = tuple(f"status: {status}"' tools/item_reads.py && ! grep -qF 'def read_front_matter' tools/generator_check.py && ! grep -qF '.get("status") == "done"' tools/generator_check.py
---

**Problem.** Ten reads parse item front matter by hand instead of through docket.model, and one is wrong today: item_reads looks for status: done in a file's first 400 characters, so it reads 20 of 1,624 closed items as open; the others are generator_check's own parser, open-status set, list splits and a closure count that misses dropped, item_reads's --- split, and model's own parser restating FIELD_ORDER and LIST_FIELDS

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/item_reads.py:54` looks for `status: done` or `status: dropped` in a file's first 400 characters, and 20 of the 1,624 closed items put that line past it (measured 2026-10-01; `PL-WVSX`, `PL-ZZHZ`, `PL-HBH2` among them), so it reads them as open; `:75` splits the front matter on `---`. `tools/generator_check.py:187` is its own parser, whose reason, that a YAML dependency would stop it running from a bare checkout, does not reach `docket.model`, which is standard library; `:92` is its own open-status set (agrees); `:311`, `:318` and `:332` split list fields (agree); `:342` counts closures with `== "done"`, so a dropped member does not count. `subprojects/docket/src/docket/model.py:1423`'s `known` set restates `FIELD_ORDER` (the 26 keys are equal) and `:1457`-`:1475` restate `LIST_FIELDS`.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Reproduced 2026-10-01.** 17 of 1,626 closed items put their status line at or past character 400, counted by its start offset; the sweep counted 20 of 1,624 by its own method the same day.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
