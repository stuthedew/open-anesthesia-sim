---
id: PL-RLS3
title: Record the 2026 instruction-file measurements (McMillan, Gloaguen, Anthropic's 200-line target) beside PL-H253, whose own sources PL-YJG1 found overstated
priority: P3
effort: S
status: done
classes: docs
milestone: v0.5.28
touches: docs/resident-instructions.md
blocked-by: PL-5DZ8, PL-8QMD, PL-ZGYX
added: 2026-10-04
closed: 2026-10-18
pr: 1554
payoff: the next proposal to trim the resident set for adherence meets the published measurements beside the project's own count, instead of re-deriving the case from the count alone
verify: grep -qF 'arXiv:2605.10039' docs/resident-instructions.md && grep -qF 'arXiv:2602.11988' docs/resident-instructions.md && grep -qF 'arXiv:2507.11538' docs/resident-instructions.md
---

**Problem.** `PL-H253` (the measurement that session length, not resident-set
size, is the adherence lever) rests on this project's own count - the resident
set was 2.5%-5.6% of the contexts measured - and on three external sources, two
of which `PL-YJG1` (the citation correction) found overstated. Measurements
published since carry the conclusion directly, and nothing in the tree records
them, so the next session proposing a trim for adherence's sake meets a
conclusion standing on a count and a corrected footnote.

**Why it matters.** `docs/resident-instructions.md` is the document a session
reads before reopening the resident set's size, and `CLAUDE.md` § "Session and
tool-use efficiency" says trimming is not the lever. Without the evidence
beside that claim, the argument is re-derived from the count alone each time it
is raised.

**Evidence, read 2026-10-04 from arXiv abstracts and the live Anthropic docs;
the papers' full texts were not read, so the range of file sizes each tested is
not recorded here.**

- McMillan D. "Instruction Adherence in Coding Agent Configuration Files: A
  Factorial Study of Four File-Structure Variables." arXiv:2605.10039, May 2026
  (preprint). 1,650 Claude Code CLI sessions; file size, instruction position,
  file architecture and contradictions produced no detectable effect on
  compliance; within a session, odds of compliance fell about 5.6% per
  additional generated function (OR = 0.944). https://arxiv.org/abs/2605.10039
- Gloaguen T, Mündler-Sasahara N, Müller MN, Raychev V, Vechev M. "Evaluating
  AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
  arXiv:2602.11988, Feb 2026 (preprint). Context files did not generally
  improve task success and raised inference cost by over 20% on average;
  repository overviews were not helpful; files were useful for specifying
  non-standard coding practices. Its outcome is benchmark task success, not
  adherence to a project's own rules. https://arxiv.org/abs/2602.11988
- Jaroslawicz D, Whiting B, Shah P, Maamari K. "How Many Instructions Can LLMs
  Follow at Once?" arXiv:2507.11538, Jul 2025 (preprint). Accuracy degrades
  with instruction count, with a bias towards earlier instructions.
  https://arxiv.org/abs/2507.11538
- Anthropic, "How Claude remembers your project", code.claude.com/docs/en/memory,
  read 2026-10-04: "target under 200 lines per CLAUDE.md file. Longer files
  consume more context and reduce adherence." `CLAUDE.md` was 700 lines that
  day. The vendor's adherence claim and McMillan's null disagree; the cost half
  is not in dispute.

**Done when.** `docs/resident-instructions.md` carries the four sources above
beside `PL-H253`'s entry, each with its verification status and the
disagreement named, and the resident set is otherwise unchanged by this item.

**Recommended.** Record, and trim nothing on this evidence: the project's own
count and McMillan agree that size is not the adherence lever, and the cost half
is already what the routing rule pays for. The number that would reopen the
size question is an adherence failure traced to a rule's position in the file,
which nothing has yet recorded. Apparatus documentation under the 2026-09-25
product focus: captured, not built, until a product session is not blocked by it.

**Held by the generator pause** (triage, 2026-10-04). Recording evidence
beside a conclusion that still holds fixes no defect in what exists: it is
apparatus housekeeping, which `CLAUDE.md` § "What this project is" holds while
any open item carries `generator: live`. On `main` at `8f24fe78`, `bin/docket
generators` marks `PL-R417` still generating, its last slice open in #1353.
Before promoting, check that `bin/docket generators` marks no head "still
generating"; recording it sooner is the owner's call, made by asking
(`PL-6Q9L`).

**Generator check.** One-off. Nothing misread a fact: the conclusion
`docs/resident-instructions.md` records for `PL-H253` still holds, and this
adds the sources published since that carry it. No head's `misread:` states a
fact it touches.

[superseded 2026-10-12: `PL-R417` no longer holds it; the pause it ended restarted with #1419's three live heads, below] **The pause ends with `PL-R417`, closed 2026-10-11 in `#1392`.** `PL-R417` was the last head `bin/docket generators` marked still generating, and with it closed the command marks none, so the pause this waited on ends when `#1392` merges. Nothing else holds it. It stays `blocked` only because `ready` needs a `verify:` command, which `bin/docket set` refuses `ready` without and triage writes beside the work; `bin/docket check` names it ready to promote meanwhile.

[superseded 2026-10-12] **Re-read 2026-10-12 under `PL-2349`**, whose check now refuses a `blocked` item whose every blocker has closed. `PL-R417`'s closure ended the generator pause on 2026-10-11, and `PL-74T0` restarted it the next day: #1419 (`febb37b4`) recorded `PL-5DZ8`, `PL-8QMD` and `PL-ZGYX` as live heads, and `bin/docket generators` marks all three still generating. Nothing else this brief names holds it, so it stays held by the pause, now blocked on those three - though the pause's own test is still `bin/docket generators` marking no head "still generating", not this list. The `verify:` and `payoff:` are written now, so the pull request that ends the pause can promote it in one write. The fault stands: `docs/resident-instructions.md` cites none of the three preprints (it already links the Anthropic memory page, for other claims). `verify:` reads the three arXiv ids, and was seen failing (exit 1) on 2026-10-12.

**Promoted to `ready` 2026-10-12.** `PL-8QMD` closed as the last head
`bin/docket generators` marked still generating, so the generator pause that
held this item has ended (`CLAUDE.md` § "What this project is"), and the
`verify:` and `payoff:` written above stand.
