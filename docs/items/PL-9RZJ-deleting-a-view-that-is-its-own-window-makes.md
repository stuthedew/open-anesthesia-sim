---
id: PL-9RZJ
title: Deleting a View that is its own window makes the time axis title raise 'AxisItem already deleted' tracebacks after the window closes; they fail no test, but a later Qt or pyqtgraph change could turn them into a crash or hide a real error in the log
status: untriaged
added: 2026-11-22
filed-pr: 2249
---

**Problem.** Deleting a View that is its own window makes the time axis title raise 'AxisItem already deleted' tracebacks after the window closes; they fail no test, but a later Qt or pyqtgraph change could turn them into a crash or hide a real error in the log
