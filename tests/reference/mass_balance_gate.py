"""The conservation bound the reference runs are held to, and why it is relative.

Not a `test_` module: it holds one constant, so that the release gate means one
thing rather than one thing per file that restates it.

**Why relative rather than absolute.** The mass-balance residual is rounding
accumulated once per step, so it scales with how much agent a run has handled.
An absolute bound therefore measures the dial and the run length rather than
conservation. Measured 2026-09-06 on the shipped exact step, 600 s wash-in plus
600 s washout:

| Agent | Dial | Delivered | Absolute | Relative |
| --- | --- | --- | --- | --- |
| isoflurane | 4% | 1.60 L | 3.589e-13 L | 2.243e-13 |
| isoflurane | 2% | 0.80 L | 1.794e-13 L | 2.243e-13 |
| desflurane | 4% | 1.60 L | 9.262e-14 L | 5.789e-14 |
| desflurane | 2% | 0.80 L | 4.631e-14 L | 5.789e-14 |

Halving the dial halves the absolute figure and leaves the relative one
unchanged to four significant figures. That is the whole argument: the
quantity on the right is a property of the method, the one on its left is a
property of the test's setup (`PL-4GN8`).

**The absolute bound these tests used to assert was also false past about an
hour.** Under the exact step, `absolute_error_l` first exceeds the 1e-12 L
halt tolerance at t = 3452 s at these tests' own settings, and at t = 538 s at
the sevoflurane corner of the supported envelope. The tests run to 1200 s,
which is the only reason it passed. The relative residual over the same runs
stays four orders inside the bound below.

**Where the number comes from.** Worst relative residual at any step, measured
the same day over 8 h, at the reference settings and at the envelope corner
(fresh gas 10 L/min, alveolar ventilation 12 L/min, cardiac output 10 L/min,
each agent at its calibrated dial maximum):

| Horizon | Reference settings | Worst corner |
| --- | --- | --- |
| 1200 s (what these tests run) | 2.12e-13 | 2.26e-13 |
| 1 h | 2.19e-13 | 1.04e-12 |
| 4 h | 3.75e-12 | 2.88e-12 |
| 8 h | 5.05e-12 | 6.36e-12 |

1e-10 leaves about 450x headroom at the horizon these tests actually run and
about 16x at 8 h, so neither moving a dial nor lengthening a case changes what
the gate certifies — which is what `PL-4GN8` was about. It stays an order of
magnitude inside `AGENT_ACCOUNTING_RELATIVE_TOLERANCE` (1e-9), the threshold at
which a run halts, so passing this gate says strictly more than "the run did
not stop". And a real conservation defect is orders of magnitude rather than
factors of two, so the headroom costs no sensitivity to the thing being
guarded against.

Restated here rather than imported from `core/`, for the reason
`tests/unit/test_agent_simulation_validation.py` gives: a bound that followed
the constant it is testing would move wherever that constant moved.
"""

MASS_BALANCE_RELATIVE_GATE = 1e-10
