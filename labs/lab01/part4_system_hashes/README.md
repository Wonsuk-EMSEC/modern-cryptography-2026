# Part 4: 시스템 비밀번호 레코드와 테이블 공격

[한국어](README.md) | [English](../../../en/labs/lab01/part4_system_hashes/README.md)

모든 Python 프로그램은 수업용 Docker 컨테이너 안에서 실행하세요. 이 Part의 `data/`에 있는
합성 파일만 읽고, 호스트의 `/etc/shadow`는 읽지 마세요.
고정된 SHA-256 예제 비밀번호 공간은 교육용 모델이며 실제 시스템의 비밀번호 설정이 아닙니다.

## 학습 목표와 파일

저장된 검증값(verifier)을 파싱하고, 파싱과 비밀번호 추측의 차이를 구분합니다.
전체 사전 계산 테이블과 레인보우 테이블의 끝점(endpoint)을 구성하고, 체인을 재생해 일치를 검증합니다.
저장 공간, 구성 비용, 조회 비용, 커버리지를 비교하고, 공개된 고유 솔트가 있으면 하나의 무솔트 테이블을
여러 계정에 재사용할 수 없는 이유를 설명합니다.

| 파일 | 역할 |
| --- | --- |
| `samples/analyze_shadow_hash.py` | 완성된 합성 shadow 레코드 파서 |
| `samples/table_io_demo.py` | 테이블 구성 요소를 보여 주는 완성된 공개 예제 |
| `table_common.py` | 제한된 설정, 해시, 열거, JSON 처리를 위한 제공 도우미 |
| `build_precomputation_table.py` | 전체 테이블 구성을 위한 빈 실습 파일 |
| `build_rainbow_table.py` | 레인보우 테이블 구성을 위한 빈 실습 파일 |
| `compare_table_attacks.py` | 데이터베이스 조회·비교를 위한 빈 실습 파일 |
| `data/rainbow_lab_config.json` | 필수 테이블 구성 매개변수 |
| `data/rainbow_password_database.csv` | 두 방법에 공통으로 사용하는 대상 데이터베이스 |
| `test_table_attacks.py` | 도우미 검사와 선택적으로 활성화하는 구현 검사 |
| `samples/flag_unlock_demo.py` | 공개 도우미 사용 예제. 이 Part의 정답은 포함하지 않음 |
| `data/flag_challenge.json` | 실험 결과로 여는 암호화된 완료 플래그 |

모든 import, 함수, 명령행 인자 처리, 측정, 실행 가드를 직접 작성하세요.
각 단계에서 프로그램을 실행하지 않고도 모듈을 import할 수 있어야 합니다.
나중 단계의 함수는 해당 함수를 구현한 뒤에 호출하도록 추가하세요.

수업 설정은 SHA-256, 문자 집합 `abc123`, 길이 4(`6**4 = 1296`개의 비밀번호),
체인 길이 12, 서로 다른 시작점 96개, 시드 2026입니다.
필수 실험에서는 이 범위를 변경하지 마세요.

## 1. 예제 실행 및 살펴보기

```console
cd /workspace/labs/lab01/part4_system_hashes
python3 samples/analyze_shadow_hash.py data/linux_hashes.txt
python3 samples/table_io_demo.py
python3 -m unittest test_table_attacks.py -v
```

파서는 가상의 레코드마다 `account`, 알고리즘 `id`, 사람이 읽을 수 있는 `algorithm`,
`salt_or_parameters`, `verifier`가 포함된 딕셔너리를 출력합니다.
제공된 레코드에서 각 필드를 확인하세요. 파서는 비밀번호를 크래킹하거나 서비스에 접속하지 않습니다.

테이블 예제는 설정된 공간 크기 1296, 작은 공개 공간 `['aa', 'ab', 'ba', 'bb']`,
다이제스트 길이 64, 16진수 `0f`의 정숫값·몫·나머지 15, 2, 3을 출력합니다.
시드를 사용한 재현 가능한 선택 결과와 `Grouped values after JSON round trip: ['first', 'second']`도 출력합니다.
`Temporary JSON exists: True` 다음에 `Temporary JSON removed`가 나오면 파일 생성과 정리가 확인된 것입니다.

열거, 16진수의 정수 변환, `divmod`, 시드를 사용한 선택, `dict.setdefault`, JSON 도우미를 살펴보세요.
이 예제는 평가에 사용하는 공격 테이블을 구성하지 않습니다.
구현 전에는 도우미 테스트 2개가 통과하고 완료 테스트 5개는 건너뜁니다.

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

