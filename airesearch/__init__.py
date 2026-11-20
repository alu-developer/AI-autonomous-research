"""research-director: a thin layer that keeps autonomous research honest.

It does not run experiments. Agents (Claude Code sessions, evolutionary tools, ...) do the work;
this package enforces the rules that the literature says autonomous research systems break:
preregistration, no post-hoc metric changes, full logging, independent verification from raw
outputs, a human gate before any claim, and a hard budget.
"""

__version__ = "0.1.0"
