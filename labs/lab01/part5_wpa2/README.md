# Part 5: WPA2 오프라인 후보 검증

[한국어](README.md) | [English](../../../en/labs/lab01/part5_wpa2/README.md)

**예상 소요 시간:** 40분.

**윤리 및 허가된 사용:** 제공된 수업용 PCAP과 합성 메타데이터만 사용하세요.
트래픽 캡처, 클라이언트 인증 해제, 네트워크 방해, 무선 인터페이스 사용, 제3자 자격 증명 테스트를 하지 마세요.
이 실습은 허가된 캡처 파일이 이미 제공된 시점부터 시작합니다.

이 Part에서는 패킷 관찰값을 **Python 스크립트로 추출하지 않습니다**.
저장된 PCAP을 Wireshark 또는 TShark로 살펴보고, 디코딩된 프로토콜 트리에서 필요한 필드를 찾아
직접 관찰 결과를 기록해야 합니다. 그 다음 Python으로 WPA2 후보 검증 계산을 구현합니다.

## 학습 목표

이 Part를 완료하면 다음을 할 수 있어야 합니다.

- 802.11 관리 프레임에서 SSID와 BSSID를 찾는다.
- EAPOL-Key 프레임에서 AP와 스테이션 주소를 식별한다.
- 방향, 플래그, 재전송 카운터(replay counter)로 M1, M2, M3, M4를 구분한다.
- Wireshark 프로토콜 트리에서 논스(nonce)와 MIC를 찾는다.
- WPA2-Personal의 PMK, PTK, KCK, MIC 계산을 구현한다.
- 기록된 핸드셰이크로 오프라인 후보 검증이 가능한 이유를 설명한다.
- 무선 보안 실험의 허가 범위를 명시한다.

## 사용 파일

| 파일 | 용도 |
| --- | --- |
| `data/wpa2/lab01-handshake.pcap` | 강사가 제공한 수업용 캡처 |
| `data/wpa2/lab01-pcap-wordlist.txt` | 해당 PCAP에만 사용하는 작은 후보 목록 |
| `data/wpa2_passwords.txt` | 별도의 합성 Python 레코드에 사용하는 제한된 후보 목록 |
| `CAPTURE_WORKSHEET.md` | 수동 패킷 관찰 결과를 작성하는 빈 표 |
| `data/wpa2_capture.json` | 별도의 합성 Python 계산용 데이터 |
| `samples/explain_handshake.py` | 별도의 합성 JSON 데이터에서 필드를 출력하는 예제 |
| `samples/bytes_hmac_demo.py` | 완성된 공개 바이트/KDF/HMAC API 예제 |
| `verify_candidate.py` | 학생이 검증 프로그램 전체를 작성하는 빈 파일 |
| `test_wpa2_workflow.py` | 기본 테스트와 선택적으로 활성화하는 구현 테스트 |
| `samples/flag_unlock_demo.py` | 공개 도우미 사용 예제. 이 Part의 정답은 포함하지 않음 |
| `data/flag_challenge.json` | 실험 결과로 여는 암호화된 완료 플래그 |

PCAP과 `wpa2_capture.json`은 실습을 위해 의도적으로 만든 서로 다른 두 데이터셋입니다.
SSID, 주소, 논스, MIC가 서로 같다고 가정하지 마세요.
PCAP은 수동 프로토콜 분석과 제한된 aircrack-ng 비교에 사용합니다.
JSON 데이터는 실제 패킷 트레이스에서 해당 값들이 나타나는 위치를 익힌 뒤 Python 함수에 제공하는
간결하고 재현 가능한 입력입니다.

배포된 PCAP의 SSID와 단말 MAC 주소는 가상의 수업용 식별자입니다.
이를 찾는 과정이 실습 A의 일부가 되도록 이 안내서에는 해당 값을 싣지 않았습니다.

## 1. 공개 바이트·API 예제 실행 및 살펴보기

수업용 컨테이너 안에서 실행하세요.

```console
cd /workspace/labs/lab01/part5_wpa2
python3 samples/bytes_hmac_demo.py
python3 -m unittest test_wpa2_workflow.py -v
```

