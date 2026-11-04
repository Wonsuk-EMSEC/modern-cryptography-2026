# Part07: RSA-PSS 서명과 안전한 검증

**한국어** | [English](../../../en/labs/lab03/part07/README.md)

소프트웨어 업데이트 도구가 서명이 올바르지 않은 패키지까지 받아들이고 있습니다.
서명을 만들고 검증하는 기능을 구현한 뒤, **검증에 성공한 업데이트만 허용**하도록 수정하세요.
업데이트 처리는 `ACCEPT` 출력으로만 모사하며 실제 패키지 코드를 실행하지 않습니다.

## 1. 학습 목표

1. **서명 생성:** OpenSSL EVP API로 RSA-PSS 서명을 만듭니다.
2. **서명 검증:** 정상 서명·무효 서명·API 오류를 구분합니다.
3. **업데이트 정책:** 검증 실패 후에도 처리를 계속하는 fail-open 동작을 수정합니다.

Part06을 먼저 수행할 필요는 없으며, 별도 서버 없이 진행합니다.

## 2. 제공 자료

- [starter/pss.c](starter/pss.c), [starter/pss.h](starter/pss.h): 서명·검증 함수의 TODO와 인터페이스
- [starter/update.c](starter/update.c): 수정할 업데이트 허용 함수
- [starter/update_vulnerable.c](starter/update_vulnerable.c): 분석할 취약한 업데이트 허용 함수
- [data/trusted_public.pem](data/trusted_public.pem): 사전에 신뢰한 RSA-2048 공개키
- [data/update.bin](data/update.bin), [data/update.sig](data/update.sig): 정상 업데이트와 서명
- [tests/check.py](tests/check.py), [tests/driver.c](tests/driver.c): 컴파일·서명·검증·오류 처리 검사

**수정할 파일은 `starter/pss.c`와 `starter/update.c`입니다.**
개인키는 제공하지 않으며, 검사기가 매번 새 키 두 쌍과 메시지를 만들어 서명 기능도 검사합니다.
공개키는 업데이트 패키지가 바꿀 수 없는 신뢰 기준입니다. 인증서·CA 검증은 이 실습에서 다루지 않습니다.

## 3. 수행 과제

### 1단계: 서명 생성과 검증 구현하기

> **서명 설정**
>
> RSA-2048 · RSA-PSS · SHA-256 · MGF1-SHA-256 · salt 32바이트
>
> 서명과 검증 양쪽에서 같은 설정을 명시하세요.

- **`sign_message()`: RSA-PSS 서명 생성**

    `starter/pss.c`에서 EVP DigestSign API로 구현하세요.
    필요한 서명 크기를 먼저 조회한 뒤 버퍼를 할당하고 서명합니다.
    성공하면 서명 버퍼와 길이를 출력 인자로 전달하고 1을 반환하세요.
    호출자가 `OPENSSL_free()`로 해제할 수 있는 버퍼를 사용합니다.
    API·할당 실패 시 자원을 정리하고 0을 반환하세요.

- **`verify_message()`: 서명 검증**

    같은 파일에서 EVP DigestVerify API로 구현하세요. PSS 패딩, SHA-256,
    MGF1 해시와 salt 길이를 명시하고 아래 반환값을 구분하세요.
    다른 패딩·MGF1 해시·salt 길이를 사용한 서명도 거부해야 합니다.

    | 반환값 | 의미 |
    | --- | --- |
    | `1` | 유효한 서명 |
    | `0` | 무효 서명 |
    | `-1` | API 또는 입력 오류 |

### 2단계: 검증 성공 시에만 업데이트 허용하기

먼저 `starter/update_vulnerable.c`를 읽고, 검증 결과가 0일 때 어떤 경로로 진행하는지 확인하세요.

- **`process_update()`: 업데이트 허용 여부 결정**

    `starter/update.c`에서 `verify_message()`를 호출하세요.
    **결과가 정확히 1일 때만 1을 반환**하고, 무효 서명이나 오류이면 0을 반환합니다.
    실행용 driver는 이 결과를 각각 `ACCEPT`, `REJECT`로 출력합니다.
    모든 입력을 거부하는 구현도 정답이 아닙니다. 정상 서명은 허용해야 합니다.

