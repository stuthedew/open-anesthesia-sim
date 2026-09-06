---
id: PL-N092
title: Rewrite README as a human-readable introduction to the project
priority: P2
effort: M
status: ready
classes: docs, ux
feature: project-introduction
touches: README.md, docs/MODEL.md, pyproject.toml, Makefile, .github/workflows/quality.yml, tools/readme_hold_check.py, tests/unit/test_readme_hold_check.py, docs/ARCHITECTURE.md
added: 2026-09-01
verify: python3 tools/doc_check.py check && test -f README.md && ! grep -q 'resolution the numerical method supports' README.md
not-delegable: docs/MODEL.md is a protected path, and the command below bounds only the mechanical half - whether the rewritten README actually introduces the project to a first-time reader is the judgment a check cannot make, which is the whole of this item
---

**Problem.** `README.md` does not introduce the project to a person meeting it
for the first time. It reads as accumulated implementation notes rather than as
prose written for a reader, and it descends into detail that belongs in
`docs/MODEL.md` or nowhere. The project owner's example, at `README.md:40`:

> Concentrations are displayed to 0.01 percentage points, which is the
> resolution the numerical method supports rather than the resolution the
> floating-point values carry.

That sentence is a defensible statement about the display contract, but it is
answering a question no first-time reader has yet thought to ask, several
screens before they have been told what the simulator simulates.

**Why it matters.** The README is the only document most readers will open, and
`CLAUDE.md`'s two-standards rule puts it on the simulator side of the line —
held to the same specialist standard as `src/` and `docs/MODEL.md`, not the
"works and stays streamlined" bar of the workflow apparatus. A README that
buries what the project *is* under display-precision rationale fails that
standard, and it fails the safety-adjacent purpose too: a reader who never
reaches the point about this being an educational simulation is the reader most
likely to misread a number later.

**Where.** `README.md` (156 lines at time of capture). Detail worth keeping but
not worth the front page moves to `docs/MODEL.md`, which is already the
authoritative specification for equations, units, assumptions, provenance,
numerical method and known limitations — so most of what gets cut is either
already there or belongs there.

**Done when.** A reader who has never seen the project can, from the README
alone: say what the simulator does and who it is for, see that it is an
educational/simulation tool and not for patient care, and get it running.
Model-internal detail is gone from the README or moved to `docs/MODEL.md`; no
statement is lost without a home. `make check` passes, including `doc-check`.

**Guidance for the session that takes this on.** The project owner named
GitHub's own README documentation as the starting point. That page is recorded
below rather than only linked, so this item needs no network to be worked:

- Source: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes>,
  read 2026-09-01 via `raw.githubusercontent.com/github/docs` (`docs.github.com`
  itself was blocked in that session; see the note below). Later sessions
  should be able to fetch the canonical URL directly.
- **What GitHub says a README should cover**, and it is a good outline as it
  stands: what the project does; why it is useful; how to get started; where to
  get help; who maintains and contributes to it.
- **Location and precedence:** GitHub reads `.github/`, then the repository
  root, then `docs/`. This repository has exactly one README, at the root, and
  the rewrite should keep it there.
- **Section links and the outline** are generated from the headings, reachable
  from the **Outline** menu on the rendered page — so headings are navigation,
  not decoration. Content past 500 KiB is truncated when viewed on GitHub,
  which is no constraint at this size.
- Extensive documentation is better placed outside the README; here that means
  `docs/MODEL.md`, which already owns equations, units, assumptions, provenance,
  numerical method and known limitations.

Beyond that page, the owner asked that the implementing session do its own
current best-practice research before writing rather than working from memory
— `CLAUDE.md`'s "consult the source rather than memory" rule. That research was
deliberately **not** done at capture time: the item is non-urgent and doing it
early would have meant designing the README in a session that was not going to
write it.

**Constraint from the tooling.** `tools/doc_check.py` holds `README.md` in
`DOC_GLOBS`, so every path the README cites must exist in the tree; it does not
assert anything about the README's structure or headings. The rewrite is free
to reorganize and free to cut, but a citation that goes stale fails
`make doc-check`.

