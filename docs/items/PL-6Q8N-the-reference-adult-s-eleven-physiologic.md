---
id: PL-6Q8N
title: The reference adult's eleven physiologic parameters have no primary source at all
priority: P1
effort: M
status: needs-decision
classes: science, docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-03
verify: uv run pytest tests/unit/test_parameters.py && python3 tools/doc_check.py check && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); assert d['weight_kg']==70.0 and d['tissue_groups']['vessel_rich']['perfusion_fraction']==0.76 and d['tissue_groups']['fat']['volume_l']==14.5; assert any('Mapleson' in s['citation'] for s in d['sources'])"
---

**Problem.** `src/anesthesia_sim/data/patients/reference_adult.json` stores
eleven numeric parameters — weight 70 kg, alveolar gas volume 2.5 L, venous
pool 1.0 L, alveolar ventilation 4 L/min, cardiac output 5 L/min, tissue
volumes 6 / 33 / 14.5 L and perfusion fractions 0.76 / 0.18 / 0.06 — and
cites exactly two sources for all of them:

1. the Gas Man Workbook and Laboratory Manual (`https://gasmanweb.com/Workbook.pdf`),
   a commercial teaching product's manual; and
2. Meybohm P, et al. 2021, a Gas Man *simulation study* whose description of
   the standard 70 kg model is a description of that product.

Under the source hierarchy now recorded in `docs/MODEL.md`, both are tier 3 —
reference implementation. **Not one of these eleven parameters has a primary
measurement cited anywhere in the tree**, and the file says nothing about the
absence. The three agent files at least record the primary measurement
alongside the stored Gas Man number and state the difference; this file has
no primary tier to record.

**Why it matters.** These eleven values set every time constant in the model.
$`\tau_i = V_i\lambda_{i:b}/Q_i`$ for each tissue group and
$`V_A/\dot V_A`$ for the lung, so they govern the shape of every curve the
simulator draws — the wash-in knee, the three-phase washout, the fat
compartment's slow tail, all of it. They are the parameters a learner is
implicitly being taught, and they are the ones with the weakest provenance in
the project. The partition coefficients, which get the scrutiny, are better
sourced than the physiology they multiply.

The Workbook citation additionally cannot be checked the way a reader checks
a citation: it is a PDF on a vendor site with no DOI, no version, no page
number in the note, and no guarantee of remaining at that URL. A provenance
record that depends on a vendor's web server is not a provenance record.

**The primary lineage exists and is reachable.** The tissue-group compartment
model with lumped vessel-rich / muscle / fat groups, and published volumes
and flows for a standard subject, is Mapleson's, not Gas Man's:

- Mapleson WW. *An electric analogue for uptake and exchange of inert gases
  and other agents.* J Appl Physiol. 1963;18:197-204. PMID 13932730.
  doi:10.1152/jappl.1963.18.1.197 — the original compartment analogue.
- Mapleson WW. *Mathematical aspects of the uptake, distribution and
  elimination of inhaled gases and vapours.* Br J Anaesth. 1964;36(3):129-139.
  PMID 14164256. doi:10.1093/bja/36.3.129
- Mapleson WW. *Circulation-time models of the uptake of inhaled anaesthetics
  and data for quantifying them.* Br J Anaesth. 1973;45(4):319-334.
  PMID 4705482. doi:10.1093/bja/45.4.319 — the title's second half is the
  point: this is the paper that publishes the quantifying data.

**Verified in the capture session only as far as existence.** All three
records were confirmed against PubMed, including journal, volume, pages and
DOI. **None of the three has been read**, and PubMed carries no abstract for
the 1964 or 1973 papers, so whether Mapleson's published volumes and flows
match 6 / 33 / 14.5 L and 76 / 18 / 6 % is exactly the open question this
item exists to answer, not a finding it asserts. Do not write a citation to
any of them into the data file without reading the table it names.

Also worth checking, and not checked here: whether the compartment volumes
trace to a standard-man reference (ICRP Publication 23, *Report of the Task
Group on Reference Man*, or its successor ICRP 89) rather than to a single
anesthesia paper. If they do, that reference belongs in the file too, since
it is where the anatomy actually comes from.

