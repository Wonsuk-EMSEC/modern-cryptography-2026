# Part03: RSA Key Generation, Encryption, and CRT

**한국어** | [English](../../../en/labs/lab03/part03/README.md)

RSA 복호화가 오래 걸리는 프로그램을 개선하려고 합니다.
같은 암호문을 한 번의 큰 거듭제곱으로 복호화하는 방법과, 두 개의 작은 거듭제곱으로
나누어 계산하는 CRT 방법을 구현하세요. 결과는 같은지, 속도는 얼마나 달라지는지 비교합니다.

## 1. 학습 목표

1. **키 계산:** 주어진 소수 p·q로 RSA 키와 CRT 계산에 필요한 값을 구합니다.
2. **암복호화:** C와 OpenSSL BIGNUM으로 RSA 암호화·직접 복호화를 구현합니다.
3. **CRT 비교:** CRT 복호화를 구현하고 직접 복호화와 정확성·속도를 비교합니다.

이 Part는 정수를 다루는 textbook RSA 실습입니다. 메시지 인코딩은 Part06에서 다룹니다.

## 2. 제공 자료

- [starter/rsa_engine.c](starter/rsa_engine.c): 구현할 네 함수의 TODO
- [starter/rsa_engine.h](starter/rsa_engine.h): `LabRSA` 구조체와 함수 인터페이스
- [starter/rsa_io.c](starter/rsa_io.c): 메모리 할당·정리, 소수 파일 읽기, 바이트 변환 보조 함수
- [data/](data/): 2048·3072비트 n을 구성하는 소수 p·q 파일(16진수 두 줄)
- [tests/check.py](tests/check.py), [tests/driver.c](tests/driver.c): 컴파일·정확성 검사·성능 측정

**수정할 파일은 `starter/rsa_engine.c`입니다.** 소수를 직접 생성하지 않고 제공된 p·q를 사용합니다.
검사기가 `LabRSA`의 BIGNUM 필드를 할당하고 p·q·e를 준비합니다.
네 함수 모두 API 반환값과 임시 메모리 할당 실패를 확인하고, 성공은 1·오류는 0을 반환하세요.
헤더와 함수 인터페이스는 유지하고, 별도 `main()`은 추가하지 마세요.

## 3. 수행 과제

### 1단계: RSA 키 값 계산하기

- **`rsa_derive(key, ctx)`: 키와 CRT 보조 값 계산**

    제공된 p·q·e=65537을 바꾸지 않고 다음 값을 계산해 `key`의 해당 필드에 저장하세요.
    d는 반드시 아래의 phi에 대한 역원으로 구합니다.

    $$n=pq,\quad \phi=(p-1)(q-1),\quad d=e^{-1}\bmod\phi$$

    $$dp=d\bmod(p-1),\quad dq=d\bmod(q-1),\quad qinv=q^{-1}\bmod p$$

    p·q를 직접 감소시키지 않도록 주의하세요. 계산에 필요한 임시 BIGNUM은 사용 후 정리합니다.

### 2단계: 암호화와 직접 복호화 구현하기

> **계산 목표**
>
> $$c=m^e\bmod n,\qquad m=c^d\bmod n$$
>
> m은 평문 정수, c는 암호문 정수입니다.

- **`rsa_encrypt(out, message, key, ctx)`: 암호화**

    `0 <= message < n`인지 확인하고, 범위 밖 입력은 0을 반환하세요.
    `BN_mod_exp`를 e·n으로 정확히 한 번 호출하여 암호문을 `out`에 저장합니다.
    연산 성공 시 1, 실패 시 0을 반환하세요.

- **`rsa_decrypt_direct(out, ciphertext, key, ctx)`: 직접 복호화**

    `0 <= ciphertext < n`인지 확인하고, 범위 밖 입력은 0을 반환하세요.
    `BN_mod_exp`를 d·n으로 정확히 한 번 호출하여 평문을 `out`에 저장합니다.
    연산 성공 시 1, 실패 시 0을 반환하세요.

### 3단계: CRT 복호화 구현하고 비교하기

- **`rsa_decrypt_crt(out, ciphertext, key, ctx)`: CRT 복호화**

    `0 <= ciphertext < n`인지 확인하고, 범위 밖 입력은 0을 반환하세요.
    `BN_mod_exp`를 정확히 두 번 호출하여 다음 값을 계산합니다.

    $$m_p=c^{dp}\bmod p,\qquad m_q=c^{dq}\bmod q$$

    두 결과를 중국인의 나머지 정리(CRT)로 재결합해 평문을 `out`에 저장하세요.
    1단계에서 계산한 `qinv`를 사용할 수 있습니다. 나머지의 차이가 음수가 될 수 있으므로
    `BN_mod_sub` 등으로 처리하고, 최종 결과는 `[0,n)` 범위에 두세요.
    성공은 1, 오류는 0을 반환하고 임시 메모리를 정리합니다.

