# Part05: RSA Low Public Exponent Attack

**한국어** | [English](../../../en/labs/lab03/part05/README.md)

## 1. 학습 목표

e=3인 textbook RSA에서 `m^3<n`이면 모듈러 축소가 일어나지 않는다는 점을
이용합니다. 부동소수점 없이 정확한 정수 세제곱근을 구현하고 공격이 적용되지 않는
입력을 구분합니다.

## 2. 도전 시나리오

짧은 메시지를 인코딩 없이 공개 지수 3으로 암호화한 애플리케이션을 분석합니다.
공개키와 암호문만 사용하여 메시지를 복구하세요. n을 인수분해할 필요가 없습니다.

## 3. 제공 자료

- [data/challenge.json](data/challenge.json): `positive`·`negative` 각각의 십진수
  문자열 n·e·c와 실제 메시지의 SHA-256. positive는 `m^3<n`을 만족합니다.
  negative에서는 모듈러 축소가 일어나 직접 세제곱근 공격이 적용되지 않습니다.
- [starter/recover.py](starter/recover.py): 정확한 근과 복구 함수의 TODO.
- [tests/check.py](tests/check.py): 재암호화, 음성 사례, 큰 정수 경계 검사.

## 4. 수행 과제

1. `integer_cube_root(value)`는 음수가 아닌 정수에 대해
   `(floor(cuberoot(value)), is_exact)`를 반환하도록 구현하세요. 음수에는
   `ValueError`를 발생시키세요. 이진 탐색이나 정수 Newton 방법을 사용할 수 있습니다.
   `float`, `value ** (1/3)` 등 반올림에 의존하지 마세요.
2. `recover(challenge)`에서 정확한 세제곱근을 구하고 `m^3<n`과
   `pow(m,e,n)==c`를 검증한 뒤 정수를 반환하세요. e가 3이 아니거나 c가 `[0,n)`
   밖이거나 직접 근 공격이 적용되지 않으면 `None`을 반환합니다.
3. 복구한 정수를 최소 길이의 big-endian 바이트로 변환하여 메시지와 SHA-256을
   확인하세요. 복구한 메시지에는 Part별 완료 플래그가 포함됩니다.
4. negative 사례에서 근의 내림값을 평문으로 받아들이지 않고 거부하는지 확인하세요.
   다른 저지수 공격이나 인수분해로 범위를 확장하지 마세요.

## 5. 실행 방법

[Lab03 환경 설정](../README.md#setup)의 공통 `course` 컨테이너에서 실행합니다.

```console
cd /workspace/labs/lab03/part05
python3 tests/check.py
```

미완성 starter에서 실제 확인한 출력이며 종료 코드는 1입니다.

```text
FAIL: AssertionError: submission failed: NotImplementedError: implement an exact integer cube root
```

완성 후 다음 명령을 실행합니다. 출력은 교수자 참조 구현으로 확인했습니다.
전체 JSON에는 복구한 정수의 증거도 포함되며, 부모 검사기가 독립적으로 검증합니다.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part05_local_checks_passed}
```

`--solution PATH`·`--data PATH`로 다른 파일·입력을 검사할 수 있습니다. 10초 제한이
있습니다. 큰 정수에서만 실패한다면 부동소수점 변환, 탐색 경계, 세제곱 바로 전후의
처리를 확인하세요. 완료 영수증은 공개된 비밀이 아닌 로컬 피드백이며 메시지 속
challenge 플래그와 별개입니다.

## 6. 성공 조건

임의의 큰 정수·완전 세제곱·그 직전과 직후 값에서
`root^3 <= value < (root+1)^3`와 정확성 표시가 맞아야 합니다.
positive의 정확한 근·범위·재암호화·메시지 해시가 모두 맞고 negative는 거부해야 합니다.
공개 fixture 외의 새 정수와 ciphertext로도 검사합니다. 최종 평가는 독립 생성한
메시지·모듈러스를 사용하며, 고정된 플래그 출력만으로 통과하지 못합니다.
negative 거부는 다른 모든 공격에 대한 안전성을 의미하지 않습니다.

## 7. 제출 항목

완성한 `recover.py`, 복구한 정수와 메시지, 재암호화·해시 검사 결과,
negative 거부 이유, [보고서](../REPORT_TEMPLATE.md)를 제출하세요.

## 8. 분석 질문

1. `m^3<n`이면 RSA 암호화가 일반 정수 세제곱과 같아지는 이유는 무엇인가요?
2. 큰 정수의 세제곱근에 부동소수점을 쓰면 어떤 오류가 생기나요?
3. 근을 내림하여 재암호화하면 negative 사례에서 어떤 결과가 나오나요?
4. 무작위 인코딩이 이 공격 조건에 어떤 영향을 주나요?
