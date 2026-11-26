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

## 1. Part02에서 발급받은 인증서 준비하기

먼저 Part02를 완료하세요. `part02/output/`의 `root.pem`, `intermediate.pem`,
`server.pem`을 사용합니다. 이 Part는 새 인증서 파일을 만들지 않고 기존 파일을
읽어 검증하므로 CA에 요청하거나 따로 접속할 필요는 없습니다.
**기존 course 터미널의 `/workspace`**에서 진행하세요.

## 2. 코드로 인증서 체인과 이름 검증하기

`verify_chain.py`의 `verify_certificate()` TODO를 완성한 뒤 실행합니다.

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

### TODO 완료 후 확인할 결과

- `verify_chain.py`는 세 사례의 검증 결과를 **다음 순서대로** 출력하고,
  마지막에 완료 표식을 표시합니다. 두 `REJECT`는 의도된 검증 결과입니다.

  ```text
  trusted chain and correct name: ACCEPT
  trusted chain, wrong name: REJECT
  missing intermediate: REJECT
  LAB04{...}
  ```

  다른 결과가 나오면 프로그램이 오류로 중단됩니다.

- `check.py`는 같은 세 조건을 재검사하며, 모두 맞으면 다음 문구를 출력합니다.

  ```text
  Part03: chain and hostname decisions: OK
  ```

## Checkpoint Questions

1. 인증서의 서명이 맞는데도 접속을 거부해야 하는 경우는 언제인가요?
2. Root CA와 중간 CA는 검증에서 각각 어떤 역할을 하나요?
3. 접속할 DNS 이름을 지정하지 않고 체인만 검사하면 어떤 판단이 빠지나요?