이 예제는 두 수업용 캡처와 관계없는 공개 값을 사용합니다. 출력은 다음과 같습니다.

```text
Ordered public bytes: 01020201
Cleared first two bytes: 0000626c69632d64617461
Toy KDF bytes: 16
SHA-256 HMAC bytes: 32
Truncated example bytes: 8
Same message verifies: True
Changed message verifies: False
```

JSON 로딩, 16진수 디코딩, 바이트 정렬, `bytearray` 수정, KDF 출력 길이, HMAC,
슬라이싱, 상수 시간 비교를 살펴보세요.
이 예제는 SHA-256과 KDF 반복 1,000회를 사용하며 WPA2 실습의 매개변수는 다릅니다.
파일은 생성하지 않습니다. 구현 전에는 데이터 검사 2개가 통과하고 구현 검사 7개는 건너뜁니다.

## 분석 도구 준비

Wireshark의 명령행 패킷 분석기인 TShark는 수업용 이미지에 설치되어 있습니다.
현재 이미지가 이번 Part 5 업데이트 이전에 빌드되었다면 컨테이너를 나온 뒤
**호스트의 저장소 루트 터미널**에서 이미지를 다시 빌드하세요.

```console
docker compose -f docker/compose.yml build
docker compose -f docker/compose.yml run --rm course bash
```

`run` 명령으로 새로운 수업용 컨테이너 셸이 열리면 도구를 확인하고 Part 5로 이동하세요.

```console
tshark --version
cd /workspace/labs/lab01/part5_wpa2
```

Compose 설정은 컨테이너의 그래픽 데스크톱을 전달하지 않습니다.
선택적으로 호스트에 설치한 Wireshark GUI에서 같은 저장소의 PCAP을 열어도 됩니다.
TShark를 이용하면 컨테이너만으로 실습할 수 있으므로 호스트에 Wireshark를 설치할 필요는 없습니다.

### 공개 플래그 유틸리티 예제

```console
python3 samples/flag_unlock_demo.py
```

예상 출력:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

예제는 실행 후 파일을 남기지 않습니다. 공통 유틸리티를 import하는 방법, 인증 실패를 처리하는 방법,
성공했을 때 반환값을 출력하는 방법을 살펴보세요.
최종 프로그램에는 이 공개 데모의 증명값이 아니라 자신의 실험 결과를 사용합니다.

## 2. PCAP 수동 분석

이 실습에서 Python 파서를 작성하거나 사용하지 마세요.
정답 표를 바로 출력하는 TShark의 `-T fields` 명령도 사용하지 마세요.
디코딩된 패킷 트리를 읽고 찾은 내용을 `CAPTURE_WORKSHEET.md`에 기록하세요.

### 방법 1: 호스트의 Wireshark GUI

1. **File > Open**을 선택하고 이 저장소의
   `labs/lab01/part5_wpa2/data/wpa2/lab01-handshake.pcap`을 여세요.
2. 인증 키 교환을 표시하도록 다음 디스플레이 필터를 입력하세요.

   ```text
   eapol
   ```

3. 표시된 프레임 4개를 살펴보세요. 802.11 헤더에서 교환에 공통으로 사용되는 BSSID를 찾고,
   프레임 방향과 Key ACK 플래그로 AP 주소와 다른 스테이션/클라이언트 주소를 구분하세요.
4. 아래의 `RECORDED_BSSID`를 방금 관찰한 BSSID로 바꾸세요.
   PCAP의 여러 비콘 프레임 중 해당 액세스 포인트의 프레임만 표시됩니다.

   ```text
   wlan.fc.type_subtype == 0x0008 && wlan.bssid == RECORDED_BSSID
   ```

5. 표시된 비콘을 선택하고 **IEEE 802.11 wireless LAN management frame**을 펼치세요.
   802.11 헤더에서 BSSID를 확인하세요. **Tagged parameters**와 **SSID parameter set**을
   펼쳐 네트워크 이름을 찾으세요.