예제는 실행 후 파일을 남기지 않습니다. 공통 유틸리티를 import하는 방법, 인증 실패를 처리하는 방법,
성공했을 때 반환값을 출력하는 방법을 살펴보세요.
최종 프로그램에는 이 공개 데모의 증명값이 아니라 자신의 실험 결과를 사용합니다.

## 2. 전체 테이블의 build_table() 구현 및 작은 공간 검사

`build_precomputation_table.py`에 다음 함수를 구현하세요.

```text
build_table(config: dict[str, int | str]) -> dict[str, str]
```

`password_space(alphabet, password_length)`를 열거하고, 설정된 알고리즘으로 각 비밀번호를 한 번씩
해시한 뒤 소문자 `digest -> password` 항목을 반환하세요.
제공된 `hash_password()`는 빠른 예제용 해시이며 비밀번호용 KDF가 아닙니다.

```console
python3 - <<'PY'
from build_precomputation_table import build_table
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2}
entries = build_table(config)
assert len(entries) == 4
assert entries[hash_password("ab")] == "ab"
assert set(entries.values()) == {"aa", "ab", "ba", "bb"}
print("Full-table check: OK")
PY
```

`Full-table check: OK`를 확인한 뒤 진행하세요.

## 3. reduce_digest() 구현 및 매핑 검사

`build_rainbow_table.py`에 `MIX_CONSTANT = 0x9E3779B1`을 정의하고 다음 함수를 구현하세요.

```text
reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str
```

`(int(digest_hex, 16) + column * MIX_CONSTANT) % (len(alphabet)**length)`를 계산하세요.
이 정수를 정확히 `length`자리의 `len(alphabet)`진수로 표현하고, 가장 높은 자리부터
`alphabet[digit]`을 사용해 문자열로 변환하세요. 맨 앞의 0에 해당하는 자리도 포함해야 합니다.
이는 제한된 비밀번호 공간으로 보내는 열 의존적 매핑이며 SHA-256의 역함수가 아닙니다.

```console
python3 - <<'PY'
from build_rainbow_table import reduce_digest
assert reduce_digest("00", 0, "ab", 2) == "aa"
assert reduce_digest("01", 0, "ab", 2) == "ab"
assert reduce_digest("ff", 0, "ab", 2) == "bb"
assert reduce_digest("00", 1, "ab", 2) == "ab"
values = [reduce_digest("1234", i, "abc123", 4) for i in range(4)]
assert all(len(value) == 4 and set(value) <= set("abc123") for value in values)
assert len(set(values)) > 1
print("Reduction check: OK")
PY
```

`Reduction check: OK`를 확인한 뒤 진행하세요.

## 4. choose_starts() 구현·검사 후 chain_endpoint() 구현

먼저 `choose_starts(config) -> list[str]`를 구현하세요. 설정된 공간을 열거하고
`random.Random(seed).sample(candidates, chain_count)`를 사용해 서로 다른 시작점을 선택하세요.
전역 난수 상태를 변경하면 안 됩니다.

```console
python3 - <<'PY'
from build_rainbow_table import choose_starts
config = {"alphabet": "ab", "password_length": 2, "chain_count": 2, "seed": 2026}
starts = choose_starts(config)
assert starts == choose_starts(config)
assert len(starts) == len(set(starts)) == 2
assert set(starts) <= {"aa", "ab", "ba", "bb"}
print("Start-selection check: OK")
PY
```

위 검사가 통과하면 `chain_endpoint(start: str, config: dict[str, int | str]) -> str`을 구현하세요.
`start`에서 시작해 열 `0 .. chain_length-1`마다 현재 비밀번호를 해시하고 다이제스트를 축약하세요.
마지막으로 축약된 비밀번호만 반환합니다.

```console
python3 - <<'PY'
from build_rainbow_table import chain_endpoint, reduce_digest
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2, "chain_length": 1}
expected = reduce_digest(hash_password("ab"), 0, "ab", 2)
assert chain_endpoint("ab", config) == expected
config["chain_length"] = 2
expected = reduce_digest(hash_password(expected), 1, "ab", 2)
assert chain_endpoint("ab", config) == expected
print("Chain check: OK")
PY
```

두 메시지가 모두 `OK`로 끝나는지 확인한 뒤 진행하세요.

## 5. 레인보우 build_table() 구현 및 끝점 그룹화 검사

