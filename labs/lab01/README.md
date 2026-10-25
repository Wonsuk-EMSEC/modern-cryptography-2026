**한국어** | [English](../../en/labs/lab01/README.md)

# Lab 01: 비밀번호 기반 인증

**예상 소요 시간:** 2–3시간. **실행 환경:** 수업용 Docker 컨테이너.

## 윤리 및 허가된 사용 범위

이 수업을 위해 제공된 가상의 인증 정보, 해시, 메타데이터와 선택 실습 자료만 사용합니다.
유출된 비밀번호를 사용하거나 `/etc/shadow`에 접근하지 마세요. 임의의 시스템 스캔,
제3자의 Wi-Fi 트래픽 캡처, 클라이언트 연결 강제 해제, 공개 서비스 공격도 금지합니다.
모든 실습은 로컬 파일 또는 교수가 관리하는 격리된 시스템을 대상으로 합니다.

## 학습 흐름

해시 → 솔트 → 통제된 온라인 추측 → 오프라인 해시 추측 → 느린 비밀번호 해싱 →
시스템 검증값 → 사전 계산/레인보우 테이블 → WPA2 오프라인 크래킹

실습을 마치면 해싱과 암호화를 구별하고, 솔트와 오프라인 추측을 설명하며, 주요 비밀번호
KDF를 비교할 수 있어야 합니다. 또한 가상의 Linux 비밀번호 레코드를 해석하고,
시간–메모리 절충을 평가하며, WPA2 후보를 오프라인으로 검증하는 과정을 설명할 수 있어야 합니다.

## 환경 설정 및 테스트