6. `eapol` 필터로 돌아가세요. 각 프레임의 수신자, 송신자, BSSID를 기록하세요.
   **802.1X Authentication**과 **WPA Key Data** 아래에서 재전송 카운터, 논스, 키 MIC,
   Key Information 플래그를 찾으세요. 명칭은 Wireshark 버전에 따라 다를 수 있습니다.
7. 아래 메시지 식별 표로 각 프레임을 M1~M4로 분류하세요.
   화면에 표시된 순서에만 의존하지 말고 프레임 번호를 기록하세요.

### 방법 2: 수업용 컨테이너의 TShark

먼저 패킷 목록을 출력해 트레이스 구성을 파악하세요.

```console
tshark -r data/wpa2/lab01-handshake.pcap
```

먼저 EAPOL-Key 프레임의 디코딩된 전체 프로토콜 트리를 출력하세요.

```console
tshark \
  -r data/wpa2/lab01-handshake.pcap \
  -Y 'eapol' \
  -V
```

수신자, 송신자, BSSID, 재전송 카운터, 논스, 키 MIC, Key Information 플래그를 읽으세요.
프레임 4개가 공유하는 BSSID를 식별하세요.
그 다음 아래의 `RECORDED_BSSID`를 해당 값으로 바꿔 관련 비콘만 살펴보세요.

```console
tshark \
  -r data/wpa2/lab01-handshake.pcap \
  -Y 'wlan.fc.type_subtype == 0x0008 && wlan.bssid == RECORDED_BSSID' \
  -V
```

802.11 헤더와 태그 매개변수를 읽어 SSID를 찾으세요.
프로토콜 트리에서 필드를 찾는 것도 실습의 일부이므로 상세 출력은 의도적으로 길게 제공됩니다.

### M1~M4 식별

AP/STA 방향과 다음 EAPOL-Key 플래그를 사용하세요. 설정된 비트는 `1`로 표시합니다.

| 메시지 | 방향 | Key ACK | Key MIC | Secure | 주요 관찰 내용 |
| --- | --- | ---: | ---: | ---: | --- |
| M1 | AP -> STA | 1 | 0 | 0 | AP가 ANonce 제공 |
| M2 | STA -> AP | 0 | 1 | 0 | STA가 SNonce와 MIC 제공 |
| M3 | AP -> STA | 1 | 1 | 1 | AP가 키 설치를 인증 |
| M4 | STA -> AP | 0 | 1 | 1 | STA가 설치를 확인 |

Wireshark는 추가 Key Information 비트를 표시할 수 있습니다.
이번 단순화된 분류에서는 방향, 위의 비트 3개, 재전송 카운터, 논스의 동작만 사용하세요.
네 행이 일관된 교환을 이루지 않으면 주소와 프레임 번호를 다시 확인한 뒤 진행하세요.

### 수동 관찰 질문

자동 파서를 참고하지 말고 워크시트를 완성하세요.

1. 비콘 프레임의 어느 필드에 SSID가 있나요? 헤더의 어느 필드에 BSSID가 있나요?
2. 어느 주소가 AP에 속하고 어느 주소가 스테이션에 속하나요?
3. 어느 프레임이 M1, M2, M3, M4인가요? 방향과 플래그를 근거로 제시하세요.
4. ANonce와 SNonce는 어느 메시지에서 처음 나타나나요?
5. 재전송 카운터는 요청/응답 쌍을 어떻게 묶어 주나요?
6. 어느 메시지의 MIC가 0이 아닌가요? M1은 왜 다른가요?

복구한 패스프레이즈를 워크시트, 보고서, 스크린샷에 넣지 마세요.

## 3. 합성 데이터 살펴보기 및 처리 과정 이해

수동 워크시트를 완성한 뒤 실행하세요.

```console
python3 samples/explain_handshake.py data/wpa2_capture.json
```

이 예제는 JSON 필드 이름과 값을 출력한 다음 키 유도 순서를 설명합니다.
각 필드 이름을 직접 찾은 패킷 트리 필드와 비교하세요.
별도의 JSON 데이터만 읽으며 PCAP을 파싱하지 않습니다. 파일은 생성하지 않습니다.

### PMK, PTK, KCK, MIC

