#!/usr/bin/env python3
"""View the supplied synthetic power traces before implementing CPA.

Run this example as supplied. It loads only traces.npy and saves a figure
containing one encryption trace and an overlay of several encryption traces.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# Save PNGs without requiring a graphical desktop inside Docker.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/lab02-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_power_traces(traces: np.ndarray, trace_index: int,
                      trace_count: int, output: Path) -> None:
    """Save one trace and an overlay of the first trace_count rows."""
    # Each row is one encryption; each column is a sample position.
    samples = np.arange(traces.shape[1])
    figure, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    try:
        axes[0].plot(samples, traces[trace_index], linewidth=1,
                     label=f"Trace {trace_index}")
        axes[0].set_title(f"Single encryption: trace {trace_index}")
        axes[0].legend()

        # Transpose (trace_count, sample_count) so each plotted column is a trace.
        axes[1].plot(samples, traces[:trace_count].T, alpha=.45, linewidth=.8)
        axes[1].set_title(f"Overlay of the first {trace_count} encryption traces")
        axes[1].set_xlabel("Sample position")

        for axis in axes:
            axis.set_ylabel("Synthetic power (arbitrary units)")
            axis.grid(alpha=.25)

        figure.tight_layout()
        output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output, dpi=150)
    finally:
        plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=int, default=0, dest="trace_index",
                        help="trace index for the upper panel (default: 0)")
    parser.add_argument("--count", type=int, default=10, dest="trace_count",
                        help="number of first traces to overlay (default: 10)")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("plots") / "power_traces.png",
                        help="output image path (default: plots/power_traces.png beside this script)")
    args = parser.parse_args()

    data_path = Path(__file__).with_name("data") / "traces.npy"
    traces = np.load(data_path, allow_pickle=False)
    if traces.ndim != 2 or not traces.shape[0] or not traces.shape[1]:
        parser.error("traces.npy must have shape (trace_count, sample_count) with data")
    if not 0 <= args.trace_index < len(traces):
        parser.error(f"trace index must be between 0 and {len(traces) - 1}")
    if not 1 <= args.trace_count <= len(traces):
        parser.error(f"count must be between 1 and {len(traces)}")

    print(f"Loaded {traces.shape[0]} traces, each with {traces.shape[1]} samples.")
    plot_power_traces(traces, args.trace_index, args.trace_count, args.output)
    print(f"Saved power-trace figure: {args.output}")


if __name__ == "__main__":
    main()
