# Part08: RSA-CRT Fault Attack

**한국어** | [English](../../../en/labs/lab03/part08/README.md)

## 1. 학습 목표 (Learning Objectives)

CRT의 한 분기만 잘못 계산되어도 RSA 비밀키가 노출될 수 있는 이유를 분석하고,
출력 직전 공개키 검증이 이 실습의 결함 모델에서 누출을 막는지 확인합니다.
여기의 raw RSA 정수 대표값 서명은 Part07의 RSA-PSS와 다른 교육용 primitive입니다.

## 2. 도전 시나리오 (Challenge Scenario)

임베디드 장치가 CRT로 서명하다 한쪽 잔여값에 오류를 넣었습니다. 공개키와
정수 대표값 `mu`, 결함 서명으로 비밀키를 복구하고, 서버가 **이후 새로 발급하는
예측 불가능한 `mu2`**에 서명하여 복구를 증명하세요.

## 3. 제공 자료 (Provided Materials)

- [starter/attack.py](starter/attack.py): 비밀 지수 복구, 새 서명, 검증 요청 TODO.
- [data/protocol.json](data/protocol.json): 공개 프로토콜과 제한 사항.
- [tests/check.py](tests/check.py): 서버가 판정한 실제 완료 상태 검사.
- [공통 HTTP 클라이언트](../common/service_client.py): `TargetClient.request(method, path, payload=None)`.
- `GET /part08/challenge`: 새로운 세션, RSA-2048 공개키, `mu`.

개인키·인수는 제공하지 않습니다. 공개 정수는 선행 0 없는 10진 문자열이며
`0 <= 값 < n`이어야 합니다. 세션은 32자리 소문자 16진수로 30분 동안 유효합니다.
요청 제한은 16 KiB, 서버 소켓 제한 시간은 5초입니다.

## 4. 과제 (Tasks)

1. 새 세션을 발급받고 `/part08/sign`에서 결함 서명과 새 `mu2`를 받으세요.
   결함은 CRT의 한 분기에만 적용되며 다른 분기의 값은 유지됩니다.
2. `v = faulty_signature^e mod n`, `gcd(v - mu, n)`의 의미를 분석하고,
   `recover_private_exponent()`를 완성하세요. 비자명한 인수인지 확인하세요.
3. 복구한 개인 지수로 `mu2`의 서명을 만들어 `/part08/verify`에 제출하세요.
   원래 `mu`의 정상 서명을 제출하는 것으로는 통과하지 못합니다.
4. `/part08/secure-sign`에 `fault:true`를 보내 오류를 차단하고 서명 필드가
   전혀 없는지 확인하세요. `fault:false`에서는 정상 서명을 받아 공개키로 검증하세요.
   이 엔드포인트는 원래 `mu`만 서명하며 임의 대표값이나 `mu2`를 서명해 주지 않습니다.
5. 세 가지 목표를 모두 완료한 후 `/part08/result`에서 플래그를 확인하세요.

필드 목록은 정확해야 하며 추가 JSON 필드는 거절됩니다. 공통 응답 `ok`는 요청 처리,
`accepted`는 애플리케이션의 승인 여부입니다.

| 메서드 / 경로 | 요청 | 성공 또는 애플리케이션 결과 |
|---|---|---|
| `GET /part08/challenge` | 없음 | `session`, `public_key:{n,e}`, `mu`, `primitive`, `expires_in` |
| `POST /part08/sign` | `{session}` | `faulty_signature`, `mu2`; 세션당 한 번 |
| `POST /part08/verify` | `{session,signature}` | `accepted`, `status:FRESH_SIGNATURE_ACCEPTED` 또는 `INVALID_FRESH_SIGNATURE` |
| `POST /part08/secure-sign` | `{session,fault:true}` | `accepted:false`, `status:FAULT_DETECTED`; **signature 필드 없음** |
| `POST /part08/secure-sign` | `{session,fault:false}` | `accepted:true`, `status:SIGNATURE_VERIFIED`, `signature` |
| `GET /part08/result?session=...` | 해당 세션 | `complete`, `checks:{fresh_signature_valid,fault_blocked,normal_signature_valid}`; 완료 시에만 `flag` |

