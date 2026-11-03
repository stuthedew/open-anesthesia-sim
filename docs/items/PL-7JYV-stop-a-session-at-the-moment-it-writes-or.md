---
id: PL-7JYV
title: Stop a session at the moment it writes or changes a regular expression in Python, make it consider and research a parser or string method first, and require a written reason where regex is still the right tool
priority: P2
effort: M
status: done
classes: infra
feature: regex-review
touches: tools/regex_check.py, tools/regex_baseline.py, .claude/hooks/regex-guard.sh, .claude/settings.json, tests/unit/test_regex_check.py, tests/unit/test_regex_guard.py, Makefile, .github/workflows/quality.yml, tests/unit/test_tools_portability.py, docs/apparatus.md, docket.toml
added: 2026-11-03
closed: 2026-11-03
pr: 1983
payoff: a session that reaches for a regular expression is stopped at the edit and asked to try a parser, an existing reader or a string method first, and one it keeps carries its reason beside it
verify: grep -q 'def test_writing_a_new_file_with_a_regular_expression_is_refused_with_the_guidance' tests/unit/test_regex_guard.py && grep -q 'regex-guard.sh' .claude/settings.json
---

**Problem.** Stop a session at the moment it writes or changes a regular expression in Python, make it consider and research a parser or string method first, and require a written reason where regex is still the right tool

The project owner asked on 2026-11-03 for a way that, whenever a session wants
to use a regular expression in code, makes it stop, consider whether that is
the best approach, and research the best practice for the task, using the
regular expression only if it still is. Their reason: regular expressions have
caused a lot of issues here and have been used as a crutch.

The record agrees. On 2026-11-03, 60 item files mention a regular expression.
`PL-9HD1` traced three defects to one front-matter pattern, and the dead end
`PL-4S6C` names a second regular expression over one fact as the cause of three
generator heads. The tree held 346 calls that build or apply a pattern, in 73
files, none with a written reason.

**Why it matters.** A regular expression reads text without knowing its
grammar, so it holds only until the first case it was not written for, and
nothing reports the miss. Each such miss here became an item, often several.
A stop at the moment of writing costs one retry, and it is the one moment a
parser or an existing reader can still be chosen cheaply.

**What was built.** The stop is a hook, and a check stands behind it.

1. `.claude/hooks/regex-guard.sh` runs `tools/regex_check.py --screen`
   before every `Edit`, `MultiEdit` and `Write` of a Python file in the
   checkout. It works out what the file would hold after the edit. Where that text holds a call to `re` or `regex` that the file did not
   hold before, with no `regex:` comment giving its reason, the hook refuses
   the edit. The refusal says what to try first. The session then writes the
   code another way, or sends the edit again with the reason beside the call.
2. `tools/regex_check.py` holds the rule and the guidance, so the hook and
   the check cannot disagree. `make check` and CI run it over every tracked
   Python file.
   It catches what the hook cannot see: an edit made through Bash, and a
   Projects thread, where the repository's hooks do not run.
3. `tools/regex_baseline.py` lets the 346 existing calls stand. It only
   shrinks. `PL-3WFF` reviews the six under `src/`, and `PL-8FT2` the rest.

Whether a regular expression is the right tool is a judgment, so no script
makes it. The check enforces only that a session made the judgment and wrote
it down. The guidance it prints asks, in order: what must the code recognise;
does a module here already read this format (`docket.model`, `docket.shell`,
`docket.markdown` and six more, each imported by a test so a rename fails it);
does the standard library have a parser for it; does a string method do it;
and, where the format is unfamiliar, what its specification or the library's
documentation says. Where the answer is still a regular expression, it asks
for `fullmatch` on whole values, one compiled pattern under a descriptive
name, `re.VERBOSE` for long patterns, no nested repetition, and tests of text
the pattern must accept and must refuse.

**Not read, by decision.** `re.escape`, which builds no pattern of its own; a
method on an already compiled pattern, whose compile is read; pytest's
`match=` argument, used about 900 times, where a stop at each new test would
fire without changing a decision; and patterns in shell, Makefiles and
workflow files, of which the shell hooks held none on 2026-11-03. A
`NotebookEdit` is not read either.

**Sources consulted before choosing the guidance.**

- Python documentation, *Regular Expression HOWTO*, introduction and § "Use
  string methods", read from `Doc/howto/regex.rst` on CPython's main branch
  on 2026-11-03: "Sometimes using the re module is a mistake", and "you may be
  better off writing Python code to do the processing; while Python code will
  be slower than an elaborate regular expression, it will also probably be
  more understandable." The same document says to use an HTML or XML parser
  rather than a pattern for those formats.
  https://docs.python.org/3/howto/regex.html
- Michael LG, Donohue J, Davis JC, Lee D, Servant F. Regexes are hard:
  decision-making, difficulties, and risks in programming regular
  expressions. ASE 2019:415-426. doi:10.1109/ASE.2019.00047. A survey of 279
  developers and 17 interviews found regular expressions hard to read, write,
  validate, search for and document.
- Wang P, Stolee KT. How well are regular expressions tested in the wild?
  ESEC/FSE 2018:668-678. doi:10.1145/3236024.3236072. Of 15,096 regular
  expressions in 1,225 Java projects, 17% had any test, and the median tested
  one had two test inputs.
- Davis JC, Coghlan CA, Servant F, Lee D. The impact of regular expression
  denial of service (ReDoS) in practice. ESEC/FSE 2018:246-256.
  doi:10.1145/3236024.3236027. Patterns that can take super-linear time were
  found in more than 10,000 JavaScript and Python modules.

The three papers were read at abstract level, through search results, on
2026-11-03.

**Shape.** The hook first lived in `.claude/hooks/` as Python that imported
the tool. `tests/unit/test_tools_portability.py` refuses a hook that imports
from `tools/`, so the rule moved into the tool behind `--screen`, with a
shell entry point in the protected directory, the shape
`.claude/hooks/pr-body-email-guard.sh` already takes. The tool imports
`docket.vcs` only for the check over the tree. Measured on 2026-11-03, an
edit of a file that is not Python pays about 0.08 s, an edit of the 921-line
`tools/fact_home_check.py` about 0.12 s, and an edit of `tools/doc_check.py`,
the largest at 10,632 lines, about 0.6 s.

**Generator check.** Work the owner asked for. It names no misread fact of
its own. The regular expressions it stops are instances of facts that heads
such as `PL-9HD1` and `PL-4S6C` already state.

**Done when.** A session that writes a regular expression with no reason in a
Python file through `Edit`, `MultiEdit` or `Write` is refused at that edit with
the guidance, `make check` and CI refuse one written any other way, and the
existing calls are listed in a baseline that only shrinks.