`build_rainbow_table.py`에 `build_table(config) -> dict[str, list[str]]`를 구현하세요.
선택한 각 시작점의 끝점을 계산하고, 해당 끝점의 리스트에 시작점을 추가하세요.
체인이 합쳐져도 모든 시작점을 유지해야 합니다. 이전 시작점을 덮어쓰거나 모든 중간 비밀번호를 저장하지 마세요.

```console
python3 - <<'PY'
from unittest.mock import patch
import build_rainbow_table as rainbow
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2,
          "chain_length": 2, "chain_count": 3, "seed": 2026}
starts = rainbow.choose_starts(config)
endpoints = rainbow.build_table(config)
assert sum(map(len, endpoints.values())) == 3
assert sorted(start for group in endpoints.values() for start in group) == sorted(starts)
with patch.object(rainbow, "chain_endpoint", return_value="aa"):
    merged = rainbow.build_table(config)
    assert merged == {"aa": starts}
print("Endpoint grouping check: OK")
PY
```

강제로 병합하는 경우는 공개 단위 테스트용 데이터입니다.
`Endpoint grouping check: OK`를 확인한 뒤 진행하세요.

## 6. lookup_precomputation() 구현 및 검사

`compare_table_attacks.py`에 다음 함수를 구현하세요.

```text
lookup_precomputation(digest: str, entries: dict[str, str]) -> tuple[str | None, int]
```

일치하는 비밀번호 또는 `None`과 새로 수행한 해시 계산 횟수를 반환하세요.
딕셔너리 조회에는 새로운 해시 계산이 필요하지 않습니다.

```console
python3 - <<'PY'
from compare_table_attacks import lookup_precomputation
from table_common import hash_password
digest = hash_password("ab")
assert lookup_precomputation(digest, {digest: "ab"}) == ("ab", 0)
assert lookup_precomputation(digest, {}) == (None, 0)
print("Full lookup check: OK")
PY
```

`Full lookup check: OK`를 확인한 뒤 진행하세요.

## 7. lookup_rainbow() 구현 및 체인 재생 검사

`compare_table_attacks.py`에 다음 함수를 구현하세요.

```text
lookup_rainbow(digest: str, endpoints: dict[str, list[str]],
              config: dict[str, int | str]) -> tuple[str | None, int]
```

마지막 열부터 0번째 열까지 대상 다이제스트가 놓일 수 있는 위치를 차례로 시도하세요.
선택한 열에서 대상 다이제스트를 축약한 다음, 남은 열에 대해 해시·축약을 진행해 후보 끝점을 구하세요.
그 끝점에 저장된 각 시작점에서 0번째 열부터 체인을 재생하세요.
비밀번호를 반환하기 전에 재생된 각 비밀번호의 해시를 **원래** 대상 다이제스트와 비교해야 합니다.
끝점 충돌만으로는 일치가 확인되지 않습니다.
검증을 포함해 끝점 예측과 체인 재생 중 수행한 모든 해시를 세세요.
검증되는 체인이 없으면 `(None, count)`를 반환하세요.

작은 레인보우 테이블의 커버리지는 불완전하므로 유효한 비밀번호 중 일부를 찾지 못하는 것이 정상입니다.
조회 함수는 검증되지 않은 값을 일치 결과로 반환하면 안 됩니다.

```console
python3 - <<'PY'
from build_rainbow_table import chain_endpoint, reduce_digest
from compare_table_attacks import lookup_rainbow
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2, "chain_length": 2}
start = "aa"
endpoints = {chain_endpoint(start, config): [start]}
for password in (start, reduce_digest(hash_password(start), 0, "ab", 2)):
    found, count = lookup_rainbow(hash_password(password), endpoints, config)
    assert found == password and count > 0
found, count = lookup_rainbow(hash_password("outside"), endpoints, config)
assert found is None and count >= 0
print("Rainbow replay check: OK")
PY
```

`Rainbow replay check: OK`를 확인한 뒤 진행하세요.

## 8. 데이터베이스 로딩 구현·검사 후 측정 추가

### load_database() 구현 및 스키마 검사

`compare_table_attacks.py`에 `load_database(path: Path) -> list[dict[str, str]]`를 구현하세요.
비어 있지 않은 CSV 레코드를 읽고, 열이 정확히 `account,sha256`인지 확인하세요.
유효하지 않거나 비어 있는 파일에는 `ValueError`를 발생시키세요.

```console
python3 - <<'PY'
import tempfile
from pathlib import Path
from compare_table_attacks import load_database
from table_common import hash_password
digest = hash_password("ab")
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "public.csv"
    path.write_text(f"account,sha256\nexample,{digest}\n", encoding="utf-8")
    assert load_database(path) == [{"account": "example", "sha256": digest}]
    path.write_text("wrong,schema\nexample,value\n", encoding="utf-8")
    try:
        load_database(path)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid schema was accepted")
print("Database loading check: OK")
PY
```

