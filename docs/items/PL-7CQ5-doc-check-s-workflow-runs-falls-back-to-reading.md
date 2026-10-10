---
id: PL-7CQ5
title: doc_check's workflow_runs falls back to reading each script_lines piece alone wherever one shell_words pass cannot read a step's script to its end, so a case construct's arms are read as commands of their own with nothing declined but the one unreadable line, and check_gate_parity compares fragments; latent
status: untriaged
feature: one-answer
added: 2026-10-10
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

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1390`.

**Done when.** A step whose script one pass cannot read is declined whole
(added to `steps` and reported by name), and the gate-parity check reads
nothing from it; a test pins the form above.
