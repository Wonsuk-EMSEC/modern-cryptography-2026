<a id="part-6-mac-then-encrypt-vs-encrypt-then-mac"></a>
# Part 6: MAC-then-Encrypt와 Encrypt-then-MAC 비교

**한국어** | [English](../../../en/labs/lab02/part6_mte_vs_etm/README.md)

**예상 소요 시간:** 40분. **실행 환경:** 수업용 Docker 컨테이너.
최종 실행에는 로컬 Lab02 대상이 필요합니다.

인증과 암호화의 순서를 이름만으로 알 수 없는 A, B 두 서비스를 비교합니다.
통제된 변경을 설계하고 유용한 패딩 정보 유출을 식별한 뒤, Part 5에서 완성한
공격을 응용하여 취약한 서비스의 보호된 메시지를 복구하세요.

`mte_vs_etm.py`는 **0바이트 파일**로 제공됩니다. import, 함수, 서비스 호출,
출력, 진입점을 작성하세요. 함수를 import할 때 대상에 연결하지 않도록 합니다.
여기에서 메시지 복구를 구현하기 전에 `../part5_padding_oracle/padding_oracle.py`의
Part 5 `recover_plaintext()`를 완성하세요.

<a id="1-run-and-understand-the-offline-sample"></a>
## 1. 오프라인 예제 실행 및 이해

