---
id: PL-N092
title: Rewrite README as a human-readable introduction to the project
priority: P2
effort: M
status: blocked
blocked-by: PL-RM83
classes: docs, ux
feature: project-introduction
touches: README.md, docs/MODEL.md
added: 2026-09-01
verify: python3 tools/doc_check.py check && ! grep -q 'resolution the numerical method supports' README.md
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
the same day; that takes effect for sessions started afterwards, so a session
working this item can fetch the canonical page and should confirm the summary
above against it rather than assuming it is still current.