4방향 핸드셰이크에서는 비밀번호를 전송하지 않습니다.
WPA2-Personal에서는 후보와 SSID로 **Pairwise Master Key(PMK)**를 생성합니다.

```text
PMK = PBKDF2-HMAC-SHA1(
    password = UTF-8(passphrase),
    salt = UTF-8(SSID),
    iterations = 4096,
    output length = 32 bytes
)
```

양쪽 참여자는 원시 주소와 논스 바이트 문자열을 같은 순서로 정렬합니다.

```text
context = min(AP_MAC, STA_MAC) || max(AP_MAC, STA_MAC)
        || min(ANonce, SNonce) || max(ANonce, SNonce)
```

6바이트 MAC 주소 2개와 32바이트 논스 2개로 76바이트 문맥(context)을 만듭니다.
PMK와 문맥을 확장해 64바이트 **Pairwise Transient Key(PTK)**를 생성합니다.

```text
block[i] = HMAC-SHA1(
    key = PMK,
    data = "Pairwise key expansion" || 0x00 || context || BYTE(i)
)

PTK = first 64 bytes of (block[0] || block[1] || ...)
```

1바이트 카운터는 0부터 시작합니다.
PTK의 처음 16바이트는 MIC로 EAPOL-Key 데이터를 인증하는 **Key Confirmation Key(KCK)**입니다.
PTK의 다른 부분에는 KEK와 TK가 있으며 여기서는 별도로 계산하지 않습니다.

후보를 검증할 때는 먼저 EAPOL 바이트의 캡처된 MIC 필드를 0으로 바꿉니다.
그 다음 HMAC-SHA1으로 후보 MIC를 계산하고 16바이트로 잘라 사용합니다.

```text
candidate + SSID -> PMK
PMK + ordered addresses/nonces -> PTK -> first 16 bytes -> KCK
KCK + normalized EAPOL -> candidate MIC -> constant-time comparison
```

MIC가 일치하면 후보로 같은 키 자료가 생성되었다는 근거가 됩니다.
다른 후보를 검사하는 데 필요한 모든 입력이 이미 로컬에 있으므로 액세스 포인트에 추측값을 보내지 않으며,
서버 측의 요청 속도 제한으로 이를 관찰할 수 없습니다.

## 4. derive_pmk() 구현 및 검사

제공된 `verify_candidate.py`는 비어 있습니다.
모든 import, 함수, 상수, 명령행 인자 처리, 실행 가드를 직접 작성하세요.
다음 상수를 정의하세요.

| 상수 | 값 |
| --- | --- |
| `PRF_LABEL` | `b"Pairwise key expansion"` |
| `PMK_ITERATIONS`, `PMK_LENGTH` | 4096, 32 |
| `PTK_LENGTH`, `KCK_LENGTH`, `MIC_LENGTH` | 64, 16, 16 |
| `EAPOL_MIC_OFFSET` | 81 |

UTF-8, PBKDF2-HMAC-SHA1, 위의 WPA2 매개변수를 사용해
`derive_pmk(candidate: str, ssid: str) -> bytes`를 구현하세요.

```console
python3 - <<'PY'
import hashlib
from verify_candidate import derive_pmk
candidate, ssid = "public-example", "PublicSampleSSID"
pmk = derive_pmk(candidate, ssid)
assert pmk == hashlib.pbkdf2_hmac("sha1", candidate.encode("utf-8"), ssid.encode("utf-8"), 4096, 32)
assert len(pmk) == 32
assert pmk != derive_pmk(candidate, "OtherSampleSSID")
print("PMK check: OK")
PY
```

`PMK check: OK`를 확인한 뒤 진행하세요. 이 검사는 수업용 패스프레이즈를 사용하지 않습니다.

## 5. build_context() 구현 및 정렬 검사

`build_context(record: dict[str, str]) -> bytes`를 구현하세요.
`ap_mac`, `client_mac`, `anonce`, `snonce`를 16진수에서 디코딩하세요.
MAC 바이트 문자열 2개와 논스 바이트 문자열 2개를 각각 따로 정렬한 뒤 MAC, 논스 순서로 연결하세요.
결과는 76바이트여야 합니다.

