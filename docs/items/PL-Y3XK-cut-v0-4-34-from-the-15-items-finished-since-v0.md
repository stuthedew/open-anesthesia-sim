---
id: PL-Y3XK
title: Cut v0.4.34 from the 15 items finished since v0.4.33: the release where the interface stopped answering in the host's colours, and the model's flow envelope stopped standing in for a machine's
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.4.35
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 770
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.34"' pyproject.toml
---

**Problem.** Cut v0.4.34 from the 15 items finished since v0.4.33: the release where the interface stopped answering in the host's colours, and the model's flow envelope stopped standing in for a machine's

The fifteen are three dark-appearance palette defects (`PL-0NVN` the three
selector popups, `PL-7W9N` the six legend checkboxes, `PL-RKRY` the bookmark
dialogs), the hover's compartment contention (`PL-0RZ0`), two
`anesthesia-machine` gate entries (`PL-8PS6` fresh gas flow range as a machine
property, `PL-439V` the Tec 6 as the second device class), five apparatus
items (`PL-FCM3`, `PL-6T44`, `PL-K4R5`, `PL-8G48`, `PL-CHQY`), three
housekeeping passes (`PL-028T`, `PL-V3QB`, `PL-WQF1`) and `PL-HP95`, the
v0.4.33 cut itself. All fifteen are merged on `origin/main`; `v0.4.33` is cut
and tagged (`ac35afb`), so nothing is outstanding from the previous release.

**`0.4.34` is the number, and the mechanical guess of `0.5.0` is refused by the
roadmap rather than by preference.** `ROADMAP.md` gives `0.5.0` to "the case
you can branch", whose gate still has `PL-D126` and `PL-WJNS` open with
`PL-WZVZ` blocked outside it, and whose `Required scope` is unbuilt - so
cutting `0.5.0` here would ship that milestone under its own name with most of
it missing. `0.6.0` through `0.9.0` are likewise spent on milestone sections.
The patch is also right on its own terms: no capability boundary is crossed.
Three palette fixes and a hover fix correct what an existing control renders
and answers; `PL-8PS6` adds a second refusal beside an existing one and the
shipped profile declares no range, so nothing displayed or refused changes
today; `PL-439V` is a written design decision.

**The one claim this cut owes a measurement is that nothing computational
moved**, because unlike the last four releases `src/anesthesia_sim/core/` and
`src/anesthesia_sim/data/` both do move here. Measured rather than asserted,
and the numbers go in the baseline section:

- `src/anesthesia_sim/data/` holds 42 numeric leaves at `v0.4.33` and 42 at
  `HEAD`, none differing in value and none added or removed; the only key
  added anywhere in the tree is `reference_circle_system.json`'s
  `deliverable_fresh_gas_flow_range`, whose value is `null`.
- The `core/` diff removes no numeric literal at all. The four it adds are
  three in prose and one range guard (`numeric_value < 0.0`).
- `tests/reference/` resolves to `fcb3eca` at both ends, so every
  published-reference expected value is byte-identical and still met.

