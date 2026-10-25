<a id="part-7-cpa-against-aes"></a>
# Part 7: AES에 대한 CPA

**한국어** | [English](../../../en/labs/lab02/part7_aes_cpa/README.md)

첫 라운드의 합성 전력 누출 데이터로 AES-128 키를 복구한 뒤 암호화된 레코드를
복호화합니다. 실제 하드웨어는 필요하지 않습니다. 트레이스는 구현에서 생기는
누출을 모델링하며, AES에 대한 수학적 해독을 의미하지는 않습니다.

`aes_cpa.py`는 **0바이트 파일**로 제공됩니다. import, 분석, 그래프 작성,
파일 읽기, 출력, `main()`을 포함한 전체 프로그램을 작성하세요. 예제는
독립적으로 실행되며 수업용 키를 복구하지 않습니다. 아래 함수는 분석을 시작하거나
수업 데이터를 읽지 않고 import할 수 있어야 합니다.

<a id="1-run-and-understand-the-samples"></a>
## 1. 예제 실행 및 이해

Part 7에는 [공통 수업용 컨테이너](../README.md#setup)만 필요합니다.
아래 명령은 **컨테이너 안**에서 실행하세요.

```console
cd /workspace/labs/lab02/part7_aes_cpa
python3 samples/model_demo.py
python3 samples/power_trace_demo.py
```

두 예제를 실행 순서대로 읽어 보세요. `model_demo.py`는 공개 S-box와
해밍 가중치 보조 함수, 합성 트레이스 생성, 상관계수의 부호, 공개 예시 키를
사용한 CBC 패킷을 보여 줍니다. 예상 출력에는 다음이 포함됩니다.

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

해밍 가중치는 값이 1인 비트의 개수입니다. AES 평문은 16바이트이며 각
트레이스에는 샘플 위치가 240개 있습니다. 상관계수는 **여러 관측값에 걸친**
변화를 측정하며 양수나 음수일 수 있습니다. CBC 패킷은 16바이트 IV와 암호문
블록 하나로 이루어집니다. 이 예제는 알려진 공개 값을 사용하며 수업용 암호화
레코드를 읽거나 복호화하지 않습니다.

트레이스 보기 예제는 `data/traces.npy`만 읽고 다음을 출력합니다.

```text
Loaded 550 traces, each with 240 samples.
```

이어서 `plots/power_traces.png`로 끝나는 저장 경로를 출력합니다. 호스트 편집기에서
`labs/lab02/part7_aes_cpa/plots/power_traces.png`를 여세요. 위쪽 패널은
트레이스 0을, 아래쪽 패널은 처음 10개 트레이스를 겹쳐 보여 줍니다.
한 행은 한 번의 암호화 측정이며 한 열은 샘플 위치입니다. x축은 샘플 위치이고
전력은 임의 단위를 사용합니다. 진폭이 가장 큰 피크가 키를 알려 준다고
가정하지 말고 트레이스의 모양과 차이를 비교하세요.

다른 트레이스를 보면서 더 많은 측정값을 겹치려면 다음을 실행하세요.

```console
python3 samples/power_trace_demo.py --trace 25 --count 20 --output plots/power_traces_trace25.png
```

Matplotlib은 수업용 이미지에 설치되어 있습니다. 예제에서 `Agg` 백엔드를
선택하고 그림을 저장하고 닫는 방법을 읽어 보세요. 여러분의 프로그램도 그래픽
데스크톱 없이 PNG를 저장해야 합니다.

<a id="2-write-and-check-hypothesis_matrix"></a>
## 2. `hypothesis_matrix()` 작성 및 확인

`aes_cpa.py`에 구현하세요.

```python
hypothesis_matrix(plaintexts: np.ndarray, byte_index: int) -> np.ndarray
```

제공된 `model.py`에서 `SBOX`와 `hamming_weight`를 import하세요.
모든 키 바이트 후보 `k`와 평문 행 `i`에 대해 다음을 예측합니다.

`H[k, i] = HW(SBox(plaintexts[i, byte_index] XOR k))`.

추측값을 행으로 하는 `(256, N)` 형태의 부동소수점 배열을 반환하세요.
NumPy 브로드캐스팅을 사용하고, 트레이스마다 Python 반복문을 사용하지 마세요.
평문 형태가 `(N, 16)`이 아니거나 바이트 인덱스가 `0..15` 범위를 벗어나면
`ValueError`를 발생시키세요.

상관계수를 구현하기 전에 이 함수를 확인하세요.

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

예상 출력은 `Hypothesis matrix check: OK`입니다. 여기서 확인하는 추측값은
공개 테스트 값이며 복구한 문제의 바이트가 아닙니다.

<a id="3-write-and-check-pearson_correlations"></a>
## 3. `pearson_correlations()` 작성 및 확인

다음을 구현하세요.

```python
pearson_correlations(hypotheses: np.ndarray, traces: np.ndarray) -> np.ndarray
```

입력의 형태는 `(256, N)`과 `(N, S)`이며, `(256, S)`를 반환합니다.
각 원소는 동일한 `N`번의 암호화에 대해 한 후보의 예측 누출 벡터와 트레이스의
샘플 열 하나를 비교합니다. 벡터에서 평균을 빼고 내적을 노름의 곱으로 나누어
정규화하세요. 이 함수 안에서 절댓값을 취하지 말고 부호 있는 상관계수를
유지합니다.

호환되지 않는 형태에는 `ValueError`를 발생시키세요. 값이 일정한 가설 행이나
트레이스 열은 분산이 0입니다. 해당 비교 결과를 0으로 하여 출력에 NaN이나
무한대가 없고 모든 값이 유한하도록 만드세요.

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

예상 출력은 `Signed correlation and constant-vector checks: OK`입니다.
강한 음의 상관관계도 강한 양의 상관관계처럼 유용한 증거입니다. 후보 점수
계산은 다음 단계에서 별도로 수행합니다.

<a id="4-write-and-check-recover_key_byte"></a>
## 4. `recover_key_byte()` 작성 및 확인

다음을 구현하세요.

```python
recover_key_byte(traces: np.ndarray, plaintexts: np.ndarray, byte_index: int) -> int
```

직접 작성한 가설 함수와 상관계수 함수를 사용하세요. 각 추측값에 대해
**모든 샘플에서 상관계수 절댓값의 최댓값**을 점수로 계산하고, 최고 점수의
추측값을 Python `int`로 반환합니다. 부호 있는 상관계수 자체의 최댓값을
점수로 사용하지 마세요.

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

예상 출력은 `One-byte synthetic CPA check: OK`입니다. 이 검사는 키를
의도적으로 공개하고 잡음이 작은 트레이스를 사용하여 통제된 개발 중간 점검을
제공합니다.

<a id="5-write-and-check-recover_full_key"></a>
## 5. `recover_full_key()` 작성 및 확인

다음을 구현하세요.

```python
recover_full_key(traces: np.ndarray, plaintexts: np.ndarray) -> bytes
```

`0..15` 위치를 복구하고 AES 키 순서에 맞는 정확히 16바이트를 반환하세요.
평문 수와 트레이스 수가 일치하지 않으면 `ValueError`를 발생시킵니다.

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

예상 출력은 `Full-key synthetic CPA check: OK`입니다. 수업용 키를 공개하지
않고 바이트 순서와 0번 이외 바이트에 대한 일반화 여부를 검사합니다.

<a id="6-write-and-check-pkcs7_unpad"></a>
## 6. `pkcs7_unpad()` 작성 및 확인

AES의 16바이트 블록 크기에 맞게 `pkcs7_unpad(data: bytes) -> bytes`를
구현하세요. Part 3의 구현을 수정해 사용해도 됩니다. 비어 있거나 블록 경계에
맞지 않는 입력, 유효하지 않은 길이 바이트, 일관되지 않은 패딩 바이트에는
`ValueError`를 발생시키세요.

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

예상 출력은 `AES padding validation check: OK`입니다.

<a id="7-write-and-check-decrypt_flag"></a>
## 7. `decrypt_flag()` 작성 및 확인

다음을 구현하세요.

```python
decrypt_flag(key: bytes, iv: bytes, ciphertext: bytes) -> bytes
```

16바이트 AES-128 키, 16바이트 IV, 비어 있지 않고 블록 경계에 맞는 암호문을
요구하세요. 잘못된 입력에는 `ValueError`를 발생시킵니다. CBC를 복호화하고
패딩을 검사한 뒤 제거하세요. Part 3의 구성 실습과 달리 **여기서는 라이브러리의
AES-CBC를 사용해도 됩니다**. 패딩이 제거된 바이트열을 반환합니다.

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

예상 출력은 `Recovered-key decryption check: OK`입니다. 이 테스트는 알려진
공개 키를 사용하며 수업용 플래그를 포함하지 않습니다.

<a id="8-write-and-check-plot_sample_correlations"></a>
## 8. `plot_sample_correlations()` 작성 및 확인

다음을 구현하세요.

```python
plot_sample_correlations(axis: plt.Axes, correlations: np.ndarray,
                         byte_index: int, best_guess: int) -> None
```

전달받은 축에 그리세요. 이 함수에서 그림을 저장하거나 닫지 마세요.
형태가 `(256, S)`인 입력에서 행 `k`는 후보 `k`의 부호 있는 상관계수이며,
열은 샘플 위치를 나타냅니다.

- x축에는 샘플 위치, y축에는 부호 있는 피어슨 상관계수를 사용하고 범위는
  `[-1, 1]`로 지정하세요. 축 레이블, 제목, 0 기준선을 포함합니다.
- 나머지 255개 후보는 흐린 곡선으로 그리고 최고 후보를 강조하세요.
  추측값을 식별할 수 있는 범례 레이블을 넣습니다.
- 최고 후보에서 상관계수 **절댓값**이 가장 큰 샘플을 수직선으로 표시하고,
  주석이나 범례에 해당 샘플 인덱스와 **부호 있는** 상관계수를 적으세요.
  곡선의 음수 피크도 그대로 표시합니다.

수업용 트레이스를 사용하기 전에 의도적으로 음의 상관관계가 승리하는 사례를
확인하세요.

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

예상 출력은 `Signed correlation plot check: OK`입니다. 테스트 PNG는
컨테이너의 `/tmp`에 저장됩니다. 이후 `--plots` 실행으로 분석 그림을 공통
저장소에 저장하세요.

<a id="9-write-and-check-figure-saving"></a>
## 9. 그림 저장 작성 및 확인

빈 파일에는 그림 저장 코드도 제공되지 않습니다. 다음을 구현하세요.

```python
save_plots(traces: np.ndarray, scores: np.ndarray, correlations: np.ndarray,
           byte_index: int, best_guess: int, output_dir: Path) -> None
```

필요하면 출력 디렉토리를 만들고 아래의 PNG 세 개를 저장한 뒤 모든 그림을
닫으세요. 세 번째 그림에는 직접 작성한 상관계수 그래프 함수를 사용합니다.

| 파일 | 내용 |
| --- | --- |
| `example_traces.png` | 샘플 위치에 따른 처음 20개 트레이스. 20개보다 적으면 전체 트레이스 |
| `key_guess_scores_byte_0.png` | 최대 절대 상관계수로 계산한 256개 점수 전체와 최고 후보 표시 |
| `sample_correlations_byte_0.png` | 부호 있는 상관계수 곡선, 최고 후보, 레이블이 있는 피크 |

마지막 두 파일명에는 선택한 바이트 번호를 사용하세요. 먼저 수업 데이터셋과
무관한 배열로 저장 기능을 검증합니다.

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

예상 출력은 `Three-figure saving check: OK`입니다.

<a id="10-write-file-loading-and-main"></a>
## 10. 파일 읽기 및 `main()` 작성

`main() -> None`과 실행 가드가 있는 진입점을 구현하세요. Part 디렉토리와
Lab02 디렉토리 어디서 실행해도 동작하도록 `__file__`을 기준으로 `data/`를
찾습니다.

| 입력 | 형식과 용도 |
| --- | --- |
| `data/plaintexts.npy` | `(N, 16)` 형태의 알려진 평문 바이트. 행마다 한 번의 암호화에 대응 |
| `data/traces.npy` | 평문 행과 대응하는 `(N, S)` 형태의 트레이스 샘플 |
| `data/secret_ciphertext.bin` | 바이너리 패킷. 처음 16바이트는 IV, 나머지는 CBC 암호문 |
| `model.py` | 공개 S-box, 해밍 가중치 보조 함수, 합성 테스트 데이터 생성기 |

`np.load(..., allow_pickle=False)`로 NumPy 배열을 읽고 행 수가 일치하는지
확인하세요. 패킷은 바이트열로 읽어 IV와 암호문을 분리합니다. 이 작업을
`load_data()`로 구성하고 `byte_attack_details()` 보조 함수로 분석 배열을
유지해도 됩니다. 이러한 내부 보조 함수의 이름과 시그니처는 자유롭게 정하되,
앞에서 지정한 함수의 인터페이스는 유지해야 합니다.

`argparse`로 다음 옵션을 지원하세요.

- `--byte J`: 위치 `J`를 분석합니다. 기본값은 0이며 `0..15` 범위를 벗어나는
  값은 거부하세요. 최고 키 바이트 추측값과 점수를 출력합니다.
- `--plots DIRECTORY`: 바이트 분석 모드에서 같은 점수와 상관계수로 선택한
  바이트의 그림 세 개를 모두 저장합니다.
- `--all`: 전체 16바이트 키를 복구하여 16진수로 출력하고, 수업용 패킷을
  복호화한 뒤 ASCII 레코드를 출력합니다.

최종 실행에서 합성 생성기로 제공된 수업 데이터를 대체하지 마세요. 추측한
바이트, 전체 키, 복호화한 메시지를 하드코딩하지 마세요.

```console
python3 -c 'import aes_cpa; print("Import check: OK")'
python3 aes_cpa.py --help
```

import 시 `Import check: OK`만 출력되어야 하며, `--help`는 공격을 시작하지
않고 세 옵션을 모두 설명해야 합니다.

<a id="11-run-the-course-data-inspect-the-figures-and-finish"></a>
## 11. 수업 데이터 실행, 그림 확인 및 마무리

작은 검사들이 통과한 뒤 실행하세요.

```console
python3 aes_cpa.py --byte 0 --plots plots
python3 aes_cpa.py --all
cd /workspace/labs/lab02
make grade PART=7
```

바이트 실행은 추측한 바이트와 점수를 출력하고 분석 PNG 세 개를 생성합니다.
호스트 편집기에서 `labs/lab02/part7_aes_cpa/plots` 아래의 그림을 여세요.
전체 실행은 16바이트 키를 32자리 16진수로 출력하고 `FLAG{...}`가 포함된
메시지를 출력합니다. 실제 키와 플래그 값은 이 문서에 제공하지 않습니다.
다른 바이트를 선택하면 점수·상관계수 파일명의 바이트 번호가 바뀝니다.
Matplotlib은 컨테이너에 데스크톱이 없어도 파일을 저장합니다.

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part7_aes_cpa/aes_cpa.py --byte 0 --plots part7_aes_cpa/plots
byte 0: best guess = <key byte in hex>; score = <correlation score>

python3 part7_aes_cpa/aes_cpa.py --all
recovered AES-128 key: <recovered key in hex>
FLAG{<recovered value>}
```

여덟 함수 검사와 import 검사가 모두 통과하고, CLI 옵션이 동작하고, 16바이트를
모두 복구하고, 암호화 레코드를 복호화하고, 그림 세 개가 그래프 요구 사항을
만족하며, 해당 Part의 채점 검사가 통과하면 완료입니다. 모든 Part를 마친 뒤에는
`PART` 없이 `make grade`를 실행하세요.

`recover_key_byte()`가 동작하면 선택 실험으로 부분집합을 비교할 수 있습니다.

```console
cd /workspace/labs/lab02/part7_aes_cpa
python3 trace_count_experiment.py
```

트레이스 수와 해당 조건에서 복구한 바이트 추측값이 출력됩니다. 작은 부분집합은
결과가 불안정할 수 있으므로 개수가 늘어날 때 결과를 비교하세요. 이 보조 도구는
`aes_cpa.py`에서 여러분이 작성한 `recover_key_byte()`를 import합니다.

<a id="checkpoint-questions"></a>
## 확인 질문

보고서에는 선택한 바이트의 점수, 최고 후보의 샘플 위치와 부호 있는 상관계수,
전체 키 복구 결과를 기록하세요. 수업 제출 방침에 따라 필수 그래프를 포함하고
다음을 설명합니다.

1. 이 모델에서 AES 키의 각 바이트를 독립적으로 공격할 수 있는 이유는 무엇인가요?
2. 트레이스가 많아지면 보통 올바른 추측과 잘못된 추측을 더 잘 구분할 수 있는 이유는 무엇인가요?
3. CPA가 AES 알고리즘 자체가 아닌 구현의 정보 누출을 공격하는 이유는 무엇인가요?
4. 최고 후보의 상관계수 절댓값이 가장 큰 샘플 위치는 어디인가요? 해당 피크는
   다른 후보와 어떻게 다르며, 음의 상관관계도 유용한 이유는 무엇인가요?
5. 선택 실험을 수행했다면 트레이스 수가 추측값에 어떤 영향을 주었나요?

복구한 키, 플래그, 해당 답을 드러내는 그래프는 지정된 수업 채널로만 제출하고
공개 예제 출력에 포함하지 마세요.

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 스크린샷에서 확인할 수 있는 바이트 0의 추측값과 점수, 복구한 전체 키
- [ ] 최고 후보의 샘플 위치와 부호 있는 상관계수
- [ ] 생성한 트레이스, 키 추측 점수, 부호 있는 샘플 상관계수 그래프
