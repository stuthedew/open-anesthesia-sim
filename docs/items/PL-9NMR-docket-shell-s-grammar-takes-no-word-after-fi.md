---
id: PL-9NMR
title: docket.shell's grammar takes no word after fi, done, esac, }, ]], a closing )) or a subshell's ) for a command's head, where bash reads a reserved word, so if [[ a ]] then case ... inside a $( ) closes the substitution at its pattern's parenthesis and if (( 1 )) then ((1 + is cut at its newline; latent
status: untriaged
feature: one-answer
added: 2026-10-12
---

**Problem.** docket.shell's grammar takes no word after fi, done, esac, }, ]], a closing )) or a subshell's ) for a command's head, where bash reads a reserved word, so if [[ a ]] then case ... inside a $( ) closes the substitution at its pattern's parenthesis and if (( 1 )) then ((1 + is cut at its newline; latent

**Found 2026-10-12 building `PL-0CJC`**, which reads a head past what
`function`, `time` and `coproc` take. bash 5.2.21 reads a reserved word after
any token its parse.y's `reserved_word_acceptable` names, and that list also
holds the closing words - `fi`, `done`, `esac`, `}`, `]]` (`COND_END`), a
closing `))` (`ARITH_CMD`) and any `)` - where `docket.shell._Grammar` takes no
head, so a `then`, `do` or `esac` written straight after one, with no `;`, is
read as a plain word, and whatever it opens is lexed as words too.

**Reproduced 2026-10-12** on the branch carrying `PL-0CJC`, against bash
5.2.21, which runs each as one command:

```text
x=$(if [[ a ]] then case b in b) echo in;;
esac; fi)
echo "[$x]"
```

bash prints `[in]`; `script_lines` gives three pieces, the first ending after
`echo in;;`, because the `case` after `]] then` is read as a word and its
pattern's `)` closes the `$(`. `if (( 1 )) then ((1 +` over `2)) && echo
arith; fi` is cut after the `+`, and `if (true) then [[ a == a &&` and
`if { true; } then [[ a == a &&` over `b == b ]] ...; fi` after the `&&`.
`case a in a) while false; do :; done esac` runs in bash, where docket reads
the `esac` as a word and leaves the `case` open; no reader is misled by that
one alone, since a `)` in a clause closes no pattern.

Latent: a `git grep` outside `docs/items/` finds none of these shapes in a
script, a workflow step or a fence.

**Why it matters.** The same as `PL-0CJC`'s: `docket.shell` is the one reader
docket's verify audits, `tools/doc_check.py`'s workflow readers and the Bash
guards share (`PL-JNYL`), so a command it cuts short is misread by all of them
at once, and every piece reads as complete.

**Generator check.** A member of `PL-R417`, beside `PL-0CJC`: the reader takes
a physical line for a statement its format continues. Latent, so an ordinary
item under that closed, spent head.

**Done when.** The word after each closing word is read as a command's head,
as bash's `reserved_word_acceptable` reads it, and each shape above is a shell
case in `subprojects/docket/tests/test_shell.py` holding docket to bash's
reading.
