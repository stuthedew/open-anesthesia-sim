---
id: PL-1V3X
title: "Cut v0.4.24: the release where core/ settled what its dimensionless numbers are called"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.25
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 565
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.24"' pyproject.toml && test -f docs/releases/v0.4.24.md
---

**Problem.** Cut v0.4.24: the release where core/ settled what its dimensionless numbers are called

**Ten finished items since v0.4.23**, offered and approved by the project owner
on 2026-09-14. `v0.4.23` was confirmed tagged on the remote at `7dd1a03` before
the cut, so `bin/docket release`'s refusal-on-untagged-predecessor did not
apply, and `main`'s own quality run #1906 on `4b4f80d` was confirmed green
first - the run that proved `main` had recovered from the `PL-6TQH` store error.
`list_sessions` showed no live session carrying a cut and none asking for one.

**A patch, and the version policy is why.** `ROADMAP.md` § "Versioning
decision" picks the number for the capability boundary a release crosses, and
this crosses none: the only behavioral change is a render-loop cache that makes
an unchanged frame cheaper. `bin/docket wave` puts the project between numbered
steps on `v0.4.x` with Gate 1 next, so `0.4.24` is the patch-track successor.

**What the release does not touch, measured rather than asserted.** A release
that renames the scientific core's vocabulary is exactly the one in which a
value could move unnoticed, so the claim is made on tree objects and executable
lines rather than on the diff's prose:

- `tests/reference/` resolves to `42ce3b2` at both `v0.4.23` and here - every
  published-reference expected value byte-identical, and still met by the suite.
- `src/anesthesia_sim/data/` resolves to `6960c78` at both, unmoved now across
  three releases.
- Eleven files under `src/` change and **no numeric literal in executable code
  does**: every changed line carrying a number is a docstring or a comment, and
  the only executable changes in the display layer are `NewType` annotations,
  which erase at runtime.

**What is in this commit.** `make release VERSION=0.4.24` wrote the bump,
`docs/releases/v0.4.24.md`, the `milestone:` stamps and the relocked `uv.lock`.
Written by hand, which it does not generate:

- the `v0.4.24` version-table row, and `v0.4.23` demoted from current baseline;
- the "Current baseline: v0.4.24" section, in four subsections.

Nothing cited § "Current baseline: v0.4.23", checked before the rename and
confirmed by `make check` after - the breakage `PL-MHYG` caused at the previous
cut did not recur.

**One thing rides this item's id rather than taking one of its own.**
`bin/docket record` wrote the seven `pr` numbers the base was owed: `PL-1PSX`
to #563, and `PL-6KNM`, `PL-6TQH`, `PL-BDNB`, `PL-BQ46`, `PL-KL2Q`, `PL-XP6W`
to #561.

**After the merge.** The tag is the project owner's to push; this environment
cannot push a tag ref (`PL-N936`), and attempting it fails convincingly rather
than loudly.


**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.24 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. The row's first sentence, which stays in the table, reads: "**The release where `core/` settled what its dimensionless numbers are called, and nothing it computes moved.**" In the quote, § "Symbols" and § "Tissue groups" are `docs/MODEL.md`'s.

> The second half of that sentence is a tree-object identity rather than a reading of the diff: `tests/reference/` resolves to `42ce3b2` at both `v0.4.23` and here, so every published-reference expected value is byte-identical and still met, and `src/anesthesia_sim/data/` resolves to `6960c78` at both, unmoved now across three releases. Eleven files under `src/` change and **not one numeric literal in executable code does** - every changed line carrying a number is a docstring or a comment. **Six of the ten items complete `core-domain-language` at 16 of 16**, and they are one question rather than six: how many dimensionless kinds `core/` carries, which of them a type may separate, and which names describe a quantity against a range. `PL-6KNM` renames `require_concentration_fraction` to `require_fraction` on the evidence that all eleven call sites in `core/` pass a `..._partial_pressure_fraction`, so not one passes a concentration and a reader met two names for one kind on one line. `PL-BQ46` adds `MacMultiple` beside `Fraction` and `Percent`, and the hazard it refuses is reachable and arithmetic rather than hypothetical: sevoflurane's MAC-awake band is 0.34 +/- 0.05 MAC against a MAC of 2.0%, drawn at **0.58-0.78%**, and a circuit fraction at the vaporizer's own 8% maximum passed into the same call clears every runtime guard - 0.08 - 0.05 is still positive - and draws the band at **0.06-0.26%**, below the awakening concentration, where a falling trace crosses it late or never with nothing on screen saying so. `PL-KL2Q` states at the aliases which vocabulary a new field takes, by layer rather than by quantity, and records the merged `Annotated` form as priced and refused. `PL-BDNB` renames one integral and records four deliberate leaves at their bindings. `PL-XP6W` gives § "Symbols" the f_i row its own § "Tissue groups" already used. **The one change a learner could notice is `PL-1PSX`**, and its own brief did not survive measurement. `SimulationView._refresh_view` regrouped the whole recorded control timeline every frame - 0.88 ms at a thousand entries, 8.8 ms at ten thousand, 94.6 ms at a hundred thousand against a 200 ms frame - for an answer identical to the previous frame's on every frame that recorded nothing. The item blamed the playback multiplier, reasoning that a drag emits at the event rate while simulated time advances at the multiplied rate; it does not. A change is recorded only once per simulation step and a step is a property of the tick, so 600 slider events at 60 Hz record **100 entries at 1x, 5x, 20x, 60x and 300x alike**, and one entry for a drag made while paused. The item also proposed keying the cache on the record's length, which would have displayed a wrong value: `_record_control_change` *replaces* the newest entry when one control moves twice inside a step, leaving the record the same length and a different record, so the panel would have stated a setting the run was never computed under. The key is the record's identity, and both regression tests were confirmed to fail against the length-keyed version. No ceiling was put on the record, and the reason is recorded rather than assumed: a cap would retire the beginning of a case, and it would bound nothing, `RunDefinition._segments` growing one stretch *and one keyframe* per accepted change and being unbounded too. **The plan reader was wrong about the gate in two ways**, both in the commands every session opens with. `PL-WZBX`: `wave` counted debt the milestone itself exists to clear as clearable *before* it, moving Gate 1 from `3 this gate can clear` to `0 ... 2 the milestone clears itself`, and the beat from `clear the gate` to `implement v0.5.0`. `PL-TNB6`: `next` told every session that `v0.4.x` clears Gate 1, where the timeline makes the gate a row of its own that no patch may ship. **And one closure that never landed is the release's sharpest lesson.** `PL-6TQH` asked the owner to tag `v0.4.23`; the tag went up, the session that cut the release ended `failed` before closing the item, and `docket check --verify` on the next push to `main` errored because an open item's command already passed. `main` was red for seven hours and **no pull request could have shown it** - `quality.yml` replays the whole store only on a push to `main`, a pull request getting `--verify --verify-base` scoped to its own diff. Ten items, two of which are the `v0.4.23` cut and its tag.