[수업용 컨테이너](../README.md#setup)를 준비하세요. 컨테이너 안에서 실행합니다.

```console
cd /workspace/labs/lab02/part6_mte_vs_etm
python3 samples/service_demo.py
```

`local_example()`과 `main()`을 읽어 보세요. 오프라인 예제는 공개 메시지의
HMAC-SHA-256을 계산하고 태그를 덧붙인 뒤, Base64 인코딩과 디코딩을 거쳐
메시지와 태그를 분리합니다. 예상 출력은 다음과 같습니다.

```text
message: b'Sample record'
HMAC-SHA-256 tag: 32 bytes
public packet: 45 bytes
tag verification: True
```

메시지는 13바이트이고 SHA-256 태그는 고정된 32바이트이므로 Base64 인코딩 전
길이는 45바이트입니다. 인코딩은 표현만 바꾸며 암호화나 인증을 수행하지 않습니다.
`hmac.compare_digest()`가 예제 태그를 새로 계산한 태그와 비교합니다.
이 예제는 공개 데모 키를 사용하며 수업용 비밀이나 복구 알고리즘을 포함하지
않습니다.

최종 실습에는 제공된 `client.py`를 사용합니다. `ServiceClient(name)`은
`"A"` 또는 `"B"`를 받고, `item()`은 이미 디코딩된 바이너리 패킷을 반환하며,
`query(packet)`은 공개 응답 문자열을 반환합니다. 패킷을 직접 인코딩할
필요는 없습니다. 클라이언트는 질의 수를 계산하고 연결 종료를 위한 `with`
블록도 지원합니다.

<a id="2-write-and-check-probe"></a>
## 2. `probe()` 작성 및 확인

`mte_vs_etm.py`에 구현하세요.

```python
probe(service: ServiceClient, packet: bytes) -> tuple[str, str]
```

원래 패킷의 수정 가능한 복사본 두 개를 서로 독립적으로 만드세요. 첫 번째는
바이트 인덱스 `0`을 `1`과 XOR하여 IV 바이트를 수정합니다. 두 번째는 바이트
인덱스 `20`을 `1`과 XOR하여 암호문 바이트를 수정합니다. 이 순서대로 각각을
bytes로 `service.query()`에 제출하고 `(iv_response, ciphertext_response)`를
반환하세요.

두 변경을 한 패킷에 누적하거나, 원본을 수정하거나, 이 보조 함수 안에서
서비스 동작을 추론하지 마세요. 나중에 해석할 관찰 결과만 기록하는 함수입니다.
수업용 패킷은 두 탐색을 모두 수행하기에 충분히 깁니다.

**대상을 실행하지 않고** 패킷 구성부터 확인하세요.

```console
python3 - <<'PY'
from mte_vs_etm import probe
packet = bytes(range(48))
class StubService:
    def __init__(self):
        self.calls = []
    def query(self, candidate):
        assert isinstance(candidate, bytes)
        self.calls.append(candidate)
        return ("IV_RESPONSE", "CIPHERTEXT_RESPONSE")[len(self.calls) - 1]
service = StubService()
assert probe(service, packet) == ("IV_RESPONSE", "CIPHERTEXT_RESPONSE")
expected_iv = bytearray(packet)
expected_iv[0] ^= 1
expected_ciphertext = bytearray(packet)
expected_ciphertext[20] ^= 1
assert service.calls == [bytes(expected_iv), bytes(expected_ciphertext)]
assert packet == bytes(range(48))
print("Independent probe check: OK")
PY
```

예상 출력은 `Independent probe check: OK`입니다. 이 응답 문자열은 테스트용
이름이며, 수업용 두 서비스에서 실제로 관찰한 결과가 아닙니다.

<a id="3-write-and-check-recover_vulnerable_message"></a>
## 3. `recover_vulnerable_message()` 작성 및 확인

다음을 구현하세요.

```python
recover_vulnerable_message(packet: bytes, padding_query: Callable[[bytes], bool]) -> bytes
```

Part 5에서 완성한 `recover_plaintext(packet, query)`를 재사용하거나
수정해서 사용하세요. 형제 Part 디렉토리에서 해당 구현을 import할 수 있도록
만듭니다. 존재하지 않는 시작 코드나 강사용 해답을 import하지 마세요.

제공된 `padding_query` 콜백은 패딩의 유효성을 불리언으로 반환합니다.
먼저 전체 CBC 평문을 복구하고 패딩을 제거하세요. 취약한 구성의 평문에는
`message || HMAC-SHA-256 tag`가 들어 있으므로 패딩을 제거한 뒤 마지막
**32바이트**를 분리하고 메시지 바이트열을 반환합니다. 복구한 내용이 32바이트보다
짧다면 유효한 보호 레코드로 조용히 처리하지 말고 `RuntimeError`를 발생시키세요.
실습에서는 실제 레코드의 태그를 독립적으로 검증할 MAC 키를 제공하지 않습니다.

키가 공개된 간단한 테스트 오라클로 이 래퍼 함수를 확인하세요. 테스트 코드는
보호된 메시지를 구성하고 복호화한 패딩의 유효성만 응답하며, 복구 공격을
구현하지 않습니다.

```console
python3 - <<'PY'
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from mte_vs_etm import recover_vulnerable_message
key, iv, message = bytes(range(16)), bytes(range(16, 32)), b"public demo"
tag = hmac.new(b"public-demo-key", message, hashlib.sha256).digest()
packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message + tag, 16))
counts = {"queries": 0}
def padding_query(candidate):
    counts["queries"] += 1
    if len(candidate) < 32 or len(candidate) % 16:
        return False
    try:
        padded = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
        unpad(padded, 16)
        return True
    except ValueError:
        return False
assert recover_vulnerable_message(packet, padding_query) == message
assert counts["queries"] > 0
print("Oracle recovery and MAC separation check: OK")
PY
```

예상 출력은 `Oracle recovery and MAC separation check: OK`입니다. 실패는
Part 5 복구, 패딩 제거, 잘못된 태그 분리에서 발생할 수 있습니다. 수업용
서비스에 질의하기 전에 해결하세요.

<a id="4-write-main-and-connect-the-client"></a>
## 4. `main()` 작성 및 클라이언트 연결

`main() -> None`과 실행 가드가 있는 진입점을 구현하세요. 모듈을 import할 때는
서비스 클라이언트를 만들지 않고 함수만 정의해야 합니다.

`argparse`로 선택 인자 `--recover-service`를 받고 선택지는 `A`, `B`로
지정하세요. 선택하지 않으면 각 서비스에서 항목을 받아 변경 없이 제출하여
기준 응답을 구하고, `probe()`를 호출한 뒤 원본, IV 변경, 암호문 변경 응답을
출력합니다. 이 관찰을 해석할 수 있도록 여기서 실행을 끝내세요.

서비스를 선택한 경우에는 추가로 해당 서비스에 연결하여 항목을 요청하고,
패킷과 `service.padding_valid` 콜백을 `recover_vulnerable_message()`에
전달하세요. ASCII 메시지와 해당 연결의 `service.queries`를 출력합니다.
컨텍스트 관리자로 연결을 닫으세요.

`padding_valid()`는 `PADDING_OK`와 `ACCEPTED`를 `True`로 매핑합니다.
관찰을 통해 서비스 응답이 유용한 패딩 정보를 드러낸다고 확인한 뒤에만 복구에
사용하세요. 모든 요청을 같은 응답으로 거부하는 서비스는 이 메서드가 있다고
해서 유용한 불리언 오라클이 되지는 않습니다.

```console
python3 -c 'import mte_vs_etm; print("Import check: OK")'
python3 mte_vs_etm.py --help
```

import 시에는 `Import check: OK`만 출력되어야 합니다. `--help`는 연결하지
않고 `--recover-service`와 두 선택지를 안내해야 합니다.

<a id="5-start-the-target-and-compare-live-responses"></a>
## 5. 대상 시작 및 실제 응답 비교

Part 5에서 대상을 계속 실행 중이라면 그대로 사용하세요. 그렇지 않으면 저장소
루트의 **호스트 터미널**에서 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

`lab02-target`이 `healthy`가 될 때까지 기다리세요. 버전이 고정된 GHCR 이미지가
두 서비스를 모두 제공하며, 클라이언트에는 내부 서비스 이름이 이미 설정되어
있습니다. 터미널만 사용하는 경우에는
`docker compose -f docker/compose.yml exec course bash`로 `course`에 접속하세요.

수업용 컨테이너 안에서 실행합니다.

```console
cd /workspace/labs/lab02/part6_mte_vs_etm
python3 samples/service_demo.py --target
python3 mte_vs_etm.py
```

예제는 오프라인 출력을 반복하고 항목을 받은 뒤 변경 없이 제출합니다.
두 원본 응답 모두 `ACCEPTED`여야 하며, 각 기준 응답 연결은 질의 수 1을
보고합니다. 수락 결과는 서비스가 자신의 수정되지 않은 항목을 처리할 수
있음을 보여 줄 뿐, 인증 순서를 알려 주지는 않습니다.

이어서 여러분의 프로그램이 통제된 변경을 적용합니다. 각 서비스의 응답 패턴을
기록하세요. 잘못된 패딩과 이후의 인증 실패를 구분하는 응답인지, 패딩이 유용한
정보를 제공하기 전에 거부하는 응답인지 관찰합니다. 이 관찰로 서비스를
선택하세요. 올바른 알파벳은 의도적으로 문서에 제공하지 않습니다.

<a id="6-run-selected-recovery-and-finish"></a>
## 6. 선택한 서비스 복구 실행 및 마무리

유용한 패딩 오라클이 있는 서비스를 식별한 뒤 실행하세요.

```console
python3 mte_vs_etm.py --recover-service SERVICE_LETTER
cd /workspace/labs/lab02
make grade PART=6
```

`SERVICE_LETTER`를 관찰에 따라 선택한 `A` 또는 `B`로 바꾸세요. 복구에
성공하면 `FLAG{...}`가 포함된 메시지와 오라클 질의 수가 출력됩니다.
덧붙여진 바이너리 MAC은 메시지의 일부로 출력하지 않습니다. 선택한 알파벳,
복구한 메시지, 플래그를 하드코딩하지 마세요.

<a id="example-output"></a>
## 출력 예시

성공한 실행의 출력 형식은 다음과 같습니다. 예시에서는 값을 가렸습니다.
보고서에는 실제 결과를 포함하세요. 수업용 컨테이너 안의
`/workspace/labs/lab02`에서 실행하고, `SERVICE_LETTER`를 관찰에 따라 선택한
`A` 또는 `B`로 바꾸세요.

```console
python3 part6_mte_vs_etm/mte_vs_etm.py --recover-service SERVICE_LETTER
Service A: original=<response>, modified=('<IV modification response>', '<ciphertext modification response>')
Service B: original=<response>, modified=('<IV modification response>', '<ciphertext modification response>')
FLAG{<recovered value>}
oracle queries: <query count>
```

두 작은 검사와 import·CLI 검사가 동작하고, 두 서비스의 기준 응답과 탐색 응답을
기록하고, 서비스 선택의 근거를 제시하고, 메시지를 복구하며, 해당 Part의 채점
검사가 통과하면 완료입니다. 모든 Part를 마친 뒤에는 `PART` 없이
`make grade`를 실행하세요.

서비스 질의 제한에 도달하면 **호스트 터미널**에서 대상을 초기화하기 전에
반복문을 점검하세요.

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

`healthy` 상태를 기다린 뒤 새 항목을 받고 복구 전에 탐색을 반복하세요.
재시작하면 Part 5와 6의 질의 수가 모두 초기화됩니다. 마쳤다면 수업용 셸에서
나간 뒤 호스트에서 Lab02 대상을 중지합니다.

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

공통 수업용 컨테이너는 계속 사용할 수 있습니다. 다른 방법은
[세션 정리 안내](../README.md#finish-or-restart-a-session)를 참고하세요.

<a id="checkpoint-questions"></a>
## 확인 질문

보고서에는 두 서비스의 원본·수정 응답 패턴, 선택 이유, 복구 질의 수를
포함하고 다음을 설명하세요.

1. 어떤 응답 패턴을 관찰하면 유용한 패딩 정보를 식별할 수 있나요?
2. MAC을 암호화해도 패딩 동작이 관찰될 수 있는 이유는 무엇인가요?
3. 복호화 전에 인증하면 같은 오라클을 막을 수 있는 이유는 무엇인가요?
4. 인증이 암호문뿐 아니라 IV도 포함해야 하는 이유는 무엇인가요?

두 서비스 모두 블랙박스로 다루고 구현이나 키를 조사하지 마세요. 복구한
플래그는 지정된 수업 채널로 제출하고 공개 소스 코드나 예제 출력에 포함하지
마세요.

<a id="report-checklist"></a>
## 보고서 체크리스트

- [ ] 확인 질문의 답변
- [ ] 주요 코드 변경 사항과 동작 방식 설명
- [ ] 실행 스크린샷과 복구한 FLAG
- [ ] 두 서비스의 원본, IV 수정, 암호문 수정 응답
- [ ] 스크린샷에서 확인할 수 있는 선택한 서비스와 복구 질의 수
