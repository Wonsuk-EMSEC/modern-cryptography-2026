# Part08: CRL로 폐기된 서버 인증서 거부하기

**한국어** | [English](../../../en/labs/lab04/part08/README.md)

[Part02](../part02/README.md)에서 만든 인증서 서명 요청(CSR)으로 새 서버 인증서를 발급받습니다. 인증서를 폐기한 뒤에도 서명과 유효기간은 그대로일 수 있습니다. 이 Part에서는 인증서 폐기 목록(CRL)을 직접 받아 검증에 적용했을 때만 결과가 달라지는지 확인합니다.

## 학습 목표

- 인증서 체인 검증과 폐기 상태 확인이 별개의 단계임을 설명합니다.
- 중간 CA가 서명한 CRL을 사용하여 폐기된 서버 인증서를 거부합니다.
- 같은 CSR로 재발급받은 새 인증서가 다른 일련번호를 가지며 현재 CRL로 검증되는지 확인합니다.

## 선행 준비와 제공 자료

[Lab04 공통 Docker 환경](../README.md)의 `course`와 `lab04-ca`를 시작하고 **Part02를 먼저 완료**하세요. `labs/lab04/part02/output/request.csr`이 필요합니다. CA를 재시작하면 CA 키와 폐기 기록이 초기화됩니다. CSR 파일은 재사용할 수 있지만 이전 실행의 인증서·CRL과 새 CA의 자료를 섞지 말고 이 Part를 처음부터 다시 실행하세요.

| 경로 | 내용 |
|---|---|
| [revoke.py](revoke.py) | 실행 가능한 실습 코드와 `verify_with_crl()` TODO |
| [data/](data/) | 정적 비밀 자료 없음. 인증서와 CRL은 실행 중 실습용 CA에서 받음. |
| [check.py](check.py) | 구현 결과를 확인하는 공개 검사 |

**이 Part를 완료하려면 `revoke.py`의 `verify_with_crl()` TODO를 직접 구현해야 합니다.** 제공된 `main()`은 Part02의 CSR을 이용해 매번 새 인증서를 발급받고, 폐기 전후의 검증을 순서대로 실행합니다. 이전 실행에서 폐기한 인증서가 다음 실행의 출발점이 되지 않도록 새 인증서를 발급합니다.

## 수행 과제

`verify_with_crl(root, intermediate, leaf, crl, hostname)`은 OpenSSL 인증서 검증 결과인 `subprocess.CompletedProcess`를 반환해야 합니다. Root CA 인증서는 신뢰 기준, 중간 CA 인증서는 체인 구성 재료로 사용하고, TLS 서버 용도와 `hostname`도 검사하세요. `crl`이 없으면 폐기 상태 검사를 하지 않고, 있으면 해당 CRL을 검증에 적용합니다. `-CRLfile`은 받아 온 CRL 파일을 제공하고, `-crl_check`는 최종 서버 인증서의 폐기 상태 검사를 요청합니다. **CRL 파일을 제공하기만 해서는 폐기 상태 검사가 활성화되지 않습니다.** 이 실습의 CRL은 서버 인증서의 발급자인 중간 CA가 서명합니다. [OpenSSL `verify` 문서](https://docs.openssl.org/3.0/man1/openssl-verify/)

프로그램의 실행 흐름에서 다음 네 결과를 관찰하세요.

| 순서 | 검증 대상과 조건 | 예상 결과 |
|---|---|---|
| 1 | 새 인증서, 폐기 전 CRL 적용 | `before revocation with CRL: ACCEPT` |
| 2 | 그 인증서 폐기 후, CRL 없이 검증 | `after revocation without CRL: ACCEPT` |
| 3 | 폐기 후 갱신된 CRL 적용 | `after revocation with CRL: REJECT` |
| 4 | 같은 CSR로 새로 발급한 인증서, 갱신된 CRL 적용 | `new certificate with CRL: ACCEPT` |

실습용 CA에 인증서 폐기를 요청하는 API는 `POST /revoke`(요청 본문에 `certificate_pem`), 현재 CRL을 PEM으로 받는 API는 `GET /crl`입니다. 제공된 `main()`이 이 요청들을 처리합니다. CRL은 Docker 내부에서 `GET /crl`로 **명시적으로 받아** 사용하며 자동 다운로드는 하지 않습니다. 표의 2번 결과는 폐기되지 않았다는 증거가 아니라 폐기 정보를 검증에 적용하지 않았다는 뜻입니다.

이 실습은 일련번호별 폐기 효과를 비교하려고 같은 CSR을 재사용합니다. **개인키 유출 때문에 인증서를 폐기했다면 실제 서비스에서는 새 개인키와 CSR을 만들어야 합니다.**

## 실행과 완료

다음 명령은 **course 컨테이너의 `/workspace`**에서 실행합니다. 개인 PC의 브라우저나 운영체제 신뢰 목록을 바꿀 필요는 없습니다.

```console
cd /workspace
python3 labs/lab04/part08/revoke.py
python3 labs/lab04/part08/check.py
```

TODO가 남아 있으면 `NotImplementedError`가 발생합니다. 공개 검사는
`revoke.py`가 필요한 파일을 만든 다음 실행하세요.

## TODO 완료 후 확인할 결과

`revoke.py`가 성공하면 위 표의 `ACCEPT`, `ACCEPT`, `REJECT`, `ACCEPT` 결과가
순서대로 출력되고 마지막 줄에 `LAB04{...}` 완료 표식이 나옵니다. 세 번째
`REJECT`는 갱신된 CRL에 의해 폐기된 인증서가 거부된 경우여야 합니다.

`part08/output/`에는 `root.pem`, `intermediate.pem`, `old.pem`, `new.pem`,
`before.crl`, `after.crl`이 생깁니다. `old.pem`과 `new.pem`은 같은 CSR의 공개키를
담지만 일련번호가 달라야 합니다. 두 일련번호는 다음처럼 직접 비교할 수 있습니다.

```console
openssl x509 -in labs/lab04/part08/output/old.pem -noout -serial
openssl x509 -in labs/lab04/part08/output/new.pem -noout -serial
```

`check.py`까지 통과하면 `Part08: CRL, serial numbers, and hostname decisions: OK`가
표시됩니다. 이 검사는 CRL 서명과 폐기된 일련번호, 재발급 인증서, 잘못된 호스트
이름의 거부도 확인합니다. 완료 표식은 실습 실행 흐름에 대한 피드백입니다.
실제 서비스의 폐기 상태를 증명하지는 않습니다.

갱신된 CRL의 발급자와 폐기된 일련번호를 직접 살펴보려면 다음을 실행하세요.

```console
openssl crl -in labs/lab04/part08/output/after.crl -noout -issuer -text
```

## 확인 질문

1. 폐기된 인증서의 서명과 유효기간이 정상이어도 왜 사용을 거부해야 하나요?
2. `-CRLfile`과 `-crl_check`는 각각 어떤 역할을 하나요?
3. 폐기 후 CRL 없이 검증하면 계속 수락되는 이유는 무엇인가요?
4. 같은 CSR로 재발급한 인증서가 갱신된 CRL로 검증되는 이유는 무엇인가요?
5. CRL 대신 OCSP로 폐기 상태를 확인한다면 정보의 최신성과 조회 방식에서 무엇이 달라질까요?
