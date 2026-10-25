<a id="part-4-cbc-bit-flipping-attack"></a>
# Part 4: CBC 비트 플리핑 공격

**한국어** | [English](../../../en/labs/lab02/part4_cbc_bit_flipping/README.md)

**실행 환경:** 수업용 Docker 컨테이너. 제공된 로컬 대상만 사용하세요.

CBC 암호화는 패킷을 인증하지 않습니다. 이 Part에서는 수업용 토큰의 의미를
바꾸는 프로그램을 작성하고 수정 전후의 검증 결과를 비교합니다. 최종적으로
성공한 응답에는 플래그가 포함됩니다.

제공된 `cbc_bit_flipping.py`는 비어 있습니다. import, 함수, `main()`,
실행 가드를 직접 작성하세요. 함수를 import해도 네트워크 요청이 발생하지
않아야 합니다.

<a id="1-run-the-offline-sample"></a>
## 1. 오프라인 예제 실행

[수업용 컨테이너](../README.md#setup)를 준비한 뒤 컨테이너 안에서 실행하세요.

```console
cd /workspace/labs/lab02/part4_cbc_bit_flipping
python3 samples/cbc_token_demo.py
```

예제의 입력, 암호화, 패킷 인코딩, 디코딩, 출력을 읽어 보세요. 수업용 대상과
독립적인 공개 데모 값을 사용합니다.

```text
message: b'Sample token'
packet: 32 bytes = 16 IV + 16 ciphertext
base64 round-trip: True
recovered: b'Sample token'
CBC round-trip: OK
```

바이너리 패킷에 16바이트 IV와 완전한 암호문 블록들이 순서대로 들어 있는지
확인하세요. Base64는 이 바이트들을 표현하는 방식입니다. 패딩을 제거한 복구
메시지는 원래 메시지와 일치합니다.

<a id="2-implement-and-immediately-check-token-modification"></a>
## 2. 토큰 수정 구현 및 즉시 확인

`cbc_bit_flipping.py`에 다음 인터페이스를 구현하세요.

```python
forge_admin_token(normal_token: str) -> str
```

입력과 반환값은 `IV || ciphertext`를 인코딩한 Base64 문자열입니다. 수업용
토큰의 첫 평문 블록에는 ASCII 필드 `admin=0;`가 들어 있습니다. 복호화하면
이 필드가 `admin=1;`이 되는 수정된 패킷을 반환하세요. 패킷 인코딩과 블록
구조는 유지합니다. 다음 CBC 관계를 사용하세요.

```text
P_i = D_K(C_i) XOR C_(i-1)
C_0 = IV
```

이전 블록을 바꿀 때 선택한 평문 바이트가 어떻게 바뀌는지 판단하세요.
함수에서는 서비스의 암호화 키를 사용할 수 없습니다. 서로 다른 IV로 새로 발급한
토큰에도 동작하는 방법이어야 합니다.

서비스 호출을 추가하기 전에 다음 공개 로컬 테스트를 실행하세요. 테스트의 키는
테스트 코드가 패킷을 만들고 확인하는 데만 사용됩니다.

```console
python3 - <<'PY'
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cbc_bit_flipping import forge_admin_token

key = bytes(range(16))
for iv in (bytes(range(16, 32)), bytes([7]) * 16):
    message = b"admin=0;userid=1042"
    packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    original = base64.b64encode(packet).decode("ascii")
    modified = base64.b64decode(forge_admin_token(original), validate=True)
    recovered = unpad(AES.new(key, AES.MODE_CBC, modified[:16]).decrypt(modified[16:]), 16)
    assert len(modified) == len(packet)
    assert b"admin=1;" in recovered
    assert b"userid=1042" in recovered
print("Local token check: OK")
PY
```

두 IV에 대해 `Local token check: OK`가 출력된 뒤에만 다음 단계로 진행하세요.

<a id="3-observe-the-target-client"></a>
## 3. 대상 클라이언트 관찰

저장소 루트의 **호스트 터미널**에서 로컬 대상을 시작하세요.

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

대상이 정상 상태인 `healthy`여야 합니다. 수업용 컨테이너의 Part 디렉토리로
돌아와 다음을 실행하세요.

```console
python3 samples/cbc_token_demo.py --target
```

오프라인 출력에 더해, 예제는 블록 경계에 맞는 대상 패킷과 정상 검증 응답을
출력합니다. 일반 토큰은 관리자 권한을 부여하면 안 됩니다. `client.py`를
수정하지 말고 응답을 관찰하세요.

예제의 대상 연결 분기를 읽어 보세요. 제공된 `client.issue()`는 Base64 토큰을,
`client.verify(token)`은 서비스의 응답 문자열을 반환합니다. 두 함수가 연결을
직접 관리합니다.

<a id="4-write-the-program-entry-point"></a>
## 4. 프로그램 진입점 작성

이제 `cbc_bit_flipping.py`에 `main()`과 실행 가드를 작성하세요.

1. 제공된 클라이언트로 새로운 일반 토큰을 요청합니다.
2. 원래 토큰을 검증하고 응답을 출력합니다.
3. 검사를 마친 `forge_admin_token()` 함수를 호출합니다.
4. 반환된 토큰을 검증하고 응답을 출력합니다.

네트워크 요청은 진입점 안에 두세요. 실행할 때마다 발급받은 토큰에서 수정된
패킷을 만들어야 합니다.

<a id="5-run-the-complete-exercise"></a>
## 5. 전체 실습 실행

```console
python3 cbc_bit_flipping.py
```

원래 응답과 수정 후 응답을 기록하세요. 수정된 토큰의 검증이 성공하면 관리자
권한이 부여되고 `FLAG{...}`가 포함됩니다. 무작위 IV와 토큰 문자열은 실행마다
달라질 수 있습니다.

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행합니다.

```console
python3 part4_cbc_bit_flipping/cbc_bit_flipping.py
normal: <original token response>
modified: <administrator response> FLAG{<recovered value>}
```

이 Part의 구현 검사만 실행하세요.

```console
cd /workspace/labs/lab02
make grade PART=4
```

<a id="6-completion-and-report"></a>
## 6. 완료 기준 및 보고서

- [ ] 두 IV 모두 로컬 테스트를 통과합니다.
- [ ] 프로그램이 새로운 일반 토큰을 요청하고 검증합니다.
- [ ] 수정 후 검증에서 관리자 권한을 얻고 플래그를 반환받습니다.
- [ ] Part 4 구현 검사가 통과합니다.
- [ ] 보고서에서 CBC의 이전 블록이 평문에 미치는 영향을 설명합니다.
- [ ] 보고서에서 암호화만으로 수정이 탐지되지 않은 이유를 설명합니다.

프로그램, 검증 관찰 결과, 설명을 제출하세요. 플래그는 강사가 지정한 채널로
제출합니다. Part 5를 계속할 경우 대상을 실행해 두세요. 대상 사용을 마쳤다면
호스트에서 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

공통 수업용 컨테이너는 계속 사용할 수 있습니다. 정리 방법은
[세션 안내](../README.md#finish-or-restart-a-session)를 참고하세요.

<a id="checkpoint-questions"></a>
## 확인 질문

1. AES 키를 몰라도 공격자가 선택한 평문 바이트를 바꿀 수 있는 이유는 무엇인가요?
2. 암호문 블록의 비트를 바꾸면 수정한 암호문 블록 자체에 대응하는 평문 블록에는
   어떤 영향을 주나요?
3. 이 결과가 AES의 결함이 아니라 무결성 보장의 부재를 보여 주는 이유는 무엇인가요?
4. 이러한 수정을 막으려면 인증 암호에 어떤 속성이 있어야 하나요?

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 스크린샷에서 확인할 수 있는 원래 토큰과 수정한 토큰의 검증 응답
