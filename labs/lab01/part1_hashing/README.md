**한국어** | [English](../../../en/labs/lab01/part1_hashing/README.md)

# Part 1: 해시와 솔트

가상의 수업용 비밀번호만 사용합니다. 아래 명령은 모두 수업용 Docker 컨테이너 내부에서
실행합니다. 단순 SHA-256과 `SHA256(salt || password)`는 동작 원리를 보여주기 위한 것입니다.
실서비스의 비밀번호 저장에는 Part 3에서 소개하는 비밀번호 KDF가 필요합니다.

## 학습 목표와 제공 파일

문자열을 UTF-8로 인코딩하고, 해싱과 암호화를 구별하며, 해시값의 결정성을 이해하고,
공개 솔트의 역할과 한계를 설명합니다. 해싱에는 복호화 키가 없습니다. 솔트는 계정 간
공통 사전 계산의 재사용을 막지만, 약한 비밀번호를 강하게 만들거나 각 추측을 느리게 만들지는 않습니다.

| 파일 | 역할 |
| --- | --- |
| `samples/hash_bytes_demo.py` | 완성된 공개 메시지 해싱 예제 |
| `samples/salt_bytes_demo.py` | 완성된 공개 솔트, 16진수, 바이트 연결 예제 |
| `hash_password.py` | 비어 있는 학생 실습 파일 |
| `salted_hash.py` | 비어 있는 학생 실습 파일 |
| `test_hashing.py` | 기본 검사와 선택적으로 활성화하는 구현 검사 |
| `data/` | 본 과제와 별개인 선택 실습용 MD5 충돌 데이터 |
| `samples/flag_unlock_demo.py` | 공개 도우미 사용 예제. Part 정답은 포함하지 않음 |
| `data/flag_challenge.json` | 실험 결과로 여는 암호화된 완료 플래그 |

실습 파일에는 import 문, 함수, 실행 코드가 없습니다. 모두 직접 작성하세요.
실행 코드는 `main()` 안에 두고 `if __name__ == "__main__":` 조건 아래에서만 호출하여,
함수를 가져오는 것만으로 입력을 요구하지 않도록 합니다.

## 1. 예제 실행 및 분석

```console
cd /workspace/labs/lab01/part1_hashing
python3 samples/hash_bytes_demo.py
python3 samples/salt_bytes_demo.py
pytest -q test_hashing.py
```

첫 번째 예제는 `Input bytes: b'Public sample'`, 입력 길이 13, `Digest bytes: 32`,
`Hex characters: 64`, SHA-256 해시값, `Repeat matches: True`를 출력합니다.
16진수 해시값은 실행할 때마다 동일합니다. 선택 인자 `--input`을 살펴보고 완성된 프로그램이
바이트를 읽는 방법을 확인하세요.

두 번째 예제는 `Salt bytes: 16`, 32자리 무작위 솔트의 16진수 표현, 64자리 검증값과 함께
솔트 디코딩, 같은 솔트를 사용했을 때의 재현성, 솔트 변경의 효과를 확인하는 세 개의 `True`를
출력합니다. 생성되는 솔트와 검증값은 보통 실행할 때마다 달라집니다. 생성 파일은 남지 않습니다.
`bytes.fromhex(salt.hex())`는 원래의 공개 솔트를 복원합니다.

구현 전에는 pytest가 기본 검사 하나의 통과와 구현 검사 두 개의 건너뜀을 보고합니다.
건너뛴 검사는 아직 작성해야 할 실습이 있다는 의미입니다.

### 공개 플래그 유틸리티 예제

```console
python3 samples/flag_unlock_demo.py
```

예상 출력:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

이 예제는 파일을 남기지 않습니다. 공통 유틸리티를 가져오는 방법, 인증 실패를 처리하는 방법,
성공한 반환값을 출력하는 방법을 살펴보세요. 최종 프로그램은 이 공개 데모 증명값 대신
자신의 실험 결과를 사용합니다.

## 2. hash_password() 작성 및 검사

`hash_password.py`에 대화형 코드를 추가하기 전에 다음 인터페이스를 구현합니다.

| 함수 | 입력 | 반환값 |
| --- | --- | --- |
| `hash_password(password: str) -> str` | 가상 비밀번호 문자열 | 소문자 64자리 SHA-256 16진수 문자열 |

문자열을 UTF-8로 인코딩하고 결과 바이트를 해싱합니다. 입력 문자열의 공백을 제거하거나
정규화하는 등 어떤 변경도 하지 마세요. 필요한 import 문을 추가합니다.

이 함수만 사용하는 다음 공개 데이터 검사를 바로 실행합니다.

```console
python3 - <<'PY'
import hashlib
from hash_password import hash_password
for text in ("fictional", "한글-example", ""):
    result = hash_password(text)
    assert result == hashlib.sha256(text.encode("utf-8")).hexdigest()
assert hash_password("fictional") != hash_password("different")
print("Unsalted function check: OK")
PY
```

`Unsalted function check: OK`를 확인한 뒤에만 다음으로 진행합니다. 같은 입력의 해시값은
같아야 하고, 입력이 달라지면 해시값도 달라져야 합니다.

## 3. salted_hash() 작성 및 검사

`salted_hash.py`에 다음을 구현합니다.

| 함수 | 입력 | 반환값 |
| --- | --- | --- |
| `salted_hash(password: str, salt: bytes) -> str` | 비밀번호 문자열과 전달받은 솔트 바이트 | `salt || UTF8(password)`의 소문자 SHA-256 16진수 문자열 |

이 함수는 호출자가 전달한 솔트를 사용하며, 새 솔트로 바꾸면 안 됩니다.
새 솔트 생성은 등록 과정 또는 대화형 프로그램에서 수행합니다.