- **정상·변조·오류 비교하기**

    정상 업데이트는 허용하고, 메시지·서명 변조나 다른 공개키는 거부하는지 확인하세요.
    검사기는 `EVP_DigestVerifyFinal()`이 음수 오류를 반환하는 상황도 만들어 검사합니다.

## 4. 실행 방법

[Lab03 환경 설정](../README.md#setup)을 마친 뒤 **course 컨테이너 터미널**에서 실행하세요.
추가 설치나 별도 서버는 필요 없습니다.

먼저 제공된 서명이 정상인지 OpenSSL로 확인합니다. TODO 구현 전에도 실행할 수 있습니다.

```console
cd /workspace/labs/lab03/part07
openssl dgst -sha256 -verify data/trusted_public.pem -signature data/update.sig \
  -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 \
  -sigopt rsa_mgf1_md:sha256 data/update.bin
```

예상 출력은 `Verified OK`입니다. 세 함수를 구현한 뒤 같은 디렉터리에서 검사하세요.
검사기가 C 소스를 자동으로 컴파일합니다. TODO가 남아 있다면 실패하는 것이 정상입니다.

```console
python3 tests/check.py
```

성공 시 출력:

```text
Part07: fresh RSA-PSS signing, trusted verification, tampering, wrong key, malformed input, EVP error: OK
LAB03{part07_local_checks_passed}
```

`LAB03{part07_local_checks_passed}`는 비밀값이 아니므로 보고서에 공개해도 됩니다.

<details>
<summary>취약 버전과 수정 버전 직접 비교하기</summary>

`pss.c`와 `update.c` 구현 후, 같은 컨테이너 터미널과 디렉터리에서 실행하세요.
원본 메시지는 유지하고 변조한 복사본을 `/tmp`에 만듭니다.

```console
cp data/update.bin /tmp/lab03-update-modified.bin
printf '\nmodified\n' >> /tmp/lab03-update-modified.bin
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter \
  starter/pss.c starter/update_vulnerable.c tests/driver.c \
  -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss-vulnerable
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter \
  starter/pss.c starter/update.c tests/driver.c \
  -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss-fixed
/tmp/lab03-pss-vulnerable update data/trusted_public.pem /tmp/lab03-update-modified.bin data/update.sig
/tmp/lab03-pss-fixed update data/trusted_public.pem /tmp/lab03-update-modified.bin data/update.sig
/tmp/lab03-pss-fixed update data/trusted_public.pem data/update.bin data/update.sig
```

예상 출력은 순서대로 `ACCEPT`, `REJECT`, `ACCEPT`입니다.

</details>

<details>
<summary>다른 구현 파일 검사하기</summary>

```console
python3 tests/check.py --pss /path/pss.c --update /path/update.c
```

OpenSSL 헤더를 찾지 못하면 `course` 컨테이너에서 실행 중인지 확인하세요.

</details>

## 5. 성공 조건

- **서명:** 새 메시지의 서명이 독립 OpenSSL 검증을 통과합니다.
- **정상 입력:** 정상 서명이 있는 업데이트는 `ACCEPT`입니다.
- **비정상 입력:** 메시지·서명 변조, 다른 공개키, 짧거나 빈 서명, 잘못된 키 파일, 다른 서명 설정은 거부합니다.
- **API 오류:** `EVP_DigestVerifyFinal()`의 음수 오류도 `REJECT`로 처리합니다.

## 6. 제출 항목

완성한 `pss.c`, `update.c`와 [보고서 양식](../REPORT_TEMPLATE.md)의 Part07을 작성해 제출하세요.
취약점의 원인과 수정 설명, 정상·변조·오류 검사 로그, 로컬 완료 표식과
아래 Checkpoint Questions 전체 답변을 포함하세요. 개인키는 제출하지 마세요.

## 7. Checkpoint Questions

1. 검증의 반환값 1, 0, 음수는 각각 무엇을 뜻하나요?
2. 원래 제어 흐름은 무효 서명을 왜 허용하나요?
3. 서명자와 검증자가 PSS·MGF1·salt 설정을 명시적으로 맞추는 이유는 무엇인가요?
4. 모든 입력을 거부하는 수정이 올바른 해결책이 아닌 이유는 무엇인가요?
5. 패키지가 자신의 검증 공개키를 지정할 수 있다면 어떤 신뢰 문제가 생기나요?
6. Part08의 raw RSA 정수 서명과 이 Part의 RSA-PSS를 구분해서 설명하세요.
