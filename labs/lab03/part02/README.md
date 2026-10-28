# Part02: 예측 가능한 키 복구와 안전한 난수 생성

**한국어** | [English](../../../en/labs/lab03/part02/README.md)

## 1. Learning Objectives — 학습 목표

AES 자체의 강도와 키 생성의 안전성을 구분하고, 실제 glibc `srand()`/`rand()`
출력을 재현하여 암호화된 PDF를 복구합니다. OpenSSL 난수 API를 사용하고 실패 시
암호화를 중단하는 구현을 작성합니다.

## 2. Challenge Scenario — 실습 시나리오

회사의 기밀 보고서가 AES-128로 암호화되었습니다. 감사 중 암호문과 원래 C 소스를
확보했습니다. 보고서는 **2026-10-07 11:00경** 작성되었고 암호화 시각은
**2026-10-07 10:00:00–11:59:59, Asia/Seoul (UTC+09:00)** 범위입니다.
공개 메타데이터의 epoch 초는 양 끝을 포함합니다. 키나 정확한 시각은 제공하지 않습니다.

기존 PDF 암호화 소스가 없어 이 실습은 AES-128-CBC와 PKCS#7을 사용하도록 새로
구성했습니다. `time(NULL)`의 초 값을 seed로 하는 glibc의 C PRNG를 그대로 사용합니다.
Python의 `random`은 이 바이트열을 재현하지 않습니다. 동일한 glibc 환경인 공통
수업 컨테이너에서 생성·복구하세요.

## 3. Provided Materials — 제공 자료

| 파일 | 용도 |
| --- | --- |
| `data/confidential_report.enc` | 자체 헤더와 IV를 포함하는 암호화 PDF |
| `data/challenge.json` | 시간 구간, 포맷, 원본 PDF의 SHA-256 |
| `starter/pdf_encryption.c` | 감사에서 발견한 취약한 원본 코드 |
| `starter/recover.py` | 복구 함수와 CLI의 TODO |
| `starter/secure_random.c` | 안전한 키·IV 생성 함수의 TODO |
| `tests/check.py`, `tests/rng_driver.c` | 공개 피드백 검사와 독립 암호화 호출자 |

포맷은 8바이트 `LAB03E1\n`, 16바이트 IV, 나머지 CBC 암호문 순서입니다.
마지막 `\n`은 실제 LF 한 바이트입니다. 패딩은 OpenSSL EVP의 기본 PKCS#7입니다.
키는 포함되지 않습니다. 복호화된 PDF의 실습 영수증은 로컬 완료 자료이며, 숨겨진
교수자 채점 플래그는 별도 인스턴스에서 관리됩니다.

## 4. Tasks — 수행 과제

1. 원본 C 소스에서 seed, 키, IV가 만들어지는 순서를 분석하세요.
2. `recover(encrypted, start, end) -> bytes`를 작성하세요. 지정 범위의 후보를
   열거하고 C 라이브러리의 출력을 재현하여 전체 PDF를 복구하세요. IV를 후보
   판별에 사용할 수 있습니다. 키·seed·PDF·영수증을 하드코딩하지 마세요.
3. 원본 해시와 PDF 구조를 확인하고 PDF 안의 실습 영수증을 보고하세요.
4. `generate_key_iv()`를 작성하세요. 키는 `RAND_priv_bytes(key, 16)`, IV는
   `RAND_bytes(iv, 16)`를 사용하고 **각 호출이 1을 반환한 경우에만** 성공하세요.
   실패하면 0을 반환하여 호출자가 암호화 전에 중단하도록 하세요. `rand()`, 시각,
   고정값으로 대체하거나 직접 seed를 설정하지 마세요.
5. 공개 검사로 PDF 암·복호화, 두 난수 API의 실패 주입, 같은 시간 구간에 대한
   원래 공격의 실패를 확인하세요. 키 파일이나 복구 PDF를 `data/`에 추가하지 마세요.

## 5. How to Run — 실행 방법

[Lab03 실행 안내](../README.md)를 따라 저장소 루트의 호스트에서 시작합니다.

```console
docker compose -f docker/compose.yml run --rm course
```

Docker 시작 출력은 설치 상태에 따라 달라집니다. 컨테이너에서 실행하세요.

```console
cd /workspace/labs/lab03/part02
gcc -std=c11 -O2 -Wall -Wextra -Werror starter/pdf_encryption.c -lcrypto -o /tmp/lab03-pdf-encryption
python3 starter/recover.py --output /tmp/lab03-recovered.pdf
python3 tests/check.py
```

GCC는 성공 시 출력하지 않습니다. TODO 완성 후 복구 CLI는 제공 인스턴스에서
`Recovered 710 PDF bytes`를 출력합니다. 완성된 참조 구현으로 확인한 검사 출력:

```text
Part02: PDF SHA-256, glibc recovery, secure round-trip, RNG failures, bounded attack: OK
LAB03{part02_local_checks_passed}
```

미완성 starter는 실패하는 것이 정상입니다. 다른 위치의 구현은
`python3 tests/check.py --recovery /path/recover.py --secure /path/secure_random.c`로
검사합니다. `--data-dir`로 같은 포맷의 새 인스턴스를 지정할 수 있습니다.
`openssl/evp.h` 또는 라이브러리를 찾지 못하면 공통 수업 컨테이너인지 확인하세요.
학생이 별도로 패키지를 설치할 필요는 없습니다.

## 6. Success Conditions — 성공 조건

전체 PDF의 SHA-256과 페이지·xref 구조가 일치해야 합니다. 안전한 구현은 실제
두 OpenSSL API를 사용하고 정상 암·복호화를 수행하며, 각 API의 0 및 음수 반환을
주입했을 때 암호화를 시작하지 않아야 합니다. 기존 7,200개 시각 후보로 새 키·IV를
복구할 수 없어야 합니다. 이 공격의 실패나 통계 검사가 완전한 보안을 증명하지는
않습니다. 로컬 영수증은 비밀이 아니며 최종 채점은 격리된 환경의 새 입력으로 합니다.

## 7. Submission Requirements — 제출물

`recover.py`, `secure_random.c`, 복구 PDF의 SHA-256, 복구한 실습 영수증,
후보 개수·실행 시간, 테스트 로그와 분석 답변을 제출하세요. 복구 PDF와 민감한
중간값은 지정된 비공개 수업 채널로 제출하세요. 제출 코드에 공개 인스턴스의 답을
넣거나 성공 메시지만 출력해서는 통과할 수 없습니다.

## 8. Analysis Questions — 분석 질문

1. 128비트 AES 키를 사용해도 이 생성 방식의 탐색 공간이 작은 이유는 무엇인가요?
2. 키 다음에 생성된 공개 IV가 후보 seed를 판별하는 데 왜 도움이 되나요?
3. glibc 대신 다른 C 라이브러리를 쓰면 어떤 문제가 생길 수 있나요?
4. 키와 IV의 역할 및 사용하는 난수 API를 구분해서 설명하세요.
5. 난수 생성 실패 시 재시도·대체값 사용 없이 중단해야 하는 이유는 무엇인가요?
6. CBC만으로 메시지 무결성을 보장할 수 있나요? 이번 복구 공격의 원인과 구분하세요.
