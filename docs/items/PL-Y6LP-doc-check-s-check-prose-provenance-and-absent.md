---
id: PL-Y6LP
title: doc_check's check_prose_provenance and _absent_paths read a marker only where it is a line of its own, so one written at a sentence's end or inside a block quote is read as nothing beside a well-formed marker, and a stale value in docs/MODEL.md prose passes the provenance check; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
closed: 2026-10-18
pr: 1527
payoff: a provenance marker written at a sentence end or in a block quote is held to its data file or refused by name, so a stale clinical value in docs/MODEL.md cannot pass beside a well-formed marker
verify: grep -q 'def test_a_marker_at_a_sentence_end_or_in_a_block_quote_is_read_or_refused' tests/unit/test_doc_check.py
---

**Problem.** doc_check's check_prose_provenance and _absent_paths read a marker only where it is a line of its own, so one written at a sentence's end or inside a block quote is read as nothing beside a well-formed marker, and a stale value in docs/MODEL.md prose passes the provenance check; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/doc_check.py`. `check_prose_provenance` holds a value stated in
`docs/MODEL.md` prose to the stored entry its provenance marker names, and
`_absent_paths` reads the marker that excuses a deleted path. Both find a marker
only where the HTML comment is its whole line. `docs/MODEL.md` writes each one
that way today, but CommonMark 0.31.2 reads the same comment as inline raw HTML
at a sentence's end (§ 6.6) and inside a block quote as an HTML block in it
(§ 5.1), and nothing refuses either form.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15, with
a scratch `docs/MODEL.md` stating a blood/gas partition coefficient of 0.69
where the named entry holds 0.65. A marker on its own line under the sentence
was refused for the mismatch, the control. Written at the sentence's end, or
inside a block quote, with no other marker in the file, the check failed for
finding no marker at all; beside one well-formed marker elsewhere in the file,
it passed. Latent: every tracked marker is a line of its own.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, against the test suite's
scratch `docs/MODEL.md` with prose stating 0.9 where the entry holds 0.5: the
marker on its own line is refused for the mismatch; at the sentence's end, or
inside a block quote, beside the file's well-formed marker, the check passes;
at the sentence's end with no other marker, it fails for finding none. Still
latent: every marker outside a code span stands on a line of its own.

**Why it matters.** A clinical value in the model specification that no longer
matches its stored source is the case this check exists for, and the inline
form passes it in silence.

**Generator check.** Not a member of `PL-R417`: the marker is one line, never
split; the fault is which lines are asked whether they hold one.

**Done when.** Both readers find a marker wherever CommonMark reads the
comment, or `doc_check` refuses a marker in any other position by name, pinned
by a test for the inline and block-quoted forms beside a well-formed marker.