**Where.**

- `src/anesthesia_sim/data/patients/reference_adult.json` — the two `sources`
  entries and their notes. The eleven stored values are read, not changed.
- `docs/MODEL.md` — the "Where this project stands" paragraph under "Source
  hierarchy", which currently records this gap and must be updated when it
  closes.

**Approach.** Sourcing work only. **Change no stored value in this item**;
`data/` is a protected path under `docket.toml` and every one of these eleven
numbers moves a displayed curve.

1. Read Mapleson 1973's quantifying tables and record, per parameter, whether
   the shipped value matches, differs, or is absent.
2. Where it matches, add the primary citation with the tier, the value, and
   the reference conditions.
3. Where it differs, cite the primary source, keep the shipped value, and
   state the difference and why the shipped one was kept — the form the agent
   files already use for their blood:gas coefficients.
4. Where the primary literature has nothing, record "no primary source has
   been adopted for this value" explicitly, which `docs/MODEL.md` now names
   as a legitimate provenance state.
5. Replace or supplement the bare Workbook URL with a citation carrying an
   edition and a section, so the record survives the URL.

**Relationship to `PL-0NQ1` (the reference patient's cited sources disagree
on vessel-rich perfusion).** `PL-0NQ1` reconciles one number — the stored
0.76 against De Wolf's published 75.8 — inside the existing tier-3 framing.
This item asks the prior question, which source these parameters should have
at all. Working this one first subsumes `PL-0NQ1`'s note work; working
`PL-0NQ1` first writes a note that this item then rewrites. Recommend
sequencing this first, or working them together.

**Found.** Project owner, 2026-09-03, stating that Gas Man was provided as a
starting point and a working example rather than as a definitive citation,
and is not acceptable as a primary source. The Mapleson records were located
in that session; the tier framing they are judged against was written into
`docs/MODEL.md` in the same session.

**Narrowed 2026-09-03 — the gap is now recorded; the reading is not done.**
The labeling half landed under `PL-D6LX` (decide whether to adopt
primary-literature partition coefficients). `reference_adult.json`'s two
`sources` notes now name their tier, say that Meybohm et al. adds a journal
name to the same tier-3 provenance rather than a second independent source,
and state in those words that **no primary source has been adopted for any of
the eleven parameters**. The three Mapleson papers are named there as the
primary lineage and explicitly as located-but-unread.

So the finding is no longer that the file is silent about its provenance. What
remains is the substantive half, unchanged: **read Mapleson 1973's quantifying
tables** (and 1963/1964 as needed), and record per parameter whether the
shipped value matches, differs, or is absent. Steps 1-5 under "Approach" stand
as written; step 4's gap statement now exists at file level and becomes
per-parameter as each is checked. Still no stored value may change here.

**Done when.** Every one of the eleven parameters in `reference_adult.json`
carries either a primary citation with its tier and reference conditions, or
an explicit recorded statement that no primary source has been adopted and
the stored value is the Gas Man default; the Workbook citation names an
edition and section rather than resting on a vendor URL; `docs/MODEL.md`'s
"Where this project stands" paragraph matches what the file now holds; and no
stored value has changed.

**Reconnaissance, 2026-09-06 — the reading this item is built on cannot be
done from a session, and the escape hatch that used to cover exactly this
closed the day before.** Nothing in `reference_adult.json` or `docs/MODEL.md`
was changed; this records what was measured, so the next session does not buy
the same discovery twice.

*Reachability, measured against the routes `.claude/rules/citing-sources.md`
prescribes.* All three papers resolve in PubMed and nowhere else:

| Paper | PMID | DOI | Abstract | PMC full text |
| --- | --- | --- | --- | --- |
| Mapleson 1963, J Appl Physiol 18:197-204 | 13932730 | 10.1152/jappl.1963.18.1.197 | none | no |
| Mapleson 1964, Br J Anaesth 36:129-139 | 14164256 | 10.1093/bja/36.3.129 | none | no |
| Mapleson 1973, Br J Anaesth 45:319-334 | 4705482 | 10.1093/bja/45.4.319 | none | no |

