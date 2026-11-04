# Part04: RSA Factorization Attack

**한국어** | [English](../../../en/labs/lab03/part04/README.md)

Part03에서는 소수 p·q가 주어졌지만, 이번에는 공개키와 암호문만 주어집니다.
다만 RSA 키를 만들 때 사용한 소수 하나가 지나치게 작다는 사실을 알고 있습니다.
이 작은 인수를 찾아 비밀 지수와 원래 메시지를 복구하세요.

## 1. 학습 목표

1. **인수분해:** 주어진 상한 안에서 시험 나눗셈으로 n의 인수를 찾습니다.
2. **평문 복구:** p·q로 비밀 지수를 계산하고 암호문을 복호화합니다.
3. **결과 확인:** 복구한 바이트의 길이·해시와 재암호화 결과를 확인합니다.

## 2. 제공 자료

- [starter/recover.py](starter/recover.py): 구현할 `solve(challenge)` 함수
- [data/challenge.json](data/challenge.json): 공개키·암호문과 탐색 조건
- [tests/check.py](tests/check.py): 인수·비밀 지수·복구 평문 검사

| 입력 항목 | 의미 |
| --- | --- |
| `n`, `e`, `c` | RSA 모듈러스·공개 지수·암호문(십진수 문자열) |
| `factor_bound` | 작은 인수의 탐색 상한(포함) |
| `message_bytes` | 원본 메시지의 바이트 길이 |
| `plaintext_sha256` | 복구 결과 확인용 SHA-256 |

## 3. 수행 과제

> **공격 흐름**
>
> $$n=pq\quad\longrightarrow\quad\phi=(p-1)(q-1),\quad d=e^{-1}\bmod\phi\quad\longrightarrow\quad m=c^d\bmod n$$
>
> 작은 연습 예: n=55, e=3, c=13입니다. 실제 과제 입력은 `challenge.json`을 사용하세요.

- **`solve(challenge)`: 인수분해로 평문 복구**

    `starter/recover.py`에 구현하세요. `challenge`는 검사기가 읽어 전달하는 딕셔너리입니다.
    `n`, `e`, `c`를 정수로 변환한 뒤, 2부터 `factor_bound`까지 시험 나눗셈으로 인수를 찾으세요.
    찾은 인수를 p로 두고 q=n/p를 정수 연산으로 구합니다. 탐색 상한을 넘기지 마세요.

    phi와 d를 계산하고 `e*d mod phi == 1`인지 확인하세요.
    이어서 암호문을 복호화합니다. 이 Part에서는 내장 `pow`를 사용할 수 있습니다.

    복호화한 정수를 **정확히 `message_bytes`바이트의 big-endian**으로 변환하세요.
    선행 0도 원본의 일부이므로 생략하면 안 됩니다. SHA-256이 `plaintext_sha256`과 같고,
    복구한 정수를 재암호화하면 원래 c가 나오는지 확인하세요.

    p·q·d는 정수, `message_hex`는 복구한 바이트의 16진수 문자열로 반환합니다.
    정답 인수·비밀 지수·평문을 코드에 상수로 넣으면 안 됩니다.

    ```python
    {'p': p, 'q': q, 'd': d, 'message_hex': message.hex()}
    ```

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
추가 설치나 별도 서버는 필요 없습니다.

```console
cd /workspace/labs/lab03/part04
python3 tests/check.py
```

미완성 starter에서는 다음 오류가 나오는 것이 정상입니다.
`solve()`를 구현하거나 수정한 뒤 같은 명령으로 다시 검사하세요.

```text
FAIL: AssertionError: submission failed: NotImplementedError: factor the weak modulus and decrypt
```

성공하면 JSON 출력에 다음 값이 표시됩니다(일부 발췌).

```json
{
  "status": "PASS",
  "receipt": "LAB03{part04_local_checks_passed}"
}
```

`proof`에는 반환한 p·q·d·`message_hex`가 표시됩니다. 복구한 메시지는 이 과제의
짧은 검증 값이며, PDF나 별도 파일이 생성되는 것은 아닙니다.
`LAB03{part04_local_checks_passed}`는 비밀값이 아니므로 보고서에 공개해도 됩니다.

<details>
<summary>추가 옵션과 오류 확인</summary>

`--solution PATH`로 다른 구현 파일을, `--data PATH`로 다른 JSON 입력을 검사할 수 있습니다.
전체 검사 제한은 10초이며, 제출 함수가 실행되는 하위 프로세스는 8초 제한입니다.
시간을 초과하면 탐색 상한을 확인하고, 해시가 다르면 정수 변환·바이트 길이·big-endian 순서를 확인하세요.

</details>

## 5. 성공 조건

- **인수분해:** p·q가 서로 다르고 각각 1보다 크며, 곱은 n이고 작은 인수는 탐색 상한 이내입니다.
- **비밀 지수:** `0 < d < phi`이고 `e*d mod phi == 1`입니다.
- **복구 결과:** 복호화·재암호화가 일치하고, 바이트 길이와 SHA-256이 제공된 값과 같습니다.

## 6. 제출 항목

완성한 `recover.py`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part04를 작성해 제출하세요.
p·q·d, 복구 바이트의 16진수, 탐색한 후보 수·실행 시간, 해시·재암호화 검사 결과와
아래 Checkpoint Questions 전체 답변을 포함하세요.

## 7. Checkpoint Questions

1. 한 인수가 작으면 다른 인수가 커도 왜 이 공격이 가능한가요?
2. n의 인수분해가 비밀 지수를 계산할 수 있게 하는 이유는 무엇인가요?
3. 복호화된 정수를 바이트로 바꿀 때 길이를 지정해야 하는 이유는 무엇인가요?
4. 복호화·재암호화와 SHA-256 확인은 각각 어떤 오류를 찾나요?
