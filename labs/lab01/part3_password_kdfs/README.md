**한국어** | [English](../../../en/labs/lab01/part3_password_kdfs/README.md)

# Part 3: 오프라인 비밀번호 크래킹과 비밀번호 KDF

**예상 소요 시간:** 40분. 모든 작업은 수업용 Docker 컨테이너 내부에서 실행합니다.
가상의 수업용 데이터베이스와 로컬 계정만 사용합니다. 이 실험은 오프라인입니다.
추측은 로컬에서 계산되며 로그인 서비스에 전달되지 않습니다.

## 학습 목표와 파일

솔트가 없는 SHA-256 추측과 솔트가 있는 SHA-256 추측의 비용을 비교하고, 입력 조건이 허용할
때만 계산을 재사용하며, 추측 비용을 전용 비밀번호 KDF와 연결합니다.
CSV/16진수 처리, 연산 횟수 집계, 시간 측정, KDF 매개변수, 평문 비밀번호 없이 로컬에
검증값을 저장하는 방법을 배웁니다.

| 파일 | 역할 |
| --- | --- |
| `samples/csv_hash_demo.py` | 완성된 공개 CSV/16진수/해시 단일 후보 예제 |
| `samples/benchmark_kdfs.py` | 다섯 가지 방식의 완성된 벤치마크 |
| `samples/register_login_demo.py` | 완성된 로컬 PBKDF2 등록/로그인 예제 |
| `crack_unsalted.py`, `crack_salted.py` | 비어 있는 학생 실습 파일 |
| `compare_cost.py` | 두 함수가 동작한 뒤 실행하는 제공 비교 도구 |
| `data/unsalted_hashes.csv` | 가상의 `account,sha256` 레코드 |
| `data/salted_hashes.csv` | 가상의 `account,salt_hex,sha256` 레코드 |
| `data/lab01-small.txt` | 고정된 수업용 단어 목록 |
| `test_dictionary_cost.py` | 제공 데이터 검사와 선택적으로 활성화하는 구현 검사 |
| `samples/flag_unlock_demo.py` | 공개 도우미 사용 예제. Part 정답은 포함하지 않음 |
| `data/flag_challenge.json` | 실험 결과로 여는 암호화된 완료 플래그 |

두 실습 파일에 import 문, 함수, CLI, 실행 조건을 작성합니다. 모듈을 가져올 때 대화형 작업이나
실행 코드가 동작하지 않도록 합니다. 수업용 계정 이름, 비밀번호, 대상 해시값 또는 측정 횟수를
하드코딩하지 마세요.

## 1. CSV 예제 실행 및 분석

```console
cd /workspace/labs/lab01/part3_password_kdfs
python3 samples/csv_hash_demo.py
python3 -m unittest test_dictionary_cost.py -v
```

예제는 임시 공개 레코드를 생성하고 `csv.DictReader`로 읽은 뒤, 솔트를 디코딩하고
공개 후보 하나를 검사한 다음 임시 파일을 제거합니다.

```text
CSV fields: account, salt_hex, sha256
Account: example
Salt bytes: 11
Single candidate matches: True
Hash computations: 1
Elapsed: <seconds> seconds
```

시간을 제외한 모든 값은 고정됩니다. `Path`, CSV 필드 접근, UTF-8 인코딩,
`bytes.fromhex()`, 시간 측정의 시작·종료 범위를 살펴보세요. 이 예제는 후보 하나에 대한
API 사용법을 보여줍니다. 제한된 사전 탐색은 직접 구현해야 합니다.
기본 테스트 모음에서는 제공 데이터 검사 하나가 통과하고 구현 검사 두 개가 건너뛰어집니다.

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

## 2. 솔트 없는 crack() 작성 및 검사

`crack_unsalted.py`에 다음을 구현합니다.

```text
crack(target_csv: Path, wordlist: Path) -> tuple[dict[str, str], int, float]
```

`(recovered_accounts, hash_computations, elapsed_seconds)`를 반환합니다.
첫 번째 값은 계정 이름을 일치하는 후보에 대응시키는 매핑입니다.

`account,sha256` CSV 행과 UTF-8 단어 목록을 읽습니다. 각 줄의 앞뒤 공백을 제거하고
빈 줄은 건너뜁니다. 후보마다 `SHA256(UTF8(candidate))`를 **한 번만** 계산한 뒤,
해시값을 모든 계정의 대상 값과 비교합니다. 대상 해시값이 같은 계정들을 포함해 일치하는
모든 계정을 복구하세요. 모든 계정이 이미 일치했더라도 전체 단어 목록을 처리하여,
솔트 없는 경우의 계산 횟수가 비어 있지 않은 후보 줄 수와 정확히 같도록 합니다.
대상 16진수 문자열의 대소문자는 일관되게 처리합니다. 후보 계산 구간을
`time.perf_counter()`로 측정하세요.

공개 단어 세 개를 사용하는 다음 검사를 바로 실행합니다.

