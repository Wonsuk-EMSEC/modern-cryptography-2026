# Part01: OpenSSL 키 쌍 생성과 암호화된 개인키 열기

**한국어** | [English](../../../en/labs/lab04/part01/README.md)

OpenSSL로 RSA 키 쌍을 생성하고 개인키를 비밀번호로 암호화합니다. 생성된 공개키는
개인키에서 유도됩니다. 직접 작성한 Python 코드로 암호화된 개인키를 열어 공개키가
일치하는지 확인합니다. 이 개인키는 [Part02](../part02/README.md)의 인증서 발급
요청에도 사용합니다. 실행 환경은 [Lab04 안내](../README.md)를 따릅니다.

## 학습 목표

- OpenSSL로 RSA 키 쌍을 만들고 암호화된 PKCS#8 개인키와 공개키를 저장합니다.
- 알고 있는 비밀번호로 개인키를 열고, 공개키 일치 여부를 코드로 확인합니다.
- 공개키와 암호화된 개인키의 ASN.1 구조에서 알고리즘 OID(Object Identifier,
  객체 식별자)와 PBKDF2 반복 횟수를 찾습니다.

## 제공 자료와 과제

- [decrypt_key.py](decrypt_key.py): 입력부터 결과 출력까지 이어지는 실습
  코드. **`decrypt_key()`의 TODO를 직접 구현해야 합니다.**
- [check.py](check.py): 복호화 함수의 선택적 공개 검사.

`decrypt_key(encrypted_pem, password)`는 암호화된 PEM 바이트와 알고 있는
비밀번호 바이트를 받아 RSA 개인키 객체를 반환해야 합니다. 설치된
`cryptography`의 `serialization.load_pem_private_key()`를 사용하세요. 이미
제공된 `main()`은 복호화된 키에서 공개키를 유도해 `public.pem`과 비교하고,
일치하면 `LAB04{...}` 완료 표식을 출력합니다. 평문 개인키나 비밀번호를
출력하거나 저장소에 올리지 마세요. 비밀번호가 틀리면 `ValueError`가 발생하도록
복호화 함수의 오류를 그대로 전달하세요.

## 1. OpenSSL로 키 쌍 만들기

아래 명령은 모두 **course 컨테이너의 `/workspace`**에서 실행합니다.

```console
mkdir -p labs/lab04/part01/output
umask 077
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -quiet | \
  openssl pkcs8 -topk8 -v2 aes-256-cbc -v2prf hmacWithSHA256 -iter 200000 \
  -out labs/lab04/part01/output/private_encrypted.pem
openssl pkey -in labs/lab04/part01/output/private_encrypted.pem -pubout \
  -out labs/lab04/part01/output/public.pem
```

첫 줄의 파이프는 OpenSSL이 무작위로 생성한 RSA 개인키를 곧바로 PKCS#8 암호화
명령에 전달합니다. 따라서 평문 개인키 파일은 만들지 않습니다. `pkcs8`이
비밀번호를 두 번 물으면 직접 정해 입력하고, `pkey`가 물을 때 같은 비밀번호를
입력하세요. `private_encrypted.pem`은 PBES2/PBKDF2-HMAC-SHA256과 AES-256-CBC로
보호됩니다. `public.pem`은 공개키 파일입니다. `umask 077`은 새 파일의 접근
권한을 현재 사용자로 제한합니다. 비밀번호는 Part02에서도 필요합니다.

## 2. OID와 암호화 매개변수 확인하기

OID는 알고리즘을 식별하는 점으로 구분된 숫자입니다. 다음 명령으로 공개키와
암호화된 PKCS#8 파일을 살펴보세요. `asn1parse`에는 OID의 이름이,
`list -objects`에는 이름과 숫자 OID의 대응이 표시됩니다.

```console
openssl asn1parse -in labs/lab04/part01/output/public.pem -i | sed -n '1,5p'
openssl asn1parse -in labs/lab04/part01/output/private_encrypted.pem -i | sed -n '1,15p'
openssl list -objects | grep -E '^(rsaEncryption|PBES2|PBKDF2|hmacWithSHA256|AES-256-CBC)'
```

첫 명령의 `OBJECT`는 공개키의 RSA 알고리즘을 나타냅니다. 두 번째 명령에서
PBES2, PBKDF2, PRF, AES 암호의 `OBJECT`를 찾고, 마지막 명령에서 각각의
숫자 OID를 확인하세요. `INTEGER` 항목은 PBKDF2
반복 횟수를 **16진수**로 표시합니다. `OCTET STRING` 중 하나는 salt이고 다른
하나는 AES용 IV입니다. 이 값들의 역할을 구분해 기록하세요.

## 3. 코드로 개인키 열기

`decrypt_key.py`의 TODO를 완성한 뒤 실행합니다.

```console
python3 labs/lab04/part01/decrypt_key.py
python3 labs/lab04/part01/check.py
```

첫 명령이 비밀번호를 묻습니다. 구현 전에는 `NotImplementedError`가 발생합니다.
구현 후에는 개인키와 공개키가 일치하는지 확인하고 완료 표식을 보여 줍니다.
비밀번호가 틀리면 개인키를 열 수 없습니다. 두 번째 명령은 선택적 검사입니다.
`private_encrypted.pem`을 보관해 Part02에서 사용하세요.

## 확인 질문

1. `genpkey`가 만드는 RSA 키 쌍에서 공개키와 개인키는 어떤 관계인가요?
2. RSA 공개키의 OID와 PBES2, PBKDF2, PRF, AES의 OID는 각각 무엇을 지정하나요?
3. salt와 반복 횟수는 비밀번호로 보호한 파일을 여는 과정에 어떤 영향을 주나요?