VS Code에서는 공통 [수업용 컨테이너 설정 안내](../../README.md#use-vs-code-with-the-course-container)를 따릅니다.
**저장소 루트**를 열고 **Dev Containers: Reopen in Container**를 실행하세요.
모든 Part와 실습을 이 창에서 진행합니다. 이 창의 Python 실행·디버깅 명령과 통합 터미널은
수업용 환경을 사용하며, 기본 인터프리터는 `/opt/course-venv/bin/python3`입니다.
공통 안내에는 이전에 저장한 인터프리터 선택을 한 번 수정하는 방법도 나와 있습니다.

터미널만 사용한다면 **호스트 터미널**에서 저장소 루트로 이동한 뒤 아래 명령을 실행합니다.
필요한 경우 공통 이미지를 빌드하고, 공용 수업 컨테이너를 백그라운드에서 시작한 다음
상태를 확인합니다.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml ps
```

`-d` 옵션은 `course`를 백그라운드에서 실행합니다. `ps` 결과에 `Up`(실행 중)이 표시되어야 합니다.
두 실습은 동일한 `docker/compose.yml`과 수업 컨테이너를 사용합니다.
대상 서버에는 별도 프로필이 있으며 **기본적으로 시작되지 않습니다**.

| 대상 서비스 | 프로필 | 사용 실습 |
| --- | --- | --- |
| `lab01-ssh-target` | `lab01-ssh` | Lab01 Part 2 |
| `lab02-target` | `lab02` | Lab02 Part 4–6 |

대상 서버는 해당 Part에서 필요할 때만 그 Part의 README에 따라 시작합니다.
Lab01 Part 2는 [SSH 대상 설정 안내](part2_dictionary_attack/README.md#step-1-build-and-start-the-isolated-target)를 따르세요.

컨테이너에 연결된 VS Code에서는 통합 터미널을 엽니다. 터미널만 사용한다면
**호스트 터미널**에서 실행 중인 수업 컨테이너의 셸을 엽니다.

```console
docker compose -f docker/compose.yml exec course bash
```

이 명령은 컨테이너 셸을 엽니다. 호스트의 VS Code 창을 컨테이너에 연결하는 명령은 아닙니다.

이어서 **컨테이너 내부**에서 실습 테스트를 실행합니다.

```console
cd /workspace/labs/lab01
pytest -q
```

각 번호별 Part에는 독립적으로 실행할 수 있는 `samples/` 예제와 비어 있는 실습 파일이 있습니다.
Part README를 위에서부터 순서대로 따라가세요. 예제를 관찰하고, 함수 하나를 작성한 뒤,
바로 이어지는 작은 예제 검사를 실행하는 과정을 반복합니다. 함수 검사를 마친 다음 프로그램의
진입점을 작성하고 제공된 파일을 연결합니다. 마지막 절에는 필요한 출력과 보고서 증거가
설명되어 있습니다. 실습 파일이 비어 있어도 제공 데이터의 기본 검사는 실행됩니다.
해당 함수를 완성한 뒤에만 구현 검사를 활성화하세요. 테스트 파일과 역할, 완성한 Part의
실행 명령은 [테스트](#tests)를 참고하세요.

각 Part의 마지막에는 해당 실험 결과로 암호화된 완료 플래그를 엽니다. 정확한 증명값 형식은
Part README를 따르고, 반환된 `FLAG{...}` 줄을 출력하세요. 공통 도우미는
[`common/README.md`](common/README.md)에 설명되어 있습니다. 공개 예제는 학생 구현이
완성되기 전에도 실행할 수 있습니다.

각 Part의 제공 데이터는 해당 Part의 `data/` 디렉토리에 있습니다. 공용 데이터 폴더를
참조하지 않고 각 Part 디렉토리에서 명령을 실행할 수 있습니다.

## 실습 진행 순서

1. **해시와 솔트(20분).** [Part 1 README](part1_hashing/README.md)를 읽고 예제를 실행합니다.
   `hash_password.py`와 `salted_hash.py`를 구현하고 검사한 뒤 두 프로그램을 실행합니다.
   예상 결과는 일정한 해시값, 실행마다 달라지는 솔트/해시값 쌍, Part 완료 플래그입니다.
   확인할 내용: 해싱과 암호화를 구별하고 계정마다 고유한 솔트가 필요한 이유를 설명하세요.
2. **통제된 온라인 사전 공격(25분).** [Part 2 README](part2_dictionary_attack/README.md)를 읽습니다.
   과제로 지정되었다면 격리된 Compose SSH 대상을 시작하고, 시도 횟수가 제한된 클라이언트를
   작성·검사한 뒤 로컬 로그를 관찰하고 대상 컨테이너를 제거합니다. 예상 결과는 민감한 값을
   가린 상태 정보, 시도 횟수, 서버에서 확인한 실패 기록, Part 완료 플래그입니다.
   확인할 내용: SSH 서비스가 이러한 추측을 관찰하고 속도를 제한할 수 있는 이유는 무엇인가요?
3. **오프라인 크래킹과 비밀번호 KDF(40분).** [Part 3 README](part3_password_kdfs/README.md)를 읽고
   솔트가 없는 경우와 있는 경우의 크래킹 프로그램을 구현합니다. `compare_cost.py`를 실행한 뒤
   KDF 벤치마크와 로컬 등록/검증 데모를 실행합니다. 예상 결과는 해시 계산 횟수 비교,
   KDF 실행 시간 중앙값, 평문을 저장하지 않는 인증, Part 완료 플래그입니다.
   확인할 내용: 솔트가 사전 계산의 재사용을 막는 원리를 설명하고 SHA-256, PBKDF2, bcrypt,
   scrypt, Argon2id를 비교하세요.
4. **시스템 해시와 테이블 공격(35분).** [Part 4 README](part4_system_hashes/README.md)를 읽고
   제공된 shadow 형식 파일을 파싱합니다. 이어서 제한된 교육용 비밀번호 데이터베이스에 대해
   전체 사전 계산과 레인보우 테이블을 구현합니다. 예상 결과는 파싱한 검증값 필드와 테이블 생성
   작업량, 저장 공간, 조회 작업량, 커버리지 비교, Part 완료 플래그입니다.
   확인할 내용: 시간–메모리 절충과 솔트가 공통 테이블 재사용을 막는 이유를 설명하세요.
5. **WPA2 검증(40분).** [Part 5 README](part5_wpa2/README.md)를 읽고 Wireshark 또는 TShark로
   수업용 PCAP을 직접 분석합니다. 캡처 워크시트를 작성하고 PMK → PTK → KCK → MIC 과정을
   구현한 뒤 제한된 로컬 검사를 실행합니다. 예상 결과는 완전한 M1–M4 순서의 분석 증거,
   수업 전용 단어 목록에서 찾은 일치 후보 하나, Part 완료 플래그입니다.
   확인할 내용: 각 키 유도 단계와 오프라인 추측에 대한 속도 제한의 한계를 설명하세요.
6. **보고서(15분).** 실제 비밀번호를 포함하지 않고 결과와 확인 질문에 대한 답변을 정리합니다.

실제 인증 정보는 포함되어 있지 않습니다. 제공된 PCAP은 허가된 이 오프라인 실습에만 사용합니다.
교수는 격리된 호스트 전용 네트워크에 의도적으로 취약하게 구성한 Ubuntu VM을 선택적으로
제공할 수 있으나, 핵심 실습에 필수는 아닙니다.

<a id="tests"></a>

## 테스트

테스트는 제공된 데이터, 예제, 학생 함수를 자동으로 검사합니다.
**수업용 컨테이너 내부**에서 실행하세요.

```console
cd /workspace/labs/lab01
make test
```

`make test`는 각 번호별 Part 디렉토리와 `tests/`에서 테스트를 수집해 `pytest -q`를 실행합니다.
기본 검사는 구현 전에도 실행되며, 학생 함수가 필요한 검사는 기본적으로 건너뜁니다.
이 단계의 `skipped` 결과는 정상이며, 미완성 함수가 올바르다는 의미는 아닙니다.

현재 진행 중인 실습은 각 Part의 테스트 파일로 검사합니다.

| 테스트 파일 | 역할 |
| --- | --- |
| [part1_hashing/test_hashing.py](part1_hashing/test_hashing.py) | 예제 존재 여부, 해싱의 결정성, 서로 다른 솔트의 효과를 검사합니다. |
| [part2_dictionary_attack/test_ssh_dictionary_attack.py](part2_dictionary_attack/test_ssh_dictionary_attack.py) | 제한된 단어 목록, 고정 SSH 대상 설정, 후보 불러오기를 검사합니다. |
| [part3_password_kdfs/test_dictionary_cost.py](part3_password_kdfs/test_dictionary_cost.py) | 데이터 스키마, 복구한 후보, 솔트 유무에 따른 추측의 해시 계산 횟수를 검사합니다. |
| [part4_system_hashes/test_table_attacks.py](part4_system_hashes/test_table_attacks.py) | 제공된 비밀번호 공간과 데이터베이스, 테이블 생성, 축약 함수, 조회를 검사합니다. |
| [part5_wpa2/test_wpa2_workflow.py](part5_wpa2/test_wpa2_workflow.py) | 메타데이터와 로컬 PCAP, PMK, PTK, KCK, MIC, 사전 검증을 검사합니다. |

Part의 필수 함수를 완성하면 `LAB01_GRADE=1`로 구현 검사를 활성화하고 해당 테스트 파일을
선택합니다. 예를 들어 Part 3 크래킹 프로그램 두 개를 모두 완성했다면 다음과 같이 실행합니다.

```console
LAB01_GRADE=1 python3 -m pytest -q part3_password_kdfs/test_dictionary_cost.py
```

환경 변수는 구현 검사를 활성화하고, 파일 경로는 검사할 Part를 선택합니다.
각 Part README에 해당 검증 명령이 나와 있습니다. 완성한 Part 하나를 선택하면
다른 미완성 실습의 검사를 실행하지 않을 수 있습니다.

저장소의 `tests/`에는 다음 파일도 있습니다.

| 파일 | 역할 |
| --- | --- |
| `test_password_authentication.py` | 등록/검증 예제와 shadow 파서 예제, 선택적으로 활성화하는 Part 1 해싱 및 Part 5 검증 함수를 검사합니다. |
| `test_md5_collision.py` | 제공된 충돌 파일의 내용이 다르고, MD5 해시값은 같으며, SHA-256 해시값은 다른지 검사합니다. 이 데이터 검사는 학생 구현 없이 실행됩니다. |
| `__init__.py` | `tests/`를 가져올 수 있는 Python 패키지로 만듭니다. |

자동 테스트는 로컬 제공 데이터 또는 작은 가상 입력을 사용합니다. Part 2의 테스트 파일은
SSH 요청 없이 상수와 단어 목록 처리를 검사하므로 대상 서버가 필요하지 않습니다.
실제 Part 2 온라인 실험에는 `lab01-ssh-target`이 필요합니다. 해당 README에 따라 서비스를
시작하세요. 테스트 통과는 선택된 동작을 검증하므로, 완성한 프로그램도 실행해 해당 Part가
요구하는 출력과 완료 플래그를 수집해야 합니다. 테스트 파일은 제공된 상태로 유지하고
실습 파일을 구현하세요.
