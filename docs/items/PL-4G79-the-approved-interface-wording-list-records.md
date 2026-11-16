---
id: PL-4G79
title: The approved interface wording list records only default runs, so a string shown only after a setting change, with a bookmark or price, or in a halt or failure notice is held by no approved list
status: untriaged
added: 2026-11-11
---

**Problem.** The approved interface wording list records only default runs, so a string shown only after a setting change, with a bookmark or price, or in a halt or failure notice is held by no approved list

**Found by** `PL-86VL`'s blind review, 2026-11-11. The approved list records
the default run of each agent at fixed times. The notices most likely to carry
a sentence a clinician acts on, such as a halt after a failed Reset
(`PL-MVCF`), a refused setting, or a failure that withholds values, appear
only after an event, so no approved list holds their wording. The forbidden-
phrase checks in `tests/integration/simulation_view/` still apply to
them. Recording them needs a way to bring each state about in the test, as
`tests/integration/test_failed_start_over.py` does for the halt.
