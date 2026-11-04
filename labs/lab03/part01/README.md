# Part01: Modular Exponentiation and Primality Testing

**한국어** | [English](../../../en/labs/lab03/part01/README.md)

RSA 키 생성에 사용할 소수 검사 프로그램을 점검합니다. 개발자는 “Fermat 검사를
통과한 수를 소수로 사용하면 된다”고 주장합니다. 이 판단을 믿어도 될까요?

먼저 검사에 필요한 거듭제곱 연산을 구현하고, 시험 나눗셈과 Fermat 검사의 결과와
속도를 비교하세요. 마지막으로 Fermat 검사를 통과하는 128비트 합성수를 찾아
개발자의 주장을 검증합니다. 찾은 합성수는 실제 RSA 키 생성에 사용하지 마세요.

## 1. 학습 목표

이 실습은 다음 세 단계로 진행합니다.

1. **거듭제곱 계산:** 같은 값을 구하는 느린 방법과 빠른 방법을 구현하고 비교합니다.
2. **소수 검사:** 정확히 판정하는 방법과 빠르게 후보를 걸러내는 방법을 비교합니다.
3. **반례 찾기:** 소수가 아닌데도 Fermat 검사를 통과하는 128비트 수를 찾습니다.

## 2. 제공 자료

- [starter/math_challenges.py](starter/math_challenges.py) : 다섯 함수의 TODO 구현
- [starter/prime64.py](starter/prime64.py) : 3단계에서 작은 인수들의 소수성을 확인하는 `is_prime64()`
- [data/challenge.json](data/challenge.json) : 소수 검사 비교 입력과 합성수 탐색 구간
- [tests/check.py](tests/check.py) : 구현 검사와 성능 측정

`challenge.json`에는 16·20·24·28·32비트 비교 입력과, 각각 해가 있는 네 개의
탐색 구간이 있습니다. 구간마다 후보 t는 100,001개 이하입니다.

## 3. 수행 과제

### 1단계: 같은 거듭제곱을 두 방법으로 계산하기

`starter/math_challenges.py`의 다음 두 함수를 구현하고, 곱셈 횟수와 실행 시간을 비교하세요.

> **계산 목표**
>
> $$r = b^e \bmod m$$
>
> 예:
>
> $$3^5 \bmod 7 = 243 \bmod 7 = 5$$
>
> 여기서 `b = base`, `e = exponent`, `m = modulus`입니다.

- **`naive_modular_exponentiation(base, exponent, modulus)`: 반복 곱셈**

    `1 % modulus`에서 시작해 밑을 `exponent`번 곱하고, 곱셈마다 나머지를 구하세요.
    음수 지수 또는 0 이하의 모듈러스에는 `ValueError`를 발생시킵니다.
    지수 0이면 곱셈 없이 초기값을 반환하며, 모듈러스 1과 음수 밑도 처리해야 합니다.
    `pow`, `**`, 외부 거듭제곱 함수로 반복 곱셈을 대신하지 마세요.

- **`modular_exponentiation(base, exponent, modulus)`: Square-and-Multiply**

    `1 % modulus`에서 시작해 지수의 이진 표현을 맨 앞 비트부터 처리하세요(MSB-first).
    맨 앞 비트를 포함해 매 비트마다 현재 결과를 제곱하고, 비트가 1이면 밑을 한 번 더 곱합니다.
    각 곱셈 직후 나머지를 구하세요. 예를 들어 지수 13은 `1101`이므로 제곱 4번과 추가 곱셈 3번이 필요합니다.
    음수 지수 또는 0 이하의 모듈러스에는 `ValueError`를 발생시키고, 지수 0·모듈러스 1·음수 밑도 처리하세요.
    `pow`, `**`, 외부 거듭제곱 함수로 구현을 대신하지 마세요.

- **결과와 속도 비교하기**

    두 함수의 결과가 내장 `pow(base, exponent, modulus)`와 일치하는지 확인하세요.
    직접 구현한 두 함수의 곱셈 횟수와, 두 함수·내장 `pow`의 실행 시간을 비교합니다.
    내장 `pow`는 정답 확인과 성능 비교용으로만 사용하세요.

### 2단계: 두 소수 검사 비교하기

같은 파일에서 다음 두 함수를 구현하세요. 두 함수 모두 `True` 또는 `False`를 반환하지만,
**`True`가 의미하는 바는 서로 다릅니다.**

- **`is_prime_exact(n)`: 시험 나눗셈으로 정확히 판정하기**

    2부터 n의 제곱근까지 나누어떨어지는 인수가 있는지 검사하세요. 제곱근 경계도 포함해야 합니다.
    인수가 있으면 `False`, 없으면 `True`입니다. `n < 2`이면 `False`를 반환합니다.
    이 함수는 직접 구현하며, 제공된 `is_prime64()`로 대신하지 않습니다.

- **`fermat_test(n, base)`: Fermat 검사로 소수 후보 걸러내기**

    `base`와 n이 서로소일 때 `base^(n-1) mod n == 1`인지 확인하세요.
    거듭제곱은 **1단계에서 만든 `modular_exponentiation()`**을 호출합니다.
    `n < 2`이거나 두 수의 최대공약수가 1이 아니면 `False`를 반환합니다.
    여기서 `True`는 검사를 통과했다는 뜻이며, 소수라는 보장은 아닙니다.

