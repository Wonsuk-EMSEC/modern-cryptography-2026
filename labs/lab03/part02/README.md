# Part02: 예측 가능한 키 복구와 안전한 난수 생성

**한국어** | [English](../../../en/labs/lab03/part02/README.md)

AES-128로 암호화된 기밀 PDF와 암호화에 사용된 C 코드를 확보했습니다.
코드를 살펴보니 암호화 시각을 난수의 시작값(seed)으로 사용하고 있습니다.
대략적인 시각만 알아도 키를 찾아 PDF를 복구할 수 있을까요?

## 1. 학습 목표

1. **PDF 복구:** 시각을 seed로 사용하는 난수의 출력을 재현해 암호화 키를 찾습니다.
2. **난수 생성 수정:** OpenSSL로 키·IV를 생성하고, 난수 생성 실패 시 암호화를 중단하도록 합니다.

## 2. 제공 자료

- [starter/pdf_encryption.c](starter/pdf_encryption.c): 분석할 원본 암호화 코드
- [starter/recover.py](starter/recover.py): PDF 복구 함수의 TODO와 제공된 실행 코드
- [starter/secure_random.c](starter/secure_random.c): 안전한 키·IV 생성 함수의 TODO
- [data/confidential_report.enc](data/confidential_report.enc): 암호화된 PDF
- [data/challenge.json](data/challenge.json): 탐색 시간 구간, 파일 포맷, 원본 PDF의 SHA-256
- [tests/check.py](tests/check.py), [tests/rng_driver.c](tests/rng_driver.c): 복구·암복호화·오류 처리 검사

암호화 시각은 **2026-10-07 10:00:00–11:59:59, Asia/Seoul (UTC+09:00)** 범위입니다.
`challenge.json`의 `start_epoch`와 `end_epoch`는 이 구간을 초 단위로 나타냅니다.
양 끝을 포함하면 후보는 **7,200개**이며, 정확한 시각과 키는 제공되지 않습니다.

## 3. 수행 과제

### 1단계: 시각으로 만든 키를 찾아 PDF 복구하기

먼저 `starter/pdf_encryption.c`에서 `srand()` 호출과 키·IV 생성 순서를 확인하세요.

> **암호화 파일 구조**
>
> `헤더 8바이트 | IV 16바이트 | AES-128-CBC 암호문`
>
> 헤더는 `LAB03E1\n`이며, `\n`은 실제 LF 한 바이트입니다. 키는 파일에 포함되지 않습니다.

- **`recover(encrypted, start, end) -> bytes`: PDF 복구**

    `starter/recover.py`에 구현하세요. `encrypted`는 파일 전체 바이트이고,
    `start`와 `end`는 탐색할 epoch 초입니다. 양 끝을 포함한 후보 시각마다 원본 코드와
    같은 순서로 키·IV를 생성하세요. 파일에 저장된 IV를 후보 판별에 사용할 수 있습니다.

    Python의 `random` 대신 **glibc의 `srand()`·`rand()`** 출력을 재현해야 합니다.
    Python 표준 라이브러리 `ctypes`로 C 라이브러리를 호출할 수 있습니다.
    운영체제별 난수 구현 차이를 피하도록 수업용 `course` 컨테이너에서 실행하세요.

    AES-128-CBC로 복호화하고 PKCS#7 패딩을 제거한 **PDF 전체 바이트**를 반환하세요.
    키·seed·PDF·실습 영수증을 하드코딩하면 안 됩니다.

- **복구 결과 확인하기**

    PDF가 정상적으로 열리는지 확인하고, SHA-256을 `challenge.json`의 `sha256`과 비교하세요.
    PDF 안의 실습 영수증, 탐색한 후보 개수와 실행 시간도 기록합니다.
    검사기는 PDF의 페이지와 xref(객체 위치를 기록한 표) 구조도 확인합니다.

### 2단계: 안전한 키·IV 생성으로 바꾸기

