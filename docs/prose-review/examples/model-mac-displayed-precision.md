# A passage of `docs/MODEL.md`: the MAC paragraphs of § "Displayed precision"

The owner approved this pair on 2026-11-04 (`PL-J1ZM`).

## Why the after is better

It gives the clinician the three per-agent steps and both display behaviours in 54 words, and moves the derivation and every test name to the developer note.

## Before, 277 words

```text
**The MAC resolution is derived from this one, not chosen beside it.** A MAC
multiple is a percent divided by the agent's own `mac_percent`. So the
resolution above already fixes how finely the quotient is known. Stating a
second resolution independently would mean re-deriving two numbers whenever
this one is re-measured. The rule is one line: **the finest power of ten that
is nowhere finer than the percent resolution converted into MAC.** That
conversion is agent-specific. Converted, 0.01 percentage points is 0.005 MAC
for sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane. So the
binding agent is isoflurane at 0.0083 MAC, and **0.01 MAC** is the finest power
of ten at or above it.
`test_the_mac_resolution_is_derived_from_the_percent_resolution` repeats this
arithmetic for every shipped agent.

The smallest change the MAC readout can show is therefore 0.02 percentage points
of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane, never less than the
percent readout's. The two readouts round separately, so the MAC value can
occasionally change while the percent stays the same. The three per-agent
figures have no test yet (`PL-19W8`).
<!-- not-restated: 0.06 -->

The below-resolution form applies to the MAC line for the same reason it
applies to the percent line, and it matters more there, not less. A
compartment clears 0.01 MAC later than it clears 0.01 percentage points. So
`0.00 ×MAC` beneath a percent line that already shows the compartment filling
would make the two readouts contradict each other. `<0.01 ×MAC` states what is
known, and `test_format_mac_multiple_marks_a_value_below_the_resolution` holds
that form. The derivation test named above re-runs the derivation against
every shipped agent. So adding an agent or changing the percent resolution
fails there rather than silently over-claiming.
```

## After, 120 words

```text
The MAC readout's step, 0.01 MAC, is 0.02 percentage points of sevoflurane,
0.012 of isoflurane and 0.06 of desflurane, never finer than the percent
readout's. The readouts round separately, so the MAC value can occasionally
change while the percent does not. A MAC value above zero but below one step
shows as `<0.01 ×MAC`.
<!-- not-restated: 0.06 -->

**For developers.** Dividing the percent step by the smallest `mac_percent`,
isoflurane's, gives 0.0083 MAC. The MAC step is that, rounded up to a power of
ten. `test_the_mac_resolution_is_derived_from_the_percent_resolution` repeats
this arithmetic for every shipped agent, so a new agent or percent step that
would over-claim fails there.
`test_the_mac_digit_can_move_alone_at_a_rounding_boundary` checks the second
sentence, and `test_format_mac_multiple_marks_a_value_below_the_resolution`
the `<0.01 ×MAC` form. The three per-agent figures have no test yet (`PL-19W8`).
```
