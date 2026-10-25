**한국어** | [English](../../../en/labs/lab01/part2_dictionary_attack/README.md)

# Part 2: 통제된 온라인 SSH 사전 공격

**예상 소요 시간:** 25분. 고정된 `labstudent@lab01-ssh-target:22` 서비스와 제공된
107개 항목의 수업용 단어 목록만 사용합니다. 후보는 순서대로 시도하고 최대 120개로 제한하며,
실패 후에는 지연을 둡니다. 임의의 대상, 계정, 포트, 외부 단어 목록 또는 동시 실행 옵션을
추가하지 마세요.

이 실험은 온라인으로 진행됩니다. 각 추측이 서버에 도달하므로 서버는 이를 기록하거나,
지연하거나, 차단할 수 있습니다. Part 3에서는 로컬 오프라인 검증과 비교합니다.

## 학습 목표와 파일

비밀번호만 사용하는 SSH 인증을 구현하고, 모든 실행 결과에서 자원을 닫으며,
제한된 순차 시도의 비용을 측정하고 서버 측 관찰 결과를 해석합니다.

| 파일 | 역할 |
| --- | --- |
| `samples/ssh_api_demo.py` | 완성된 오프라인 Paramiko, CLI, 자원 정리, 시간 측정 예제 |
| `ssh_dictionary_attack.py` | 비어 있는 학생 실습 파일 |
| `data/ssh-lab-wordlist.txt` | 고정된 가상 후보 107개의 단어 목록 |
| `test_ssh_dictionary_attack.py` | 제공 데이터 검사와 선택적으로 활성화하는 구현 검사 |
| `samples/flag_unlock_demo.py` | 공개 도우미 사용 예제. Part 정답은 포함하지 않음 |
| `data/flag_challenge.json` | 실험 결과로 여는 암호화된 완료 플래그 |

import 문, 상수, 함수, CLI, 실행 조건을 포함해 프로그램 전체를 작성합니다.
파일을 가져오는 것만으로 네트워크 요청이 발생해서는 안 됩니다.

## 1. 예제 실행 및 분석

저장소의 Docker 안내에 따라 수업용 컨테이너에 들어간 뒤 다음을 실행합니다.

```console
cd /workspace/labs/lab01/part2_dictionary_attack
python3 samples/ssh_api_demo.py
python3 -m unittest test_ssh_dictionary_attack.py -v
```

예제 출력:

```text
Nonempty lines: 2
Client class: SSHClient
Transport before connect: None
Authentication error type: AuthenticationException
Client closed; no network request sent
Elapsed: <seconds> seconds
```

이 예제는 `connect()`를 호출하지 않으므로 SSH 대상이 필요하지 않습니다.
`argparse`, 선택적인 텍스트 입력, `perf_counter()`, `try/finally`가 어떻게 연결되는지 살펴보세요.
선택 인자 `--notes`는 로컬 텍스트 파일에서 비어 있지 않은 줄의 수를 셉니다.
시간은 달라지지만 나머지 표시 값은 고정됩니다. 파일은 생성하지 않습니다.

구현 전에는 제공 데이터 테스트 하나가 통과하고 구현 검사 두 개는 건너뜁니다.
기본 검사는 인증을 수행하거나 일치하는 후보를 공개하지 않습니다.

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

## 2. 상수와 load_candidates() 작성 및 검사

`ssh_dictionary_attack.py`에 다음 실습용 상수를 정의합니다.

```text
TARGET_HOST = "lab01-ssh-target"
TARGET_PORT = 22
TARGET_USERNAME = "labstudent"
MAX_CANDIDATES = 120
```

`load_candidates(path: Path) -> list[str]`를 구현합니다. UTF-8로 줄을 읽고 앞뒤 공백을
제거한 뒤 빈 줄을 건너뛰되 순서는 유지합니다. 남은 후보가 120개를 초과하면 `ValueError`를
발생시키세요. 최종 CLI 실습에서는 제공된 단어 목록만 사용합니다.

네트워크 코드를 작성하기 전에 다음 작은 검사를 실행합니다.

