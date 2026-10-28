# Part07: RSA-PSS 서명과 안전한 검증

**한국어** | [English](../../../en/labs/lab03/part07/README.md)

## 1. Learning Objectives — 학습 목표

OpenSSL EVP API로 RSA-PSS 서명과 검증을 구현하고, 유효하지 않은 서명을
허용하는 fail-open 제어 흐름을 수정합니다. 정상 입력과 오류 입력을 모두 검사합니다.

## 2. Challenge Scenario — 실습 시나리오

소프트웨어 업데이트 도구가 서명 검증 실패 후에도 패키지를 처리합니다. 신뢰할
공개키는 사전에 설치되며 패키지가 교체하지 못합니다. 취약한 로컬 프로그램의
잘못된 결과 처리를 확인하고 정상적으로 서명된 업데이트만 처리하도록 수정하세요.
실습의 업데이트 처리는 `ACCEPT` 출력으로 모사하며 패키지 코드를 실행하지 않습니다.
인증서나 CA 검증은 다루지 않습니다.

## 3. Provided Materials — 제공 자료

| 파일 | 용도 |
| --- | --- |
| `data/trusted_public.pem` | 사전에 신뢰한 RSA-2048 공개키 |
| `data/update.bin`, `data/update.sig` | 정상 업데이트와 RSA-PSS 서명 |
| `starter/pss.h`, `starter/pss.c` | 함수 인터페이스와 서명·검증 TODO |
| `starter/update_vulnerable.c` | 의도적으로 취약한 업데이트 정책 |
| `starter/update.c` | 수정할 업데이트 정책 TODO |
| `tests/driver.c`, `tests/check.py` | 크기가 제한된 파일 입출력과 독립 검사 |

개인키는 제공하지 않습니다. 공개 검사는 매번 별도의 새 키 두 쌍과 새 메시지를
생성합니다. 서명 파라미터는 **RSA-2048, SHA-256, MGF1-SHA-256, salt 32바이트**로
고정합니다.

## 4. Tasks — 수행 과제

1. `sign_message()`를 EVP DigestSign API로 구현하세요. 크기 조회 후 서명 버퍼를
   할당하고, 실패 시 버퍼 소유권을 명확히 정리하세요. 성공은 1, 실패는 0입니다.
2. `verify_message()`를 EVP DigestVerify API로 구현하세요. PSS 패딩, MGF1 해시,
   salt 길이를 명시하세요. 반환값은 유효 1, 무효 0, API·입력 오류 -1입니다.
3. 메시지 수정, 서명 수정, 잘못된 공개키로 검증해 보세요. 오류와 무효를 모두
   거부해야 합니다. 다른 패딩·MGF1 해시·salt 길이도 허용하지 마세요.
4. `update_vulnerable.c`에서 결과 0이 어떤 흐름으로 처리되는지 확인하세요.
   `update.c`를 작성하여 **검증 결과가 정확히 1일 때만** 업데이트를 처리하세요.
5. 검증 API의 오류를 주입한 검사와 정상 입력 검사를 함께 통과하세요. 모든 입력을
   거부하거나 모든 입력을 허용하는 정책은 성공할 수 없습니다.

## 5. How to Run — 실행 방법

[Lab03 실행 안내](../README.md)를 따라 저장소 루트의 호스트에서 시작합니다.

```console
docker compose -f docker/compose.yml run --rm course
```

Docker 시작 출력은 설치 상태에 따라 달라집니다. 컨테이너 안에서 공개 입력을
독립적으로 확인하세요.

```console
cd /workspace/labs/lab03/part07
openssl dgst -sha256 -verify data/trusted_public.pem -signature data/update.sig -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256 data/update.bin
```

확인한 출력:

```text
Verified OK
```

TODO를 완성한 뒤 빌드하고 실행하세요. GCC는 성공 시 출력하지 않습니다.

```console
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter starter/pss.c starter/update.c tests/driver.c -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss
/tmp/lab03-pss update data/trusted_public.pem data/update.bin data/update.sig
python3 tests/check.py
```

참조 구현으로 확인한 업데이트 출력은 `ACCEPT`입니다. 이어지는 검사 출력:

```text
Part07: fresh RSA-PSS signing, trusted verification, tampering, wrong key, malformed input, EVP error: OK
LAB03{part07_local_checks_passed}
```

미완성 starter는 의도적으로 실패합니다. 다른 소스는
`python3 tests/check.py --pss /path/pss.c --update /path/update.c`로 검사합니다.
취약 버전은 위 빌드에서 `starter/update.c`를 `starter/update_vulnerable.c`로 바꾸어
비교하세요. 수정 메시지를 원래 서명으로 검증하면 취약 버전은 `ACCEPT`, 수정
버전은 `REJECT`를 출력해야 합니다. OpenSSL 헤더가 없으면 수업 컨테이너인지
확인하세요. 학생의 별도 패키지 설치는 필요하지 않습니다.

## 6. Success Conditions — 성공 조건

새 메시지의 서명이 독립 OpenSSL 검증을 통과하고, 정상 업데이트가 처리되어야
합니다. 메시지·서명 변조, 다른 공개키, 짧거나 빈 서명, 잘못된 키 파일, 다른
서명 파라미터, `EVP_DigestVerifyFinal()`의 음수 오류를 모두 거부해야 합니다.
공개 영수증은 비밀 플래그가 아닙니다. 최종 평가는 격리된 환경에서 제출 소스와
새 인스턴스를 사용하며 정상·비정상 동작을 모두 확인한 뒤 교수자 결과를 발급합니다.

## 7. Submission Requirements — 제출물

`pss.c`, `update.c`, 취약점의 원인과 수정 설명, 정상·변조·오류 검사 로그,
로컬 영수증과 분석 답변을 제출하세요. 개인키는 제출 코드나 학생 배포 자료에
넣지 마세요. 고정 서명이나 성공 문자열을 출력하는 코드는 통과하지 못합니다.

## 8. Analysis Questions — 분석 질문

1. 검증의 반환값 1, 0, 음수는 각각 무엇을 뜻하나요?
2. 원래 제어 흐름은 무효 서명을 왜 허용하나요?
3. 서명자와 검증자가 PSS·MGF1·salt 설정을 명시적으로 맞추는 이유는 무엇인가요?
4. 모든 입력을 거부하는 수정이 올바른 해결책이 아닌 이유는 무엇인가요?
5. 패키지가 자신의 검증 공개키를 지정할 수 있다면 어떤 신뢰 문제가 생기나요?
6. Part08의 raw RSA 정수 서명과 이 Part의 RSA-PSS를 구분해서 설명하세요.
