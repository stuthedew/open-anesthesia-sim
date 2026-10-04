---
id: PL-Z0T3
title: dataclasses.replace() on PatientCompartments rewrites the tissue and venous flows of the original it shares those sub-objects with, because __post_init__ calls _update_blood_flows on them: a running system is left perfusing at the twin's cardiac output while its snapshot reports the old one, until the next step's tissue-sum check halts the run (found reviewing #1350)
status: untriaged
added: 2026-10-04
---

**Problem.** dataclasses.replace() on PatientCompartments rewrites the tissue and venous flows of the original it shares those sub-objects with, because __post_init__ calls _update_blood_flows on them: a running system is left perfusing at the twin's cardiac output while its snapshot reports the old one, until the next step's tissue-sum check halts the run (found reviewing #1350)
