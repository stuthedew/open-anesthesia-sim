---
id: PL-TKRT
title: reference_adult.json carries no sources entry for ICRP Committee II 1960, the document its longest provenance chain terminates at, because the schema requires a resolvable url and none could be verified from a session container
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json
added: 2026-09-10
closed: 2026-09-10
verify: uv run pytest tests/unit/test_parameters.py && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); assert any('icrp.org' in s['url'] for s in d['sources'])"
---

**Problem.** reference_adult.json carries no sources entry for ICRP Committee II 1960, the document its longest provenance chain terminates at, because the schema requires a resolvable url and none could be verified from a session container

**Why it matters.** The `sources` array is the machine-checked half of this
file's provenance: `make check` validates every entry's `tier`, `adopted` flag
and locator, and a reader auditing where a stored number came from reads that
array rather than the prose. ICRP Committee II's Table 8, page 151, is where
the reference patient's longest chain terminates — Gas Man (tier 3) to Lowe and
Ernst (tier 2) to this — and it is the one link in that chain the array does
not name. `docs/MODEL.md`'s "Parameter provenance" carries the reading in full
and the Lowe and Ernst entry points at it, so nothing is lost; what is missing
is the machine-readable record.

**What happened, 2026-09-10 (`PL-LT51`).** The entry was written and then
withdrawn before it was committed. `_SourcePayload.url` is a required
`NonEmptyString` and every one of the twelve entries in the file resolves to a
real identifier — ten DOIs, a PubMed Central article, a publisher PDF, and
`https://search.worldcat.org/oclc/6665746` for the Lowe and Ernst monograph,
which is the shape a book takes here. ICRP Publication 2 predates *Annals of
the ICRP* and so has no DOI, and no OCLC number for it was in hand. Direct
HTTPS to `www.icrp.org`, `journals.sagepub.com` and `doi.org` each returned
nothing through the egress proxy, so nothing could be checked.

**A guessed URL was the one thing that must not happen.** `.claude/rules/
citing-sources.md` forbids supplying a citation element from memory, and a
locator that does not resolve is worse in a provenance record than an absence
that says so: the absence is visible, the wrong link is not.

**What it needs, and it is one line.** A resolvable identifier for
*Recommendations of the International Commission on Radiological Protection.
Report of Committee II on Permissible Dose for Internal Radiation. Pergamon
Press, Oxford, 1960* — an OCLC number for a WorldCat link, matching the Lowe
and Ernst precedent, or the ICRP's own publication page if it lists Publication
2. Then the entry goes back, with the note already drafted in `docs/MODEL.md`.

**Done when.** `reference_adult.json`'s `sources` array names ICRP Committee II
1960 with a locator someone has opened, and the two sentences in that file
recording the absence come out.

## Outcome, 2026-09-10: the project owner supplied the locator

`https://www.icrp.org/publication.asp?id=icrp%20publication%202` — the
publication's own ICRP catalogue page, sent within minutes of the gap being
raised, and not opened from a session container, which cannot reach
`www.icrp.org`. The entry is in `reference_adult.json` with that `url`, tier
`secondary`, `adopted: false`, and the note says where the locator came from
and that it was not opened here.

**The item existed for about ten minutes and is still worth keeping.** It
records that the entry was withheld rather than filled from memory, which is
the decision the `sources` array's value depends on and the one thing a later
reader could not otherwise tell — a locator that resolves and a locator that
was guessed look identical once written.

**The `verify:` command was run both ways**: exit 1 with the entry withdrawn,
exit 0 with it restored.

**One thing this leaves for `PL-LT51`.** ICRP Publication 2 predates *Annals of
the ICRP* and has no DOI, so the locator is a catalogue page rather than the
document. Nobody on this project has opened the report beyond pages 150 and
151, and whether Table 8 carries sources of its own elsewhere in it is still
unknown.
