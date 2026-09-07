---
id: PL-1JDD
title: Make the source tier machine-readable so doc_check can decide it
priority: P1
effort: M
status: done
classes: infra, science
feature: model-spec-accuracy
touches: src/anesthesia_sim/data, src/anesthesia_sim/core/parameters.py, tools/doc_check.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/unit/test_parameters.py, tests/unit/test_doc_check.py, tests/reference/test_sevo_patient.py
blocked-by: PL-6Q8N, PL-D6LX
added: 2026-09-03
closed: 2026-09-07
verify: uv run pytest tests/unit/test_parameters.py tests/unit/test_doc_check.py && python3 tools/doc_check.py check && grep -q check_source_tiers tools/doc_check.py && python3 -c "import json,glob,sys; t={'primary','secondary','reference-implementation'}; f=sorted(glob.glob('src/anesthesia_sim/data/**/*.json',recursive=True)); d=[json.load(open(p)) for p in f]; sys.exit(0 if d and all(x['schema_version']==2 and all(s.get('tier') in t and isinstance(s.get('adopted'),bool) for s in x['sources']) and (any(s['tier']=='primary' and s['adopted'] for s in x['sources']) or (x.get('provenance_gap') or '').strip()) for x in d) else 1)"
---

**Problem.** `docs/MODEL.md` § "Source hierarchy" now states which sources may
be named as the authority for a stored value, and nothing enforces it. Every
`sources` entry in every data file is free prose: a citation, a URL, and a
note. A session can add a reference-implementation citation as a file's only
source, and no check in `make check` will say a word — which is how the
current state arose, and how it would arise again.

`tools/doc_check.py` already walks the data files in both directions for
`check_provenance`, so the traversal exists. What it cannot see is the one
thing that matters here, because the tier is not recorded anywhere a program
can read.

**Why it matters.** This is `CLAUDE.md`'s "find the decidable part and put it
in code" applied to the standard that was just written. A prose rule in
`docs/MODEL.md` is re-derived by every session that happens to read it and
skipped by every session that does not; a schema field checked by `make check`
is paid for once. It is also the only part of the provenance problem a tool
can honestly own.

**The decidable half, and where the line falls.** Two things are decidable
without judgment:

1. **Is a tier declared, and is it in the vocabulary?** Exact, mechanical.
2. **Does this data file have at least one source declared `primary`, or an
   explicit recorded gap?** Also exact.

One thing is not, and the check must not attempt it:

3. **Is a citation declared `primary` actually a primary measurement?** That
   needs a human who has read the paper. A tool guessing at it — by author,
   by journal, by a keyword denylist on "Gas Man" — would be authoritative
   and wrong, which `CLAUDE.md` names as worse than no tool. `PL-9T8T`
   reached the same conclusion about checking an author list and correctly
   built nothing.

The difference between 1–2 and 3 is that the tier is *declared* data. The
tool checks that a claim was made and is well-formed; a reviewer checks that
it is true. That is the same split `check_provenance` already runs on: it
decides that a documented key exists and holds the stated value, never that
the value is right.

**Approach.**

1. Add an optional-then-required `tier` field to each `sources` entry, from
   the closed vocabulary `primary`, `secondary`, `reference-implementation` —
   the three tiers `docs/MODEL.md` names. Validate it in the payload models
   in `src/anesthesia_sim/core/parameters.py` beside the existing field
   validation, so a bad tier fails at load rather than at check time.
2. Add an optional top-level `provenance_gap` string to the agent and patient
   payloads: the recorded statement that no primary source has been adopted
   and why. Present it as a value a reader can find, not as a comment.
3. Bump `schema_version` to 2 in all four data files and record the schema
   change in `docs/MODEL.md`.
4. Add `check_source_tiers` to `tools/doc_check.py`: every `sources` entry
   declares a tier in the vocabulary, and every data file either declares at
   least one `primary` source or carries a non-empty `provenance_gap`. Fail
   hard — both are exact rules, and `CLAUDE.md` reserves advisories for
   signals needing context.
5. Standard library only in `doc_check.py`, per the existing constraint: it
   must run in a checkout with no virtualenv, and `json` is stdlib.

