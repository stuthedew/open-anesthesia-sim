---
id: PL-Y88W
title: CLAUDE.md's first architecture rule, ROADMAP.md's development rules and docs/resident-instructions.md all still say 'independent of Flet', a toolkit the tree no longer imports, so the resident rule names the wrong dependency in every session
priority: P2
effort: S
status: done
classes: defect, infra
feature: worker-instructions
touches: CLAUDE.md, ROADMAP.md, docs/resident-instructions.md
added: 2026-09-16
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -q 'independent of the UI toolkit' CLAUDE.md && grep -q 'independent of the UI toolkit' ROADMAP.md
---

**Problem.** CLAUDE.md's first architecture rule, ROADMAP.md's development rules and docs/resident-instructions.md all still say 'independent of Flet', a toolkit the tree no longer imports, so the resident rule names the wrong dependency in every session

**The three lines, found by `PL-3SQT` while taking Flet out of
`pyproject.toml`.**

- `CLAUDE.md:131` - "Keep scientific/simulation code independent of Flet."
  This is resident: it loads at launch in every session.
- `ROADMAP.md:3317` - "Keep simulation code independent of Flet, wall-clock
  time, filesystem state, ..."
- `docs/resident-instructions.md:136` - names the same invariant as one of the
  ones tested for residency.

**Why it is a capture and not a defect that misleads.** The rule's *intent*
still holds and a session obeying it literally does the right thing, so
nothing is silently wrong; the cost is that the resident instruction names a
package the tree does not import and the enforcement lives elsewhere.
`tools/import_boundary_check.py` is what actually carries it now, in two
shapes - `flet` and `flet_charts` permitted in no module under `src/`, and
`PySide6`, `pyqtgraph` and `numpy` in none under `core/` (`PL-9KDK`).

**The question this is really asking** is whether the rule should name the
current toolkit or stop naming one at all. "Independent of the UI toolkit" is
the invariant, and it is the phrasing that does not go stale on the next port;
`PL-YVM1` adopted the same principle for version numbers - outside
`ROADMAP.md` the port is named by what it is, never by a version.

**Not fixed in `PL-3SQT`'s branch on purpose.** `CLAUDE.md` sits in the cached
prefix of every request, so it is edited in its own session
(`CLAUDE.md` § "Session and tool-use efficiency"), and this is outside that
item's `touches`.

**Why it matters.** Not for the stale name, which misleads nobody - a session
obeying "independent of Flet" literally does the right thing. It matters
because `tools/import_boundary_check.py` cites this rule as the authority for
holding `PySide6`, `pyqtgraph` and `numpy` out of `core/`, and the rule as
written names none of them; and because `docs/resident-instructions.md`, which
is what § "When a resident rule is retired" reads to decide whether a resident
rule still earns its place, records this invariant as having no check behind it
when it now has one. The prose is cosmetic; the ledger is an instrument, and
the instrument is wrong.

**Analysed 2026-09-16 (`PL-3SQT`), and the finding is worse than the three
stale names.** It is three layers, and the third is the one that matters.

*One - the surface.* `CLAUDE.md:131` ("Keep scientific/simulation code
independent of Flet"), `ROADMAP.md:3317` (the same inside the scientific
milestone rules) and `docs/resident-instructions.md:136` (the same, inside the
list of seven invariants that file argues residency for) all name a
distribution `PL-3SQT` has just removed from `pyproject.toml` and that
`tools/import_boundary_check.py` permits in no module under `src/`. Nobody is
misled into a wrong action by it - a session obeying it literally does the
right thing - so this layer alone is cosmetic.

*Two - the citation points the wrong way round.* `import_boundary_check.py`
cites `CLAUDE.md` as the source of this rule three times, and each time
restates it **more correctly than its source does**: "keeps simulation code
independent of the toolkit" (line 22), "keeps simulation code independent of
the UI toolkit, and the interface has left this one" (line 230), "`CLAUDE.md`
keeps simulation code independent of the UI toolkit" (line 257). Since
`PL-9KDK` that tool confines `PySide6`, `pyqtgraph` and `numpy` out of `core/`
**on this rule's authority**, and the cited authority names none of the three.
A reader following the citation to check what the boundary rests on finds a
narrower rule than the boundary enforces.

*Three - the residency ledger undercounts, and it is the ledger the retirement
test reads.* `docs/resident-instructions.md` says of the seven architecture
invariants: "Two of them are *also* enforced by a check
(`tools/import_boundary_check.py` confines the wall clock and the process
generator out of `core/`, and holds Pydantic to one module)". After `PL-9KDK`
that is **three** - toolkit independence joined the wall clock and determinism
- and the parenthetical names the toolkit boundary nowhere. That file is what
§ "When a resident rule is retired" reads to decide whether a rule has a
carrier, so an undercount there is an error in the instrument rather than in
the prose.