`Database loading check: OK`를 확인한 뒤 진행하세요.

### attack_database() 구현 및 측정값 검사

`attack_database(database, lookup) -> tuple[dict[str, str], int, float]`를 구현하세요.
소문자로 표현된 각 대상 다이제스트에 제공된 조회 함수를 호출하고, 조회 시 해시 횟수를 합산하세요.
검증된 일치 결과를 계정별로 모으고 수행 시간을 측정하세요.

```console
python3 - <<'PY'
from compare_table_attacks import attack_database
from table_common import hash_password
digest = hash_password("ab")
rows = [{"account": "example", "sha256": digest}]
found, count, elapsed = attack_database(rows, lambda value: ("ab", 0))
assert found == {"example": "ab"} and count == 0 and elapsed >= 0
found, count, elapsed = attack_database(rows, lambda value: (None, 3))
assert found == {} and count == 3 and elapsed >= 0
print("Database measurement check: OK")
PY
```

`Database measurement check: OK`를 확인한 뒤 진행하세요.

## 9. 세 프로그램의 메인 로직과 JSON 결과물 작성

`argparse`, `Path`, `perf_counter()`, `load_config()`, `write_json()`을 사용하세요.
생성 파일은 Git이 추적하지 않는 `generated/` 아래에 저장하세요.

| 프로그램 | 위치 인자 | 결과물의 필수 필드 |
| --- | --- | --- |
| `build_precomputation_table.py` | 설정 JSON, 출력 JSON | `type="full-precomputation"`, `config`, `build_hashes`, `build_seconds`, `entries` |
| `build_rainbow_table.py` | 설정 JSON, 출력 JSON | `type="rainbow-endpoints"`, `config`, `build_hashes`, `build_seconds`, `endpoints` |
| `compare_table_attacks.py` | 데이터베이스 CSV, 전체 테이블 JSON, 레인보우 JSON | 방법별 측정값을 한 행씩 출력. 결과 파일은 필요 없음 |

전체 테이블 구성의 해시 횟수는 비밀번호 공간 크기이며, 레인보우 테이블 구성의 해시 횟수는
`chain_count * chain_length`입니다. 테이블 구성 시간은 JSON 직렬화 시간과 분리해서 측정하세요.
각 구성 프로그램은 항목 수 또는 시작점 수, 해당하는 경우 서로 다른 끝점 수, 구성 해시 횟수,
소요 시간(초), 직렬화된 파일 크기(바이트)를 보고해야 합니다.

비교 프로그램은 두 테이블의 JSON 파일을 읽고 같은 데이터베이스에 두 방법을 적용합니다.
복구 계정 수/전체 계정 수, 구성 해시 횟수, 구성 시간(초), 저장 레코드 수, 서로 다른 끝점 수,
파일 크기(바이트), 조회 해시 횟수, 조회 시간(초)을 보고하세요.
레인보우 테이블의 저장 레코드 한 개는 시작점/끝점 쌍이며, 끝점을 공유하는 시작점도 각각 포함합니다.
복구한 수업용 비밀번호 대신 개수만 출력하세요.

```console
python3 -c "import build_precomputation_table, build_rainbow_table, compare_table_attacks; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_table_attacks.py -v
```

활성화된 테스트 7개가 모두 통과해야 합니다.

### 공통 완료 유틸리티

메인 프로그램 전체는 직접 작성해야 합니다. 암호화 봉투 파일의 경로는 셸의 현재 디렉토리가 아니라
실습 파일을 기준으로 해석하세요. 번호가 붙은 Part 실습 파일에서 제공된 공통 유틸리티를
import하려면 다음을 사용하세요.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)`는 암호화 봉투를 인증한 뒤 `FLAG{...}` 문자열을 반환합니다.
증명값이 잘못되면 `ValueError`가 발생합니다. 봉투를 변경하지 말고 구현과 증명값 형식을 점검하세요.
공개 데모 증명값은 데모 결과물만 열 수 있으며 이 Part의 플래그를 열 수는 없습니다.
계산한 Part 플래그는 강사가 지정한 채널로 제출하세요.

### 전체 테이블·레인보우 비교 후 플래그 열기

`compare_table_attacks.py`의 메인에서 전체 테이블 공격이 반환한 복구 계정 매핑을 유지하세요.
입력 데이터베이스의 모든 계정이 포함되는지 확인한 다음 `canonical_account_proof(full_recovered)`를
호출하고, 결과를 `data/flag_challenge.json`에 대한 `unlock_flag()`에 전달하세요.
두 방법의 측정값 행을 출력한 뒤 반환된 `FLAG{...}`를 출력하세요.

정규화된 텍스트는 계정 키를 정렬하고 유니코드를 보존한 간결한 JSON입니다.
`json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
공개 매핑 `{"b": "public-two", "a": "public-one"}`의 경우
`{"a":"public-one","b":"public-two"}`가 됩니다.
공통 인코더를 사용하고 복구한 수업용 매핑이나 증명값을 출력하지 마세요.