**Notes.** Captured 2026-09-01 as an explicitly non-urgent item — the project
owner raised it in passing, not as work to start. Not a `safety` or `science`
class: nothing here is a wrong clinical value, only a badly ordered one.

`docs.github.com` was unreachable during capture — the environment's network
access level did not allow it — so the guidance above was read from the same
article's source in the public `github/docs` repository, through
`raw.githubusercontent.com`, which the default Trusted allowlist covers. The
project owner added `docs.github.com` to the environment's **Allowed domains**
after that capture, but it was **still blocked** when retried on 2026-09-05
(`EGRESS_BLOCKED` from the egress proxy). Do not budget a session on fetching
it. What worked instead was `WebSearch`, which returns the page's text in its
result summary; `raw.githubusercontent.com/github/docs` remains the other
route. The guidance quoted above was re-confirmed that way on 2026-09-05 and
is current.

## Restated against `PL-RM83`, 2026-09-05

`PL-RM83` (decide what `README.md` is for) is closed and this item is
unblocked. Its decision section carries the full reasoning and the standards it
was taken against - read it before writing. In short:

- **Two audiences**, both trained in science, medicine and/or code: **A**, a
  potential contributor interested in anesthesiology and code; **B**, a
  clinician-user with no interest in the code who wants to run the simulator.
  Neither needs anesthesia or programming explained from first principles.
- **Audience B cannot be served yet.** There is no packaged build and
  `ROADMAP.md` item 23 puts packaging out of scope for now, so the README tells
  audience B what the simulator is, what it is not for, and that it is not yet
  distributed as an application - and does not offer them a setup path they
  cannot complete. The `uv` quickstart is written for audience A.
- **The boundary rule:** if changing the model, a constant, or a parameter set
  would make the sentence wrong, it belongs in `docs/MODEL.md`. Everything
  needed to decide and to start stays in the README.
- **Status is capability, not version:** what the simulator models today and
  what it does not, with a relative link to `ROADMAP.md`. No version string, no
  restatement of the milestone table.
- **Links to files in this repository are relative**, per GitHub's own
  guidance - absolute links break in clones.

Two additions from the standards research that the original brief predates:

- **A statement of need opens the document.** JOSS requires a README to "clearly
  state what problems the software is designed to solve and who the target
  audience is." With the audiences now decided this is writable, and it is the
  natural first section - it answers the question the current README defers.
- **Citation and contribution files are a separate item**, `PL-8DDG` (add
  `CITATION.cff`, and decide whether `CONTRIBUTING.md` is warranted yet). Do not
  fold them into this rewrite; link to them if they exist by then.

