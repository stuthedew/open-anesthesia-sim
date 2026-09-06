---
id: PL-XTMB
title: The Gas Man Workbook citation still rests on a bare vendor URL with no edition, section or DOI
status: untriaged
added: 2026-09-06
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