전체 커버리지를 보장하는 **전체 테이블** 결과를 증명값으로 사용하세요.
레인보우의 부분적 커버리지는 정상적인 결과입니다.
레인보우 방법의 구현, 실행, 결과 해석도 반드시 수행해야 합니다.

## 10. 수업용 테이블 생성 및 비교

```console
python3 build_precomputation_table.py data/rainbow_lab_config.json generated/precomputation.json
python3 build_rainbow_table.py data/rainbow_lab_config.json generated/rainbow.json
python3 compare_table_attacks.py data/rainbow_password_database.csv generated/precomputation.json generated/rainbow.json
```

전체 테이블에는 항목 1,296개가 있으며 구성에 해시 1,296회를 사용합니다.
레인보우 테이블은 시작점 96개와 구성 해시 1,152회를 사용하며, 서로 다른 끝점은 최대 96개입니다.
끝점 수가 시작점 수보다 적으면 체인이 합쳐진 것입니다.

전체 테이블은 새로운 조회 해시 없이 제공된 모든 대상을 복구해야 합니다.
레인보우 테이블에서는 부분적 커버리지와 0보다 큰 조회 비용이 나타나야 합니다.
정확한 소요 시간과 JSON 크기는 달라질 수 있습니다.
두 측정값 행 뒤에 복구한 `FLAG{...}`를 출력하며 비교가 끝납니다.
대상별 하드코딩을 추가하지 마세요.

마지막으로 무솔트 테이블을 솔트가 있는 경우에 그대로 재사용할 수 없는 이유를 관찰하세요.

```console
python3 - <<'PY'
import hashlib
import json
from pathlib import Path
entries = json.loads(Path("generated/precomputation.json").read_text())["entries"]
public = b"abc1"
print("Unsalted present:", hashlib.sha256(public).hexdigest() in entries)
print("Salted present:", hashlib.sha256(b"public-salt:" + public).hexdigest() in entries)
PY
```

예상 출력은 `Unsalted present: True`와 `Salted present: False`입니다.
공개 솔트는 조회 키를 바꾸므로 서로 다른 솔트에는 별도의 사전 계산이 필요합니다.
실제 비밀번호 저장에는 추가로 비밀번호용 KDF가 필요합니다.

## 11. 완료 확인 및 보고서

- [ ] 처음에 비어 있던 파일 3개에 완성된 프로그램을 작성했다.
- [ ] 단계별 공개 검사와 활성화된 모든 테스트가 통과한다.
- [ ] 두 결과물이 필수 스키마와 결정적인 설정을 사용한다.
- [ ] 두 방법이 예외 처리 없이 같은 수업용 데이터베이스를 공격한다.
- [ ] 전체 커버리지와 레인보우의 한계를 측정하고 설명했다.
- [ ] 솔트 관찰 결과와 합성 레코드 파싱을 문서화했다.
- [ ] 최종 프로그램이 자신의 `data/flag_challenge.json`을 인증하고 Part 플래그를 출력한다.

Python 파일 3개와 다음 비교 표를 사용한 보고서를 제출하세요.

| 방법 | 구성 해시 횟수 | 구성 시간(초) | 저장 레코드 수 | 서로 다른 끝점 수 | JSON 바이트 수 | 복구/전체 | 조회 해시 횟수 | 조회 시간(초) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 전체 테이블 | | | | 해당 없음 | | | | |
| 레인보우 | | | | | | | | |

파싱과 추측의 차이, 축약이 해시의 역함수가 아닌 이유, 끝점 병합이 커버리지에 미치는 영향,
레인보우가 절약하는 저장 공간과 추가하는 조회 비용, 솔트가 무솔트 사전 계산의 공유를 막는 이유를 설명하세요.
개념적으로 저장하는 값과 JSON의 부가 비용을 함께 논의하세요.
복구한 수업용 비밀번호를 공개하지 마세요.
