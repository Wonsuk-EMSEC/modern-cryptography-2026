# Part03: RSA Key Generation, Encryption, and CRT

**한국어** | [English](../../../en/labs/lab03/part03/README.md)

## 1. 학습 목표

C와 OpenSSL BIGNUM으로 RSA 키의 수학적 관계를 구현하고, 동일한 모듈러 거듭제곱
루틴을 사용한 직접 복호화와 CRT 복호화의 정확성·중앙값 성능을 비교합니다.

## 2. 도전 시나리오

제약된 장치의 RSA 엔진을 개발합니다. 먼저 RSA를 정확히 구현하고, 두 작은
모듈러스에서의 연산과 CRT 재결합으로 비밀키 연산을 가속해야 완료됩니다.
이 Part의 정수 단위 textbook RSA는 구현 학습용입니다. 메시지 인코딩은 Part06에서 다룹니다.

## 3. 제공 자료

- [starter/rsa_engine.h](starter/rsa_engine.h): `LabRSA` 필드와 네 함수의 계약.
- [starter/rsa_engine.c](starter/rsa_engine.c): 핵심 계산의 TODO.
- [starter/rsa_io.c](starter/rsa_io.c): 할당·정리, 16진수 인수 파일 읽기,
  `lab_from_bytes`·`lab_to_bytes` 변환 보조 함수.
- [data/](data/): 2048·3072비트 n을 구성하는 공개 소수 p와 q. 각 파일은 16진수 두 줄입니다.
  키 구현 과제이므로 이 소수는 의도적으로 공개됩니다.
- [tests/driver.c](tests/driver.c), [tests/check.py](tests/check.py): 독립 정답 검사와 벤치마크.

## 4. 수행 과제

1. 제공된 p·q·e=65537을 유지하고 `rsa_derive`에서 n과
   `phi=(p-1)(q-1)`에 대한 d를 계산하세요. `dp=d mod(p-1)`,
   `dq=d mod(q-1)`, `qinv=q^-1 mod p`도 계산합니다.
2. `rsa_encrypt`, `rsa_decrypt_direct`를 작성하세요. 각 함수는 각각 e·n 또는
   d·n으로 `BN_mod_exp`를 정확히 한 번 호출합니다. 입력은 `[0,n)`여야 합니다.
3. `rsa_decrypt_crt`는 `BN_mod_exp`를 정확히 두 번 호출하여
   `mp=c^dp mod p`, `mq=c^dq mod q`를 구한 뒤 CRT로 재결합합니다.
   음수 차이는 `BN_mod_sub` 등으로 처리하고 결과를 `[0,n)`에 두세요.
4. 모든 API 반환값과 할당 실패를 확인하세요. 성공은 1, 오류는 0입니다.
   헤더와 함수 인터페이스를 유지하고 별도 `main`을 추가하지 마세요.
5. 키 생성·초기화·입출력을 제외한 2048·3072비트의 직접/CRT 복호화 시간,
   반복 중앙값과 배속을 보고하세요. 같은 `BN_mod_exp`를 양쪽에서 사용합니다.

## 5. 실행 방법

[Lab03 환경 설정](../README.md#setup)의 공통 `course` 컨테이너에서 실행합니다.
GCC와 OpenSSL 개발 파일은 이미지에 포함됩니다. 검사기가 제출 소스를 임시 경로에
`gcc -std=c11 -O2 -Wall -Wextra -Werror ... -lcrypto`로 컴파일합니다.

```console
cd /workspace/labs/lab03/part03
python3 tests/check.py
```

미완성 starter에서 실제 확인한 출력입니다. 종료 코드는 1이며 행 번호는 변경될 수 있습니다.

```text
FAIL: AssertionError: 2048-bit check failed:
FAIL: saved_p && saved_q && rsa_derive(&k,ctx)==1 (line 99)
```

완성 후 다음 명령을 실행하세요. 아래 출력은 교수자 참조 구현으로 확인했습니다.

```console
python3 tests/check.py --fresh | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part03_local_checks_passed}
```

`--fresh`는 측정 전에 새 2048·3072비트 키를 생성합니다. `--solution PATH`로
다른 C 파일을 지정할 수 있습니다. 자세한 수치는 파이프 없이 실행해 JSON에서 확인하세요.
컴파일 오류는 stderr를 확인하고, 성능 변동이 크면 CPU 부하를 줄여 재측정하세요.
컴파일은 20초, 각 키 크기 실행은 45초 제한입니다.

## 6. 성공 조건

n·d·dp·dq·역원, 0·1·n-1·p·q와 무작위 메시지의 암복호화, 범위 밖 입력 거부를
검사합니다. 링커의 `BN_mod_exp` 래퍼로 실제 피연산자와 호출 횟수를 확인하므로
CRT 함수에서 직접 복호화를 다시 호출하거나 성공 문구만 출력하면 통과하지 못합니다.

warm-up 후 9회 측정의 중앙값을 사용하며 매 연산에 새로운 암호문을 제공합니다.
입력 준비·정답 비교·키 생성·파일 I/O는 측정 밖에서 수행합니다. 동일 라이브러리로
전체 모듈러스 거듭제곱과 두 작은 모듈러스 거듭제곱의 기준 시간을 직접 측정하고,
기준 배속 R에 대해 필요한 배속을 `1 + 0.35*(R-1)`로 조정합니다. 제출 구현의
직접·CRT 시간도 각 기준 시간의 1.8배 이내여야 합니다. 고정 밀리초 기준은 없습니다.
R이 1.05 이하이면 측정 환경을 점검해야 합니다. 강의 Docker 측정은 교수자가 별도 확인합니다.

`LAB03{part03_local_checks_passed}`는 비밀이 아닌 로컬 피드백입니다. 최종 평가는
새 소수·메시지를 사용하여 소스 자체를 격리된 환경에서 실행합니다.

## 7. 제출 항목

완성한 `rsa_engine.c`, 경고 없는 빌드·검사 로그, 두 키 크기의 직접/CRT 중앙값과
배속 표, [보고서](../REPORT_TEMPLATE.md)를 제출하세요. 헤더를 변경했다면 함께 제출하고 이유를 설명하세요.

## 8. 분석 질문

1. dp와 dq로 지수를 줄여도 원래 복호화 결과가 유지되는 이유는 무엇인가요?
2. p 또는 q의 배수인 메시지에 대해서도 구현이 동작하나요?
3. CRT의 두 거듭제곱과 재결합 중 어떤 비용이 지배적인가요?
4. 키 생성이나 I/O를 측정에 포함하면 비교가 어떻게 왜곡되나요?
