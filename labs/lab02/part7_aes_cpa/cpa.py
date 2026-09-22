#!/usr/bin/env python3
"""Compatibility entry point for the Part 7 CPA starter.

The TODO implementation lives in :mod:`starter`, matching the other Lab02
parts.  This filename is provided because the Part description calls the
student attack program ``cpa.py``.
"""

from __future__ import annotations

try:
    from .starter import (decrypt_flag, hamming_weight, hypothesis_matrix,
                          load_data, main, pearson_correlations,
                          recover_full_key, recover_key_byte, save_plots)
except ImportError:  # pragma: no cover - direct script execution.
    from starter import (decrypt_flag, hamming_weight, hypothesis_matrix,
                         load_data, main, pearson_correlations,
                         recover_full_key, recover_key_byte, save_plots)


if __name__ == "__main__":
    main()