**The cut may also clear `pr:` backfills.** `bin/docket record` bare writes
every one the base can supply; let it ride the release commit rather than
composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.34` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for any `pr:` backfill the base can supply.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a
   baseline section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.

**Retitled during the cut.** The working title said "the machine abstraction
gets its second device class". Reading `PL-439V` against the tree showed that
is wrong: it closed as **satisfied by `PL-FG9D`'s specification**, which
shipped in `v0.4.33`, so the Tec 6 entered `docs/machine-abstraction.md` one
release ago and nothing about it landed here. The title now names what this
release actually moves.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.34 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Fifteen items, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed - three palette fixes and a hover fix correct what existing controls render and answer, `PL-8PS6` adds a second refusal beside an existing one over a profile that declares no range, and `PL-439V` closes as a reading of a design that shipped in `v0.4.33` - and every number above it is spent. **Unlike the four releases before it this one moves the computational trees, and nothing computational moved even so**, measured rather than asserted: `src/anesthesia_sim/core/` resolves to `89683c3` at `v0.4.33` and `0c8e708` here and `src/anesthesia_sim/data/` to `0769358` and `ab3499f`, but the data tree holds 42 numeric leaves at both ends with none differing in value and none added or removed, the only key added anywhere under it being `reference_circle_system.json`'s `deliverable_fresh_gas_flow_range` at `null`; the `core/` diff removes no numeric literal at all and the four it adds are three in prose and one range guard; and `tests/reference/` resolves to `fcb3eca` at both ends, so every published-reference expected value is byte-identical and still met. **The dark-appearance half is three faults with one cause**, `platform-palette` at 4 of 6: a control declaring only a `color:` declares its label and leaves its surface to the host, and a stylesheet on a *parent* makes every descendant resolve from the application palette instead of the parent. `PL-7W9N` is the one that carries - all six legend check boxes resolve `Base #1e1e1e` against a tick the label's stylesheet had set to `INK #243B53`, **1.35:1**, so an unchecked box is a solid dark square on a light panel, the shape a *filled* box has elsewhere - and it is a legibility defect rather than a wrong reading only because a hidden compartment also loses its swatch and goes `MUTED`. `PL-0NVN` is the three selector popups, `PL-RKRY` the two dialogs. A stylesheet was measured and refused (`QAbstractSpinBox` loses its steppers, a styled `QCheckBox::indicator` its tick), so the declaration is `qt_widgets.declare_interface_colours`, writing the `Active` and `Inactive` groups from the **widget's own** palette and leaving `Disabled` as the platform supplied it; PySide6's `QPalette()` is not the application's palette, which is what made a first attempt render an unchecked box dark. **The durable half is a check**: `tests/integration/test_dark_appearance.py`, 462 new lines, walks the whole rendered tree under a dark host palette and fails on any content widget resolving to it, and `tools/contrast_check.py`'s blanket `setPalette` refusal narrowed to "only from a function a requirement cites by name" rather than going away. Every colour the interface declares is still a light-theme value; `PL-KRZW` and `PL-4L49` are open. **`PL-0RZ0` is `PL-JVHL`'s failure one axis over**: `nearest_trace_point` kept the single globally nearest point inside a 12 px radius, so a 2 px movement decided which *compartment* answered - fat's value under muscle's label, where the two can differ severalfold. Generalising the ratified run rule to compartments (project owner, 2026-09-20, ratified, over recording the measurement and deferring to `PL-QYBW`) makes every `(run, compartment)` inside the radius answer at its own nearest point, byte-identical output on the 54.3-99.5% of hovers whose readings share a compartment, removing the choice rather than improving it. Two findings the measurement had not reached: two compartments of one run do not share an instant, since nearest is measured in two dimensions (`PL-1K9G`), and the branched case's alveolar trace contends with fat by 20 minutes, which is `PL-QYBW`'s compression now displayed rather than resolved invisibly. **`PL-8PS6` separates two bounds that had been one constant** - `core/supported_ranges.py`'s 0.0-10.0 L/min is what the lumped compartment structure is claimed over, while what a machine's flowmeters deliver is a profile field refusing in its own words - because merged, a second profile reaching 15 L/min would widen the domain the reference gates were driven over with no statement in that module changing. The shipped profile declares `null`, and **the null is the record**: survey section (b8) found the deliverable range unknown for all eight machines and names ISO 80601-2-13:2022 while stating its text was not reached. Its `Done when.`'s demand for a primary source is corrected rather than met. `PL-439V` closes as **already satisfied** by `v0.4.33`'s `docs/machine-abstraction.md`, which names the Tec 6 as `fixed_volume_percent` and records that the distinction is a declared coincidence until `PL-5K5C` gives the model an ambient pressure. **It completes `gate-remaining-cost`, 2 of 2** (`PL-FCM3` names the ids an entry outside the gate waits on; with `PL-TGFY` from `v0.4.32`), and `PL-6T44` stops `next` and `wave` reading `status: blocked` literally while `PL-K4R5` stops a correct close-out `REJECT`ing whenever an item's deliverable is a changed output string. `PL-8G48` and `PL-CHQY` are `PL-JFQ3` recurring within the hour of its closing; `PL-028T`, `PL-WQF1` and `PL-V3QB` are the queue passes, and `PL-HP95` is the `v0.4.33` cut. **The gate stands at 175 of 178**, `PL-D126` and `PL-WJNS` open inside it and `PL-WZVZ` deferred outside on `PL-TH35` and `PL-R1WQ` under item 34's no-new-display-surface rule.