```console
python3 - <<'PY'
import hashlib
import tempfile
from pathlib import Path
from crack_unsalted import crack
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    words, targets = base / "words.txt", base / "targets.csv"
    words.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    targets.write_text("account,sha256\n"
        + "example_a," + hashlib.sha256(b"beta").hexdigest() + "\n"
        + "example_b," + hashlib.sha256(b"gamma").hexdigest() + "\n", encoding="utf-8")
    found, count, elapsed = crack(targets, words)
    assert found == {"example_a": "beta", "example_b": "gamma"}
    assert count == 3 and elapsed > 0
print("Unsalted search check: OK")
PY
```

`Unsalted search check: OK`를 확인한 뒤 다음으로 진행합니다. 계정별 입력으로 해시값이
달라지지 않기 때문에 후보 해시 세 개로 두 계정을 모두 검사할 수 있습니다.

## 3. 솔트를 적용한 crack() 작성 및 검사

`crack_salted.py`에 같은 함수 시그니처와 튜플 형식을 구현합니다.
`account,salt_hex,sha256`을 읽고 각 계정의 공개 솔트를 디코딩합니다.
계정마다 단어 목록 순서대로 후보를 시도하며 `SHA256(salt || UTF8(candidate))`를 계산합니다.
해당 계정에서 처음 일치하면 탐색을 중단하고 다음 계정으로 진행합니다.
성공한 비교를 포함해 모든 해시 계산 횟수를 셉니다. 일치하는 후보가 없는 계정은
복구 결과 매핑에 포함하지 않습니다.

```console
python3 - <<'PY'
import hashlib
import tempfile
from pathlib import Path
from crack_salted import crack
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    words, targets = base / "words.txt", base / "targets.csv"
    words.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    salts = [b"fixture-salt-01", b"fixture-salt-02"]
    rows = ["account,salt_hex,sha256"]
    for account, salt, word in zip(["example_a", "example_b"], salts, [b"beta", b"gamma"]):
        rows.append(f"{account},{salt.hex()},{hashlib.sha256(salt + word).hexdigest()}")
    targets.write_text("\n".join(rows) + "\n", encoding="utf-8")
    found, count, elapsed = crack(targets, words)
    assert found == {"example_a": "beta", "example_b": "gamma"}
    assert count == 5 and elapsed > 0
print("Salted search check: OK")
PY
```

`Salted search check: OK`를 확인한 뒤 다음으로 진행합니다. 첫 계정에는 후보 두 개,
두 번째 계정에는 세 개가 필요하므로 계산 횟수는 5입니다.
이 검사는 솔트를 적용한 구현만 가져옵니다.

## 4. 두 메인 프로그램 작성

`argparse`, `main()`, 실행 조건을 추가합니다. 각 프로그램은 로컬 위치 인자 두 개를 받습니다.
먼저 해당 대상 CSV를, 다음으로 단어 목록을 받으세요. 자신의 `crack()`을 호출하고
복구한 계정 **수**, 해시 계산 횟수, 경과 시간(초), 초당 해시 계산 수를 출력합니다.
복구한 수업용 후보는 출력하지 말고 함수가 반환하는 매핑 안에만 유지합니다.

```console
python3 -c "import crack_unsalted, crack_salted; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_dictionary_cost.py -v
```

가져오기 검사에서는 공격이 실행되면 안 됩니다. 활성화한 테스트 세 개를 모두 통과해야 합니다.

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

### 두 결과를 완료 플래그에 연결

`crack_salted.py`의 메인 함수를 확장하여 자신의 지표를 출력한 뒤, 완성한
`crack_unsalted.py`에서 `crack()` 함수를 가져옵니다. 선택한 솔트 CSV와 같은 디렉토리의
`unsalted_hashes.csv`에 대해 같은 단어 목록으로 실행합니다.
각 스크립트의 `crack()` 반환 규약은 변경하지 않습니다.

복구한 두 계정 매핑이 동일하고, 두 입력 CSV에 있는 모든 계정 이름이 복구되었는지 확인합니다.
일부만 복구했거나 결과가 다르면 실험이 미완성입니다. 조건을 모두 만족하면
`canonical_account_proof(recovered)`를 호출하고 그 결과를 `data/flag_challenge.json`의
증명값으로 사용합니다. 반환된 `FLAG{...}`를 `crack_salted.py`의 마지막 줄에 출력합니다.

