<a id="part-2-double-des-meet-in-the-middle-attack"></a>
# Part 2: Double-DES 중간 일치 공격

**한국어** | [English](../../../en/labs/lab02/part2_double_des_mitm/README.md)

**예상 소요 시간:** 35분. **실행 환경:** 수업용 Docker 컨테이너.

독립적인 두 축소 공간 키가 `C = E_K2(E_K1(P))` 방식으로 레코드를 보호합니다.
알려진 쌍 두 개와 중간 일치(MITM) 탐색으로 두 키 ID를 모두 복구한 뒤
레코드를 복호화하세요.

`double_des_mitm.py`는 **0바이트 파일**로 제공됩니다. import와 `main()`을
포함한 전체 프로그램을 작성하세요. 예제는 탐색을 수행하지 않고 구성 방식과
파일 형식을 보여 줍니다. 함수는 import해서 사용할 수 있도록 작성하세요.

<a id="1-run-and-understand-the-samples"></a>
## 1. 예제 실행 및 이해

[수업용 컨테이너](../README.md#setup)를 준비한 뒤 컨테이너 안에서 실행하세요.

```console
cd /workspace/labs/lab02/part2_double_des_mitm
python3 samples/double_des_roundtrip.py
python3 samples/data_loading.py
```

왕복 예제를 실행 순서대로 읽어 보세요. 공개 예시 키 ID `17`과 `93`은 각각
8비트 공간을 사용합니다. 18바이트 평문에 `0x06` 6개를 추가하면 DES 블록 3개인
24바이트가 됩니다. 암호화는 `key1`, `key2` 순서로 적용하며 복호화는 역순입니다.
다음 출력을 확인하세요.

```text
Plaintext: b'Hello, Double DES!'
Recovered: b'Hello, Double DES!'
Intermediate-value check: OK
Double-DES round-trip check: OK
```

중간값 검사는 첫 번째 암호화 결과와 첫 번째 복호화 결과를 비교합니다.
올바른 키에서는 `E_K1(P) = D_K2(C)`가 성립하며, 이것이 탐색 테이블의
근거입니다. **두 계층을 적용하기 전에 한 번 패딩하고, 두 계층을 모두 복호화한
뒤 한 번 패딩을 제거하세요.** 중간 데이터는 이미 완전한 블록들로 이루어져
있습니다.

데이터 읽기 예제는 `Bits per key ID: 16`, `Known pairs: 2`, 각 쌍의
8바이트 블록, `Public data shape check: OK`를 출력합니다. 실제 문제는
예제의 8비트와 달리 **키당 16비트**를 사용합니다. JSON 쌍의 문자열에는
`bytes.fromhex()`가 필요하며, 바이너리 형식의 암호화 레코드에는
`read_bytes()`가 필요합니다.

<a id="2-write-and-check-double_encrypt"></a>
## 2. `double_encrypt()` 작성 및 확인

`double_des_mitm.py`에 다음 인터페이스를 구현하세요.

```python
double_encrypt(block: bytes, key1: bytes, key2: bytes) -> bytes
```

8바이트 블록 하나와 인코딩된 DES 키 두 개를 받습니다. 구성 방식에 맞는 순서로
`common.des`의 `encrypt_block()`을 사용하세요. 블록에 패딩을 추가하거나
제거하지 마세요.

예제는 공통 보조 함수의 import 방법을 보여 줍니다. 실습 파일은 `samples/`보다
한 디렉토리 위에 있으므로 경로를 조정하세요.

복호화를 추가하기 전에 이 함수를 확인하세요.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt
from common.des import encrypt_bytes, make_des_key
block = b"CRYPTO26"
key1, key2 = make_des_key(7, 8), make_des_key(91, 8)
expected = encrypt_bytes(encrypt_bytes(block, key1), key2)
assert double_encrypt(block, key1, key2) == expected
print("Double-DES encryption check: OK")
PY
```

예상 출력은 `Double-DES encryption check: OK`입니다. 이 공개 예시 키는
실제 문제와 무관합니다.

<a id="3-write-and-check-double_decrypt"></a>
## 3. `double_decrypt()` 작성 및 확인

대응하는 단일 블록 인터페이스를 구현하세요.

```python
double_decrypt(block: bytes, key1: bytes, key2: bytes) -> bytes
```

키를 역순으로 적용하여 `decrypt_block()`을 두 번 사용합니다. 패딩을 추가하거나
제거하지 마세요. 2단계에서 완성한 함수를 사용해 다음 검사를 실행하세요.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt, double_decrypt
from common.des import make_des_key
block = b"CRYPTO26"
key1, key2 = make_des_key(7, 8), make_des_key(91, 8)
assert double_decrypt(double_encrypt(block, key1, key2), key1, key2) == block
print("Double-DES decryption check: OK")
PY
```

`Double-DES decryption check: OK`가 출력된 뒤 다음 단계로 진행하세요.

<a id="4-write-and-check-recover_keys"></a>
## 4. `recover_keys()` 작성 및 확인

다음을 구현하세요.

```python
recover_keys(pairs: list[tuple[bytes, bytes]], key_bits: int) -> list[tuple[int, int]]
```

입력 튜플마다 `(plaintext, ciphertext)`가 들어 있습니다. 인코딩된 키 바이트가
아닌, 검증된 `(key1_id, key2_id)` 튜플의 리스트를 반환하세요.

1. 쌍이 두 개 미만이거나 `key_bits`가 `1..20` 범위를 벗어나면 `ValueError`를
   발생시키세요.
2. 첫 번째 키의 각 ID에 대해 첫 번째 평문의 중간값을 계산합니다. 충돌을
   보존하도록 중간 바이트열을 ID의 **리스트**에 매핑하세요.
3. 첫 번째 암호문에서 역방향으로 모든 두 번째 키 ID를 적용하여 일치하는
   중간값을 찾으세요.
4. 남은 쌍들로 후보를 검증하고 검증된 쌍만 반환하세요.

두 키의 매핑 모두 `make_des_key()`를 사용하세요. 모든 첫 번째 키와 두 번째 키의
조합을 중첩 반복문으로 전수 조사하는 방식을 기본 방법으로 사용하지 마세요.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt, recover_keys
from common.des import make_des_key
bits, id1, id2 = 8, 7, 91
key1, key2 = make_des_key(id1, bits), make_des_key(id2, bits)
pairs = [(block, double_encrypt(block, key1, key2))
         for block in (b"CRYPTO26", b"BLOCK-02")]
assert recover_keys(pairs, bits) == [(id1, id2)]
for bad_pairs, bad_bits in ((pairs[:1], bits), (pairs, 21)):
    try:
        recover_keys(bad_pairs, bad_bits)
    except ValueError:
        pass
    else:
        raise AssertionError("reject invalid search parameters")
print("MITM small-fixture check: OK")
PY
```

예상 출력은 `MITM small-fixture check: OK`입니다. 각 키 공간의 후보가
256개뿐인 상태에서 실패 원인을 해결하세요.

<a id="5-write-and-check-decrypt_flag"></a>
## 5. `decrypt_flag()` 작성 및 확인

다음을 구현하세요.

```python
decrypt_flag(encrypted: bytes, key1_id: int, key2_id: int, key_bits: int) -> bytes
```

ID를 키로 매핑하고 각 블록의 두 암호화 계층을 역순으로 복호화한 뒤,
패딩된 메시지를 합치고 `unpad8()`을 한 번 호출하세요. `decrypt_bytes()`를
사용해도 됩니다. 패딩이 제거된 바이트열을 반환합니다.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import decrypt_flag
from common.des import encrypt_bytes, make_des_key, pad8
message, bits, id1, id2 = b"public Double-DES demo", 8, 7, 91
key1, key2 = make_des_key(id1, bits), make_des_key(id2, bits)
encrypted = encrypt_bytes(encrypt_bytes(pad8(message), key1), key2)
assert decrypt_flag(encrypted, id1, id2, bits) == message
print("Double-DES record check: OK")
PY
```

예상 출력은 `Double-DES record check: OK`입니다. 탐색 없이 여러 블록 처리,
계층 순서, 마지막 패딩 제거를 검사합니다.

<a id="6-write-main-and-connect-the-files"></a>
## 6. `main()` 작성 및 파일 연결

실행 가드가 있는 진입점과 `main() -> None`을 구현하세요. Part 디렉토리와
Lab02 디렉토리에서 모두 동작하도록 `__file__`을 기준으로 `data/`를 찾습니다.

`data/known_pairs.json`을 JSON으로 읽으세요. `key_bits`가 각 키의 공간을
결정하며, 각 `pairs` 항목에는 16진수 `plaintext`와 `ciphertext`가 들어
있습니다. 데이터 읽기 예제처럼 블록으로 변환하세요.

`time.perf_counter()`로 `recover_keys()`의 실행 시간을 측정하고 초 단위 시간과
검증된 쌍의 수를 출력하세요. 제공된 문제에서는 정확히 한 쌍이 나와야 합니다.
0개나 여러 개가 나오는 경우도 명확히 처리하세요. 복구한 두 ID를 출력하고
`data/encrypted_flag.bin`을 읽은 뒤 `decrypt_flag()`를 호출하여 ASCII 결과를
출력합니다.

```console
python3 -c 'import double_des_mitm; print("Import check: OK")'
```

import 시 탐색이 시작되지 않고 `Import check: OK`만 출력되어야 합니다.

<a id="7-run-the-supplied-instance-and-finish"></a>
## 7. 제공된 문제 실행 및 마무리

```console
python3 double_des_mitm.py
cd /workspace/labs/lab02
make grade PART=2
```

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part2_double_des_mitm/double_des_mitm.py
verified_pairs=<verified pair count> elapsed=<seconds>s
key1_id=<recovered first ID> key2_id=<recovered second ID>
FLAG{<recovered value>}
```

세 함수 검사와 import 검사가 통과하고, 알려진 두 쌍으로 복구한 키 쌍을
검증할 수 있고, 레코드가 복호화되며, 해당 Part의 채점 검사가 통과하면
완료입니다. 제공된 16비트 매개변수를 유지하세요. 모든 Part를 마친 뒤에는
`PART` 없이 `make grade`를 실행합니다.

<a id="checkpoint-questions"></a>
## 확인 질문

소요 시간, 검증된 쌍의 수, 정방향 테이블의 후보 수, 서로 다른 중간값 수를
보고하세요. 후보 ID는 `2**key_bits`개이며, 충돌 때문에 서로 다른 딕셔너리
키의 수는 줄어들 수 있습니다. 다음을 설명하세요.

1. 단순 탐색에 약 `2**(2*n)`번의 연산이 필요한 이유는 무엇인가요?
2. MITM은 작업량과 메모리 요구량을 어떻게 바꾸나요?
3. 테이블 항목마다 ID 리스트를 유지해야 하는 이유는 무엇인가요?
4. 일치 결과를 다른 쌍으로 검증해야 하는 이유는 무엇인가요?
5. 암호를 두 번 적용해도 보안 강도가 자동으로 두 배가 되지 않는 이유는 무엇인가요?

키나 평문을 하드코딩하지 마세요. 플래그는 지정된 수업 채널로 제출하고
공개 코드나 예제 출력에 포함하지 마세요.

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 스크린샷에서 확인할 수 있는 검증된 쌍의 수와 소요 시간
- [ ] 예상 정방향 테이블 크기, 실제 후보 수, 서로 다른 중간값 수
