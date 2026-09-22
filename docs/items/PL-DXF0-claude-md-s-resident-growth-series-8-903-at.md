---
id: PL-DXF0
title: CLAUDE.md's resident-growth series (8,903 at inception, 49,991 on 2026-09-13, 60,199 on 2026-09-19) is now on a different basis from what make check prints: PL-44DG added the SessionStart digest and skill descriptions to the total, so a reader comparing the series against a fresh reading over-reads about 4,900 characters as growth
priority: P3
effort: S
status: ready
classes: infra
feature: resident-gauge-basis
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-21
payoff: the resident-growth series is compared like with like, instead of about 4,700 characters of basis change being read as instruction growth
verify: grep -q 'def test_resident_line_names_the_instruction_file_subtotal' tests/unit/test_doc_check.py
---

**Problem.** CLAUDE.md's resident-growth series (8,903 at inception, 49,991 on 2026-09-13, 60,199 on 2026-09-19) is now on a different basis from what make check prints: PL-44DG added the SessionStart digest and skill descriptions to the total, so a reader comparing the series against a fresh reading over-reads about 4,900 characters as growth

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `python3 tools/doc_check.py check` prints a
resident total of 71,212 characters. Of that, 625 are the docket skill's
description and 4,070 are the SessionStart digest's output: 4,695 characters on
a basis that did not exist when the series was taken. The instruction files
alone come to 66,517. The series itself is at `CLAUDE.md` line 454.

**Why it matters.** The series is what makes resident growth a decision rather
than a default. `CLAUDE.md` asks every edit to the resident set to name what it
pays with, and argues its growth rate from these numbers. Compare today's
printed total against the 2026-09-19 figure and you read 11,013 characters of
growth, of which 4,695 is the change of basis. Nothing flags the mismatch,
because each number is right on its own basis.

**Done when.** The gauge's line names the instruction-file subtotal alongside
the whole payload and says which one `CLAUDE.md`'s series is taken on. A test in
`tests/unit/test_doc_check.py` holds it. **Triage chose this over restating the
series in `CLAUDE.md`.** It keeps the series comparable on every future reading
at no resident cost, where an edit to the series would have to be repeated at
each change of basis.
