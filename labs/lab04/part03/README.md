# Part03: 인증서 체인과 서버 이름 검증하기

**한국어** | [English](../../../en/labs/lab04/part03/README.md)

[Part02](../part02/README.md)에서 받은 서버 인증서를 어떤 조건에서 신뢰할 수
있는지 확인합니다. 신뢰하는 Root CA, 중간 CA, 접속하려는 서버 이름은 각각
다른 역할을 합니다. 실행 환경은 [Lab04 안내](../README.md)를 따릅니다.

## 학습 목표

- Root CA를 신뢰 기준으로 사용하고 중간 CA를 체인 구성 재료로 사용합니다.
- 체인 검증과 서버 이름 검증을 함께 수행합니다.
- 같은 인증서에서 중간 CA 또는 접속 이름만 바꿔 실패 원인을 구분합니다.

## 제공 자료와 과제

- [verify_chain.py](verify_chain.py): 세 가지 검증 사례와 출력 흐름이 보이는 실습 코드. **`verify_certificate()`의 TODO를 직접 구현해야 합니다.**
- [check.py](check.py): 수락·거부 결과를 다시 확인하는 선택적 검사.
- Part02에서 생성한 `part02/output/root.pem`, `intermediate.pem`, `server.pem`.

`verify_certificate(root, intermediate, leaf, hostname)`에서 `openssl verify`를
실행하고 `subprocess.CompletedProcess`를 반환하세요. `root.pem`만 신뢰할
인증서로 사용하고, 전달된 경우에만 `intermediate.pem`을 체인 구성에
사용하세요. TLS 서버 용도와 `hostname`의 일치 여부도 검사해야 합니다.
시스템에 설치된 다른 CA가 결과에 영향을 주지 않도록 신뢰 저장소를 지정하세요.
OpenSSL 옵션은 `openssl verify -help`로 확인할 수 있습니다.

## 실행과 예상 동작

먼저 Part02의 발급 결과를 준비하세요. **course 컨테이너의 `/workspace`**에서
실행합니다.

```console
python3 labs/lab04/part03/verify_chain.py
python3 labs/lab04/part03/check.py
```

완성된 프로그램은 다음 세 사례의 결과를 보여주고 `LAB04{...}` 완료 표식을
출력합니다. TODO가 남아 있다면 `NotImplementedError`가 발생합니다.

| 사례 | 예상 결과 | 관찰할 원인 |
|---|---|---|
| 신뢰 체인과 올바른 이름 | ACCEPT | Root까지 연결되고 SAN 이름이 일치함 |
| 정상 체인과 다른 이름 | REJECT | SAN 이름이 일치하지 않음 |
| 중간 CA 누락 | REJECT | Root까지 연결할 체인 재료가 부족함 |

서버 인증서는 같은 파일을 사용하고 조건 하나씩만 바꿉니다. 중간 CA를 신뢰
기준에 직접 추가하지 마세요. `part02/output/`은 CA 재시작 후 새로 발급받아야 합니다.

## 확인 질문

1. 인증서의 서명이 맞는데도 접속을 거부해야 하는 경우는 언제인가요?
2. Root CA와 중간 CA는 검증에서 각각 어떤 역할을 하나요?
3. 접속할 DNS 이름을 지정하지 않고 체인만 검사하면 어떤 판단이 빠지나요?
