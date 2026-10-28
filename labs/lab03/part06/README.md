# Part06: Textbook RSA Malleability and RSA-OAEP

**한국어** | [English](../../../en/labs/lab03/part06/README.md)

## 1. 학습 목표 (Learning Objectives)

Textbook RSA의 곱셈 관계와 실제 애플리케이션 입력의 관계를 설명하고, 같은
변형을 RSA-OAEP에 적용했을 때 결과가 달라지는 이유를 실험합니다. OAEP 설정은
RSA-2048, SHA-256, MGF1-SHA-256, 빈 label입니다.

## 2. 도전 시나리오 (Challenge Scenario)

송금 서비스가 정수 금액을 textbook RSA로 암호화했습니다. 가로챈 암호문과 공개키만
이용하여 원래 금액의 **2배**를 처리하게 만드세요. 서버는 복호화한 금액을
공개하지 않으며, 발급한 해당 세션 암호문의 지정된 변형만 인정합니다.

## 3. 제공 자료 (Provided Materials)

- [starter/attack.py](starter/attack.py): 암호문 수정, OAEP 암호화, 요청 전송 TODO.
- [data/protocol.json](data/protocol.json): 공개 프로토콜과 제한 사항.
- [tests/check.py](tests/check.py): 서버가 생성한 새 세션의 완료 여부 검사.
- [공통 HTTP 클라이언트](../common/service_client.py): `TargetClient.request(method, path, payload=None)`.
- `GET /part06/challenge`: 실행 시 공개키와 새로운 공개 도전 데이터를 제공합니다.

공개 정수는 선행 0 없는 10진 문자열이며 `0 <= 값 < n`이어야 합니다. 세션은
32자리 소문자 16진수이며 30분 후 만료합니다. JSON 요청은 16 KiB 이하입니다.
원래 송금 금액, 개인키, 교수용 채점 플래그는 제공하지 않습니다.

## 4. 과제 (Tasks)

1. 새 세션의 `public_key.n`, `public_key.e`, `ciphertext`, `multiplier`를 읽으세요.
   RSA의 `c' = c · r^e mod n` 관계가 송금 금액에 미치는 영향을 분석하세요.
2. `modify_ciphertext()`와 `attack(client, challenge)`의 textbook RSA 단계를 완성하세요.
3. `encrypt_oaep()`로 공개 `oaep_amount`의 **ASCII 바이트**를 암호화하세요.
   정수의 이진 표현을 암호화하는 것이 아닙니다. OAEP의 해시·MGF1·label을 모두 지정하세요.
4. 정상 OAEP 요청을 먼저 성공시키고, 그 **동일한 암호문**에 같은 배수 변형을 가한
   요청이 거절되는지 확인하세요. 임의의 깨진 암호문 제출은 완료 조건이 아닙니다.
5. 모든 응답을 확인하고 결과 엔드포인트에서 서버가 판정한 완료 상태를 확인하세요.

요청·응답 스키마는 다음과 같습니다. 아래 JSON 필드 외 추가 필드는 거절됩니다.
각 응답의 공통 `ok`는 요청 처리 여부이며, 송금 승인 여부는 `accepted`입니다.

| 메서드 / 경로 | 요청 | 성공 또는 애플리케이션 결과 |
|---|---|---|
| `GET /part06/challenge` | 없음 | `session`, `public_key:{n,e}`, `ciphertext`, `multiplier:"2"`, `oaep_amount:"100"`, `oaep:{hash,mgf1_hash,label}`, `expires_in` |
| `POST /part06/transfer` | `{session,ciphertext}` | `accepted`, `status:MODIFIED_TRANSFER_ACCEPTED` 또는 `OBJECTIVE_NOT_MET` |
| `POST /part06/oaep/transfer` | `{session,ciphertext,stage:"normal"}` | `accepted`, `status:NORMAL_TRANSFER_ACCEPTED` 또는 `OAEP_REJECTED` |
| `POST /part06/oaep/transfer` | `{session,ciphertext,stage:"tampered"}` | `accepted:false`, `status:OAEP_REJECTED`; 지정 변형이 아니면 `OBJECTIVE_NOT_MET` |
| `GET /part06/result?session=...` | 해당 세션 | `complete`, `checks:{textbook_modified,oaep_normal,oaep_tamper_rejected}`; 완료한 경우에만 `flag` |

