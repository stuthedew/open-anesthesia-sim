---
id: PL-YCWZ
title: Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for
status: untriaged
feature: qt-port
added: 2026-09-10
---

**Problem.** Add headless rendering tests over the real Qt interface, which is what PL-2QMK has been waiting for

**`v0.5.1`'s Required scope, item 6, and it closes `PL-2QMK`.**

`PL-2QMK` records that no session in the web container can visually confirm a
chart change, because Flet's web renderer fetches Flutter assets the egress
proxy denies. That is what blocks `PL-90Y6`, `PL-3355`, `PL-W8DQ`, `PL-GVXP`
and the rest of `presentation-safety`.

**The capability is already demonstrated rather than assumed.**
`spikes/qt/qt_spike.py --screenshot` writes a PNG of the running interface in
that very container, with a dial change drawn in it, under
`QT_QPA_PLATFORM=offscreen`. This item is what turns that from a flag into
tests: assertions over the real interface at a fixed size, so a presentation
change can be reviewed by a session rather than only by the project owner.

**What such a test may assert is the design question.** A pixel-exact snapshot
is brittle across Qt versions and font stacks; what is worth asserting is
nearer to "the alveolar trace is drawn", "the MAC-awake band sits between these
two axis values", "no trace leaves the plot". Decide that before writing many.
