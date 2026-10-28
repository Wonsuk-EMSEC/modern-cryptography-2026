# Part04: RSA Factorization Attack

**한국어** | [English](../../../en/labs/lab03/part04/README.md)

## 1. 학습 목표

작은 인수를 가진 RSA 모듈러스를 제한된 시험 나눗셈으로 인수분해하고, 비밀 지수와
평문을 복구합니다. 공개키의 전체 비트 길이만으로 인수분해 난도를 판단하면 안 되는
이유를 설명합니다.

## 2. 도전 시나리오

레거시 애플리케이션의 공개키와 암호화된 짧은 검증 값을 확보했습니다. 한 소수가
지나치게 작다는 감사 기록과 공개 탐색 상한을 이용하여 비밀키를 재구성하세요.

## 3. 제공 자료

- [data/challenge.json](data/challenge.json): 십진수 문자열 `n`, `e`, `c`,
  작은 인수의 포함 상한 `factor_bound`, 평문 바이트 길이와 SHA-256.
  정답 인수·비밀 지수·평문은 공개하지 않습니다.
- [starter/recover.py](starter/recover.py): `solve(challenge)` TODO.
- [tests/check.py](tests/check.py): 인수·비밀키·복호화 값의 공개 검사기.

문서용 별도 예: `n=55`, `e=3`, `m=7`, `c=13`입니다. 이 예는 공개 연습용이며
실제 challenge의 인수나 평문을 제공하지 않습니다.

## 4. 수행 과제

1. `n`, `e`, `c`를 정수로 읽으세요. 공개 상한 안에서 시험 나눗셈으로 인수를 찾고
   다른 인수를 구하세요. 고급 인수분해 알고리즘은 필요하지 않습니다.
2. phi와 d를 계산하고 `e*d mod phi == 1`을 확인하세요.
3. 복호화한 정수를 `message_bytes`바이트 big-endian으로 변환하세요. 선행 0도
   보존하고 SHA-256을 확인하세요.
4. `{'p': int, 'q': int, 'd': int, 'message_hex': str}`을 반환하세요.
   복호화 결과를 다시 암호화하여 원래 암호문과 일치하는지 확인하세요.
   소스에 challenge의 정답을 상수로 넣지 마세요.

## 5. 실행 방법

[Lab03 환경 설정](../README.md#setup)으로 공통 `course` 컨테이너를 시작한 뒤 실행합니다.

```console
cd /workspace/labs/lab03/part04
python3 tests/check.py
```

미완성 starter에서 실제 확인한 출력이며 종료 코드는 1입니다.

```text
FAIL: AssertionError: submission failed: NotImplementedError: factor the weak modulus and decrypt
```

완성 후 다음 명령을 실행합니다. 출력은 교수자 참조 구현으로 확인했습니다.
전체 JSON에는 인수·d·평문의 증거도 포함되며, 부모 검사기가 독립적으로 검증합니다.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part04_local_checks_passed}
```

다른 파일·입력은 `python3 tests/check.py --solution PATH --data PATH`로 검사합니다.
실행 제한은 10초입니다. 상한을 넘어 무한히 탐색하거나 큰 인수까지 나누지 마세요.
정수 변환·바이트 길이·big-endian 순서를 확인하면 해시 불일치를 진단할 수 있습니다.

## 6. 성공 조건

서로 다른 비자명한 인수의 곱이 n이고 작은 인수가 공개 범위 안에 있어야 합니다.
d는 phi에 대한 올바른 역원이어야 하며, 복호화·재암호화·원본 길이·SHA-256이
모두 일치해야 합니다. 복구한 다섯 바이트는 이 challenge만의 검증 값입니다.
`LAB03{part04_local_checks_passed}`는 공개된 비밀이 아닌 로컬 완료 영수증입니다.
최종 평가는 독립적으로 생성한 키와 평문으로 수행하므로 영수증 출력이나 공개
정답의 재사용만으로 통과하지 못합니다.

## 7. 제출 항목

완성한 `recover.py`, p·q·d와 복구한 바이트의 16진수, 탐색한 후보 수·실행 시간,
해시·재암호화 검사 결과와 [보고서](../REPORT_TEMPLATE.md)를 제출하세요.

## 8. 분석 질문

1. 한 인수가 작으면 다른 인수가 커도 왜 이 공격이 가능한가요?
2. n의 인수분해가 비밀 지수를 계산할 수 있게 하는 이유는 무엇인가요?
3. 복호화된 정수를 바이트로 바꿀 때 길이를 지정해야 하는 이유는 무엇인가요?
4. 복호화·재암호화와 SHA-256 확인은 각각 어떤 오류를 찾나요?
