---
paths:
  - "/docs/MODEL.md"
  - "/docs/INTERFACE.md"
  - "/README.md"
  - "/docs/ARCHITECTURE.md"
  - "/docs/interface-provenance.md"
  - "/docs/machine-abstraction.md"
  - "/docs/machine-survey.md"
  - "/docs/references/**"
  - "/ROADMAP.md"
  - "/docs/consultant-brief.md"
---

# Who reads each document

`.claude/rules/plain-writing.md` says how to write for a reader, and names the
readers of the texts a session writes without opening a document first. This
table names the readers of each document. It loads when a session opens one of
them, which is before the session writes in it (`PL-7YHK`).
`tools/new_prose.py` reads both tables.

| Kind of text | Reader | What they know | What they do not know | What they will do with it |
| --- | --- | --- | --- | --- |
| `docs/MODEL.md` | A clinician or educator | Anesthesia pharmacology and physiology. | Numerical-methods terms such as "operator split", software terms, e-notation such as "4e-4", and this repository's own names. | Decide whether to trust a displayed value, or learn how the simulation works. |
| `docs/MODEL.md` | A developer, or someone who forked the project | Python, and the basics of anesthesia. | Numerical-methods terms such as "first-order method", and this repository's own names. | Change a value or an equation for a goal of their own. |
| `docs/INTERFACE.md` | A contributor who changes the interface | Anesthesia, Python and software development. | This repository's own names and history, and decisions taken in sessions they did not see. | Find what the interface must show and do before changing it, and the test that checks each requirement. |
| `README.md` | An educator or trainee in anesthesiology or critical care | Anesthesia and critical care. | Software terms, numerical-methods terms, and this repository's own names. | Decide whether to use the simulator, then install it and run a case. |
| `README.md` | A contributor who knows both anesthesia and code | Anesthesia, Python and software development. | This repository's own names and history. | Decide whether to work on the simulator, then set it up. |
| `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md` and `docs/machine-survey.md` | A contributor who knows both anesthesia and code | Anesthesia, Python and software development. | This repository's own names and history, and the outside designs and machines it studied. | Find where a change belongs, and what it must keep. |
| `docs/machine-survey.md` and `docs/references/` | A clinician or educator | Anesthesia pharmacology, physiology and equipment, and how to read a paper's methods. | Software terms, and this repository's own names. | Check a stored value, or a difference between machines, against its published source. |
| `ROADMAP.md` | The project owner, or a contributor deciding what to build next | Anesthesia, critical care, and what the project is for. | The internal names of tests, checks and tools, and decisions taken in sessions they did not see. | Decide what a release holds and what it leaves out. |
| `docs/consultant-brief.md` | An outside reviewer: a new session given the text below the brief's dividing line as its first message | Python, anesthesia and software review. | This repository, its history and its rules. | Review the repository critically, and report what it finds. |