```console
python3 - <<'PY'
import hashlib
from salted_hash import salted_hash
first, second = b"a" * 16, b"b" * 16
value = salted_hash("fictional", first)
assert value == hashlib.sha256(first + b"fictional").hexdigest()
assert value == salted_hash("fictional", first)
assert value != salted_hash("fictional", second)
assert salted_hash("한글", first) == hashlib.sha256(first + "한글".encode("utf-8")).hexdigest()
print("Salted function check: OK")
PY
```

`Salted function check: OK`를 확인한 뒤에만 다음으로 진행합니다. 서버는 로그인할 때
같은 계산을 반복할 수 있도록 솔트와 검증값을 모두 저장합니다.

## 4. 대화형 프로그램 추가

각 파일에 `main()`과 실행 조건을 작성합니다. 가상 비밀번호가 화면에 표시되거나 셸 인자로
전달되지 않도록 `getpass.getpass()`를 사용합니다.

- `hash_password.py`: 비밀번호 하나를 읽고 해시값을 출력합니다.
- `salted_hash.py`: 비밀번호 하나를 읽고 `secrets.token_bytes()`로 16바이트 무작위 솔트를
  생성한 뒤 `salt=<hex>`와 `digest=<hex>`를 출력합니다.
- 두 프로그램 모두 빠른 SHA-256이 교육용 구성임을 밝혀야 합니다.

두 파일을 가져와도 입력 요청이나 출력이 발생하지 않는지 검사합니다.

```console
python3 -c "import hash_password, salted_hash; print('Import check: OK')"
```

### 공통 완료 유틸리티

메인 프로그램 전체는 여전히 직접 작성해야 합니다. 암호화 봉투의 경로는 셸의 현재 디렉토리가
아닌 실습 파일을 기준으로 지정하세요. 번호별 Part의 실습 파일에서 제공된 공통 유틸리티를
가져오려면 다음 코드를 사용합니다.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)`는 암호화 봉투를 인증한 뒤 `FLAG{...}` 문자열을 반환합니다.
잘못된 증명값은 `ValueError`를 발생시킵니다. 봉투를 변경하지 말고 구현과 증명값 형식을
점검하세요. 공개 데모 증명값은 데모 파일만 열 수 있으며 이 Part의 플래그는 열 수 없습니다.
계산한 Part 플래그는 교수가 지정한 경로로 제출합니다.

### 공개 해시 챌린지 완료

최종 `salted_hash.py` 프로그램은 무작위 솔트 시연 이후 Part 1의 완료 플래그를 열어야 합니다.
이 챌린지는 공개되어 있으며 직접 작성한 두 해싱 함수가 모두 필요합니다. 앞에서 입력한 가상
비밀번호 및 생성한 무작위 솔트와는 별개의 과제입니다.

`json.loads()`로 `data/flag_challenge.json`을 읽습니다. `challenge` 객체에는 `input`과
`salt_hex`가 있습니다. 직접 작성한 `hash_password()`로 솔트 없는 SHA-256 16진수 문자열을
계산하고, 고정 공개 솔트를 디코딩한 뒤 `salted_hash()`로 솔트를 적용한 16진수 문자열을
계산합니다. 증명값 형식은 다음과 같습니다.

```text
<unsalted lowercase hex>:<salted lowercase hex>
```

콜론은 정확히 하나만 사용하고 공백은 넣지 않습니다. 미리 계산한 해시값을 프로그램에
붙여 넣지 마세요. `unlock_flag(flag_path, proof)`를 호출하고 반환된 `FLAG{...}`를 마지막
줄에 출력합니다. 고정 챌린지 솔트로 무작위 솔트 시연을 대체하지 말고 두 관찰 결과를 모두 남깁니다.

## 5. 전체 실습 실행

```console
python3 hash_password.py
python3 hash_password.py
python3 salted_hash.py
python3 salted_hash.py
LAB01_GRADE=1 pytest -q test_hashing.py
```

네 번의 실행에 모두 같은 가상 비밀번호를 입력합니다. 솔트 없는 출력은 같아야 하며,
무작위 솔트와 솔트를 적용한 해시값은 달라져야 합니다. 이후 다른 입력으로 반복하세요.
해시값은 16진수 64자리이고, 솔트는 16진수 32자리입니다.

활성화한 테스트 결과는 `3 passed`여야 합니다. 최종 `salted_hash.py` 출력에는 공개 해시
챌린지를 연 뒤 독립된 `FLAG{...}` 줄이 포함됩니다. 이 대화형 프로그램들은 파일을 생성하지 않습니다.

## 6. 완료 확인 및 보고서

- [ ] 처음에 비어 있던 두 파일에 함수, import 문, 메인 프로그램을 작성했습니다.
- [ ] 작은 함수 검사 두 개와 활성화한 모든 테스트를 통과했습니다.
- [ ] 같은 입력에서 솔트 없는 해시값이 반복됩니다.
- [ ] 무작위 솔트를 사용하면 솔트가 적용된 검증값이 달라집니다.
- [ ] 모듈을 가져올 때 대화형 작업이 실행되지 않습니다.
- [ ] 최종 프로그램이 자신의 `data/flag_challenge.json`을 인증하고 Part 플래그를 출력합니다.

Python 파일 두 개, 가상 입력으로 실행한 명령과 관찰한 해시값/솔트, 테스트 결과, 짧은 설명을
제출합니다. 해싱과 암호화의 차이, 솔트를 저장해야 하는 이유, 솔트가 공개되는 이유,
솔트와 빠른 SHA-256의 조합이 여전히 실서비스 비밀번호 저장에 부적절한 이유를 설명하세요.