- **결과와 속도 비교하기**

    두 복호화 결과가 원래 평문과 같은지 확인하세요.
    2048·3072비트 키에서 직접/CRT 복호화의 반복 측정 중앙값과 배속을 비교합니다.
    양쪽 모두 `BN_mod_exp`를 사용하고, 키 생성·초기화·입출력 시간은 제외하세요.

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
검사기가 C 소스를 자동으로 컴파일합니다. 추가 설치나 별도 서버는 필요 없습니다.

```console
cd /workspace/labs/lab03/part03
python3 tests/check.py
```

미완성 starter에서는 다음 오류가 나오는 것이 정상입니다. 행 번호는 달라질 수 있습니다.
구현하거나 수정한 뒤 같은 명령으로 다시 검사하세요.

```text
FAIL: AssertionError: 2048-bit check failed:
FAIL: saved_p && saved_q && rsa_derive(&k,ctx)==1 (line 99)
```

제공된 소수로 통과했다면 새 소수로도 검사하세요. 새 소수 생성 시간은 성능 측정에서 제외됩니다.

```console
python3 tests/check.py --fresh
```

성공하면 JSON 출력에 다음 값이 표시됩니다(일부 발췌).

```json
{
  "status": "PASS",
  "receipt": "LAB03{part03_local_checks_passed}"
}
```

<details>
<summary>검사 결과 읽기와 추가 옵션</summary>

JSON의 `performance`에는 키 크기별 측정 결과가 있습니다.

| 항목 | 의미 |
| --- | --- |
| `bits` | RSA 모듈러스 n의 비트 길이 |
| `direct_ns`, `crt_ns` | 직접·CRT 복호화 시간의 중앙값(ns) |
| `speedup` | 직접 복호화 시간 / CRT 복호화 시간 |
| `required_speedup` | 해당 환경에서 요구하는 최소 배속 |
| `baseline_direct_ns`, `baseline_split_ns` | 성능 기준 계산에 쓰는 전체·분할 거듭제곱 시간 |

`--solution PATH`로 다른 C 파일을, `--data PATH`로 소수 파일 디렉터리를 지정할 수 있습니다.
컴파일 오류는 오류 출력을 확인하세요. 컴파일 제한은 20초, 각 키 크기의 실행 제한은 45초입니다.
성능 결과가 불안정하면 CPU 부하를 줄이고 같은 컨테이너에서 다시 측정하세요.

</details>

## 5. 성공 조건

- **키 계산:** n·d·dp·dq·qinv가 올바르고 제공된 p·q·e를 유지합니다.
- **암복호화:** 0·1·n−1·p·q와 무작위 평문이 정상 처리되고, 범위 밖 입력은 거부합니다.
- **연산 방식:** 지정된 피연산자로 암호화·직접 복호화는 `BN_mod_exp` 1회, CRT 복호화는 2회를 호출합니다.
- **성능:** 두 키 크기에서 CRT 복호화가 직접 복호화 대비 성능 기준을 만족합니다.

<details>
<summary>성능 측정 기준</summary>

준비 실행(warm-up) 후 9회 측정의 중앙값을 사용하며, 매 연산마다 새로운 암호문을 제공합니다.
입력 준비·정답 비교·키 생성·파일 I/O는 측정에서 제외합니다.

검사기는 같은 라이브러리의 전체 모듈러스 거듭제곱과 두 작은 모듈러스 거듭제곱으로 기준 배속 R을 구합니다.
필요한 배속은 `1 + 0.35*(R-1)`이며, 제출 구현의 직접·CRT 시간도 각각의 기준 시간의 1.8배 이내여야 합니다.
고정 밀리초 기준은 없습니다. R이 1.05 이하이면 측정 환경을 점검해야 합니다.
강의 Docker 측정은 교수자가 별도로 확인합니다.

</details>

## 6. 제출 항목

완성한 `rsa_engine.c`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part03을 작성해 제출하세요.
경고 없는 빌드·검사 로그, 두 키 크기의 직접/CRT 중앙값·배속 표와 아래 Checkpoint Questions 전체 답변을 포함하세요.
헤더를 변경했다면 함께 제출하고 이유를 설명하세요.

## 7. Checkpoint Questions

1. dp와 dq로 지수를 줄여도 원래 복호화 결과가 유지되는 이유는 무엇인가요?
2. p 또는 q의 배수인 메시지에 대해서도 구현이 동작하나요?
3. CRT의 두 거듭제곱과 재결합 중 어떤 비용이 지배적인가요?
4. 키 생성이나 I/O를 측정에 포함하면 비교가 어떻게 왜곡되나요?
