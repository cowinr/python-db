"""
runner.py
=========
Shared output utilities for the python-db demo scripts.

Provides tabular result formatting and a standardised connection-result
reporter so all demos produce consistent terminal output.

Not intended for standalone execution — import from individual demo scripts.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def print_table(rows: list, headers: list[str], col_width: int = 22) -> None:
    """Print a list of row objects as a fixed-width plain-text table."""
    row_tuples = [tuple(row) for row in rows]
    header_line = "  ".join(h.ljust(col_width) for h in headers)
    divider = "  ".join("-" * col_width for _ in headers)
    print(f"\n  {header_line}")
    print(f"  {divider}")
    for row in row_tuples:
        print("  " + "  ".join(str(v).ljust(col_width) for v in row))
    print()


def report_result(label: str, passed: bool, detail: str = "") -> None:
    """Log a standardised PASSED / FAILED result line."""
    suffix = f" — {detail}" if detail else ""
    if passed:
        log.info("%s: PASSED%s", label, suffix)
    else:
        log.error("%s: FAILED%s", label, suffix)