HTTP 오류는 `{ok:false,error:...}`입니다. 잘못된 입력은 400, 알 수 없거나 만료된
세션은 404, 이미 완료된 단계의 재전송 또는 순서 오류는 409, 큰 요청은 413입니다.
매 실행마다 새 세션을 사용하세요. 서비스는 임의 복호화 결과를 제공하지 않습니다.

## 5. 실행 방법 (How to Run)

먼저 [Lab03 시작 안내](../README.md)를 따르세요. 로컬 대상 이미지는 교수가
빌드 또는 게시해야 하며, GHCR 태그가 이미 공개되었다고 가정하지 않습니다.
저장소 루트의 **호스트 터미널**에서 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml exec course bash
```

`ps`의 기대 상태는 `lab03-target`이 `healthy`인 것입니다. Docker 실행 결과는
환경에 따라 달라집니다. 수업용 컨테이너에서 상태를 확인합니다.

```console
cd /workspace
python3 -c 'from labs.lab03.common.service_client import TargetClient; print(TargetClient().request("GET", "/health"))'
```

실제 HTTP 검사에서 확인한 응답:

```text
{'ok': True, 'service': 'lab03-target'}
```

미완성 starter의 실행:

```console
python3 labs/lab03/part06/tests/check.py
```

실제 미완성 starter의 출력이며 종료 코드는 1입니다.

```text
Part06 incomplete: TODO: implement textbook RSA ciphertext modification
```

TODO를 구현한 후 같은 명령으로 검사합니다. 직접 실행도 가능합니다.

```console
python3 labs/lab03/part06/starter/attack.py
```

완료 검사에서 출력되는 첫 줄은 다음과 같습니다. 다음 줄의 `LAB03{...}` 값은
서버가 발급하며 실행마다 달라집니다. 이 첫 줄은 교수용 참조 구현으로 검증했습니다.

```text
Part06 complete: target verified all objectives
```

다른 파일을 검사하려면 `--solution /workspace/경로/attack.py`를 지정하세요.
교수 제공 서버는 `--url https://강사제공주소` 또는 `LAB03_TARGET_URL`로 선택합니다.
접속 오류가 발생하면 서비스의 `healthy` 상태, 컨테이너 내부 실행 여부, URL을 확인하세요.
상태가 만료되었다면 처음부터 새 세션을 발급받으세요. 대상 종료와 로그 확인은 호스트에서:

```console
docker compose -f docker/compose.yml --profile lab03 logs --tail=30 lab03-target
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
```

## 6. 완료 조건 (Success Conditions)

동일 세션에서 지정된 textbook RSA 변형, 정상 OAEP 송금, 그 OAEP 암호문의 배수 변형
거절을 **모두** 서버가 확인해야 플래그를 반환합니다. 출력 문자열만 제출하거나, 다른
세션의 결과를 재사용하거나, 임의 암호문을 제출하는 것으로는 통과하지 못합니다.

로컬 Docker는 연습용입니다. Docker를 제어하는 사용자는 이미지·프로세스·메모리를
조사할 수 있습니다. 로컬 비밀의 은닉을 채점 보안으로 간주하지 마세요. 실제 비공개
평가는 교수가 관리하는 서버와 별도 키·플래그를 사용합니다.

## 7. 제출물 (Submission Requirements)

완성한 `attack.py`, 각 단계의 요청·응답 기록, 서버 플래그, 아래 분석 답변을
제출하세요. 개인키를 제출할 필요는 없습니다. 플래그는 강사 지정 채널로 제출하세요.

## 8. 분석 질문 (Analysis Questions)

1. 원래 금액을 몰라도 정확히 2배가 되는 이유는 무엇인가요? 모듈러 감김이 없도록
   금액을 작게 제한한 이유는 무엇인가요?
2. 정상 OAEP 요청의 성공을 먼저 확인해야 하는 이유는 무엇인가요?
3. OAEP 암호문 변형이 거절되었다는 사실이 송금자의 인증이나 송금 권한을 보장하나요?
4. textbook 단계의 성공만으로 플래그를 주지 않는 이유는 무엇인가요?
