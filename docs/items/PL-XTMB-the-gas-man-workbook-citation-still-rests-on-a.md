---
id: PL-XTMB
title: The Gas Man Workbook citation still rests on a bare vendor URL with no edition, section or DOI
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.6
touches: src/anesthesia_sim/data/patients/reference_adult.json, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-06
pr: 410
verify: uv run pytest tests/unit/test_parameters.py && python3 tools/doc_check.py check && python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json')); s=d['sources']; assert any('Appendix B' in x['citation'] and 'page 168' in x['citation'] for x in s); assert any('Lowe and Ernst, 1981' in x['note'] for x in s); assert d['tissue_groups']['fat']['volume_l']==14.5"
---

**Problem.** `src/anesthesia_sim/data/patients/reference_adult.json` cites "Gas
Man Workbook and Laboratory Manual. Default Options: Patient Defaults." against
`https://gasmanweb.com/Workbook.pdf`. That is the tier-3 source of all eleven
stored values, and it names no edition, no version, no page and no DOI. A
provenance record that depends on a vendor keeping one PDF at one URL is not a
provenance record: when the file moves or the edition changes, nothing in this
repository says which document the numbers came from.

**Why it matters.** It is the *only* source for every value in the reference
patient, so it is the single citation in the project whose loss would leave
eleven numbers with no stated origin at all. `PL-6Q8N` reduced the harm - five
of the eleven now carry a reachable measurement cited alongside - but reduced
is not removed, and none of those five is the source of a stored value.

**Why `PL-6Q8N` did not do it.** It was step 5 of that item's Approach and is
the one part that could not be done from a session. `gasmanweb.com` is refused
by the egress proxy (measured 2026-09-06), so the document could not be opened
to read its own title page. Search returned a plausible record - Philip JH,
*Gas Man: Understanding Anesthesia Uptake and Distribution*, Addison-Wesley,
1984, and a later Med Man Simulations edition - and
`.claude/rules/citing-sources.md` § "A search result is not a source" is
precisely the rule against writing that into a data file. Nothing was recorded
rather than something unverified.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json`, the first
`sources` entry, which currently states the absence explicitly.

**Done when.** The citation names the edition and the section it was read
from, taken from the document itself rather than from a search summary - which
needs either a session that can reach the vendor, or the project owner reading
the title page and reporting it. Recording that no citable edition exists is
also an acceptable close, provided somebody looked.

**Closed 2026-09-06, and it turned out to be much more than a citation tidy.**
The project owner supplied the Workbook's front matter and its appendices and
bibliography as PDFs the same day, which is the route the item said it would
need. Read at the source; the repository does not hold them, because they are
publisher-copyright material and it is public.

*The citation now names what it should.* Philip JH, *Gas Man(R) Workbook and
Laboratory Manual*, Med Man Simulations, Inc., Chestnut Hill MA; document dated
2012-05-16 with the preface dated October 2010; **Appendix B, "The Gas Man
Approach", Model Parameters table, page 168**. The author, publisher and dates
come from the cover, the PDF's own `/Title` and `/Author`, and the signed
preface.

*The old citation pointed at the wrong section.* It named "Default Options:
Patient Defaults", which is page 183 in Appendix E: a description of the
interface controls that carries none of the values. The numbers are in
Appendix B.

*The file was wrong about its own contents, and that is the finding.* This note
asserted, until today, that the Workbook was "the source of every stored value
in this file". The table supplies **seven of the eleven**. Present and exactly
equal: `alveolar_gas_volume_l` 2.5, the three tissue volumes 6.0/33.0/14.5 and
the three flow fractions 0.76/0.18/0.06. `default_cardiac_output_l_min` 5.0
appears only as the sum of the flow column (3.80 + 0.90 + 0.30). `weight_kg`
and `default_alveolar_ventilation_l_min` are interface defaults the supplied
chapters state no number for. And `venous_blood_volume_l` 1.0 **is not in the
table at all** - its `Blood` row reads 5.00 L - which is now `PL-3YZW`.

*The lineage is Lowe and Ernst, not Mapleson.* The note beneath the table
reads, in these words, "Values for volume, flow and relative flow are taken
from Lowe and Ernst, 1981", its reference 23 being *The Quantitative Practice
of Anesthesia: Use of Closed Circuit*, Williams & Wilkins. The Workbook
attributes nothing to Mapleson, whose papers this file named as its primary
lineage until `PL-6Q8N` removed the framing earlier the same day - on the
strength of their titles, never having been opened. Lowe and Ernst is recorded
as located and unread, with nothing claimed about its contents, which is the
discipline the Mapleson entries were removed for failing. `PL-7HDS` carries
reading it.

*Also captured, not worked here:* `PL-ZP7Z` - the same table's notes attribute
the volatile partition coefficients to Yasuda, Targ and Eger (as the
`Anesthesiology 69:A615` abstract, not the 1989 *Anesthesia & Analgesia*
paper), and sevoflurane's a sentence later to "the package insert and Abbott
data", neither of which is what the agent files say.

*Route and depth,* per `.claude/rules/citing-sources.md`: read at full-text
depth from a copy supplied by the project owner. That is a third route the rule
does not describe - it names PubMed and `docs/references/`, and this document
can be in neither - which is `PL-XJ5P`'s gap, now with a worked instance.

**Docs swept:** `src/anesthesia_sim/data/patients/reference_adult.json` (the
Workbook entry rewritten to carry both the citation and, as a quotation from
it, the Lowe and Ernst attribution - deliberately not a `sources` entry of its
own, since an unread document given its own citation line is the Mapleson
failure again, and the schema's non-empty `url` requirement made the point by
refusing the empty one), `docs/MODEL.md`
§ "Parameter provenance" (the Mapleson paragraph replaced with the read
lineage and the seven-of-eleven correction). The provenance table's eleven rows
are unchanged: no value and no key changed, and `make doc-check` confirms it.