```console
python3 - <<'PY'
from verify_candidate import build_context
record = {"ap_mac": "020000000001", "client_mac": "010000000001",
          "anonce": "22" * 32, "snonce": "11" * 32}
expected = bytes.fromhex("010000000001020000000001" + "11" * 32 + "22" * 32)
assert build_context(record) == expected
record["ap_mac"], record["client_mac"] = record["client_mac"], record["ap_mac"]
record["anonce"], record["snonce"] = record["snonce"], record["anonce"]
assert build_context(record) == expected
assert len(expected) == 76
print("Context ordering check: OK")
PY
```

`Context ordering check: OK`를 확인한 뒤 진행하세요.

## 6. derive_ptk() 구현 및 확장 검사

`derive_ptk(pmk: bytes, context: bytes) -> bytes`를 구현하세요.
`PRF_LABEL || 0x00 || context || BYTE(counter)`에 대한 HMAC-SHA1 블록을 연속으로 계산하세요.
카운터는 0부터 시작합니다. 충분한 블록을 연결한 다음 처음 64바이트를 취하세요.
모든 과정에서 원시 바이트 문자열을 사용하세요.

```console
python3 - <<'PY'
import hashlib
import hmac
from verify_candidate import derive_ptk
pmk, context = bytes(range(32)), bytes(range(76))
expected = b"".join(hmac.new(pmk, b"Pairwise key expansion\x00" + context + bytes([i]),
                             hashlib.sha1).digest() for i in range(4))[:64]
assert derive_ptk(pmk, context) == expected
assert derive_ptk(pmk, context + b"x") != expected
print("PTK expansion check: OK")
PY
```

`PTK expansion check: OK`를 확인한 뒤 진행하세요.

## 7. derive_kck() 구현 및 슬라이스 검사

`derive_kck(ptk: bytes) -> bytes`를 구현하세요. PTK의 처음 16바이트를 반환합니다.

```console
python3 - <<'PY'
from verify_candidate import derive_kck
ptk = bytes(range(64))
assert derive_kck(ptk) == bytes(range(16))
print("KCK check: OK")
PY
```

`KCK check: OK`를 확인한 뒤 진행하세요.

## 8. normalized_eapol() 구현 및 바이트 보존 검사

`normalized_eapol(record: dict[str, str]) -> bytes`를 구현하세요.
`record["eapol"]`을 디코딩하고, 입력이 97바이트보다 짧으면 `ValueError`를 발생시키세요.
슬라이스 `81:97`의 16바이트 MIC 필드만 정확히 0으로 바꾸세요.
나머지 바이트를 모두 보존하고 불변 객체인 `bytes`를 반환하세요.

```console
python3 - <<'PY'
from verify_candidate import normalized_eapol
raw = bytes(range(100))
normalized = normalized_eapol({"eapol": raw.hex()})
assert len(normalized) == len(raw)
assert normalized[:81] == raw[:81] and normalized[97:] == raw[97:]
assert normalized[81:97] == bytes(16)
try:
    normalized_eapol({"eapol": bytes(96).hex()})
except ValueError:
    pass
else:
    raise AssertionError("truncated EAPOL was accepted")
print("EAPOL normalization check: OK")
PY
```

`EAPOL normalization check: OK`를 확인한 뒤 진행하세요.

## 9. compute_mic() 구현 및 공개 메시지 검사

`compute_mic(kck: bytes, eapol: bytes) -> bytes`를 구현하세요.
이미 정규화된 EAPOL 바이트에 HMAC-SHA1을 적용하고 다이제스트의 처음 16바이트를 취하세요.

```console
python3 - <<'PY'
import hashlib
import hmac
from verify_candidate import compute_mic
key, message = bytes(range(16)), b"public-EAPOL-example"
expected = hmac.new(key, message, hashlib.sha1).digest()[:16]
assert compute_mic(key, message) == expected
assert compute_mic(key, message + b"x") != expected
print("MIC check: OK")
PY
```

`MIC check: OK`를 확인한 뒤 진행하세요.

