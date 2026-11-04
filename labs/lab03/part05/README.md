# Part05: RSA Low Public Exponent Attack

**한국어** | [English](../../../en/labs/lab03/part05/README.md)

공개 지수 e=3으로 짧은 메시지를 인코딩 없이 RSA 암호화한 프로그램을 분석합니다.
메시지가 충분히 작다면, n을 인수분해하거나 비밀키를 구하지 않고도 복구할 수 있습니다.
암호문의 세제곱근으로 메시지를 찾고, 이 방법이 적용되지 않는 입력은 구분해 보세요.

## 1. 학습 목표

1. **정수 세제곱근:** 큰 정수의 세제곱근을 부동소수점 없이 계산합니다.
2. **평문 복구:** 공격 조건을 확인하고, 정확한 근에서 메시지를 복구합니다.
3. **적용 범위:** 공격이 적용되지 않을 때 잘못된 평문 대신 `None`을 반환합니다.

## 2. 제공 자료

- [starter/recover.py](starter/recover.py): 구현할 두 함수의 TODO
- [data/challenge.json](data/challenge.json): 공격 성공·실패 사례와 메시지 해시
- [tests/check.py](tests/check.py): 정수근·복구 결과·경계값 검사

| 입력 항목 | 의미 |
| --- | --- |
| `positive` | m³<n을 만족하는 사례의 n·e·c(십진수 문자열) |
| `negative` | 모듈러 축소가 일어나 직접 세제곱근 공격이 적용되지 않는 사례의 n·e·c |
| `message_sha256` | positive에서 복구할 메시지의 SHA-256 |

## 3. 수행 과제

> **공격 조건**
>
> $$e=3,\quad m^3<n\quad\Longrightarrow\quad c=m^3\bmod n=m^3\quad\Longrightarrow\quad m=\sqrt[3]{c}$$
>
> 예: n=55, m=3이면 c=27이므로 세제곱근 3으로 평문을 복구할 수 있습니다.

### 1단계: 정확한 정수 세제곱근 구하기

- **`integer_cube_root(value)`: 정수근과 정확성 여부 반환**

    `starter/recover.py`에 구현하세요. 음수가 아닌 정수에 대해 `(root, is_exact)`를 반환합니다.
    `root`는 세제곱근을 내린 정수이고, `is_exact`는 `root³ == value`인지 나타내는 bool입니다.
    예를 들어 27에는 `(3, True)`, 28에는 `(3, False)`를 반환합니다.

    이진 탐색이나 정수 Newton 방법으로 구현하세요. `float`, `value ** (1/3)` 등
    부동소수점 반올림에 의존하면 안 됩니다. 0·1도 처리하고, 음수에는 `ValueError`를 발생시키세요.

### 2단계: 평문 복구와 공격 조건 확인하기

- **`recover(challenge)`: 적용 가능한 경우에만 평문 반환**

    같은 파일에 구현하세요. `challenge`에는 positive 또는 negative **한 사례의 n·e·c**가 전달됩니다.
    세 값을 정수로 변환하고 `integer_cube_root()`로 c의 세제곱근을 구하세요.

    정확한 근 m에 대해 `m³<n`과 `pow(m,e,n)==c`를 확인한 뒤 **정수 m**을 반환합니다.
    e가 3이 아니거나 c가 `[0,n)` 밖이거나 정확한 근이 아니면 `None`을 반환하세요.
    내림한 근을 평문으로 받아들이거나, 다른 저지수 공격·인수분해로 확장하지 마세요.

- **메시지 확인하기**

    복구한 정수를 최소 길이의 big-endian 바이트로 바꾸고,
    SHA-256을 `challenge.json`의 `message_sha256`과 비교하세요. 메시지에는 이 Part의 플래그가 들어 있습니다.
    Part04의 고정 바이트 길이 변환과 구분하세요.

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
추가 설치나 별도 서버는 필요 없습니다.

```console
cd /workspace/labs/lab03/part05
python3 tests/check.py
```

미완성 starter에서는 다음 오류가 나오는 것이 정상입니다.
두 함수를 구현하거나 수정한 뒤 같은 명령으로 다시 검사하세요.

```text
FAIL: AssertionError: submission failed: NotImplementedError: implement an exact integer cube root
```

성공하면 JSON 출력에 다음 값이 표시됩니다(일부 발췌).

```json
{
  "status": "PASS",
  "receipt": "LAB03{part05_local_checks_passed}"
}
```

`proof.m`은 복구한 정수, `proof.negative_rejected`는 negative 사례의 거부 여부입니다.
메시지 문자열은 검사기가 출력하지 않으므로, 복구한 정수를 바이트로 변환해 확인하세요.
`LAB03{part05_local_checks_passed}`는 비밀값이 아니므로 보고서에 공개해도 됩니다.
이 검사 완료 표식은 복구 메시지 안의 플래그와 별개입니다.

<details>
<summary>추가 옵션과 오류 확인</summary>

`--solution PATH`로 다른 구현 파일을, `--data PATH`로 다른 JSON 입력을 검사할 수 있습니다.
전체 검사 제한은 10초이며, 제출 함수가 실행되는 하위 프로세스는 8초 제한입니다.
큰 정수에서만 실패한다면 부동소수점 사용, 탐색 경계, 완전 세제곱 바로 전후 값의 처리를 확인하세요.

</details>

## 5. 성공 조건

- **정수근:** 큰 정수·완전 세제곱·그 직전과 직후 값에서 `root³ <= value < (root+1)³`이며 정확성 표시가 맞습니다.
- **positive 복구:** 정확한 근·범위·재암호화·메시지 SHA-256이 모두 맞습니다.
- **negative 거부:** 직접 세제곱근 공격이 적용되지 않으면 `None`을 반환합니다.
  공개 데이터 외의 새 정수·암호문과 잘못된 e·c 입력도 검사합니다.

negative 거부는 다른 모든 공격에도 안전하다는 뜻은 아닙니다.

## 6. 제출 항목

완성한 `recover.py`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part05를 작성해 제출하세요.
복구한 정수·메시지, 재암호화·해시 검사 결과, negative 거부 이유와
아래 Checkpoint Questions 전체 답변을 포함하세요.

## 7. Checkpoint Questions

1. `m^3<n`이면 RSA 암호화가 일반 정수 세제곱과 같아지는 이유는 무엇인가요?
2. 큰 정수의 세제곱근에 부동소수점을 쓰면 어떤 오류가 생기나요?
3. 근을 내림하여 재암호화하면 negative 사례에서 어떤 결과가 나오나요?
4. 무작위 인코딩이 이 공격 조건에 어떤 영향을 주나요?
