---
id: PL-4KSZ
title: Cut v0.5.4 from the sixteen items finished since v0.5.3: the first release since the MVP that changes what a learner sees - a window wholly in its own colours, and refusals that name what refused and the control that ends them - with nothing computational moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.5
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 903
payoff: the sixteen items finished since v0.5.3 ship under their own number and stop being re-offered in every session digest, and the first release since the MVP to move app/ states what a learner now sees and proves by measurement that no computed value moved with it
verify: grep -q "^version = \"0.5.4\"" pyproject.toml
---

**Problem.** Sixteen items have closed since v0.5.3 and are re-offered in every
session digest. They complete two features - `platform-palette` and
`git-silence-channel` - and ten of them are Gate 2 entries. None is a
milestone, and every number above this one is spent, so this is a patch on §
"Versioning decision"'s test rather than a capability boundary.

## What this release contains, by tree object

Unlike v0.5.1 through v0.5.3, `src/` moves, so the no-computational-movement
claim is measured rather than read off one hash:

| Object | v0.5.3 | cut | |
| --- | --- | --- | --- |
| `src/` | `422b27e1` | `b9e24035` | **moved** |
| `src/anesthesia_sim/core/` | `061714b0` | `d9e3ca9f` | **moved** - three guard names, one docstring |
| `src/anesthesia_sim/data/` | `ab3499fd` | `ab3499fd` | identical |
| `src/anesthesia_sim/app/` | `01bc2d90` | `50d13b33` | **moved** - first time since v0.5.0 |
| `tests/reference/` | `a1848300` | `a1848300` | identical |
| `.github/` | `da3c9510` | `da3c9510` | identical |

`core/` was compared by syntax tree with module, class and function docstrings
stripped: it differs at exactly three call sites, the name argument
`AlveolarCompartment`, `VenousBloodCompartment` and `TissueGroup` pass to
`require_fraction` (`PL-SPN6`), and it holds 133 numeric literals at both ends
with none differing. `app/`'s move is `PL-KRZW`'s application palette and
`PL-WG73`'s fork-lock sentence; neither formats, rounds or computes a displayed
value. **No equation, parameter, constant, numerical method, solver step or
displayed clinical value moves.** `docs/MODEL.md` moves in § "Minimum displayed
outputs" (`PL-036`) and § "Color contrast, and the standard this interface is
held to" (`PL-KRZW`, `PL-4L49`) only.

## The theme

The first release since the MVP whose changes a learner can see: the window
stops drawing the host's colours around a light interface (`PL-KRZW`, with
`PL-4L49` making the contrast report say what nothing measures), the comparison
lock names the Reset that actually ends a comparison instead of a phrase no
control carries (`PL-WG73`), and a refused fraction names the compartment that
refused it (`PL-SPN6`). The tooling half is one shape - a git that did not
answer, read as an answer (`PL-ZPDM`, `PL-73P0`, `PL-T441`, `PL-WF3X`). The
baseline section in `ROADMAP.md` is written around that rather than around the
class labels.

## Shipped as cut

`list_sessions` showed two sibling sessions live when this cut was taken - one
titled "What's next", one "Triage", both created within the minute before this
one and neither with a closing block yet - and neither holding a release;
`bin/docket flight` reported no branch claiming an item, and no ref carried a
cut. The mechanical half was pushed first, so `bin/docket release` refuses a
second cut from either of them. This is therefore not `PL-66FP`'s
two-sessions-one-release case as far as anything could see.

The cut ships as taken, on `PL-V065`'s ratified precedent (project owner,
2026-09-21): anything merging between this cut and the tag sits inside the
`v0.5.4` tag without being named in its notes, and takes the `### also inside
this tag's span` pointer `PL-P669` introduced. This item closes here and ships
under the next release, for the structural reason `PL-CY4F` closes under this
one - a cut cannot stamp itself.

**Done when.** `pyproject.toml` reads 0.5.4, `docs/releases/v0.5.4.md` holds
the notes, `ROADMAP.md` carries the version-table row with the `current
baseline` mark moved onto it and a baseline section, `make check` is green, and
the tag is run by the project owner on the merge commit.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.4 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Sixteen items, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed - every change corrects what an existing control renders or says - and every number above it is spent, v0.6.0 through v0.9.0 being given to milestone sections. **It is the first release since the MVP to move `src/anesthesia_sim/app/`**, off the object it had held since v0.5.0 (`01bc2d9` to `50d13b3`, four files, +149/-8), **and nothing computational moved with it, measured rather than asserted**: `src/anesthesia_sim/data/` (`ab3499f`) and `tests/reference/` (`a184830`) are byte-identical, so no stored parameter and no published-reference expected value changed; `core/` moves (`061714b` to `d9e3ca9`), but with docstrings stripped its syntax tree differs at exactly three call sites, each the name a `require_fraction` guard reports, and it holds 133 numeric literals at both ends with none differing. **`platform-palette` completes, 6 of 6.** `PL-KRZW` declares the interface's light palette on the `QApplication` before the first widget exists (project owner, 2026-09-20, ratified, over leaving the host appearance alone and over a second palette for dark support), so the chrome no stylesheet reaches stops drawing a dark host around a light window - the page's scroll bar went from 94.3% of its pixels darker than mid-grey to 0% under the test suite's dark host palette - and it is a palette rather than `styleHints().setColorScheme` because that hint was observed being ignored outright. `PL-4L49` makes the contrast report count what nothing measures - 7 control kinds, each named by the test that admits it - and holds every text-bearing control in the built dashboard to declaring its own foreground, because a report counting only declared pairs read identically whether the interface was covered or had three illegible buttons on it. **`PL-WG73` is the one a learner would have paid for**: the comparison lock read "Reset the case to end this one", a phrase no control carries, while two Resets are drawn and the one a learner reaches for - the branch's - discards everything simulated since the fork and leaves the lock standing. It now reads "Run 1's Reset ends it and starts the case over; Run 2's Reset only returns Run 2 to where it branched", filled from the labels the screen carries so the instruction and the control cannot drift apart again. `PL-SPN6` names the compartment in a refused fraction - five compartments were raising one string, so a halted run could not say which had refused. `PL-036` binds each of `docs/MODEL.md`'s 21 minimum displayed outputs to the display test that holds it (project owner, 2026-09-22, ratified, over the `SimulationSnapshot`-field mechanism, which three of the entries have no field for). **The tooling half is one shape: a git that did not answer, read as an answer.** `git-silence-channel` completes, 2 of 2, with `PL-ZPDM` - on silence `vcs.tags` returned an empty set, and an empty set is a project the untagged-release gate holds to nothing, so the one gate guarding a gap that cannot be repaired afterwards waved the cut through; `PL-73P0` stops `bin/docket verify` certifying a branch's scope against a `main` nothing established; `PL-T441` and `PL-WF3X` make a git read address the store the command actually read. **Ten of the sixteen are Gate 2 entries**, which stands at 22 of 185 cleared at this cut, and `PL-CY4F`, the v0.5.3 cut, closes here because a cut cannot stamp itself.
