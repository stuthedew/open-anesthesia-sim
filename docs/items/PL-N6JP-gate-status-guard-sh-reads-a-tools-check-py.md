---
id: PL-N6JP
title: gate-status-guard.sh reads a tools/*_check.py invocation as a gate whatever its arguments, so python3 tools/pr_body_check.py --help | head is refused as throwing a verdict away, though --help prints usage and exits 0 with no verdict to lose - met 2026-09-26 in ordinary work, by the PL-61FT design session
status: dropped
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh
added: 2026-09-26
closed: 2026-09-27
reason: Premise false when filed: tools/pr_body_check.py has no --help - its main tests argv only for --anchors, --recover and --compare, so --help runs its default report - and the guard read the command right, as a tools/*_check.py whose status the pipe loses. The fifteen checks whose argparse --help prints usage are refused with no verdict at stake, but that was found by probing, and PL-61FT's bound works a false refusal only when met; the brief says what an exemption would then need.
---

**Problem.** gate-status-guard.sh reads a tools/*_check.py invocation as a gate whatever its arguments, so python3 tools/pr_body_check.py --help | head is refused as throwing a verdict away, though --help prints usage and exits 0 with no verdict to lose - met 2026-09-26 in ordinary work, by the PL-61FT design session

**Reproduced 2026-09-27: the premise does not hold.** `tools/pr_body_check.py`
has no `--help`. Its `main` reads its arguments by hand - today it tests them
only for `--anchors`, `--recover` and `--compare` - and every version since it
was written has (`PL-843V`, `4d70a2c7`, 2026-09-20; `git log -S argparse`
finds none that imported it). So given `--help` it runs its default report: on
`origin/main` at `8e96e1ec`, `python3 tools/pr_body_check.py --help` printed
"pr-body: no squash commit on origin/main lost its body without a recovered
file." and exited 0. The guard read the command right - it runs a
`tools/*_check.py` and pipes the status away, which is what its list calls a
gate - and the exemption the title asks for, resting on `--help` printing
usage, would pass the very command it cites as though it ran nothing.

**What `--help` does across the 18 checks, the same day.** Fifteen parse their
arguments with `argparse`, print their usage and exit 0. Three read `argv` by
hand and have no usage to print: `pr_body_check.py` and `left_behind_check.py`
ignore `--help` and run their report, and `possessive_section_check.py` takes
it for the root to scan and exits 1 on a `FileNotFoundError`. So `--help |
head` on one of the fifteen is refused with no verdict at stake. That is a
false refusal, but one this triage found by probing rather than one a session
met, and `PL-61FT`'s bound works a false refusal when it is met and never
probes for one.

**If one is met.** Exempting `-h` or `--help` ahead of any `--` is sound only
once every `tools/*_check.py` exits 0 on it without checking: the three above
made to, and a test running each check's `--help` to pin it. Without that, a
check that ignores `--help` has its verdict piped away unrefused, and the
`_check.py` suffix is matched precisely so that a check added later is guarded
without anyone remembering to.

**Generator check.** A member of `PL-61FT` already, and the fact misread here
is that head's, what a shell command does when run - misread by the session
that filed it rather than by a guard. That reader is a judgment, not a
function, and triage's reproduce step is what caught it. No new fact, so no
new head.
