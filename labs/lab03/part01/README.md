# Part01: Modular Exponentiation and Primality Testing

**한국어** | [English](../../../en/labs/lab03/part01/README.md)

## 1. 학습 목표

MSB부터 처리하는 Square-and-Multiply를 구현하고, 정확성·연산 횟수·상대
실행 시간으로 평가합니다. 제곱근까지의 시험 나눗셈과 Fermat 검사를 비교하고,
128비트 합성수가 base 2의 Fermat 검사를 통과할 수 있음을 보입니다.

## 2. 도전 시나리오

자원이 제한된 암호 장치의 거듭제곱과 소수 선별 모듈을 개발합니다. 느린 구현은
정답을 계산해도 성능 검사를 통과하지 못합니다. 공격자로서는 잘못된 소수 판정을
유도하는 구조적 합성수를 만들어야 합니다. 이 수를 이후 RSA의 소수로 사용하지 마세요.

## 3. 제공 자료

- [starter/math_challenges.py](starter/math_challenges.py): 다섯 함수의 계약과 TODO.
- [starter/prime64.py](starter/prime64.py): `0 <= n < 2**64`에서 정확한 소수 판정 보조 함수.
  세 번째 문제의 인수 검사에 사용하며, 시험 나눗셈 구현을 대신하지 않습니다.
- [data/challenge.json](data/challenge.json): 검증된 16·20·24·28·32비트 입력과
  해가 있는 네 개의 서로 겹치지 않는 탐색 구간. 각 구간은 100,001개 후보 이하입니다.
- [tests/check.py](tests/check.py): 공개 피드백 도구. 반환값을 직접 검사합니다.

## 4. 수행 과제

1. `naive_modular_exponentiation(base, exponent, modulus)`와
   `modular_exponentiation(...)`을 구현하세요. 음수 지수 또는 양수가 아닌
   모듈러스에는 `ValueError`를 발생시키세요. 지수 0, 모듈러스 1, 음수 밑도 처리합니다.
2. 빠른 함수는 맨 앞 비트를 포함한 모든 지수 비트를 MSB부터 처리합니다. 각 비트에서
   제곱하고, 비트가 1이면 밑을 곱하며, 각 곱셈 직후 모듈러 축소를 수행하세요.
   `pow`, `**`, 외부 거듭제곱 도구로 구현을 대신하지 마세요.
3. `is_prime_exact(n)`은 제곱근 경계까지 시험 나눗셈으로 구현하고,
   `fermat_test(n, base)`는 직접 작성한 빠른 거듭제곱 함수를 호출하세요.
   `n < 2` 또는 base와 n이 서로소가 아니면 Fermat 검사는 거짓을 반환합니다.
   크기가 같은 소수, 작은 인수가 있는 합성수, 작은 인수가 없는 합성수를 비교하세요.
4. `generate_pseudoprime(t_min, t_max)`에서 주어진 포함 구간을 실제로 탐색하세요.
   `p1=6t+1`, `p2=12t+1`, `p3=18t+1`이 모두 소수이면 `n=p1*p2*p3`를 검사하고
   `{'t': t, 'factors': [p1,p2,p3], 'n': n}`을 반환합니다. n은 정확히 128비트이고
   base 2의 Fermat 검사를 통과해야 합니다. 후보가 없으면 `ValueError`입니다.
   128비트 수 전체에 시험 나눗셈을 수행하지 마세요.
5. 세 구현의 곱셈 횟수와 실행 시간, 입력별 소수 검사 결과를 보고서에 기록하세요.
   정확한 소수 판정과 probable-prime 판정의 차이를 설명하세요.

## 5. 실행 방법

[Lab03 환경 설정](../README.md#setup)으로 공통 `course` 컨테이너를 시작하세요.
컨테이너의 `/workspace`에서 다음 명령을 실행합니다. 추가 설치는 필요 없습니다.

```console
cd /workspace/labs/lab03/part01
python3 tests/check.py
```

미완성 starter에서 실제 확인한 출력이며 종료 코드는 1입니다.

```text
FAIL: NotImplementedError: implement MSB-first square-and-multiply
```

완성 후 다음 명령으로 요약합니다. 아래 성공 출력은 교수자 참조 구현으로 확인한
결과입니다. 전체 JSON에는 현재 환경에서 측정한 시간과 연산 횟수가 포함됩니다.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part01_local_checks_passed}
```

검사는 30초 제한을 사용합니다. 상대 성능이 불안정하면 다른 CPU 작업을 줄이고
동일 컨테이너에서 다시 측정하세요. `--solution PATH`와 `--data PATH`로 별도
제출 파일·입력을 검사할 수 있습니다. 모듈 import 시 자동으로 탐색을 시작하지 마세요.

## 6. 성공 조건

무작위·경계 입력의 정확성, MSB 처리 순서, 지수 L비트에서 `L+popcount(exponent)`번의
곱셈을 확인합니다. 순진한 구현은 지수만큼 곱해야 합니다. 75,001·125,003·200,003의
지수에서 warm-up 후 반복 측정한 중앙값을 비교하며 프로세스 시작과 파일 I/O는 제외합니다.
필요 배속은 실행 환경의 naive/내장 pow 비율로 조정한
`min(10, max(2, naive_time / pow_time / 20))`입니다. 고정 밀리초 기준은 없습니다.
강의 Docker 환경의 최종 성능 기록은 교수자가 별도로 확인합니다.

두 소수 검사와 561 같은 Fermat 반례도 통과해야 합니다. 모든 탐색 구간의 서로 다른
후보에 대해 인수의 소수성, 구조, 곱, 합성수임, 128비트, base 2 검사를 확인합니다.
`LAB03{part01_local_checks_passed}`는 공개된 비밀이 아닌 로컬 완료 영수증입니다.
최종 평가는 새로운 구간·입력으로 소스 코드를 실행하므로 영수증만 출력해도 통과하지 않습니다.

## 7. 제출 항목

완성한 `math_challenges.py`, 각 구간의 t·세 인수·n, 연산 횟수와 반복 측정 중앙값 표,
실행 환경과 명령, [보고서](../REPORT_TEMPLATE.md)를 제출하세요. 함수는 import 가능해야 합니다.

## 8. 분석 질문

1. 지수가 k배가 될 때 순진한 구현과 Square-and-Multiply의 비용은 어떻게 달라지나요?
2. 작은 인수가 있는 합성수에서는 어떤 검사가 더 빠르며, 왜 그런가요?
3. base 2의 Fermat 통과만으로 소수임을 증명할 수 없는 이유는 무엇인가요?
4. 세 인수와 구조 조건이 단순한 Fermat 통과 이상의 증거를 제공하는 이유는 무엇인가요?