**It should not be retired, and this repository has already argued that.**
§ "When a resident rule is retired" (`PL-NJTZ`) would seem to reach it - the
failure mode *is* caught deterministically now. § "What stays resident"
answers it for this exact family and wins: "the checks are cited from
`CLAUDE.md` rather than replacing it: the check fails at `make check`, after
the code is written, and the invariant is cheaper to hold before.
`import_boundary_check.py` also cites `CLAUDE.md` as the source of the rule,
so deleting the line would strand the citation." Two further reasons point the
same way. The check reads `import` statements and nothing else, so it never
sees a `core/` function shaped around display dimensions or a calculation that
moved into a callback - the invariant is wider than its carrier. And the
retirement section's own "Not a licence to rewrite" clause describes this
shape exactly: evidence gone stale while the other triggers have no carrier.

**Name the invariant, not the vendor.** The replacement wording is already
written, three times, in the tool that enforces it: **"independent of the UI
toolkit."** That makes the citation true, and it survives the next port -
which is `PL-YVM1`'s principle for version numbers ("outside `ROADMAP.md` the
port is named by what it is, never by a version") applied to the same failure
one category over.

**Rejected: naming the current toolkit.** "Independent of PySide6 and
pyqtgraph" reintroduces precisely the failure mode being fixed, and is
narrower than the boundary it would describe - `numpy` is in that boundary and
is not a toolkit.

**Done when** the four edits below have landed in one session, because
`CLAUDE.md` sits in the cached prefix of every request:

1. `CLAUDE.md:131` - "independent of Flet" becomes "independent of the UI
   toolkit". Resident cost **+10 characters**, so `make check`'s resident
   total moves from 50570 and the growth instrument reports it; that is the
   instrument working, not a reason to prefer a shorter word.
2. `ROADMAP.md:3317` - the same substitution, inside "Development rules for
   scientific milestones".
3. `docs/resident-instructions.md:136` - the same, in the seven-invariant
   list.
4. `docs/resident-instructions.md` (the paragraph below it) - "Two of them"
   becomes "Three of them", and the parenthetical names the toolkit boundary
   alongside the wall clock, the process generator and Pydantic.

**And a fifth, which is what makes this an audit trail rather than a silent
rewording.** Record it in § "What stays resident" as a dated correction in the
form `PL-X19T` already used there - *"Corrected 2026-09-07, +450 characters,
no routing change"* - naming the character delta and stating that no block
arrived or left. § "When a resident rule is retired" requires a retirement to
be recorded; a correction that changes what a resident rule *says* deserves
the same, and the precedent for the format is in the file.

**Not protected, and no test is owed.** `docket.toml`'s `protected_paths` are
`src/anesthesia_sim/core`, `src/anesthesia_sim/data` and `docs/MODEL.md`;
none of the four files is one. Nothing executable changes, so the `verify:`
command pairs `doc_check.py check` - which passes today and proves the tree is
consistent - with a `grep` for the phrase the work removes. Run 2026-09-16 on
the unedited tree: exit 1.

**Closed 2026-09-16, same session, on the project owner's approval.** All five
edits landed: `CLAUDE.md:131` and `ROADMAP.md`'s scientific-milestone rule now
read "independent of the UI toolkit"; `docs/resident-instructions.md`'s
seven-invariant list reads the same; its check count went from *two* to
*three*, with the toolkit boundary named beside the wall clock, the process
generator and Pydantic; and the correction is recorded in § "What stays
resident" in `PL-X19T`'s dated form. `make check` reports the resident total
at **50580 characters, 10 more than `origin/main`** - the delta the note
states, which is the growth instrument agreeing with its own ledger.

**Done in this session rather than a fresh one, against this item's own
suggestion.** The brief proposed a separate session because `CLAUDE.md` sits
in every request's cached prefix. `CLAUDE.md` § "The queue, and how the project
owner works" overrides that directly: an approved change to how sessions work
is made *before the session ends*, and it names this as "the one case where
editing this file mid-session is right despite the cache cost". The rule won.

**The `verify:` command was rewritten before closing, because the first one
was a bad specification rather than merely unlucky.** It read
`! grep -q 'independent of Flet' ...` across the three files - which forbids
those files from *quoting* the retired wording, and the fifth edit above is a
ledger entry whose job is to quote it. § "When a resident rule is retired"
requires that a later session "be able to find where a rule went instead of
concluding it was dropped", so the record has to carry the old phrase. The
command now greps for the wording the work *adds*, in the two files that carry
the rule, paired with `doc_check.py check` as the shape the `docket` skill
prescribes. Run against `origin/main` with `git archive`: exit 1. Run on this
tree: exit 0.
