<a id="part-5-padding-oracle-attack"></a>
# Part 5: 패딩 오라클 공격

**한국어** | [English](../../../en/labs/lab02/part5_padding_oracle/README.md)

**실행 환경:** 수업용 Docker 컨테이너와 제공된 로컬 Lab02 대상.

로컬 오라클은 수정된 AES-CBC 패킷의 PKCS#7 패딩이 유효한지만 알려 줍니다.
이 불리언 응답을 이용해 보호된 평문을 복구하세요. 복구한 메시지에는
`FLAG{...}`가 들어 있습니다.

제공된 `padding_oracle.py`는 0바이트 학생용 파일입니다. import, 함수,
`main()`, 실행 가드를 작성하세요. 복구 함수는 대상에 연결하지 않고 import할 수
있어야 합니다. 제공된 `oracle_client.py`가 로컬 프로토콜을 처리하고 요청 수를
계산합니다.

<a id="1-run-and-understand-the-sample"></a>
## 1. 예제 실행 및 이해

[Lab02 환경 준비](../README.md#setup)에 따라 수업용 컨테이너에 접속한 뒤
다음을 실행하세요.

```console
cd /workspace/labs/lab02/part5_padding_oracle
python3 samples/padding_demo.py
```

예제는 공개 메시지와 표준 PKCS#7 함수를 사용하며 다음을 출력합니다.

```text
message: b'Sample record'
padded: b'Sample record\x03\x03\x03'
length: 13 -> 16 bytes
valid suffix: True
damaged suffix: rejected
```

패딩 접미부의 모든 바이트가 마지막 패딩 바이트와 일치해야 함을 관찰하세요.
마지막 바이트가 그대로여도 접미부 안의 다른 바이트를 바꾸면 패딩이 유효하지
않습니다. 예제의 `local_example()`과 `main()`을 읽으며 바이트 처리, 예외 처리,
출력을 따라가세요.

수업용 패킷은 `IV || C_1 || C_2 || ...`이며 블록 크기는 16바이트입니다.
`OracleClient.query(packet)`은 `True` 또는 `False`를 반환하며 평문은
공개하지 않습니다. 개발할 때 대상의 실행별 질의 제한을 고려하세요.

<a id="2-implement-one-block-recovery-and-check-it"></a>
## 2. 단일 블록 복구 구현 및 확인

`padding_oracle.py`에 구현하세요.

```python
recover_block(previous: bytes, target: bytes, query: Callable[[bytes], bool]) -> bytes
```

`previous`는 IV 또는 이전 암호문 블록이며, `target`은 평문을 복구하려는
암호문 블록입니다. 둘 다 16바이트입니다. 패딩 바이트를 포함한 16바이트 평문
블록을 반환하세요. `query`의 불리언 결과만 사용합니다. 오른쪽에서 왼쪽으로
복구하며, 후보를 받아들이기 전에 1바이트 패딩에서 생길 수 있는 모호성을
해결하세요.

공개 테스트 값만 사용하는 작은 메모리 내 오라클로 확인하세요. 복구 함수가
받는 것은 콜백, 블록, 불리언 응답뿐입니다. 이 테스트에 키가 있는 이유는
응답을 만들기 위해서입니다.

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from padding_oracle import recover_block

key, iv = bytes(range(16)), bytes(range(16, 32))
message = b"Sample record"
padded = pad(message, 16)
target = AES.new(key, AES.MODE_CBC, iv).encrypt(padded)

def query(packet: bytes) -> bool:
    if len(packet) < 32 or len(packet) % 16:
        return False
    candidate_iv, candidate_ciphertext = packet[:16], packet[16:]
    clear = AES.new(key, AES.MODE_CBC, candidate_iv).decrypt(candidate_ciphertext)
    try:
        unpad(clear, 16)
        return True
    except ValueError:
        return False

assert recover_block(iv, target, query) == padded
print("One-block recovery: OK")
PY
```

복구한 블록이 공개된 패딩 적용 메시지와 일치하면 다음 단계로 진행하세요.

<a id="3-implement-full-packet-recovery-and-check-it"></a>
## 3. 전체 패킷 복구 구현 및 확인

다음을 구현하세요.

```python
recover_plaintext(packet: bytes, query: Callable[[bytes], bool]) -> bytes
```

패킷을 IV와 암호문 블록으로 나누세요. 각 블록에 검사를 마친 `recover_block()`을
재사용하고, 복구한 블록을 합친 뒤 마지막 PKCS#7 접미부를 검사하여 패딩 없는
평문을 반환합니다. 암호문 블록이 여러 개인 패킷도 처리하세요.

다음 공개 2블록 테스트를 사용하세요. 콜백은 로컬 대상과 마찬가지로 불리언만
반환하는 인터페이스입니다.

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from padding_oracle import recover_plaintext

key, iv = bytes(range(16)), bytes(range(16, 32))
message = b"Sample message across two blocks"
packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))

def query(candidate: bytes) -> bool:
    if len(candidate) < 32 or len(candidate) % 16:
        return False
    clear = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
    try:
        unpad(clear, 16)
        return True
    except ValueError:
        return False

assert recover_plaintext(packet, query) == message
print("Full-packet recovery: OK")
PY
```

`Full-packet recovery: OK`가 출력된 뒤에만 다음 단계로 진행하세요.

<a id="4-observe-the-supplied-target-interface"></a>
## 4. 제공된 대상 인터페이스 관찰

저장소 루트의 **호스트 터미널**에서 로컬 대상을 시작하세요.

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

정상 상태인 `healthy`가 되면 수업용 컨테이너의 Part 디렉토리에서 실행하세요.

```console
python3 samples/padding_demo.py --target
```

오프라인 출력에 이어 암호문 블록 수, 원래 패킷의 패딩 유효성 결과, 질의 수
`1`이 출력됩니다. 정상 패킷의 패딩은 유효해야 합니다. 예제는
`data/ciphertext.hex`를 읽어 패킷을 변경 없이 제출하며, 복구는 수행하지
않습니다.

<a id="5-write-the-program-entry-point"></a>
## 5. 프로그램 진입점 작성

`padding_oracle.py`에 `main()`과 실행 가드를 작성하세요.

1. `data/ciphertext.hex`를 읽고 16진수 텍스트를 바이트열로 변환합니다.
2. `with` 블록으로 `OracleClient()`를 엽니다.
3. 패킷과 `oracle.query`를 `recover_plaintext()`에 전달합니다.
4. 복구한 메시지와 `oracle.queries`를 출력합니다.

Part 디렉토리에서 실행할 수 있도록 예제의 경로 처리 방식을 따르세요.
복구 함수는 클라이언트와 데이터 파일에 독립적으로 작성합니다.

<a id="6-run-the-complete-exercise"></a>
## 6. 전체 실습 실행

```console
python3 padding_oracle.py
```

출력에는 `FLAG{...}` 형식의 복구 메시지와 오라클 질의 수가 포함되어야 합니다.
질의 수는 구현에 따라 달라질 수 있습니다. 각 평문 바이트는 패킷 수정과
불리언 질의 인터페이스를 통해 얻어야 합니다.

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part5_padding_oracle/padding_oracle.py
FLAG{<recovered value>}
oracle queries: <query count>
```

Lab02 디렉토리에서 해당 Part의 구현 검사를 실행하세요.

```console
cd /workspace/labs/lab02
make grade PART=5
```

대상의 질의 제한에 도달하면 반복문을 점검한 뒤 호스트 터미널에서 대상을
초기화하고 정상 상태가 될 때까지 기다리세요.

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

<a id="7-completion-and-report"></a>
## 7. 완료 기준 및 보고서

- [ ] 단일 블록과 전체 패킷의 공개 검사가 통과합니다.
- [ ] 최종 프로그램이 제공된 패킷을 읽고 오라클 응답만 사용합니다.
- [ ] 모든 평문 블록을 복구하고 패딩을 검사하며 `FLAG{...}`를 출력합니다.
- [ ] 질의 수를 출력하고 Part 5 구현 검사가 통과합니다.
- [ ] 보고서에서 불리언 응답이 드러내는 정보와 이전 블록이 대상 평문 블록에
      미치는 영향을 설명합니다.

학생 프로그램, 질의 수, 설명을 제출하세요. 플래그는 강사가 지정한 채널로
제출합니다. Part 6을 계속한다면 대상을 실행해 두고, 그렇지 않으면 호스트
터미널에서 중지하세요.

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

<a id="checkpoint-questions"></a>
## 확인 질문

1. 불리언 오라클은 수정한 패킷에 대해 어떤 정보를 알려 주나요?
2. 이 작은 정보만으로 전체 평문 블록을 알아낼 수 있는 이유는 무엇인가요?
3. 인증되지 않은 입력에 대해 수신자가 구별 가능한 패딩 오류를 반환하면 안 되는
   이유는 무엇인가요?
4. 이 Part는 CBC의 XOR 관계를 Part 4의 공격과 어떻게 연결하나요?

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 스크린샷에서 확인할 수 있는 오라클 질의 수
