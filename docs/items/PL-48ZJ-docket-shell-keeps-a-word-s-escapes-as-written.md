---
id: PL-48ZJ
title: docket.shell keeps a $'...' word's escapes as written, so p $'\x41' is the words p and \x41 to docket and the guard hooks, where bash hands p the word A; latent
priority: P2
effort: S
status: ready
classes: defect
feature: shell-reads-as-bash
touches: subprojects/docket/src/docket/shell.py, subprojects/docket/tests/test_shell.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: a word spelt through an ANSI-C escape is checked by the Bash guards as the word bash passes on, so a prune spelt that way is refused like any other
verify: grep -q 'def test_an_ansi_c_word_reads_as_bash_reads_it_in_the_c_locale' subprojects/docket/tests/test_shell.py && ! grep -qF 'id="PL-48ZJ"' subprojects/docket/tests/test_shell.py
---

**Problem.** docket.shell keeps a $'...' word's escapes as written, so p $'\x41' is the words p and \x41 to docket and the guard hooks, where bash hands p the word A; latent

**Found 2026-10-12** while building `PL-C4XY`'s bash comparison in
`subprojects/docket/tests/test_shell.py`: a `$'...'` word holding a backslash
gave docket a different word from bash's, so the generator draws `$'...'`
without one and the comparison pins today's reading as a known departure
naming this item.

**Reproduced 2026-10-12** against `shell.py` as `main` holds it at `eb520ef4`:

```text
p $'\x41'     bash runs: p A      shell_words: p, \x41     flat_reading: p, \x41
p $'a\'b'     bash runs: p a'b    shell_words: p, a\'b     flat_reading: p, a\'b
p $'a\nb'     bash runs: p with a, a newline and b as one word; both views: p, a\nb
```

Bash replaces each backslash escape in a `$'...'` string as the ANSI C
standard specifies (Bash Reference Manual §3.1.2.4 "ANSI-C Quoting"). The
lexer finds where one ends, an escaped apostrophe included, but keeps the
text between as written (`shell.py`'s "its escapes kept as written, which no
reader decodes"), so the word every reader is handed is not the one bash
passes on.

**Reach.** A guard keyed on a word reads `$'\x41'` as `\x41`. Latent: on
2026-10-12 no workflow step, tracked `.sh` file or fenced sample writes a
`$'...'` with a backslash in it, and `verify:` fields refuse a `$'` at its `$`
(`PL-C45K`).

**Why it matters.** The Bash guards read a command's words through this
lexer, so a word spelt through an escape is not the word they check:
`$'\x67it' fetch --prune` passes `no-prune-guard`, which refuses `git fetch
--prune`, where bash runs `git fetch --prune` (measured 2026-10-12). That is a
gap in a safety-floor guard of `PL-P95F`'s kind, latent because nobody writes
the form, and docket's verify audit and `doc_check` read the same wrong word.

**Which locale, decided at triage, 2026-10-12.** A `\u` or `\U` escape above
0x7f is the one reading that depends on the locale: bash 5.2.21 writes the
character's UTF-8 under `C.UTF-8`, and under `C` and `POSIX` the escape
itself, as `\u00E9` or `\U0001F600`; at or above 0x80000000 it writes
nothing under either (measured 2026-10-12). The fix reads the `C` locale's,
the one `PL-V690`'s locale string is read in and the one these sessions' Bash
calls run in (`locale` printed `LC_CTYPE="POSIX"` on 2026-10-12), rather than
refusing the word, which would leave a guard failing open on a command bash
runs. The comparison draws no such escape, since its bash inherits whichever
locale the run has.

**Not a recurrence of `PL-3Z8B`**, which `docket new` matched on the shared
`touches`: that item is what an arithmetic body is, and this is what one
quoting form's text is. The match is withdrawn because of this paragraph.

**Generator check.** Found by `PL-C4XY`'s comparison, which is what stops a
departure of this kind reaching `main` from now on; read against `bin/docket
generators --misread` on 2026-10-12, it misreads no recorded fact.

**Done when.** A `$'...'` word's text has its escapes replaced as §3.1.2.4
lists them and bash replaces them in the C locale, in both `shell_words` and
`flat_reading`, the comparison draws `$'...'` with escapes in it, and its
known departure row for this is gone.