정규 인코딩은 계정 키를 사전순으로 정렬하고, 불필요한 공백 없이 유니코드를 텍스트로 유지한
JSON입니다: `json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
공개 매핑 `{"b": "public-two", "a": "public-one"}`의 정확한 증명값은
`{"a":"public-one","b":"public-two"}`입니다. 공통 인코더를 사용하고, 실제 복구한 매핑이나
그 증명값을 절대 출력하지 마세요.

`compare_cost.py`는 제공된 지표 비교 도구로 유지합니다.
플래그를 열었더라도 두 탐색 구현과 측정값 비교를 모두 수행해야 합니다.

## 5. KDF 예제 실행 및 시간 해석

비밀번호 KDF는 매 검증과 추측의 비용을 의도적으로 높입니다. 솔트는 고유성을 제공하고,
작업 계수는 CPU 또는 메모리 비용을 부과합니다. 둘 다 약한 비밀번호의 엔트로피를 늘리지는 않습니다.

```console
python3 samples/benchmark_kdfs.py --trials 3
python3 samples/benchmark_kdfs.py --trials 5
```

각 실행은 다섯 가지 방식 모두의 실행 시간 중앙값을 밀리초로 출력합니다.

| 출력 행 | 설정 | 관찰할 내용 |
| --- | --- | --- |
| `SHA-256 (unsafe)` | 작업 계수 없음 | 빠른 기준선 |
| `PBKDF2-100k` | HMAC-SHA-256, 100,000회 반복 | 반복 계산 |
| `bcrypt-cost-10` | 로그형 비용 계수 10 | CPU 비용 |
| `scrypt-N=2^14` | `n=2**14, r=8, p=1` | 메모리/CPU 비용 |
| `Argon2id-32MiB` | 시간 비용 2, 32,768 KiB, 병렬도 1 | 메모리 비용 |

스크립트는 측정 전에 각 연산을 미리 실행합니다. 정확한 시간과 순서는 호스트마다 다를 수
있습니다. 매개변수, 중앙값, 시행 횟수, 하드웨어 환경을 기록하세요.
비밀번호 저장에서 빠른 결과가 바람직한 목표는 아닙니다.
이 벤치마크의 고정 솔트는 실험 재현을 위한 것이며 등록에 사용하기 위한 것이 아닙니다.

## 6. 등록 예제 실행 및 레코드 확인

가상 비밀번호를 정하고 대화형으로 입력합니다.

```console
python3 samples/register_login_demo.py register student01
python3 samples/register_login_demo.py verify student01
python3 samples/register_login_demo.py verify student01
python3 -m json.tool auth_db.json
```

첫 명령은 `registered`를 출력합니다. 올바른 입력은 `verified`를, 다른 입력은
`authentication failed`를 출력합니다. JSON 레코드에서 알고리즘 `pbkdf2-sha256`,
반복 횟수 200,000, 16진수로 인코딩된 16바이트 무작위 솔트, 검증값을 확인하세요.
평문 비밀번호가 있어서는 안 됩니다. 생성되는 `auth_db.json`은 Git에서 무시됩니다.

별도로 실험하려면 두 명령 모두에 `--db /tmp/lab01-auth.json`을 전달합니다.
비밀번호를 셸 인자에 넣지 마세요. 실서비스 KDF 매개변수는 배포할 하드웨어에서 조정해야 합니다.
여기서는 수업용 설정을 사용합니다.

## 7. 수업 데이터 실행 및 비용 비교

```console
python3 crack_unsalted.py data/unsalted_hashes.csv data/lab01-small.txt
python3 crack_salted.py data/salted_hashes.csv data/lab01-small.txt
python3 compare_cost.py data
```

두 프로그램은 계산한 지표를 보고해야 합니다. `crack_salted.py`는 통합 결과를 검사한 뒤
Part 플래그도 출력합니다. 제공된 비교 도구의 출력은 다음과 같습니다.

```text
experiment   found   hashes    seconds     hashes/s
unsalted         <N>     <N>   <seconds>    <rate>
salted           <N>     <N>   <seconds>    <rate>
```

두 방식 모두 제공된 가상 레코드를 복구해야 합니다. 횟수와 시간을 기록하고 복구한 비밀번호는
공개하지 마세요. 솔트가 없으면 단어마다 해시를 한 번 계산합니다. 솔트가 있으면 계정별
조기 중단을 적용하며 최대 `accounts × words`번 계산합니다. 실행 시간은 호스트에 따라 달라지고
입력이 작으면 측정 잡음이 크므로 경과 시간과 함께 연산 횟수도 논의하세요.
이 비교에는 출력 파일이 필요하지 않습니다.

## 8. 완료 확인 및 보고서

- [ ] 비어 있던 두 실습 파일에 완전한 CLI 프로그램을 작성했습니다.
- [ ] 공개 탐색 검사 두 개와 활성화한 모든 테스트를 통과했습니다.
- [ ] 두 수업 데이터 탐색과 비교가 성공했습니다.
- [ ] 다섯 가지 KDF의 중앙값과 설정을 기록했습니다.
- [ ] 올바른 비밀번호와 잘못된 비밀번호의 로컬 로그인 결과를 관찰했습니다.
- [ ] 저장된 JSON에 평문 비밀번호가 없습니다.
- [ ] 최종 프로그램이 자신의 `data/flag_challenge.json`을 인증하고 Part 플래그를 출력합니다.

실습 파일 두 개, 지표 출력, 테스트 결과, 분석을 제출합니다. 솔트 없는 후보 계산을 재사용할
수 있는 이유, 서로 다른 솔트에 별도 계산이 필요한 이유, 중단 규칙이 계산 횟수에 미치는 영향,
솔트와 함께 KDF도 필요한 이유, 메모리를 사용하는 방식, 서버의 속도 제한이 Part 2에는 영향을
주지만 이러한 오프라인 추측은 관찰할 수 없는 이유를 설명하세요. 공개 보고서에 복구한 후보나
로컬 인증 비밀번호를 제출하지 마세요.
