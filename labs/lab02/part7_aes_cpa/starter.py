#!/usr/bin/env python3
"""Part 7 starter: recover an AES-128 key from synthetic power traces.

Complete the TODO functions in order.  The data model targets the first AES
round, so each key byte can be attacked independently.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# Lab commands run in a non-interactive Docker container.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/lab02-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Crypto.Cipher import AES

try:  # Supports both ``python starter.py`` and package imports from the repo root.
    from .model import BLOCK_SIZE, SBOX, hamming_weight
except ImportError:  # pragma: no cover - exercised by direct student execution.
    from model import BLOCK_SIZE, SBOX, hamming_weight


def hypothesis_matrix(plaintexts: np.ndarray, byte_index: int) -> np.ndarray:
    """Return predicted Hamming weights with shape ``(256, trace_count)``.

    Row ``guess`` must contain ``HW(SBox(P[i, byte_index] XOR guess))`` for
    every trace ``i``.  Keeping guesses as rows makes the later matrix
    correlation calculation compact.
    """
    if plaintexts.ndim != 2 or plaintexts.shape[1] != BLOCK_SIZE:
        raise ValueError("plaintexts must have shape (trace_count, 16)")
    if not 0 <= byte_index < BLOCK_SIZE:
        raise ValueError("byte index must be in 0..15")
    # TODO: build all 256 key-guess leakage predictions without a Python loop
    # over traces.  Return a floating-point array of shape (256, trace_count).
    raise NotImplementedError


def pearson_correlations(hypotheses: np.ndarray, traces: np.ndarray) -> np.ndarray:
    """Return Pearson correlations with shape ``(256, sample_count)``.

    ``hypotheses`` has one row per key guess and ``traces`` has one row per
    encryption.  Center both inputs, calculate the dot-product numerator, and
    divide by the product of Euclidean norms.  Avoid division by zero.
    """
    if hypotheses.ndim != 2 or traces.ndim != 2:
        raise ValueError("hypotheses and traces must both be two-dimensional")
    if hypotheses.shape[0] != 256 or hypotheses.shape[1] != traces.shape[0]:
        raise ValueError("expected hypotheses (256, trace_count) and matching traces")
    # TODO: implement vectorized Pearson correlation for every guess/sample pair.
    raise NotImplementedError


def recover_key_byte(traces: np.ndarray, plaintexts: np.ndarray, byte_index: int) -> int:
    """Return the highest-scoring key-byte guess for one AES byte position."""
    # TODO: use hypothesis_matrix() and pearson_correlations(), score each
    # guess with max(abs(correlation)), and return the best guess as an int.
    raise NotImplementedError


def recover_full_key(traces: np.ndarray, plaintexts: np.ndarray) -> bytes:
    """Recover all 16 AES-128 key bytes by repeating the byte attack."""
    # TODO: call recover_key_byte() for byte positions 0 through 15.
    raise NotImplementedError


def pkcs7_unpad(data: bytes) -> bytes:
    """Validate and remove AES-block PKCS#7 padding."""
    if not data or len(data) % BLOCK_SIZE:
        raise ValueError("invalid padded plaintext length")
    amount = data[-1]
    if not 1 <= amount <= BLOCK_SIZE or data[-amount:] != bytes([amount]) * amount:
        raise ValueError("invalid PKCS#7 padding")
    return data[:-amount]


def decrypt_flag(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt AES-CBC ciphertext with the recovered key and supplied IV."""
    if len(key) != BLOCK_SIZE:
        raise ValueError("Part 7 uses an AES-128 key")
    if len(iv) != BLOCK_SIZE or not ciphertext or len(ciphertext) % BLOCK_SIZE:
        raise ValueError("expected a 16-byte IV and complete AES ciphertext blocks")
    # TODO: decrypt ciphertext using AES-CBC with iv, then return the
    # PKCS#7-unpadded plaintext.
    raise NotImplementedError


def byte_attack_details(traces: np.ndarray, plaintexts: np.ndarray,
                        byte_index: int) -> tuple[int, np.ndarray, np.ndarray]:
    """Run one completed byte attack and retain arrays needed for plotting."""
    hypotheses = hypothesis_matrix(plaintexts, byte_index)
    correlations = pearson_correlations(hypotheses, traces)
    scores = np.abs(correlations).max(axis=1)
    return recover_key_byte(traces, plaintexts, byte_index), scores, correlations


def save_plots(traces: np.ndarray, scores: np.ndarray, correlations: np.ndarray,
               byte_index: int, best_guess: int, output_dir: Path) -> None:
    """Save the three plots requested in the Part 7 instructions."""
    output_dir.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(9, 4))
    axis.plot(traces[: min(20, len(traces))].T, alpha=0.45, linewidth=0.8)
    axis.set(title="Example synthetic power traces", xlabel="Sample position", ylabel="Amplitude")
    figure.tight_layout()
    figure.savefig(output_dir / "example_traces.png", dpi=150)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9, 4))
    axis.plot(np.arange(256), scores)
    axis.axvline(best_guess, color="tab:red", linestyle="--", label=f"best guess: {best_guess:02x}")
    axis.set(title=f"Maximum correlation by key guess (byte {byte_index})",
             xlabel="Key-byte guess", ylabel="Maximum absolute correlation")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / f"key_guess_scores_byte_{byte_index}.png", dpi=150)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9, 4))
    axis.plot(correlations[best_guess])
    axis.set(title=f"Correlation over samples for winning byte-{byte_index} guess",
             xlabel="Sample position", ylabel="Pearson correlation")
    figure.tight_layout()
    figure.savefig(output_dir / f"winning_correlation_byte_{byte_index}.png", dpi=150)
    plt.close(figure)


def load_data(data_dir: Path) -> tuple[np.ndarray, np.ndarray, bytes]:
    """Load the supplied public inputs without enabling pickle deserialization."""
    plaintexts = np.load(data_dir / "plaintexts.npy", allow_pickle=False)
    traces = np.load(data_dir / "traces.npy", allow_pickle=False)
    packet = (data_dir / "secret_ciphertext.bin").read_bytes()
    return plaintexts, traces, packet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--byte", type=int, default=0, dest="byte_index",
                        help="recover this byte first (default: 0)")
    parser.add_argument("--all", action="store_true",
                        help="recover all 16 bytes and decrypt the supplied packet")
    parser.add_argument("--plots", type=Path, metavar="DIRECTORY",
                        help="save plots for the selected byte")
    args = parser.parse_args()

    plaintexts, traces, packet = load_data(Path(__file__).with_name("data"))
    if args.all:
        key = recover_full_key(traces, plaintexts)
        print(f"recovered AES-128 key: {key.hex()}")
        print(decrypt_flag(key, packet[:BLOCK_SIZE], packet[BLOCK_SIZE:]).decode("ascii"))
        return

    best_guess, scores, correlations = byte_attack_details(traces, plaintexts, args.byte_index)
    print(f"byte {args.byte_index}: best guess = {best_guess:02x}; score = {scores[best_guess]:.4f}")
    if args.plots:
        save_plots(traces, scores, correlations, args.byte_index, best_guess, args.plots)


if __name__ == "__main__":
    main()