## 10. verify() 구현 및 공개 처리 과정 검사

`verify(candidate: str, record: dict[str, str]) -> bool`을 구현하세요.
구현한 PMK, 문맥, PTK, KCK, EAPOL 정규화, MIC 함수를 연결하세요.
캡처된 `record["mic"]`를 디코딩하고 계산한 MIC와 `hmac.compare_digest()`로 비교하세요.
불리언만 반환하고 후보나 유도한 키 자료를 출력하지 마세요.

이 검사는 완성한 기본 연산으로 별도의 공개 예제 레코드를 구성합니다.

```console
python3 - <<'PY'
from verify_candidate import (
    derive_pmk, build_context, derive_ptk, derive_kck,
    normalized_eapol, compute_mic, verify,
)
record = {"ssid": "PublicSampleSSID",
          "ap_mac": "020000000001", "client_mac": "010000000001",
          "anonce": "22" * 32, "snonce": "11" * 32, "eapol": bytes(range(100)).hex()}
public = "public-example"
pmk = derive_pmk(public, record["ssid"])
kck = derive_kck(derive_ptk(pmk, build_context(record)))
record["mic"] = compute_mic(kck, normalized_eapol(record)).hex()
assert verify(public, record) is True
assert verify("different-public-example", record) is False
print("Public pipeline check: OK")
PY
```

`Public pipeline check: OK`를 확인한 뒤 진행하세요.
왕복 검사만으로는 양쪽에서 같은 실수를 한 경우를 놓칠 수 있으므로 앞의 개별 검사도 중요합니다.

## 11. main() 작성 및 합성 실습 실행

`argparse`로 로컬 메타데이터 JSON 경로 하나를 받고,
`getpass.getpass("Candidate: ")`로 대화형 입력을 받는 `main()`을 작성하세요.
JSON을 로드하고 `verify()`를 호출해 `match` 또는 `no match`를 출력한 뒤
아래의 완료 플래그 요구 사항을 따르세요. 실행 가드를 추가하세요.
모듈을 import할 때 입력을 요구하거나 검색을 실행하면 안 됩니다.

```console
python3 -c "import verify_candidate; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_wpa2_workflow.py -v
python3 verify_candidate.py data/wpa2_capture.json
```

활성화된 테스트 9개가 모두 통과해야 합니다.
테스트는 데이터, 바이트 길이, 정렬, 입력 변화에 대한 민감도, 잘린 입력 거부,
제공된 합성 단어 목록의 후보 중 정확히 하나만 일치하는지를 검사합니다.
해당 후보는 출력하지 않습니다.

대화형 검증에서는 `data/wpa2_passwords.txt`에서 후보를 골라 프롬프트에 입력하세요.
일치하는 후보이면 `match` 다음에 플래그를 출력하고, 다른 입력이면 `no match`를 출력합니다.
액세스 포인트에는 접속하지 않습니다.

### 공통 완료 유틸리티

