---
id: PL-XF89
title: README's opening says inhaled-anesthetic where the About field and pyproject say volatile - decide which scope word the project's one-line self-description uses
status: untriaged
added: 2026-09-06
---

**Problem.** The project's one-line self-description now exists in three
places and they do not use the same scope word:

| Where | Wording | Written |
| --- | --- | --- |
| `README.md:5` | "A deterministic simulator of **inhaled**-anesthetic uptake and distribution, built for teaching." | `PL-N092`, merged in `#391` |
| GitHub "About" | "PRE-RELEASE Open-source deterministic simulator of **volatile**-anaesthetic uptake and distribution, for education..." | project owner, on or before 2026-09-06 |
| `pyproject.toml` `description` | "A deterministic simulator of **volatile**-anesthetic uptake and distribution, built for teaching..." | `PL-4MHK`, 2026-09-06 |

**Why it matters, and why this is a decision rather than a defect.** Both
words are defensible and they are answering different questions.

- **"Inhaled" names the teaching topic correctly.** "Uptake and distribution
  of inhaled anesthetics" is the standard curriculum heading, and
  `ROADMAP.md` expects nitrous oxide to arrive as a substance rather than as
  a reshaping of the record, so the broader word describes where the project
  is going. It is also the register the owner asked for: a 2026-09-01 draft
  was rejected for framing the project as a volatile-agent simulator when
  "that is the current build rather than the goal"
  (`docs/WORKING_NOTES.md`, "Open: the project's one-line self-description").
- **"Volatile" names what version 0.4.4 actually does.** Only sevoflurane,
  isoflurane and desflurane are modeled, and `README.md`'s own "What it does
  not simulate" leads with "Nitrous oxide, any second gas, and concentration
  or second-gas effects". A package `Summary` describes the artifact carrying
  it, so on that field the narrower word is the accurate one - which is why
  `PL-4MHK` used it, and why that item could not satisfy its own "agrees with
  `README.md`'s opening" and "agrees with the About description" at once.

**The decision.** Either the three agree on one word, or the divergence is
deliberate and gets stated once - README and About describe the project
(topic and destination), `pyproject.toml` describes the release (what 0.4.4
models). The second reading is coherent and is what the tree currently
implements by accident rather than by decision.

**Where.** `README.md:5`; `pyproject.toml`'s `[project] description`; the
GitHub repository "About" field, which no session can edit and which the
project owner sets under Settings.

**Also in scope, and independent of the word.** The About field spells it
"an**ae**sthetic" while the package name (`anesthesia-sim`), the module
(`anesthesia_sim`), the repository name and every document use the US
spelling. That is a one-word inconsistency in the most-read sentence the
project has.

**Notes.** `tools/doc_check.py` cannot decide this agreement and should not be
asked to: the About text is not in the tree, and the tool is standard-library
only and runs offline in a bare checkout. `PL-4MHK` records the same finding.