- **`generate_key_iv(key, iv)`: 안전한 난수 생성**

    `starter/secure_random.c`에 구현하세요. 16바이트 키는 `RAND_priv_bytes(key, 16)`,
    16바이트 IV는 `RAND_bytes(iv, 16)`로 생성합니다.
    **두 호출이 모두 1을 반환한 경우에만 1을 반환**하고, 하나라도 실패하면 0을 반환하세요.
    호출자는 이 결과가 0이면 암호화를 시작하지 않습니다.

    `rand()`, 시각, 고정값을 대체 수단으로 사용하거나 직접 seed를 설정하면 안 됩니다.
    검사기는 정상 암복호화뿐 아니라 두 API가 각각 0 또는 음수를 반환하도록 만든 상황에서도
    암호화가 중단되는지 확인합니다.

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
추가 설치나 별도 서버는 필요 없습니다.

두 함수를 구현한 뒤 검사합니다. 검사기가 C 소스를 자동으로 컴파일합니다.
TODO가 남아 있다면 실패하는 것이 정상입니다.

```console
cd /workspace/labs/lab03/part02
python3 tests/check.py
```

성공 시 출력:

```text
Part02: PDF SHA-256, glibc recovery, secure round-trip, RNG failures, bounded attack: OK
LAB03{part02_local_checks_passed}
```

검사를 통과했다면 제출할 PDF를 따로 저장하고 해시를 확인하세요.

```console
mkdir -p output
python3 starter/recover.py --output output/recovered.pdf
sha256sum output/recovered.pdf
```

제공 데이터에서는 `Recovered 710 PDF bytes`가 출력됩니다.
호스트의 `labs/lab03/part02/output/recovered.pdf`를 열어 내용을 확인하세요.
`output/`은 저장소 안에 있어 컨테이너를 종료해도 남습니다. 복구 PDF나 키 파일을 `data/`에 넣지 마세요.

`LAB03{part02_local_checks_passed}`는 비밀값이 아니므로 보고서에 공개해도 됩니다.

<details>
<summary>다른 구현 파일이나 데이터 검사하기</summary>

```console
python3 tests/check.py --recovery /path/recover.py --secure /path/secure_random.c
```

`--data-dir`로 같은 포맷의 다른 데이터를 지정할 수 있습니다.
`openssl/evp.h`나 라이브러리를 찾지 못하면 `course` 컨테이너에서 실행 중인지 확인하세요.

</details>

## 5. 성공 조건

- **PDF 복구:** 전체 PDF의 SHA-256과 페이지·xref 구조가 검사 기준과 일치합니다.
- **난수 생성:** 지정된 두 OpenSSL API로 키·IV를 만들고, 정상 암복호화가 성공합니다.
- **오류 처리:** 어느 API든 0 또는 음수를 반환하면 암호화를 시작하지 않습니다.
- **공격 재시도:** 기존 7,200개 시각 후보로 새 키·IV를 복구할 수 없습니다.

이 범위에서 공격이 실패했다는 사실만으로 모든 공격에 대한 안전성이 증명되는 것은 아닙니다.

## 6. 제출 항목

완성한 `recover.py`, `secure_random.c`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part02를 작성해 제출하세요.
복구한 PDF도 지정된 비공개 수업 채널로 제출하고, 아래 Checkpoint Questions 전체 답변을 포함하세요.

## 7. Checkpoint Questions

1. 128비트 AES 키를 사용해도 이 생성 방식의 탐색 공간이 작은 이유는 무엇인가요?
2. 키 다음에 생성된 공개 IV가 후보 seed를 판별하는 데 왜 도움이 되나요?
3. glibc 대신 다른 C 라이브러리를 쓰면 어떤 문제가 생길 수 있나요?
4. 키와 IV의 역할 및 사용하는 난수 API를 구분해서 설명하세요.
5. 난수 생성 실패 시 재시도·대체값 사용 없이 중단해야 하는 이유는 무엇인가요?
6. CBC만으로 메시지 무결성을 보장할 수 있나요? 이번 복구 공격의 원인과 구분하세요.