**Verify note.** `PL-QTN6` (freeze README edits, closed) carries a `verify:`
asserting `blocked-by: PL-RM83` in this file's frontmatter. That line is now
correctly gone, so the command no longer resolves. `PL-JZ1D` (make a closed
item's `verify:` the record it is, and stop it being rewritten) settled that as
normal rather than as a defect: once an item is `done` its command "stops being
a command and becomes the record of an experiment that was performed", and a
`grep '^blocked-by: ...'` against an item file is named there as one of the
shapes written in the expectation of stopping. Nothing runs a closed item's
command and nothing warns that one has gone stale. So it is left exactly as it
is - the hazard that rule identifies is the repair, not the dead command.

## Deferred, 2026-09-05

The project owner deferred this rewrite to `PL-XYRN` (decide when the
repository goes public, and run the human-facing pass immediately before it)
rather than running it now: several documents need the same human-facing
attention, and written to one reader over one week they cohere in a way the
same documents written singly over months do not.

Nothing above is provisional because of that. `PL-RM83` settled the audience,
the `docs/MODEL.md` boundary and the status treatment, and this brief is
restated against them; only the timing moved.

## Released, 2026-09-05 — the repository went public first

The project owner answered `PL-XYRN`: "public today. Will do human facing pass
in the nearish future." The pass no longer runs immediately before the flip, so
the `blocked-by: PL-XYRN` edge is gone and this item is `ready`. It is now the
work that closes a gap a stranger can already see, rather than work done ahead
of one — which raises its value without changing a word of the brief.

**Its `verify:` was silently passing, and is corrected here.** As written it was
`python3 tools/doc_check.py check && ! grep -q 'resolution the numerical method
supports' README.md`. `PL-WB5K` then deleted `README.md` (#366), and `grep` on a
missing file exits 2, which `!` inverts to 0 — so from that merge onward the
command **passed on a tree with none of the work done**, which is the one thing
a `verify:` exists to refuse. Nothing caught it: `docket check --verify` raises
its "already passing" advisory only for items `docket next` is about to offer,
and this item was `blocked`, so it was invisible to exactly the check that would
have found it. Corrected to `python3 tools/doc_check.py check && test -f
README.md && ! grep -q 'resolution the numerical method supports' README.md`,
run on this tree first and observed to exit 1.

**The guard has to come out as part of the work.** `tools/readme_hold_check.py`
is wired into `make check` and fails if a `README.md` exists at the repository
root, so writing one without removing the guard turns `make check` red. That
file and its test are already in this item's `touches`; this is the note saying
why they are there.

## The README no longer exists, 2026-09-05 — PL-WB5K

The project owner deleted `README.md` the same day, rather than leaving it
frozen in place: a frozen document is still read, and sessions were reading it
as instruction while a human reader could not use it. `PL-WB5K` carries the
reasoning; `docs/WORKING_NOTES.md` carries the thread.

**Three things change for this item, and the brief above is otherwise intact.**

1. This is now a **first draft, not a rewrite**. Nothing has to be preserved,
   reorganized or argued out of the document, and the "what gets cut moves to
   `docs/MODEL.md`" half of the brief is already settled — the old text is in
   git history at the commit that removed it, available if a paragraph is
   worth recovering, and required to be read for none of them.
2. The freeze rule under `.claude/rules/` is gone, replaced by
   `tools/readme_hold_check.py`, which fails `make check` and CI while a root
   `README.md` exists. **Delete that script and its two invocations — in
   `Makefile` and `.github/workflows/quality.yml` — in the commit that writes
   the README**, or this item cannot land. Remove its line from
   `docs/ARCHITECTURE.md`'s `tools/` map and delete
   `tests/unit/test_readme_hold_check.py` in the same commit.
3. **Restore `readme = "README.md"` to `pyproject.toml`**, which the deletion
   removed because the `uv_build` backend fails on a missing file. `PL-4MHK`
   (package metadata) wants the `description` field to agree with the README's
   opening paragraph, so the two are worth landing together or in that order.

**Coverage the first draft must not lose.** Two items that existed to correct
the deleted document are dropped into this list rather than left pointing at a
file that is gone. They are floors on the status section, not an outline of it:

- **The playback rate and the chart's case-length time base** (`PL-T67Y`,
  dropped). Two of v0.4.0's three headline changes, and the milestone's stated
  end state - "a learner runs one case from induction to emergence, in
  compressed time they can sit through, on a time base that spans a case" -
  is not describable without them. The playback rate is additionally a **mode**,
  which `docs/MODEL.md` § "Interface boundary" requires on screen at every rate;
  a document that never mentions it leaves a reader to meet a 60× clock
  unprepared. `PL-T67Y`'s brief carries the full case and is worth reading when
  the rewrite reaches this material.
- **The solver-disagreement bound is 2.3e-2 percentage points, not 1.2e-2**
  (`PL-X9HM`, done). The deleted README quoted the wrong row of
  `docs/MODEL.md`'s table when justifying the two-decimal readout. If the new
  document justifies the readout at all, it takes the number from `docs/MODEL.md`
  rather than from the old text in git history, which was wrong for most of its
  life and is a `science`-class error rather than a wording one.

**One addition from the session that reached the same fix independently
(2026-09-06).** Two sessions unblocked this item and repaired its `verify:`
command within the hour, byte for byte - `test -f README.md` ahead of the
`grep`, on the same diagnosis that `PL-WB5K`'s deletion had made `! grep`
succeed on a missing file. Neither saw the other; the duplicate surfaced at the
merge.

That the rot was invisible until the item left `blocked` is the general finding,
and it is `PL-RC0M`: `already_passing` replays only `ready` and
`needs-decision`, so a blocked item's command can stop discriminating and
nothing runs it until whichever pull request unblocks it goes red. Recorded
here because this item is its worked instance, and a session picking this up
should know the command was rewritten under it rather than written for it.