`WebFetch` returned `EGRESS_BLOCKED` for `doi.org`, `pubmed.ncbi.nlm.nih.gov`,
`pmc.ncbi.nlm.nih.gov`, `europepmc.org`, `journals.physiology.org`,
`www.sciencedirect.com`, `www.bjanaesthesia.org.uk` and `gasmanweb.com` —
every publisher, index and vendor route this item needs, the one the Workbook
citation itself rests on included. The item's note above is one word
optimistic: it says PubMed carries no abstract for 1964 or 1973, and in fact
**none of the three has one**. So the working route returns title, journal,
volume, pages, DOI and MeSH terms, and for this item that is the whole of it.

PubMed does supply the publisher's article identifiers, which is the one thing
worth carrying forward for whoever can reach a library: the 1973 paper is
`S0007-0912(17)48842-8` and the 1964 paper `S0007-0912(17)53625-9`, which are
the Elsevier PIIs the current British Journal of Anaesthesia archive addresses
those articles by.

*The premise is worth re-examining before that reading is bought.* This item
names the three papers as "the primary lineage" and its Done-when asks each
parameter for "a primary citation with its tier and reference conditions".
Two things now argue a successful reading would not deliver that for most of
the eleven:

- The 1973 title says what the paper is — *circulation-time models ... and
  **data for quantifying them***. A paper that assembles published
  physiological data in order to quantify a model is, under `docs/MODEL.md`
  § "Source hierarchy", a **tier 2 secondary synthesis**: legitimate for
  finding the primary source, never the authority for a stored value. Reading
  it would then yield a tier-2 citation and a pointer to whatever it cites,
  not the tier-1 record asked for here.
- PubMed's MeSH indexing of the 1973 paper is Blood Circulation Time, Blood
  Volume, Cardiac Output, Heart Rate, Pulmonary Circulation, Spirometry and
  Models Biological, with no term for organ size, adipose tissue, skeletal
  muscle or regional blood flow. Indexing is a bibliographic signal rather
  than the paper's contents, so this is evidence and not a finding — but it
  points at circulation times, blood volumes and ventilation as what the
  paper quantifies, and that is not the set of tissue-group volumes and
  perfusion fractions this file needs sourced.

*The route that used to close an item like this is gone.* `docs/references/`
exists for a source a session cannot reach, and the M4 paper was supplied by
the project owner on 2026-09-04 after `www.vldb.org` proved unreachable.
`docs/references/README.md` § "Redistribution" now forbids publisher-copyright
material in this public repository, and two such full texts were removed on
2026-09-06. So the one in-repository route that would close this item is no
longer available and nothing has replaced it. `PL-XJ5P` carries that gap;
it is a hole in the standing guidance rather than this item's to fix.

*Not attempted, deliberately.* Step 5 asks for a Workbook edition and section
in place of the bare vendor URL. Search returned a plausible-looking record —
Philip JH, *Gas Man: Understanding Anesthesia Uptake and Distribution*,
Addison-Wesley, 1984, and a later Med Man Simulations edition — and
`.claude/rules/citing-sources.md` § "A search result is not a source" is
exactly the rule against writing that into a data file. `gasmanweb.com` is
refused, so the edition could not be read at the source and none was recorded.

*State of the `verify:` command,* run this session on the unchanged tree:
`tests/unit/test_parameters.py` passes (38 tests) and `tools/doc_check.py
check` exits 0, so the first two clauses prove the tree healthy; the third —
a `sources` entry whose `citation` names Mapleson — fails with exit 1. It is
a working specification and needs no repair.

**Decision needed.** Either the project owner reads Mapleson
1973's tables through institutional access and reports the values, and this
item is written against that with the route recorded as such; or the item is
re-aimed at what is reachable — for each of the eleven, the tier the stored
value sits in, plus whatever primary measurement of the same quantity PubMed
can actually deliver, recorded alongside with the difference and explicitly
not adopted, which is the pattern the three agent files already use. The
second is answerable from inside a session and the first is not.