`fault`는 문자열이 아니라 JSON boolean입니다. HTTP 오류는 `{ok:false,error:...}`입니다.
잘못된 입력은 400, 알 수 없거나 만료된 세션은 404, 완료한 단계의 재전송 또는
순서 오류는 409, 큰 요청은 413입니다. 새 세션에서는 새로운 `mu`와 `mu2`를 사용합니다.

## 5. 실행 방법 (How to Run)

먼저 [Lab03 시작 안내](../README.md)를 따르세요. 교수가 로컬 이미지를 빌드하거나
게시해야 합니다. GHCR 태그가 이미 게시되었다고 가정하지 않습니다. 호스트의 저장소
루트에서 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml exec course bash
```

`lab03-target`의 기대 상태는 `healthy`입니다. 수업용 컨테이너 안에서 확인합니다.

```console
cd /workspace
python3 -c 'from labs.lab03.common.service_client import TargetClient; print(TargetClient().request("GET", "/health"))'
```

실제 HTTP 검사에서 확인한 응답:

```text
{'ok': True, 'service': 'lab03-target'}
```

starter를 검사합니다.

```console
python3 labs/lab03/part08/tests/check.py
```

실제 미완성 starter의 출력이며 종료 코드는 1입니다.

```text
Part08 incomplete: TODO: recover a factor, the second factor, and the private exponent
```

구현을 완성한 후 같은 검사 명령 또는 직접 실행을 사용하세요.

```console
python3 labs/lab03/part08/starter/attack.py
```

완료 검사의 첫 줄은 다음과 같습니다. 다음 줄은 실행마다 달라지는 서버의
`LAB03{...}`입니다. 이 첫 줄은 교수용 참조 구현으로 검증했습니다.

```text
Part08 complete: target verified all objectives
```

다른 구현은 `--solution /workspace/경로/attack.py`, 교수 서버는
`--url https://강사제공주소` 또는 `LAB03_TARGET_URL`로 지정합니다. 접속 오류가
나면 `healthy` 상태, 컨테이너 내부 실행, URL을 확인하세요. 만료된 세션은 새로
발급받습니다. 호스트에서 로그를 확인하거나 대상을 중지합니다.

```console
docker compose -f docker/compose.yml --profile lab03 logs --tail=30 lab03-target
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
```

## 6. 완료 조건 (Success Conditions)

서버가 새로운 `mu2`에 대한 유효한 서명, 결함 출력 차단, 무결함 서명 성공을
**모두** 확인한 경우에만 플래그를 반환합니다. 인수만 제출하거나, 결함 서명을
그대로 제출하거나, 정상 입력까지 모두 거부하는 것은 통과 조건이 아닙니다.

로컬 대상은 연습용입니다. Docker 제어권을 가진 사용자는 로컬 이미지·실행 상태를
조사할 수 있습니다. 실제 비공개 평가는 별도 키·플래그를 가진 교수 관리 서버에서
진행합니다. 컨테이너 파일 권한이나 소스 비공개만으로 로컬 비밀이 보호되지는 않습니다.

## 7. 제출물 (Submission Requirements)

완성한 `attack.py`, 인수 복구와 개인 지수 계산 설명, fresh 서명의 공개키 검증 결과,
결함/무결함 보호 경로의 요청·응답, 플래그, 아래 분석 답변을 제출하세요. 플래그는
강사 지정 채널로 제출하세요. 다른 세션의 비밀키를 공개하지 마세요.

## 8. 분석 질문 (Analysis Questions)

1. 한 CRT 분기만 잘못되었을 때 최대공약수에서 인수가 나타나는 이유는 무엇인가요?
2. 원래 대표값의 서명 대신 새로운 `mu2` 서명을 요구하는 이유는 무엇인가요?
3. 무결함 경로의 성공까지 확인해야 하는 이유는 무엇인가요?
4. 출력 검증이 이 결함 모델의 누출을 막는 이유와, 모든 물리적 결함 공격에 대한
   보안 증명을 의미하지 않는 이유를 설명하세요.