```console
python3 - <<'PY'
import tempfile
from pathlib import Path
from ssh_dictionary_attack import load_candidates
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "public.txt"
    path.write_text(" public-a \n\npublic-b\n", encoding="utf-8")
    assert load_candidates(path) == ["public-a", "public-b"]
    path.write_text("public\n" * 121, encoding="utf-8")
    try:
        load_candidates(path)
    except ValueError:
        pass
    else:
        raise AssertionError("over-limit list was accepted")
print("Bounded input check: OK")
PY
```

`Bounded input check: OK`를 확인한 뒤 다음으로 진행합니다.

## 3. try_candidate() 작성 및 서버 없는 검사

`paramiko`를 사용해 `try_candidate(candidate: str) -> bool`을 구현합니다.

1. `SSHClient` 하나를 생성합니다. 이 임시 대상에 한해서만 `AutoAddPolicy`를 설정합니다.
2. 고정 호스트, 포트, 사용자 이름, 후보 비밀번호로 `connect()`를 호출합니다.
   다른 인증 정보를 시도하지 않도록 `allow_agent=False`와 `look_for_keys=False`를 설정하고,
   연결·배너·인증에 각각 제한된 타임아웃을 지정합니다.
3. 인증에 성공하면 `True`를, `paramiko.AuthenticationException`이 발생하면 `False`를 반환합니다.
4. `finally`에서 항상 `close()`를 호출합니다. 다른 연결 오류는 그대로 드러나게 하여,
   중지된 대상과 잘못된 비밀번호를 혼동하지 않도록 합니다.

다음 검사는 클라이언트를 모의 객체로 대체하므로 네트워크 트래픽을 보내지 않습니다.

```console
python3 - <<'PY'
from unittest.mock import Mock, patch
import paramiko
import ssh_dictionary_attack as attack
for failure in (False, True):
    client = Mock()
    if failure:
        client.connect.side_effect = paramiko.AuthenticationException()
    with patch.object(attack.paramiko, "SSHClient", return_value=client):
        assert attack.try_candidate("public-fixture") is (not failure)
    client.close.assert_called_once()
    args, kwargs = client.connect.call_args
    host = kwargs.get("hostname", args[0] if args else None)
    assert host == "lab01-ssh-target"
    assert kwargs["port"] == 22 and kwargs["username"] == "labstudent"
    assert kwargs["password"] == "public-fixture"
    assert kwargs["allow_agent"] is False and kwargs["look_for_keys"] is False
print("One-attempt check: OK")
PY
```

`One-attempt check: OK`를 확인한 뒤 다음으로 진행합니다.

## 4. dictionary_attack() 작성 및 중단 규칙 검사

`dictionary_attack(candidates: list[str], delay: float = 0.25) -> tuple[str | None, int, float]`를
구현합니다. 크기 제한을 초과한 입력은 거부하고, 각 후보를 `try_candidate()`로 순서대로
시도하며 성공한 시도를 포함해 모든 시도 횟수를 셉니다. 실패 후에는 기다리고, 처음 성공하면
중단한 뒤 `(candidate_or_None, attempts, elapsed_seconds)`를 반환합니다.
경과 시간은 `time.perf_counter()`로 측정합니다. 후보는 절대 출력하지 마세요.

```console
python3 - <<'PY'
from unittest.mock import patch
import ssh_dictionary_attack as attack
with patch.object(attack, "try_candidate", side_effect=[False, True]) as attempt:
    found, count, elapsed = attack.dictionary_attack(["public-a", "public-b", "public-c"], delay=0)
    assert found == "public-b" and count == 2 and elapsed >= 0
    assert attempt.call_count == 2
with patch.object(attack, "try_candidate", return_value=False):
    found, count, elapsed = attack.dictionary_attack(["public-a"], delay=0)
    assert found is None and count == 1 and elapsed >= 0
print("Sequential search check: OK")
PY
```

`Sequential search check: OK`를 확인한 뒤 다음으로 진행합니다.

<a id="step-1-build-and-start-the-isolated-target"></a>

## 5. CLI 작성 및 격리된 대상 시작

