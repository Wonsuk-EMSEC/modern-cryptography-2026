# Part 7: CPA against AES

Recover an AES-128 key from synthetic first-round power leakage, then decrypt
an encrypted record. No physical hardware is required. The traces model an
implementation leak, not a mathematical break of AES.

`aes_cpa.py` is provided as a **zero-byte file**. Write your entire program
there: imports, analysis, plotting, file loading, output, and `main()`.
The samples run independently and do not recover the course key. The functions
below must be importable without starting analysis or reading course data.

## 1. Run and understand the samples

Part 7 needs only the [common course container](../README.md#setup). The
commands below run **inside the container**:

```console
cd /workspace/labs/lab02/part7_aes_cpa
python3 samples/model_demo.py
python3 samples/power_trace_demo.py
```

Read both samples in execution order. `model_demo.py` demonstrates public
S-box and Hamming-weight helpers, synthetic trace generation, correlation
signs, and a CBC packet with a public example key. Expected output includes:

```text
Hamming weights: [0, 1, 2, 8]
SBox[0]: 0x63
public plaintexts: shape=(4, 16), dtype=uint8
public traces: shape=(4, 240), dtype=float32
toy positive correlation: 1.0
toy negative correlation: -1.0
public CBC packet: 32 bytes
CBC recovered: b'Sample record'
```

Hamming weight counts set bits. An AES plaintext has 16 bytes; each trace
has 240 sample positions. Correlation measures variation **across observations**,
and its sign can be positive or negative. The CBC packet consists of a
16-byte IV followed by one encrypted block. This sample uses known public
values and does not load or decrypt the course's encrypted record.

The trace-viewing sample loads only `data/traces.npy` and reports:

```text
Loaded 550 traces, each with 240 samples.
```

It then reports the saved figure path, ending in `plots/power_traces.png`. Open
`labs/lab02/part7_aes_cpa/plots/power_traces.png` in your host editor.
Its upper panel shows trace 0; its lower panel overlays the first 10 traces.
A row is one encryption measurement, and a column is a sample position.
The x-axis is sample position, and power uses arbitrary units. Compare
trace shapes and differences without assuming the largest amplitude peak
identifies a key.

To view another trace and overlay more measurements:

```console
python3 samples/power_trace_demo.py --trace 25 --count 20 --output plots/power_traces_trace25.png
```

Matplotlib is installed in the course image. Read how the sample selects the
`Agg` backend, saves figures, and closes them; your program also saves PNGs
without requiring a graphical desktop.

## 2. Write and check `hypothesis_matrix()`

Implement in `aes_cpa.py`:

```python
hypothesis_matrix(plaintexts: np.ndarray, byte_index: int) -> np.ndarray
```

Import `SBOX` and `hamming_weight` from the supplied `model.py`.
For every key-byte candidate `k` and plaintext row `i`, predict

`H[k, i] = HW(SBox(plaintexts[i, byte_index] XOR k))`.

Return a floating-point array of shape `(256, N)`, with guesses as rows.
Use NumPy broadcasting; avoid a Python loop over traces. Reject plaintexts
without shape `(N, 16)` or a byte index outside `0..15` with `ValueError`.

Check this function before implementing correlations:

```console
python3 - <<'PY'
import numpy as np
from aes_cpa import hypothesis_matrix
from model import SBOX, hamming_weight
plaintexts = np.arange(64, dtype=np.uint8).reshape(4, 16)
hypotheses = hypothesis_matrix(plaintexts, 0)
assert hypotheses.shape == (256, 4)
assert np.issubdtype(hypotheses.dtype, np.floating)
expected_row = hamming_weight(SBOX[plaintexts[:, 0] ^ 7])
np.testing.assert_array_equal(hypotheses[7], expected_row)
for bad_plaintexts, bad_byte in ((plaintexts[:, :15], 0), (plaintexts, 16)):
    try:
        hypothesis_matrix(bad_plaintexts, bad_byte)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid hypothesis input accepted")
print("Hypothesis matrix check: OK")
PY
```

Expected: `Hypothesis matrix check: OK`. The one checked guess is a public
fixture, not a recovered task byte.

## 3. Write and check `pearson_correlations()`

Implement:

```python
pearson_correlations(hypotheses: np.ndarray, traces: np.ndarray) -> np.ndarray
```

Inputs have shapes `(256, N)` and `(N, S)`; return `(256, S)`.
Each element compares a candidate's predicted leakage vector with one trace
sample column across the same `N` encryptions. Center vectors and normalize
their dot products by their norms. Retain signed correlations, rather than
taking absolute values inside this function.

Reject incompatible shapes with `ValueError`. A constant hypothesis row
or trace column has zero variance: return zero for those comparisons so the
output is finite, without NaNs or infinities.

```console
python3 - <<'PY'
import numpy as np
from aes_cpa import pearson_correlations
observations = np.arange(4, dtype=float)
hypotheses = np.ones((256, 4))
hypotheses[0] = observations
traces = np.column_stack((observations, -observations, np.ones(4)))
correlations = pearson_correlations(hypotheses, traces)
assert correlations.shape == (256, 3)
np.testing.assert_allclose(correlations[0], [1, -1, 0])
np.testing.assert_allclose(correlations[1:], 0)
assert np.isfinite(correlations).all()
try:
    pearson_correlations(hypotheses, traces[:3])
except ValueError:
    pass
else:
    raise AssertionError("mismatched observation counts accepted")
print("Signed correlation and constant-vector checks: OK")
PY
```

Expected: `Signed correlation and constant-vector checks: OK`.
Strong negative correlation is useful evidence just like strong positive
correlation; candidate scoring is the next separate step.

## 4. Write and check `recover_key_byte()`

Implement:

```python
recover_key_byte(traces: np.ndarray, plaintexts: np.ndarray, byte_index: int) -> int
```

Use your hypothesis and correlation functions. Score each guess by its
**maximum absolute correlation across samples**, and return the highest
scoring guess as a Python `int`. Do not score the maximum signed correlation.

```console
python3 - <<'PY'
import numpy as np
from aes_cpa import recover_key_byte
from model import generate_traces
key = bytes((13 * index + 7) % 256 for index in range(16))
plaintexts = np.random.default_rng(42).integers(0, 256, (120, 16), dtype=np.uint8)
traces = generate_traces(plaintexts, key, noise_stddev=.15, seed=99)
guess = recover_key_byte(traces, plaintexts, 0)
assert isinstance(guess, int) and guess == key[0]
print("One-byte synthetic CPA check: OK")
PY
```

Expected: `One-byte synthetic CPA check: OK`. Here the key is deliberately
known and traces have low noise, giving a controlled development checkpoint.

## 5. Write and check `recover_full_key()`

Implement:

```python
recover_full_key(traces: np.ndarray, plaintexts: np.ndarray) -> bytes
```

Recover positions `0..15` and return exactly 16 bytes in AES key order.
Reject mismatched plaintext and trace counts with `ValueError`.

```console
python3 - <<'PY'
import numpy as np
from aes_cpa import recover_full_key
from model import generate_traces
key = bytes((13 * index + 7) % 256 for index in range(16))
plaintexts = np.random.default_rng(42).integers(0, 256, (120, 16), dtype=np.uint8)
traces = generate_traces(plaintexts, key, noise_stddev=.15, seed=99)
assert recover_full_key(traces, plaintexts) == key
try:
    recover_full_key(traces[:-1], plaintexts)
except ValueError:
    pass
else:
    raise AssertionError("mismatched observation counts accepted")
print("Full-key synthetic CPA check: OK")
PY
```

Expected: `Full-key synthetic CPA check: OK`. This checks byte ordering
and generalization beyond byte 0 without exposing the course key.

## 6. Write and check `pkcs7_unpad()`

Implement `pkcs7_unpad(data: bytes) -> bytes` for AES's 16-byte block
size. You may adapt your Part 3 implementation. Reject empty or unaligned
input, an invalid length byte, or inconsistent padding bytes with `ValueError`.

```console
python3 - <<'PY'
from aes_cpa import pkcs7_unpad
assert pkcs7_unpad(b"hello" + b"\x0b" * 11) == b"hello"
assert pkcs7_unpad(b"\x10" * 16) == b""
for malformed in (b"", b"short", b"A" * 15 + b"\x00",
                  b"A" * 14 + b"\x01\x02"):
    try:
        pkcs7_unpad(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed padding accepted")
print("AES padding validation check: OK")
PY
```

Expected: `AES padding validation check: OK`.

## 7. Write and check `decrypt_flag()`

Implement:

```python
decrypt_flag(key: bytes, iv: bytes, ciphertext: bytes) -> bytes
```

Require a 16-byte AES-128 key, a 16-byte IV, and nonempty aligned ciphertext;
reject malformed inputs with `ValueError`. Decrypt CBC and validate/remove
padding. Unlike Part 3's construction exercise, **library AES-CBC is allowed
here**. Return unpadded bytes.

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from aes_cpa import decrypt_flag
key, iv, message = bytes(range(16)), bytes(range(16, 32)), b"public CPA demo record"
ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
assert decrypt_flag(key, iv, ciphertext) == message
for bad_key, bad_iv, bad_ciphertext in ((key[:-1], iv, ciphertext),
                                       (key, iv[:-1], ciphertext),
                                       (key, iv, b"")):
    try:
        decrypt_flag(bad_key, bad_iv, bad_ciphertext)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid AES-CBC inputs accepted")
print("Recovered-key decryption check: OK")
PY
```

Expected: `Recovered-key decryption check: OK`; this fixture uses a public
known key and contains no course flag.

## 8. Write and check `plot_sample_correlations()`

Implement:

```python
plot_sample_correlations(axis: plt.Axes, correlations: np.ndarray,
                         byte_index: int, best_guess: int) -> None
```

Draw on the passed axis; do not save or close its figure in this function.
For an input of shape `(256, S)`, row `k` contains candidate `k`'s
signed correlations, while columns index sample positions.

- Use sample positions on x and signed Pearson correlation on y, with limits
  `[-1, 1]`. Include axis labels, a title, and a zero reference line.
- Draw the other 255 candidates as faint curves and highlight the winner,
  with a legend label identifying its guess.
- Mark the winning candidate's sample with the largest **absolute**
  correlation using a vertical line, and label that sample index and its
  **signed** correlation in an annotation or legend. Preserve negative peaks
  in the plotted curve.

Check a deliberate negative winner before using course traces:

```console
python3 - <<'PY'
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from aes_cpa import plot_sample_correlations
correlations = np.zeros((256, 9))
winner, peak = 23, 4
correlations[winner, peak] = -.9
figure, axis = plt.subplots()
try:
    plot_sample_correlations(axis, correlations, 0, winner)
    assert any(np.array_equal(line.get_xdata(), np.arange(9))
               and np.allclose(line.get_ydata(), correlations[winner])
               for line in axis.lines)
    assert any(np.array_equal(line.get_xdata(), [peak, peak]) for line in axis.lines)
    np.testing.assert_allclose(axis.get_ylim(), [-1, 1])
    assert axis.get_xlabel() and axis.get_ylabel() and axis.get_title()
    assert axis.get_legend() is not None
    figure.savefig("/tmp/lab02-cpa-plot-check.png")
finally:
    plt.close(figure)
print("Signed correlation plot check: OK")
PY
```

Expected: `Signed correlation plot check: OK`. The saved fixture PNG is
in the container's `/tmp`; use the later `--plots` run to save analysis
figures in the shared repository.

## 9. Write and check figure saving

The empty file has no supplied figure-saving code. Implement:

```python
save_plots(traces: np.ndarray, scores: np.ndarray, correlations: np.ndarray,
           byte_index: int, best_guess: int, output_dir: Path) -> None
```

Create the output directory as needed, write the three PNGs below, and close
every figure. Use your correlation plotting function for the third figure.

| File | Contents |
| --- | --- |
| `example_traces.png` | First 20 traces, or all traces if fewer, over sample positions |
| `key_guess_scores_byte_0.png` | All 256 maximum-absolute-correlation scores, with the winner marked |
| `sample_correlations_byte_0.png` | Signed correlation curves, winner, and labeled peak |

Use the selected byte number in the last two filenames. First verify saving
with arrays unrelated to the course dataset:

```console
python3 - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from aes_cpa import save_plots
traces = np.random.default_rng(7).normal(size=(4, 9))
correlations = np.zeros((256, 9))
correlations[23, 4] = -.9
scores = np.max(np.abs(correlations), axis=1)
before = plt.get_fignums()
with TemporaryDirectory() as temporary:
    output = Path(temporary) / "new-plots"
    save_plots(traces, scores, correlations, 0, 23, output)
    for filename in ("example_traces.png", "key_guess_scores_byte_0.png",
                     "sample_correlations_byte_0.png"):
        assert (output / filename).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
assert plt.get_fignums() == before
print("Three-figure saving check: OK")
PY
```

Expected: `Three-figure saving check: OK`.

## 10. Write file loading and `main()`

Implement `main() -> None` and a guarded entry point. Locate `data/`
relative to `__file__` so execution works from Part or Lab02 directories.

| Input | Format and use |
| --- | --- |
| `data/plaintexts.npy` | `(N, 16)` known plaintext bytes, one encryption per row |
| `data/traces.npy` | `(N, S)` trace samples, matching the plaintext rows |
| `data/secret_ciphertext.bin` | Binary packet: first 16 bytes IV, remaining bytes CBC ciphertext |
| `model.py` | Public S-box, Hamming-weight helper, and synthetic fixture generator |

Load NumPy arrays using `np.load(..., allow_pickle=False)`; check matching
row counts. Read the packet as bytes and split its IV from ciphertext.
You may organize this work into `load_data()` and retain analysis arrays
with a `byte_attack_details()` helper. Those local helper names and
signatures are your design choice; the function contracts above remain fixed.

Use `argparse` to support:

- `--byte J`: analyze position `J`, default 0; reject values outside `0..15`.
  Print the winning byte guess and score.
- `--plots DIRECTORY`: in byte-analysis mode, save all three figures for
  the selected byte using the same scores and correlations.
- `--all`: recover the full 16-byte key, print it in hexadecimal, decrypt
  the course packet, and print the ASCII record.

Do not call the synthetic generator to replace the supplied course data in
the final run. Do not hard-code a guessed byte, full key, or decrypted message.

```console
python3 -c 'import aes_cpa; print("Import check: OK")'
python3 aes_cpa.py --help
```

Expected: importing prints only `Import check: OK`; `--help` describes
all three options without starting an attack.

## 11. Run the course data, inspect the figures, and finish

After the small checks pass:

```console
python3 aes_cpa.py --byte 0 --plots plots
python3 aes_cpa.py --all
cd /workspace/labs/lab02
make grade PART=7
```

The byte run prints its guessed byte and score and creates the three analysis
PNGs. Open them under `labs/lab02/part7_aes_cpa/plots` in your host editor.
The full run prints a 16-byte key as 32 hexadecimal characters and a message
containing `FLAG{...}`; actual key and flag values are not supplied here.
Selecting another byte changes the byte number in the score and correlation
filenames. Matplotlib saves files without a container desktop.

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part7_aes_cpa/aes_cpa.py --byte 0 --plots part7_aes_cpa/plots
byte 0: best guess = <key byte in hex>; score = <correlation score>

python3 part7_aes_cpa/aes_cpa.py --all
recovered AES-128 key: <recovered key in hex>
FLAG{<recovered value>}
```

Completion means all eight function checks and the import check pass,
CLI options work, all 16 bytes
are recovered, the encrypted record decrypts, the three figures meet the
plotting requirements, and selected-Part grading passes. After all Parts,
run `make grade` without `PART`.

Once `recover_key_byte()` works, the optional experiment can compare subsets:

```console
cd /workspace/labs/lab02/part7_aes_cpa
python3 trace_count_experiment.py
```

It prints trace counts and corresponding recovered-byte guesses. Small
subsets may be unstable; compare results as counts grow. This helper imports
your `recover_key_byte()` from `aes_cpa.py`.

## Checkpoint Questions

For the report, record the selected-byte score, winning sample position and
signed correlation, and the result of full-key recovery. Include the
required plots according to the course's submission policy. Explain:

1. Why can each AES key byte be attacked independently under this model?
2. Why do more traces usually improve separation of correct and incorrect guesses?
3. Why does CPA attack implementation leakage rather than the AES algorithm?
4. Which sample position has the winning candidate's largest absolute
   correlation? How does that peak compare with the other candidates, and
   why can a negative correlation also be useful?
5. If you ran the optional experiment, how did trace count affect the guess?

Submit recovered keys, flags, and plots that disclose those answers only
through the designated course channel; keep them out of public sample output.

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Byte-0 guess and score, and the recovered full key (visible in the screenshots)
- [ ] Winning sample position and signed correlation
- [ ] Generated trace, key-guess score, and signed sample-correlation plots
