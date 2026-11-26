# Part02: CA 컨테이너에 인증서 발급 요청하기

**한국어** | [English](../../../en/labs/lab04/part02/README.md)

[Part01](../part01/README.md)에서 보호한 개인키를 열어 인증서 서명 요청(CSR)을
만듭니다. 실습용 `lab04-ca` 컨테이너에 CSR을 보내고 발급된 인증서가 자신의
공개키와 이름을 담는지 확인합니다. CA 준비와 종료는 [Lab04 안내](../README.md)를 따릅니다.

## 학습 목표

- CSR에 공개키와 요청할 DNS 이름을 넣고 자신의 개인키로 서명합니다.
- CA가 CSR을 확인한 후 서버 인증서를 발급하는 흐름을 관찰합니다.
- 개인키는 클라이언트에 남기고 CSR과 공개 인증서만 전송·수령합니다.

## 제공 자료와 과제

- [enroll.py](enroll.py): 개인키 열기, CSR 전송, 응답 확인, 파일 저장을 보여주는 실습 코드. **`make_csr()`의 TODO를 직접 구현해야 합니다.**
- [check.py](check.py): 발급된 인증서와 CSR의 공개키·용도·체인을 확인하는 선택적 검사.

`make_csr(private_key, hostname)`은 PEM 형식 CSR을 반환해야 합니다. 요청할
서버 이름은 `lab04.local.test`이고, DNS `subjectAltName`에 넣어야 합니다.
CSR은 SHA-256으로 서명합니다. CA는 이 이름의 서버 인증서를 발급하며
`CA:TRUE` 요청은 거부합니다. `POST /issue` 요청과 응답 처리는 제공 코드가
담당합니다. 응답에는 서버·중간 CA·Root CA의 공개 인증서가 포함됩니다.

## 1. Part01의 개인키와 실행 환경 준비하기

먼저 Part01을 완료하세요. [Lab04 공통 준비](../README.md)를 마쳤고 서비스를
중지하지 않았다면 CA는 이미 실행 중입니다. **기존 course 터미널의 `/workspace`**에서
진행하세요. 코드가 CA에 요청을 보내므로 CA에 따로 접속할 필요는 없습니다.

Part01에서 만든 `part01/output/private_encrypted.pem`과 그 비밀번호를 사용합니다.
개인키를 새로 만들거나 CA로 복사할 필요는 없습니다.

## 2. 코드로 CSR을 만들고 인증서 발급받기

`enroll.py`의 `make_csr()` TODO를 완성한 뒤 실행합니다.
첫 명령이 성공해 인증서 파일을 저장한 다음 두 번째 명령으로 검사하세요.

```console
python3 labs/lab04/part02/enroll.py
python3 labs/lab04/part02/check.py
```

첫 명령은 Part01 개인키의 비밀번호를 묻습니다. TODO를 구현하면 CA의
`/issue`에 CSR을 보내고 `part02/output/`에 `request.csr`, `server.pem`,
`intermediate.pem`, `root.pem`을 저장합니다. 이어서 공개키·DNS 이름을
확인하고 `LAB04{...}` 완료 표식을 출력합니다. TODO가 남아 있으면
`NotImplementedError`가 발생합니다.

CA 컨테이너를 재시작하면 CA 키와 인증서가 새로 만들어집니다. 재시작 뒤에는
이 명령으로 새 CSR과 인증서를 다시 발급받으세요. `part02/output/` 파일은
[Part03](../part03/README.md)에서 사용합니다.

### TODO 완료 후 확인할 결과

- `enroll.py`는 발급된 서버 인증서의 공개키가 CSR·개인키의 공개키와 같고,
  요청한 DNS 이름이 인증서에 있음을 확인한 뒤 저장 경로와 완료 표식을 출력합니다.

  ```text
  Certificate files: /workspace/labs/lab04/part02/output
  Issued name: lab04.local.test; CSR and certificate public key match: OK
  LAB04{...}
  ```

  `part02/output/`에 `request.csr`, `server.pem`, `intermediate.pem`,
  `root.pem` 네 파일이 생성됩니다. 개인키 파일은 이 디렉토리에 복사되지 않습니다.

- `check.py`는 CSR 서명, 공개키 일치, 서버 용도, Root까지의 체인을 다시
  확인한 뒤 다음 문구를 출력합니다.

  ```text
  Part02: CSR, public key, extensions, and trusted chain: OK
  ```

## Checkpoint Questions

1. CSR에는 어떤 정보가 들어가고, 어떤 정보는 CA가 발급 시 결정하나요?
2. CA가 반환한 인증서의 공개키가 CSR의 공개키와 같아야 하는 이유는 무엇인가요?
3. CSR만 전송할 때 CA가 신청자의 개인키를 받을 필요가 없는 이유는 무엇인가요?
