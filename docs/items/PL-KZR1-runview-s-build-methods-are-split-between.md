---
id: PL-KZR1
title: RunView's build_* methods are split between returning a stored widget (build_notice, build_off_scale_notice) and constructing a new one on each call (build_sidebar_panels, build_readout_section), with nothing in the names saying which
status: untriaged
feature: sidebar-panel-rebuild
added: 2026-09-21
---

**Problem.** RunView's build_* methods are split between returning a stored widget (build_notice, build_off_scale_notice) and constructing a new one on each call (build_sidebar_panels, build_readout_section), with nothing in the names saying which
