<a id="part-3-aes-cbc-and-pkcs7"></a>
# Part 3: AES-CBC와 PKCS#7

**한국어** | [English](../../../en/labs/lab02/part3_aes_cbc_pkcs7/README.md)

**예상 소요 시간:** 35분. **실행 환경:** 수업용 Docker 컨테이너.

단일 블록 AES 기본 연산으로 PKCS#7 패딩과 AES-CBC를 구현한 뒤 제공된
레코드를 복호화합니다. 키와 IV는 실습 입력으로 제공되며, 알려지지 않은 AES 키를
복구하는 것이 목표는 아닙니다.

`aes_cbc_pkcs7.py`는 **0바이트 파일**로 제공됩니다. import, 함수, 파일 읽기,
출력, 실행 가드가 있는 진입점을 작성하세요. 함수를 import할 때 문제 파일이
처리되지 않도록 하세요.

<a id="1-run-and-understand-the-library-sample"></a>
## 1. 라이브러리 예제 실행 및 이해

[수업용 컨테이너](../README.md#setup)를 준비한 뒤 컨테이너 안에서 실행하세요.

```console
cd /workspace/labs/lab02/part3_aes_cbc_pkcs7
python3 samples/aes_cbc_demo.py
```

메시지 패딩, 암호화, 복호화, 패딩 제거, 일치 확인으로 이어지는 예제의 실행
흐름을 읽어 보세요. 공개 예시 키와 IV, 라이브러리의 CBC와 패딩 기능으로
예상 동작을 보여 줍니다. 다음 출력을 확인하세요.

```text
Plaintext: b'Hello, AES-CBC!'
Lengths: 15 bytes -> 16 padded bytes
Recovered: b'Hello, AES-CBC!'
AES-CBC round-trip check: OK
Aligned input: 16 bytes -> 32 padded bytes
Full-block padding: 10101010101010101010101010101010
Malformed padding rejected: OK
```

15바이트 메시지에는 `0x01` 한 바이트가 필요합니다. 블록 경계에 맞는 메시지에는
`0x10` 16개로 이루어진 블록 전체가 필요합니다. 출력되는 16진수 `10`은
10진수 16을 뜻합니다. AES 복호화 후에도 패딩은 남으며, 제거하기 전에 검사해야
합니다. 마지막 바이트 `0x00`은 유효한 PKCS#7 길이가 될 수 없습니다.

**필수 함수에서는 CBC와 패딩을 직접 구현해야 합니다.**
`AES.new(key, AES.MODE_ECB)`는 단일 블록 AES 기본 연산으로만 사용하세요.
필수 함수 안에서 `AES.MODE_CBC`, 라이브러리 패딩 보조 함수, 다른 라이브러리의
운용 모드 구현을 사용하지 마세요. 예제와 테스트 명령은 독립적인 비교 기준으로
라이브러리 연산을 사용합니다.

<a id="2-write-and-check-pkcs7_pad"></a>
## 2. `pkcs7_pad()` 작성 및 확인

`aes_cbc_pkcs7.py`에 구현하세요.

```python
pkcs7_pad(data: bytes, block_size: int = 16) -> bytes
```

1바이트부터 `block_size`바이트까지 추가하며, 각 바이트 값은 모두 패딩 길이와
같아야 합니다. 블록 경계에 맞는 입력과 빈 입력에는 패딩 블록 전체를 추가하세요.
새 바이트열을 반환합니다. 블록 크기는 `1..255`를 지원하며, 유효하지 않으면
`ValueError`를 발생시키세요.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import pkcs7_pad
assert pkcs7_pad(b"") == b"\x10" * 16
assert pkcs7_pad(b"hello") == b"hello" + b"\x0b" * 11
assert pkcs7_pad(b"A" * 16) == b"A" * 16 + b"\x10" * 16
assert pkcs7_pad(b"A" * 17) == b"A" * 17 + b"\x0f" * 15
assert pkcs7_pad(b"hello", 8) == b"hello" + b"\x03" * 3
print("PKCS#7 padding checks: OK")
PY
```

예상 출력은 `PKCS#7 padding checks: OK`입니다. 실패 원인을 해결한 뒤
계속하세요.

<a id="3-write-and-check-pkcs7_unpad"></a>
## 3. `pkcs7_unpad()` 작성 및 확인

다음을 구현하세요.

```python
pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes
```

비어 있거나 블록 경계에 맞지 않는 입력, `1..block_size`를 벗어나는 패딩 길이,
모든 바이트가 패딩 길이와 같지 않은 접미부는 거부하세요. 잘못된 입력이나
유효하지 않은 블록 크기에는 `ValueError`를 발생시킵니다. 성공하면 원래의
바이트열을 반환하세요.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import pkcs7_pad, pkcs7_unpad
for message in (b"", b"hello", b"A" * 16, b"A" * 33):
    assert pkcs7_unpad(pkcs7_pad(message)) == message
assert pkcs7_unpad(pkcs7_pad(b"hello", 8), 8) == b"hello"
for invalid in (b"", b"short", b"A" * 15 + b"\x00",
                b"A" * 15 + b"\x11", b"A" * 14 + b"\x01\x02"):
    try:
        pkcs7_unpad(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed padding accepted")
print("PKCS#7 validation checks: OK")
PY
```

예상 출력은 `PKCS#7 validation checks: OK`입니다. 마지막 오류 사례를
검출하려면 마지막 바이트뿐 아니라 모든 패딩 바이트를 확인해야 합니다.

<a id="4-write-and-check-xor_bytes"></a>
## 4. `xor_bytes()` 작성 및 확인

다음을 구현하세요.

```python
xor_bytes(left: bytes, right: bytes) -> bytes
```

길이가 같은 입력의 바이트별 XOR 결과를 반환하세요. 길이가 다르면 조용히
잘라내지 말고 `ValueError`를 발생시키세요.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import xor_bytes
assert xor_bytes(b"\x00\xff", b"\x55\x0f") == b"\x55\xf0"
try:
    xor_bytes(b"a", b"ab")
except ValueError:
    pass
else:
    raise AssertionError("unequal XOR lengths accepted")
print("XOR checks: OK")
PY
```

예상 출력은 `XOR checks: OK`입니다.

<a id="5-write-and-check-cbc_encrypt"></a>
## 5. `cbc_encrypt()` 작성 및 확인

다음을 구현하세요.

```python
cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes
```

직접 작성한 함수로 평문을 패딩하세요. 각 16바이트 AES 블록에 대해
`C_i = E_K(P_i XOR C_(i-1))`를 계산하며, 첫 번째 이전 블록으로는 IV를
사용합니다. 직접 작성한 XOR 함수와 AES-ECB를 사용하세요. IV를 제외한
암호문만 반환합니다. IV 길이가 16이 아니면 `ValueError`를 발생시키세요.

공개 NIST 벡터로 바로 확인하세요.

```console
python3 - <<'PY'
import json
from pathlib import Path
from aes_cbc_pkcs7 import cbc_encrypt
vector = json.loads(Path("data/nist_cbc_vector.json").read_text())
key, iv = bytes.fromhex(vector["key"]), bytes.fromhex(vector["iv"])
plaintext = bytes.fromhex(vector["plaintext"])
expected = bytes.fromhex(vector["cbc_ciphertext_without_pkcs7_final_block"])
actual = cbc_encrypt(key, iv, plaintext)
assert actual[:len(expected)] == expected
assert len(actual) == len(expected) + 16
print("NIST CBC encryption check: OK")
PY
```

예상 출력은 `NIST CBC encryption check: OK`입니다. 벡터에는 패딩이 없지만
여러분의 함수는 마지막에 블록 전체를 추가하므로, 출력의 앞부분을 벡터와
비교하세요.

<a id="6-write-and-check-cbc_decrypt"></a>
## 6. `cbc_decrypt()` 작성 및 확인

다음을 구현하세요.

```python
cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes
```

16바이트가 아닌 IV, 빈 암호문, 블록 경계에 맞지 않는 암호문에는
`ValueError`를 발생시키세요. 각 블록에 대해 `P_i = D_K(C_i) XOR C_(i-1)`를
계산합니다. 다음 블록에 필요한 암호문을 보존하고 패딩된 평문을 합친 뒤,
직접 작성한 `pkcs7_unpad()`로 패딩을 한 번 검사하고 제거하세요.

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from aes_cbc_pkcs7 import cbc_encrypt, cbc_decrypt
key, iv = bytes(range(16)), bytes(range(16, 32))
for message in (b"", b"hello", b"A" * 16, b"A" * 33):
    reference = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    assert cbc_encrypt(key, iv, message) == reference
    assert cbc_decrypt(key, iv, reference) == message
for malformed in (b"", b"x"):
    try:
        cbc_decrypt(key, iv, malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed ciphertext accepted")
invalid_padding = AES.new(key, AES.MODE_CBC, iv).encrypt(b"A" * 15 + b"\x00")
try:
    cbc_decrypt(key, iv, invalid_padding)
except ValueError:
    pass
else:
    raise AssertionError("invalid padding accepted after decryption")
print("CBC decryption and round-trip checks: OK")
PY
```

예상 출력은 `CBC decryption and round-trip checks: OK`입니다. 빈 메시지,
짧은 메시지, 블록 경계에 맞는 메시지, 여러 블록의 메시지를 독립적으로
비교합니다. 라이브러리 모드와 패딩 호출은 테스트 데이터 생성·검증에 사용되는
것이며, 필수 구현에 포함하면 안 됩니다.

<a id="7-write-main-run-the-record-and-finish"></a>
## 7. `main()` 작성, 레코드 실행 및 마무리

실행 가드가 있는 진입점과 `main() -> None`을 구현하세요. Part 디렉토리와
Lab02 디렉토리에서 모두 실행할 수 있도록 `__file__`을 기준으로 `data/`를
찾습니다.

| 입력 | 의미 |
| --- | --- |
| `data/key.bin` | 바이트열로 읽는 AES 키 |
| `data/iv.bin` | 바이트열로 읽는 CBC IV |
| `data/encrypted_flag.bin` | 바이트열로 읽는 암호문 |
| `data/nist_cbc_vector.json` | 위에서 사용한 공개 정답 검증 벡터 |

이 바이너리 입력으로 직접 작성한 `cbc_decrypt()`를 호출하고 ASCII 평문을
출력하세요. 문제의 키를 출력하거나 코드에 넣지 말고, 복호화 메시지를
하드코딩하지 마세요.

```console
python3 -c 'import aes_cbc_pkcs7; print("Import check: OK")'
python3 aes_cbc_pkcs7.py
cd /workspace/labs/lab02
make grade PART=3
```

import하면 `Import check: OK`만, 직접 실행하면 `FLAG{...}`가 출력되어야
합니다. 다섯 함수 검사가 모두 통과하고, CBC가 AES-ECB를 기본 연산으로만
사용하며, 패딩을 검사하고, 제공된 레코드를 복호화하며, 해당 Part의 채점 검사가
통과하면 완료입니다. 모든 Part를 마친 뒤에는 `make grade`를 실행하세요.

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part3_aes_cbc_pkcs7/aes_cbc_pkcs7.py
FLAG{<recovered value>}
```

<a id="checkpoint-questions"></a>
## 확인 질문

확인한 사례와 결과를 보고한 뒤 다음을 설명하세요.

1. 블록 경계에 맞는 평문에도 패딩 블록 전체를 추가해야 하는 이유는 무엇인가요?
2. IV는 첫 CBC 블록에 어떤 역할을 하나요?
3. 암호문 블록 하나를 수정하면 어떤 평문 블록이 바뀔 수 있나요?
4. 패딩이라고 명시된 모든 바이트를 검사해야 하는 이유는 무엇인가요?
5. AES-ECB가 여기서는 단일 블록 기본 연산으로만 적합한 이유는 무엇인가요?
   여러 블록의 메시지에 ECB 모드를 직접 적용할 때의 보안 특성과 비교하세요.

플래그는 지정된 수업 채널로 제출하고 공개 코드나 예제 출력에 포함하지 마세요.

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 구현 검사 결과(`make grade PART=3`, 전체 실습 완료 후 `make grade`)