메인 프로그램 전체는 직접 작성해야 합니다. 암호화 봉투 파일의 경로는 셸의 현재 디렉토리가 아니라
실습 파일을 기준으로 해석하세요. 번호가 붙은 Part 실습 파일에서 제공된 공통 유틸리티를
import하려면 다음을 사용하세요.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)`는 암호화 봉투를 인증한 뒤 `FLAG{...}` 문자열을 반환합니다.
증명값이 잘못되면 `ValueError`가 발생합니다. 봉투를 변경하지 말고 구현과 증명값 형식을 점검하세요.
공개 데모 증명값은 데모 결과물만 열 수 있으며 이 Part의 플래그를 열 수는 없습니다.
계산한 Part 플래그는 강사가 지정한 채널로 제출하세요.

### 제한된 합성 검색 및 플래그 출력 추가

메인에서 제공된 `data/wpa2_passwords.txt`를 위한 선택 인자 `--wordlist`를 지원하세요.
이 인자가 있으면 UTF-8 파일의 각 줄에서 앞뒤 공백을 제거하고 비어 있지 않은 줄을 읽어
완성한 `verify()`로 모든 후보를 검사하세요.
후보 수를 세고 `time.perf_counter()`로 소요 시간을 측정하며 일치 후보가 정확히 하나인지 확인하세요.
후보 수, 일치 수, 시간만 보고하고 일치 후보와 유도한 모든 키 자료는 공개하지 마세요.

검증한 후보 문자열을 `data/flag_challenge.json`의 증명값으로 사용하고,
`unlock_flag(flag_path, candidate)`를 호출해 반환된 `FLAG{...}`를 마지막 줄에 출력하세요.
대화형 모드에서는 `verify()`가 `True`를 반환한 경우에만 플래그를 출력하세요.
잘못된 입력이면 플래그 없이 `no match`를 출력합니다.

완료 증명값은 합성 JSON 데이터셋에서 얻습니다.
별도의 PCAP 분석, 워크시트 작성, aircrack-ng 비교도 반드시 수행해야 합니다.

### 전체 합성 플래그 실습 실행

```console
python3 verify_candidate.py data/wpa2_capture.json --wordlist data/wpa2_passwords.txt
```

예상 출력 형식:

```text
Candidates tested: <count>
Matches: 1
Elapsed: <seconds> seconds
FLAG{...}
```

후보 수는 제공된 목록의 비어 있지 않은 줄 수와 같아야 하며, 소요 시간은 호스트에 따라 달라집니다.
봉투 인증이 성공하면 복구한 후보가 의도한 합성 실험과 일치함을 확인할 수 있습니다.

## 12. 제한된 PCAP 비교 완료

`CAPTURE_WORKSHEET.md`에 직접 기록한 BSSID를 사용하세요.
실행 전에 `AP_BSSID_FROM_WORKSHEET`를 바꾸세요.

```console
aircrack-ng \
  -w data/wpa2/lab01-pcap-wordlist.txt \
  -b AP_BSSID_FROM_WORKSHEET \
  data/wpa2/lab01-handshake.pcap
```

제공된 수업용 파일 2개만 사용하세요.
검사한 키 수와 소요 시간을 기록하고 스크린샷과 보고서에서 키를 가리세요.
도구는 제한된 PCAP 단어 목록에서 일치하는 후보를 찾아야 합니다.
다운로드한 단어 목록이나 다른 캡처로 대체하지 마세요.

PCAP과 합성 JSON은 서로 다른 데이터셋이므로 패스프레이즈와 메타데이터가 같을 필요는 없습니다.
두 오프라인 작업 과정을 비교하세요.
둘 다 로컬에서 키 자료를 유도하고 인증 데이터를 재현하며 액세스 포인트에 추측값을 보내지 않습니다.

## 13. 완료 확인 및 보고서

- [ ] `CAPTURE_WORKSHEET.md`에 직접 관찰한 필드와 M1~M4의 근거를 기록했다.
- [ ] 처음에 비어 있던 `verify_candidate.py`가 완전한 실행 프로그램이다.
- [ ] 단계별 공개 검사와 활성화된 테스트 9개가 모두 통과한다.
- [ ] 합성 사전의 후보 중 정확히 하나만 검증된다.
- [ ] 제한된 PCAP 비교가 성공한다.
- [ ] 보고서와 스크린샷에 패스프레이즈와 유도한 비밀 키 자료가 없다.
- [ ] 최종 프로그램이 자신의 `data/flag_challenge.json`을 인증하고 Part 플래그를 출력한다.

Python 파일, 완성된 워크시트, 검사 결과, 횟수·시간 측정값, PMK에서 MIC까지의 처리 과정에 대한
짧은 설명을 제출하세요.
SSID, BSSID, 스테이션 주소, 논스, MIC가 어디에 나타나는지, 방향과 플래그로 메시지를 어떻게
식별하는지, SSID와 정렬된 문맥이 왜 중요한지, 캡처된 MIC를 왜 0으로 바꿔야 하는지,
서버의 요청 속도 제한으로 오프라인 계산을 관찰할 수 없는 이유를 설명하세요.
이 단순화된 WPA2-Personal 실험을 WPA2-Enterprise나 WPA3-SAE에 그대로 적용할 수 없는 이유도 설명하세요.
