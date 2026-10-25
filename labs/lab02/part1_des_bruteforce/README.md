<a id="part-1-des-brute-force-attack"></a>
# Part 1: DES 전수 조사 공격

**한국어** | [English](../../../en/labs/lab02/part1_des_bruteforce/README.md)

**예상 소요 시간:** 25분. **실행 환경:** 수업용 Docker 컨테이너.

알려진 평문·암호문 블록 한 쌍으로 축소된 공간의 DES 키를 복구하고, 별도
레코드를 복호화한 뒤 탐색 비용을 측정합니다. 실제 DES의 유효 키 길이는
56비트지만, 이 실습은 제공된 **24비트 키 ID 공간**의 **16,777,216개 후보**만
탐색합니다.

`des_bruteforce.py`는 **0바이트 파일**로 제공됩니다. import, 함수, 파일 읽기,
출력, 진입점을 포함한 전체 프로그램을 작성하세요. 예제는 제공된 API의 사용법을
보여 주며 탐색을 수행하지 않습니다. 함수를 import해도 실제 문제의 탐색이
시작되지 않도록 작성하세요.

<a id="1-run-and-understand-the-samples"></a>
## 1. 예제 실행 및 이해

[수업용 컨테이너](../README.md#setup)를 준비하세요. 아래 명령은 모두
**컨테이너 안**에서 실행합니다.

```console
cd /workspace/labs/lab02/part1_des_bruteforce
python3 samples/des_roundtrip.py
python3 samples/data_loading.py
```

두 예제를 import부터 `main()`과 실행 가드까지 읽어 보세요. 왕복 예제는
**8비트 예제 공간**의 공개 예시 ID `17`로 키를 구성하고 `b"Hello, DES!"`에
패딩을 적용한 뒤, 암호화·복호화하고 패딩을 제거합니다. 다음 출력을 확인하세요.

```text
Plaintext: b'Hello, DES!'
Lengths: 11 bytes -> 16 padded bytes
Recovered: b'Hello, DES!'
Padding round-trip check: OK
```

DES는 8바이트 블록을 처리합니다. 덧붙이는 5바이트는 모두 `0x05`이며,
복호화한 뒤에도 `unpad8()`이 검사하고 제거하기 전까지 남아 있습니다.
키와 암호문은 16진수로 표시되지만 보조 함수는 `bytes`를 처리합니다.
평문이 8바이트이면 `pad8()`은 `0x08` 8개로 이루어진 블록 전체를 추가합니다.
해당 길이로 바꿔 왕복 결과를 확인하세요.

데이터 읽기 예제는 `Key-ID bits: 24`, 8바이트의 알려진 평문·암호문 블록,
8의 배수인 암호화 레코드 길이를 출력합니다. 마지막 줄은
`Public data shape check: OK`입니다. `json.loads()`로 매개변수를,
`read_bytes()`로 바이너리 파일을 읽습니다. 알려진 블록은 이미 정확히
8바이트이므로 **후보 비교를 위해 패딩을 추가하지 마세요**. 별도 레코드에는
패딩이 적용되어 있습니다. 두 예제 모두 문제의 키를 복구하지 않습니다.

<a id="2-write-and-check-brute_force"></a>
## 2. `brute_force()` 작성 및 확인

`des_bruteforce.py`에 다음 인터페이스를 구현하세요.

```python
brute_force(plaintext: bytes, ciphertext: bytes, key_bits: int) -> tuple[int | None, int, float]
```

요구되는 결정적 키 매핑에는 `common.des`의 `make_des_key(key_id, key_bits)`를
사용하세요. 정수 ID 자체가 인코딩된 키는 아닙니다. `encrypt_block(block, key)`는
8바이트 블록과 8바이트 키를 받습니다. 공통 보조 함수의 import 방법은 예제를
참고하되, 실습 파일은 `samples/`보다 한 디렉토리 위에 있으므로 경로를
조정하세요.

1. `key_bits`가 `1..MAX_KEY_BITS` 범위를 벗어나면 `ValueError`를 발생시키세요.
   `MAX_KEY_BITS`는 24입니다.
2. `0`부터 `2**key_bits - 1`까지 ID를 순서대로 검사합니다. 각 ID를 키로
   매핑하고 알려진 블록을 암호화하세요.
3. 첫 일치에서 멈추고 `(key_id, tested, elapsed)`를 반환하세요. 일치한 후보도
   검사 횟수에 포함하고, `time.perf_counter()`로 초 단위 시간을 측정합니다.
4. 일치하는 후보가 없으면 `(None, 2**key_bits, elapsed)`를 반환하세요.

작은 공개 테스트 데이터로 이 함수를 바로 확인하세요.

```console
PYTHONPATH=.. python3 - <<'PY'
from des_bruteforce import brute_force
from common.des import encrypt_block, make_des_key
block, bits, expected_id = b"CRYPTO26", 8, 17
ciphertext = encrypt_block(block, make_des_key(expected_id, bits))
found, tested, elapsed = brute_force(block, ciphertext, bits)
assert found == expected_id
assert tested == expected_id + 1
assert elapsed >= 0
try:
    brute_force(block, ciphertext, 25)
except ValueError:
    pass
else:
    raise AssertionError("reject an excessive key space")
print("brute_force small-fixture check: OK")
PY
```

예상 출력은 `brute_force small-fixture check: OK`입니다. 실패 원인을 해결한
뒤 다음 단계로 진행하세요. 예시 ID는 24비트 문제의 정답이 아닙니다.

<a id="3-write-and-check-decrypt_flag"></a>
## 3. `decrypt_flag()` 작성 및 확인

다음을 구현하세요.

```python
decrypt_flag(encrypted: bytes, key_id: int, key_bits: int) -> bytes
```

키를 다시 구성하고 `decrypt_bytes(data, key)`로 모든 블록을 복호화하세요.
전체 평문을 합친 후 `unpad8()`을 한 번 호출하여 패딩을 검사하고 제거합니다.
패딩이 제거된 바이트열을 반환하세요.

```console
PYTHONPATH=.. python3 - <<'PY'
from des_bruteforce import decrypt_flag
from common.des import encrypt_bytes, make_des_key, pad8
message, key_id, bits = b"public demo record", 17, 8
encrypted = encrypt_bytes(pad8(message), make_des_key(key_id, bits))
assert decrypt_flag(encrypted, key_id, bits) == message
print("decrypt_flag small-fixture check: OK")
PY
```

예상 출력은 `decrypt_flag small-fixture check: OK`입니다. 탐색과 별개로
복호화 동작을 검사합니다.

<a id="4-write-main-and-connect-the-files"></a>
## 4. `main()` 작성 및 파일 연결

`main() -> None`을 구현하고 `if __name__ == "__main__":` 아래에서만 호출하세요.
Part 디렉토리와 Lab02 루트 어디서 실행해도 동작하도록 `__file__`을 기준으로
`data/` 위치를 찾으세요.

| 입력 | 읽는 형식 | 용도 |
| --- | --- | --- |
| `data/parameters.json` | JSON | `key_bits`로 탐색 공간 선택 |
| `data/known_plaintext.bin` | bytes | 알려진 8바이트 평문 |
| `data/known_ciphertext.bin` | bytes | 비교할 암호문 |
| `data/encrypted_flag.bin` | bytes | 키 복구 후 복호화할 레코드 |

`brute_force()`를 호출하고 일치 결과가 없을 때도 명확히 처리하세요.
경과 시간이 0인 경우를 처리하면서 `tested / elapsed`로 초당 키 수를 계산하고
`decrypt_flag()`를 호출합니다. 레코드는 ASCII로 디코딩하세요. 복구한 ID,
후보 수, 소요 시간(초), 처리 속도, 평문을 출력합니다.

```console
python3 -c 'import des_bruteforce; print("Import check: OK")'
```

import 시 탐색이 시작되지 않고 `Import check: OK`만 출력되어야 합니다.

<a id="5-run-the-supplied-instance-and-finish"></a>
## 5. 제공된 문제 실행 및 마무리

```console
python3 des_bruteforce.py
cd /workspace/labs/lab02
make grade PART=1
```

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part1_des_bruteforce/des_bruteforce.py
candidate=<key ID> tested=<candidate count> elapsed=<seconds>s rate=<keys per second> keys/s
FLAG{<recovered value>}
```

순차 탐색은 CPU, Docker 자원, 구현에 따라 약 1–3분 걸릴 수 있으며, 끝날 때까지
출력이 없을 수도 있습니다. 인위적인 지연을 넣지 말고 실제 탐색 시간을
측정하세요. 매개변수와 암호문은 함께 유지해야 합니다. `key_bits`만 바꾼다고
숨겨진 키가 바뀌지는 않습니다. 최종 측정에는 원래의 24비트 데이터를 사용하세요.

두 함수 검사와 import 검사가 통과하고, 복구한 키로 알려진 쌍을 검증할 수 있고,
레코드가 `FLAG{...}`로 복호화되며, 해당 Part의 채점 검사가 통과하면 완료입니다.
모든 Part를 마친 뒤에는 `PART` 없이 `make grade`를 실행하세요.

<a id="checkpoint-questions"></a>
## 확인 질문

후보 수, 소요 시간, 측정한 속도를 보고하고 다음 질문에 답하세요.

1. 전체 `2**56`개의 유효 키 대신 축소된 공간을 사용하는 이유는 무엇인가요?
2. 측정한 속도로 `2**56`개를 검사하려면 얼마나 걸리나요? 가정을 명시하세요.
3. Python 실행 시간으로 GPU, FPGA, ASIC의 속도를 예측할 수 없는 이유는 무엇인가요?
4. 패리티 비트의 역할은 무엇이며, ID를 서로 다른 유효 키로 매핑해야 하는 이유는 무엇인가요?
5. 이 결과는 DES의 모든 라운드 함수에 수학적 약점이 있음을 보여 주나요,
   아니면 키 공간 크기의 실질적인 한계를 보여 주나요? 설명하세요.

ID나 복호화 결과를 하드코딩하지 마세요. 플래그는 지정된 수업 채널로만
제출하고 공개 코드나 예제 출력에 포함하지 마세요.

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 스크린샷에서 확인할 수 있는 후보 수, 소요 시간, 초당 키 수
