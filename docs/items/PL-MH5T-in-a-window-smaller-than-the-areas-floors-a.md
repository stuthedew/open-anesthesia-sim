---
id: PL-MH5T
title: In a window smaller than the Areas' floors, a press on a border and a zero-pixel move still rewrite the stored fractions and emit layout_changed, because _drawn_position maps the pointer through settle's apportionment while Qt draws the frames at their larger minimum sizes; reproduced as root fractions (0.4026, 0.4647, 0.1328) becoming (0.4026, 0.3492, 0.2482) with the screen unchanged (found reviewing #1880)
status: untriaged
feature: area-layout-sizing
added: 2026-10-27
---

**Problem.** In a window smaller than the Areas' floors, a press on a border and a zero-pixel move still rewrite the stored fractions and emit layout_changed, because _drawn_position maps the pointer through settle's apportionment while Qt draws the frames at their larger minimum sizes; reproduced as root fractions (0.4026, 0.4647, 0.1328) becoming (0.4026, 0.3492, 0.2482) with the screen unchanged (found reviewing #1880)
