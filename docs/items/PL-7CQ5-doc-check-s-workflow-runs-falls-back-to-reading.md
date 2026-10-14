---
id: PL-7CQ5
title: doc_check's workflow_runs falls back to reading each script_lines piece alone wherever one shell_words pass cannot read a step's script to its end, so a case construct's arms are read as commands of their own with nothing declined but the one unreadable line, and check_gate_parity compares fragments; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1472
payoff: a workflow step the shared lexer cannot read whole is declined by name, so gate parity never compares a case construct's fragments as commands CI runs
verify: grep -q 'def test_a_step_one_pass_cannot_read_is_declined_whole' tests/unit/test_doc_check.py
---

**Problem.** doc_check's workflow_runs falls back to reading each script_lines piece alone wherever one shell_words pass cannot read a step's script to its end, so a case construct's arms are read as commands of their own with nothing declined but the one unreadable line, and check_gate_parity compares fragments; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`workflow_runs`, new in `#1390`, reads each step's script in one `shell_words`
pass, and where that pass cannot reach the end it re-reads every
`script_lines` piece alone and declines only the piece that fails. A compound
command such as `case` spans lines (POSIX XCU § 2.9.4), so its arms read alone
are fragments, which is `PL-M3M4`'s form.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `bash -n`, which refuses the script below only at the
unterminated quote:

```text
case "$M" in
  check) make check ;;
esac
echo "unterminated
```

The reader gives the commands `check`, `make check` and `esac`, and adds
nothing to `steps`; without the last line it gives `make check` alone. The
fallback is also reached wherever docket's lexer is stricter than bash.
Latent: no workflow reaches the fallback today.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `workflow_runs` over that
script as a step under a `checks` job still yields `check`, `make check` and
`esac`, declines only the unterminated line in `report.declined`, and adds
nothing to `steps`. Every `run:` step in the tracked workflows still reads in
one `shell_words` pass, so none reaches the fallback.

**Why it matters.** `check_gate_parity` holds what CI runs to the Makefile's
gates, so a step read in fragments can make a gate look run by CI - an arm read
as a command - or report a difference that is not a fact, and the answer still
reads as a whole step's. `PL-5M36`'s first bullet (gate parity going on after
a line decline) and `PL-JTP1` (declines a caller cannot drop) name the same
dropped decline from other ends; whichever lands first should say so in the
others.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1390`. Re-read 2026-10-11: latent, so an ordinary item under that closed,
spent head; found live, it would reopen it.

**Done when.** A step whose script one pass cannot read is declined whole
(added to `steps` and reported by name), and the gate-parity check reads
nothing from it; a test pins the form above.
