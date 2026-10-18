---
id: PL-4RL2
title: The Gas Man simulation study at PMC7943506 is cited as Meybohm P, et al., J Clin Monit Comput 2021;35:897-908 in the reference adult, the three agent files, the circuit file, docs/MODEL.md and tests/unit/test_parameters.py, but PubMed gives it as Weber J, Schmidt J, Wirth S, Schumann S, Philip JH, Eberhart LHJ, J Clin Monit Comput 2021;35(2):343-354 (PMID 32067148), so a reader following the citation cannot find the paper by its authors or pages (found working PL-SWY5)
priority: P1
effort: S
status: done
classes: science, docs
feature: provenance
milestone: v0.5.27
touches: src/anesthesia_sim/data/patients/reference_adult.json, src/anesthesia_sim/data/agents/desflurane.json, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/machines/reference_circle_system.json, docs/MODEL.md, tests/unit/test_parameters.py, .claude/rules/sources-and-docstrings.md, ROADMAP.md
added: 2026-10-18
closed: 2026-10-18
pr: 1531
payoff: a reader following the citation of the Gas Man study at PMC7943506 finds the paper by its real authors and pages
verify: grep -qF 'Weber J, Schmidt J, Wirth S' src/anesthesia_sim/data/patients/reference_adult.json && ! grep -qi 'meybohm' docs/MODEL.md
---

**Problem.** The Gas Man simulation study at PMC7943506 is cited as Meybohm P, et al., J Clin Monit Comput 2021;35:897-908 in the reference adult, the three agent files, the circuit file, docs/MODEL.md and tests/unit/test_parameters.py, but PubMed gives it as Weber J, Schmidt J, Wirth S, Schumann S, Philip JH, Eberhart LHJ, J Clin Monit Comput 2021;35(2):343-354 (PMID 32067148), so a reader following the citation cannot find the paper by its authors or pages (found working PL-SWY5)

**Evidence.** PubMed's record for PMID 32067148, read 2026-10-18, maps to
PMC7943506 and doi:10.1007/s10877-020-00477-z. It gives the title "Context-
sensitive decrement times for inhaled anesthetics in obese patients explored
with Gas Man®", the journal J Clin Monit Comput, volume 35, issue 2, pages
343-354, and six authors, none named Meybohm. PMC's XML record of the article
(E-utilities efetch, same day) gives the same authors. The tree cited it as
"Meybohm P, et al. ... 2021;35:897-908" in
`src/anesthesia_sim/data/patients/reference_adult.json`, as "Meybohm et al."
in the three agent files' De Wolf notes, in
`src/anesthesia_sim/data/machines/reference_circle_system.json`, in three
places in `docs/MODEL.md`, in `tests/unit/test_parameters.py`'s docstring, in
`.claude/rules/sources-and-docstrings.md` and in two live passages of
`ROADMAP.md`. The title, the journal and the PMC7943506 link were right in
every case, so every reading the tree records is of the right paper.

**Why it matters.** A citation is how a reader checks a value. A reader
searching for "Meybohm 2021" or for pages 897-908 does not find this paper,
and the tree uses it as the second published description of Gas Man's
parameter set beside De Wolf et al. 2012, so its MAC and partition coefficient
comparisons could not be checked from the citation alone.

**Done when.** Every live citation of the paper names Weber et al. and the
pages 35(2):343-354, and the reference adult's entry records that it was cited
under the wrong authors and pages until the correction. Closed item briefs,
release notes and pull request bodies are records of their day and are left
as written.

**Generator check.** One-off: the citation was written once with the wrong
first author and pages, and every later mention copied it. The fact misread is
this paper's authorship, which no other item concerns.

**Closed 2026-10-18.** The reference adult's citation now reads "Weber J,
Schmidt J, Wirth S, Schumann S, Philip JH, Eberhart LHJ. ... 2021;35(2):343-354",
and its note opens by recording that it was cited as Meybohm P, et al.,
2021;35:897-908 until this correction. Every other live mention in the files
this item names now says Weber et al.