- **결과와 속도 비교하기**

    `data/challenge.json`의 `prime_sets`를 사용하세요. 각 그룹의 `values`에는 같은 비트 길이의
    소수, 작은 인수가 있는 합성수, 작은 인수가 없는 합성수가 들어 있습니다.
    두 함수의 반환값과 실행 시간을 비교하고, Fermat 검사의 `base`는 2로 설정하세요.

### 3단계: Fermat 검사를 통과하는 합성수 찾기

- **`generate_pseudoprime(t_min, t_max)`: Fermat 검사를 통과하는 합성수 찾기**

    같은 파일에서 구현하세요. 양 끝을 포함한 구간에서 t를 바꾸며 다음 수를 만듭니다.

    $$p_1=6t+1,\quad p_2=12t+1,\quad p_3=18t+1,\quad n=p_1p_2p_3$$

    세 인수가 모두 소수인지 제공된 `prime64.is_prime64()`로 확인하세요.
    각 인수는 이 함수가 지원하는 `0 <= n < 2**64` 범위에 들어갑니다.
    곱 n은 정확히 128비트이고, base 2의 Fermat 검사를 통과해야 합니다.
    비트 길이는 `n.bit_length()`로 확인할 수 있습니다. **128비트 n에 시험 나눗셈을 수행하지 마세요.**

    후보를 찾으면 `{'t': t, 'factors': [p1, p2, p3], 'n': n}`을 반환하고,
    없으면 `ValueError`를 발생시키세요. 전달받은 구간을 실제로 탐색해야 하며,
    답을 하드코딩하거나 모듈 import 시 탐색을 시작하면 안 됩니다.

검사기는 `data/challenge.json`의 `search_windows`에 있는 네 구간을 각각 전달합니다.

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
추가 설치나 별도 서버는 필요 없습니다.

```console
cd /workspace/labs/lab03/part01
python3 tests/check.py
```

미완성 starter에서는 다음 오류가 나오는 것이 정상입니다. 검사는 첫 실패에서 멈추므로,
해당 함수를 구현하거나 수정한 뒤 같은 명령으로 다시 검사하세요.

```text
FAIL: NotImplementedError: implement MSB-first square-and-multiply
```

모든 검사를 통과하면 JSON 출력에 다음 값이 표시됩니다(일부 발췌).

```json
{
  "status": "PASS",
  "receipt": "LAB03{part01_local_checks_passed}"
}
```

`LAB03{part01_local_checks_passed}`는 비밀값이 아니므로 보고서에 공개해도 됩니다.

<details>
<summary>검사 결과 읽기와 추가 옵션</summary>

| JSON 항목 | 내용 |
| --- | --- |
| `performance` | 거듭제곱 시간, 연산 수, 상대 속도 |
| `primality` | 입력별 시험 나눗셈·Fermat 검사 시간 |
| `proof` | 각 구간에서 찾은 t, 세 인수, n |

`naive_ns`는 검사기 기준 구현의 시간입니다. 직접 작성한 naive 함수의 시간과
소수 검사 반환값은 별도로 기록하세요. 내장 `pow`의 내부 곱셈 횟수는 제공되지 않습니다.

검사 제한 시간은 30초입니다. 성능 결과가 불안정하면 다른 CPU 작업을 줄이고 같은 컨테이너에서
다시 측정하세요. `--solution PATH`와 `--data PATH`로 다른 구현 파일·입력을 검사할 수 있습니다.

</details>

## 5. 성공 조건

- **1단계:** 두 함수가 경계값을 포함해 올바른 결과를 반환하고, 지정된 연산 순서·곱셈 횟수를 지킵니다.
  빠른 함수는 기준 naive 구현 대비 성능 기준도 만족해야 합니다.
- **2단계:** 두 소수 검사가 정의대로 동작하며, 561 같은 합성수의 Fermat 통과도 확인합니다.
- **3단계:** 네 구간에서 각각 서로 다른 후보를 찾고, 인수의 소수성·구조·곱·128비트 길이·base 2 검사를 만족합니다.

<details>
<summary>연산 횟수와 성능 기준</summary>

naive 함수의 곱셈 횟수는 지수와 같아야 합니다. 빠른 함수는 양수 지수가 L비트일 때
`L + popcount(exponent)`번 곱해야 합니다. `popcount`는 이진 표현에서 1인 비트의 개수입니다.

성능은 지수 75,001·125,003·200,003에서 준비 실행(warm-up) 후 반복 측정한 중앙값으로 비교합니다.
프로세스 시작과 파일 I/O는 제외합니다. 필요한 배속은 실행 환경에 따라
`min(10, max(2, naive_time / pow_time / 20))`으로 정합니다.
`naive_time`은 검사기 기준 구현, `pow_time`은 내장 `pow`의 시간이며, 고정 밀리초 기준은 없습니다.
강의 Docker 환경의 최종 성능 기록은 교수자가 별도로 확인합니다.

</details>

## 6. 제출 항목

완성한 `math_challenges.py`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part01을 작성해 제출하세요.
아래 Checkpoint Questions 전체 답변도 포함하세요.

## 7. Checkpoint Questions

1. 지수가 k배가 될 때 순진한 구현과 Square-and-Multiply의 비용은 어떻게 달라지나요?
2. 작은 인수가 있는 합성수에서는 어떤 검사가 더 빠르며, 왜 그런가요?
3. base 2의 Fermat 통과만으로 소수임을 증명할 수 없는 이유는 무엇인가요?
4. 세 인수와 구조 조건이 단순한 Fermat 통과 이상의 증거를 제공하는 이유는 무엇인가요?
