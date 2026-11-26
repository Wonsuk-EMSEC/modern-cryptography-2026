# Part07: 암호화된 개인키에 대한 사전 공격

**한국어** | [English](../../../en/labs/lab04/part07/README.md)

## 학습 목표와 배경

Part01에서는 OpenSSL로 만든 암호화된 PKCS#8 개인키를 **알고 있는 비밀번호로**
열었습니다.
이 Part에서는 공격자가 **파일 사본을 확보했고 비밀번호가 작은 사전에 포함된**
합성 상황을 실험합니다. 파일 안의 PBES2 설정은 PBKDF2-HMAC-SHA256으로 AES
암호화 키를 유도합니다. 후보를 시도하는 작업은 모두 로컬 Docker 안에서
이루어집니다. [OpenSSL PKCS#8 설명](https://docs.openssl.org/3.0/man1/openssl-pkcs8/)

## 제공 자료와 과제

| 파일 | 역할 |
|---|---|
| [attack.py](attack.py) | 직접 실행할 실습 코드. `find_password()`가 TODO입니다. |
| [data/encrypted_key.der](data/encrypted_key.der) | 암호화된 PKCS#8 개인키 |
| [data/certificate.crt](data/certificate.crt) | 해당 키의 공개 인증서 |
| [data/wordlist.txt](data/wordlist.txt) | 제한된 합성 비밀번호 후보 |
| [data/flag.enc](data/flag.enc) | 해당 공개키로 RSA-OAEP 암호화한 Flag |
| [test_part07_materials.py](test_part07_materials.py) | 자료 구조만 확인하는 공개 검사 |

이 Part를 완료하려면 `attack.py`의 미완성 `find_password()`를 직접 구현해야 합니다.

`find_password(encrypted_key, candidates)`에서 빈 줄을 건너뛰고 후보를 순서대로
시험하세요. 성공하면 UTF-8 비밀번호 **바이트**와 성공 시도를 포함한 시도 횟수를
반환하고, 끝까지 실패하면 `ValueError`를 발생시킵니다. 이미 제공된 `main()`은
복구한 개인키의 공개 부분이 인증서와 일치하는지 확인한 뒤 `flag.enc`를
복호화합니다. 비밀번호나 개인키 자체는 출력하지 마세요. 개인키 형식과 복호화는
설치된 `cryptography`의 `load_der_private_key()`를 사용합니다.

## 실행과 완료

**course 컨테이너**의 `/workspace`에서 실행합니다.

```console
python3 labs/lab04/part07/test_part07_materials.py
python3 labs/lab04/part07/attack.py
```

첫 명령은 자료 검사이며 미완성 TODO와 관계없이 통과합니다. 두 번째 명령은 TODO를
구현한 뒤 비밀번호 시도 횟수·경과 시간·초당 시도 횟수와 Flag를 출력합니다.
비밀번호 후보를 코드에 고정하지 마세요. 반복 횟수를 높이면 후보 하나를 시험하는
시간이 어떻게 달라질지 Part01에서 확인한 PBKDF2 매개변수와 연결해 설명하세요.

## TODO 완료 후 확인할 결과

`attack.py`가 끝까지 실행되면 출력 형식은 다음과 같습니다. 숫자와 Flag는 실습
자료 및 실행 환경에 따라 달라지므로 아래 표시는 형식 예시입니다.

```text
Attempts: <성공한 후보까지 시험한 횟수>
Elapsed seconds: <측정한 시간>
Attempts per second: <측정한 속도>
LAB04{...}
```

`Attempts`에는 성공한 후보도 포함됩니다. 마지막 줄에 Flag가 나오면 복구한
개인키의 공개 부분이 제공 인증서와 일치했고, 그 키로 `flag.enc`를 열었다는
뜻입니다. 실행 시간이 너무 짧아 속도를 계산할 수 없는 경우에는 속도 줄 대신
`Elapsed too short to measure`가 나올 수 있습니다. 공개 검사는 자료 파일의
형식만 확인해 `OK`를 표시하며, 비밀번호 찾기 TODO의 정답 여부는 검사하지 않습니다.

제출물은 수정한 `attack.py`, 실행 결과의 Flag와 시도 횟수·시간, 다음 질문의
답변입니다. 비밀번호나 복호화된 개인키 파일은 제출하지 않습니다.

## Checkpoint Questions

1. 파일 사본을 가진 공격자가 로그인 시도 제한 없이 후보를 시험할 수 있는 이유는 무엇인가요?
2. salt가 있어도 특정 파일에 대한 사전 공격은 왜 가능한가요?
3. 반복 횟수와 비밀번호의 예측 가능성은 각각 공격 비용에 어떤 영향을 주나요?