**Sequencing.** The gap strings this check demands are the output of
`PL-6Q8N` (the reference adult's eleven physiologic parameters have no
primary source) and `PL-D6LX` (decide whether to adopt primary-literature
partition coefficients). Landing the check first turns `make check` red until
those are written, which is either useful pressure or a broken gate depending
on how long they sit. Recommend landing this **after** `PL-6Q8N`, whose
output is the reference patient's gap statement, and writing the agent files'
tiers as part of `PL-D6LX`'s labeling fix.

**Does it earn its place every run?** Yes, and it goes quiet, which is the
point. Once every current file declares its tiers it is silent until a source
or a data file is added — which is exactly the moment the rule needs to fire
and the moment a session is least likely to have read `docs/MODEL.md`. It is
a schema gate, like the perfusion-fraction sum-to-one constraint, not a
recurring advisory.

**Found.** Project owner, 2026-09-03, on Gas Man being a working example
rather than a citable source. The prose standard was written into
`docs/MODEL.md` in that session; this item is the half of it a tool can hold.

**Done when.** Every `sources` entry in `src/anesthesia_sim/data` declares a
tier from the closed vocabulary; every data file declares a `primary` source
or a `provenance_gap`; `check_source_tiers` fails on a missing or unknown
tier and on a file with neither; `schema_version` is 2 and the change is
recorded in `docs/MODEL.md`; and `make check` passes.


**Built 2026-09-07, with rule 2 tightened from what this brief specified, and
the tightening is the finding.** The rule as written above — *does this data
file have at least one source declared `primary`, or an explicit recorded
gap?* — is satisfied by all four of this project's data files today, with no
gap statement written anywhere, including by
`src/anesthesia_sim/data/patients/reference_adult.json`, whose absent
provenance is the reason this item exists. Every agent file cites primary
measurements it has explicitly *not* adopted (Strum and Eger, Yasuda, Lerman),
and the reference patient cites five of them (Hudgel, Cattermole, Janssen,
Heinonen, Couto da Silva). A check reading the tier alone would have gone green
on all four on its first run and reported them as primary-sourced, which is
`docs/MODEL.md`'s **second** rule arriving as the exact failure it exists to
prevent — a file that looks sourced while the number in it came from somewhere
else.

The brief's rule 2 is a paraphrase of that document's **third** rule, and the
word it drops is the load-bearing one: *"Where no primary source has been
adopted, record that as an open gap."* Adoption is declared data exactly as
the tier is, and just as mechanical to check, so the fix is a second required
field rather than any judgment moving into the tool:

- `tier` on each `sources` entry classifies the **document** — the closed
  vocabulary this brief names.
- `adopted` on each entry says whether this file names that source as the
  **authority for a value it stores**.

Two orthogonal facts, which is what the prose notes in the data files were
already carrying in the phrase "Tier 1, primary measurement, cited but not
adopted". `check_source_tiers` then reads: every entry declares a tier in the
vocabulary and a boolean `adopted`, and a file with no entry that is both
`primary` and `adopted` carries a non-empty `provenance_gap`. Under that rule
the three agent files pass on two genuinely adopted primary sources each
(`mac_awake` and the vaporizer maximum) and `reference_adult.json` requires
the gap, which is the outcome the brief's "Done when" describes and its rule 2
would not have produced.

Nothing else in the approach changed, and the tool still decides nothing about
whether a citation labelled `primary` really is one — item 3 of "the decidable
half" above stands as written. Reverting to the brief's literal rule 2 is one
line in `check_source_tiers` and the `adopted` field can stay; the gap
statements would then be unenforced rather than wrong.

**Three findings captured rather than fixed here**, all surfaced by this work:
`PL-K997` (a second markdown table under `## Parameter provenance` is read as
the provenance table), `PL-FJGY` (the source hierarchy says tier 2 may never
be the authority for a stored value, and `venous_pool_volume_l` adopts one),
and `PL-LM8P` (`.claude/rules/citing-sources.md` counts twenty-six `sources`
entries where there are thirty-five).

One correction rode the data-file edit rather than being filed: the Davis and
Mapleson entry in `reference_adult.json` opened "Tier 2, published model
quantification, CITED BUT NOT ADOPTED" and then said "ADOPTED 2026-09-07 ON
THE PROJECT OWNER'S DECISION" four sentences later. Writing `adopted: true`
onto an entry whose prose says the opposite is the correct-number-wrong-label
failure, so the stale opener went with it.