제공된 로컬 단어 목록의 경로를 받아 후보를 불러오고 공격 함수를 호출하는 `main()`을
작성합니다. 고정 대상, 시도 횟수, 경과 시간(초), 성공 여부만 출력합니다.
실패 후 기본 지연은 0.25초로 유지하고 `__main__` 실행 조건을 추가합니다.
선택적으로 활성화하는 구현 검사를 실행합니다.

```console
LAB01_GRADE=1 python3 -m unittest test_ssh_dictionary_attack.py -v
```

테스트 세 개가 모두 통과해야 합니다. 이 테스트는 입력과 고정 대상을 확인하며,
앞의 모의 객체 검사는 동작을 확인합니다.

이제 **호스트 터미널**의 저장소 루트에서 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh build
docker compose -f docker/compose.yml --profile lab01-ssh up -d lab01-ssh-target
docker compose -f docker/compose.yml --profile lab01-ssh ps
```

`healthy` 상태가 될 때까지 기다립니다. 내부 Compose 네트워크는 SSH 포트를 외부에
공개하지 않습니다. 같은 네트워크의 수업용 컨테이너에 들어갑니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh run --rm course bash
cd /workspace/labs/lab01/part2_dictionary_attack
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

### 인증 성공 후 플래그 열기

`dictionary_attack()`이 일치하는 후보를 반환하면, 반환된 문자열을 그대로
`data/flag_challenge.json`의 증명값으로 사용합니다. 제공된 `unlock_flag(flag_path, match)`를
호출하고 반환된 `FLAG{...}`를 상태 지표 뒤의 마지막 줄에 출력합니다.
후보 자체는 공개하지 마세요. 일치하는 후보가 없으면 실패를 보고하고 플래그 열기를 시도하지 않습니다.

이 암호화된 플래그 파일은 로컬에 있습니다. SSH 대상에는 플래그 파일이나 새 서비스 엔드포인트가
필요하지 않습니다. 먼저 고정 서비스에서 후보를 복구해야 합니다.

## 6. 전체 실습 실행 및 증거 확인

```console
python3 ssh_dictionary_attack.py data/ssh-lab-wordlist.txt
```

출력 형식은 다음과 같아야 합니다.

```text
Target: labstudent@lab01-ssh-target:22
Attempts: <count>
Elapsed: <seconds> seconds
Result: candidate found
FLAG{...}
```

SSH 처리 비용과 호스트에 따라 수십 초가 걸릴 수 있습니다. 시도 횟수는 1–107입니다.
일치하는 후보가 출력이나 보고서에 나타나면 안 됩니다. 연결 오류가 발생하면 대상과
네트워크를 점검해야 합니다.

두 번째 호스트 터미널에서 이 대상의 로그를 확인합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh logs --tail 50 lab01-ssh-target
```

후보 값을 포함하지 않고 로그인 실패 관찰 결과를 기록합니다.
수업용 셸에서 나와 호스트에서 임시 대상 컨테이너를 제거합니다.

```console
exit
docker compose -f docker/compose.yml --profile lab01-ssh rm --stop --force lab01-ssh-target
```

## 7. 완료 확인 및 보고서

- [ ] 작은 검사 세 개와 활성화한 모든 테스트를 통과했습니다.
- [ ] 완성한 프로그램이 고정 대상과 입력 크기 제한을 유지합니다.
- [ ] 제공된 실습에서 후보를 출력하지 않고 성공을 보고합니다.
- [ ] 시도 횟수, 경과 시간, 민감한 값을 가린 서버 관찰 결과를 기록했습니다.
- [ ] 임시 대상 컨테이너를 제거했습니다.
- [ ] 최종 프로그램이 자신의 `data/flag_challenge.json`을 인증하고 Part 플래그를 출력합니다.

Python 파일과 관찰 결과를 제출합니다. 이 공격이 온라인인 이유, 서버가 관찰할 수 있는 정보,
속도 제한이 온라인 공격 비용을 바꾸는 방식, 모든 자원을 닫아야 하는 이유,
`AutoAddPolicy`를 이 임시 수업용 서비스에만 사용하는 이유를 설명하세요.
Part 3의 오프라인 CSV 검증과 비교합니다.
