<a id="lab-02-practical-security-of-block-ciphers"></a>
# Lab 02: 블록 암호의 실질적인 보안

**한국어** | [English](../../en/labs/lab02/README.md)

**예상 소요 시간:** 4–5시간. **실행 환경:** 수업용 Docker 컨테이너.

이 실습은 로컬 환경에서 진행하는 CTF 형식입니다. 각 Part는 `FLAG{...}`
형식의 값을 복구하면 완료되는 암호학 퍼즐입니다. 이 수업에서 제공한 데이터와
로컬 서비스만 대상으로 실습하세요. 명시적인 허가를 받지 않은 시스템, 장치,
계정, 서비스에는 이러한 기법을 사용하지 마세요.

<a id="learning-progression"></a>
## 학습 순서

| Part | 주제 | 핵심 내용 |
| --- | --- | --- |
| 1 | DES 전수 조사 공격 | 작은 키 공간의 위험성을 이해합니다. |
| 2 | Double-DES 중간 일치 공격 | 암호를 결합하는 방식이 중요함을 이해합니다. |
| 3 | AES-CBC와 PKCS#7 | 공격에 앞서 암호의 구성 방식을 이해합니다. |
| 4 | CBC 비트 플리핑 공격 | 기밀성이 무결성을 보장하지는 않음을 확인합니다. |
| 5 | 패딩 오라클 공격 | 복호화 동작이 평문을 유출할 수 있음을 확인합니다. |
| 6 | MAC-then-Encrypt와 Encrypt-then-MAC 비교 | 인증 순서의 중요성을 이해합니다. |
| 7 | AES에 대한 CPA | 구현 과정에서 유출되는 정보로 강력한 암호의 키도 노출될 수 있음을 확인합니다. |

모든 Part는 범위가 제한된 탐색, 생성된 데이터, 격리된 수업용 대상 서비스,
합성 트레이스만 사용합니다. 이 실습에서 전달하려는 핵심은 다음과 같습니다.

> 암호의 보안은 암호 알고리즘 자체뿐 아니라 키 길이, 결합 방식, 운용 모드,
> 인증, 오류 처리, 구현에도 달려 있습니다.

<a id="setup"></a>
## 환경 준비

Lab 01을 마치지 않아도 Lab02를 시작할 수 있습니다. 모든 실습은 같은 Docker
환경을 공유합니다. 수업용 이미지를 빌드하고 `course` 컨테이너를 시작한 뒤,
그 안에서 Python 코드를 실행합니다. **Lab 01의 환경 준비를 완료했다면 이미
공통 이미지를 빌드하고 이 컨테이너를 사용한 상태입니다.** 같은 저장소를
사용하고 아래 안내에 따라 환경을 갱신하세요.

VS Code에서는 공통 [수업용 컨테이너 설정](../../README.md#use-vs-code-with-the-course-container)에
따라 **저장소 루트**를 열고 **Dev Containers: Reopen in Container**를
실행하세요. 모든 Part와 실습에 이 창을 사용합니다. 이 설정은 Python 실행 및
디버깅 명령의 기본 인터프리터를 `/opt/course-venv/bin/python3`으로 지정하고,
통합 터미널을 `course` 안에서 실행합니다. 공통 안내에는 VS Code에서 이전에
선택한 인터프리터를 한 번 수정하는 방법도 포함되어 있습니다. 추가 대상 서비스는
여전히 2단계의 호스트 터미널 명령으로 시작해야 합니다.

**Lab 01을 위해 저장소를 이미 복제했다면** Lab02 환경을 빌드하기 전에 기존
복사본을 갱신하세요. **호스트 터미널**(Windows에서는 Ubuntu/WSL)에서
`docker/`와 `labs/`가 있는 기존 `modern-cryptography-2026` 디렉토리로
이동합니다. 수업용 컨테이너 안에 있다면 먼저 `exit`를 실행하세요. 그런 다음
다음을 실행합니다.

```console
git status
git pull --ff-only
```

최신 실습 파일, README 안내, Docker 설정이 내려받아집니다. 저장소를 다시
복제할 필요는 없습니다. Git이 로컬 작업을 덮어쓰게 된다고 알리면 해당 작업을
커밋하거나 stash에 보관한 뒤 다시 시도하세요. 브랜치가 갈라진 경우에는 작업을
보존하면서 합칠 수 있도록 강사에게 도움을 요청하세요. 갱신 후에는
[1단계](#1-prepare-the-common-course-image)에서 공통 이미지를 다시 빌드합니다.

**아직 수업용 이미지를 빌드하지 않았다면** 먼저
[사전 준비 사항](../../README.md#0-prerequisites)을 완료하세요. 로컬 복사본도
없다면 [저장소를 복제](../../README.md#1-clone-the-course-repository)하고,
이미 있다면 위 안내대로 갱신합니다. Docker가 실행 중인지 확인하세요.
**호스트 터미널**(Windows에서는 Ubuntu/WSL)에서 `docker/`와 `labs/`가 있는
저장소 루트로 이동한 뒤 다음을 실행합니다.

```console
docker compose -f docker/compose.yml build course
```

이 명령은 `docker/Dockerfile`을 사용하여 실습에 필요한 도구와 Python
라이브러리를 포함한 공통 `modern-cryptography-2026` 이미지를 빌드합니다.
첫 빌드는 몇 분 걸릴 수 있습니다. 성공적으로 완료되면 이미지가 준비된 것이므로
[2단계](#2-start-the-services-you-need)에서 컨테이너를 시작하세요. 아래 1단계에서
같은 빌드를 반복할 필요는 없습니다.

Part 4–6에는 자신의 컴퓨터에서 실행하는 대상 컨테이너도 필요합니다.
Lab 01 Part 2의 SSH 대상과 같은 방식입니다. Lab02 대상은 미리 빌드된 이미지로
제공되며, Docker Compose가 GitHub Container Registry(GHCR)에서 자동으로
내려받습니다. 강사가 운영하는 별도 서버는 필요하지 않습니다.

| 서비스 | 용도 |
| --- | --- |
| `course` | 모든 실습에서 공유하는 셸, Python 코드, 저장소 파일 |
| `lab02-target` | Part 4–6에서 상호 작용하는 로컬 애플리케이션 |

<a id="1-prepare-the-common-course-image"></a>
### 1. 공통 수업용 이미지 준비

- **Lab02부터 시작하는 경우:** 메인 README의
  [사전 준비 사항](../../README.md#0-prerequisites)과
  [저장소 복제 안내](../../README.md#1-clone-the-course-repository)를 따른 뒤,
  아래 명령으로 수업용 이미지를 빌드하세요.
- **Lab 01 환경 준비를 이미 완료한 경우:** 당시 준비한 저장소에서 위 안내대로
  `git pull --ff-only`를 실행한 뒤 빌드하세요. **Lab02를 시작하기 전에 아래의
  이미지 빌드와 2단계의 서비스 시작 명령을 다시 실행하는 것을 권장합니다.**
  Lab 01 이후 의존성 추가나 서비스 설정 변경으로 `docker/Dockerfile`과
  `docker/compose.yml`이 갱신되었을 수 있습니다. 최신 수업 파일을 사용해야
  이 명령으로 Lab02 환경 변경 사항이 적용됩니다.

`docker/Dockerfile`은 공통 수업용 이미지의 빌드 방법을 정의합니다. Part 7의
그래프 라이브러리를 포함해 모든 실습에 필요한 Python, 암호 라이브러리 및
기타 도구를 설치합니다. `docker/compose.yml`은 이미지를 빌드하고 저장소를
`/workspace`에 마운트한 `course` 컨테이너를 실행하는 방법을 Docker에
지정합니다. 실습 의존성을 수동으로 설치할 필요는 없습니다.

**호스트 터미널**(Windows에서는 Ubuntu/WSL)에서 Docker가 실행 중인지 확인하고,
`docker/`와 `labs/`가 있는 저장소 루트로 이동하세요. 수업용 셸 안에 있다면
먼저 `exit`를 실행합니다. VS Code가 컨테이너에 연결되어 있다면 별도 호스트
터미널을 사용하세요. 수업용 이미지를 빌드합니다.

```console
docker compose -f docker/compose.yml build course
```

Lab 01 환경 준비에서 사용한 것과 같은 이미지 빌드 명령입니다. 첫 빌드는
몇 분 걸릴 수 있으며, 이후 빌드에서는 가능한 경우 캐시된 레이어를 재사용합니다.
Lab02 환경을 준비한 뒤에는 갱신된 환경 파일이 제공될 때만 다시 빌드하면 됩니다.

추가 대상 서비스에는 별도 빌드 파일이 있습니다. Lab 01 SSH 대상은
`docker/lab01-ssh-target/Dockerfile`, Lab02 애플리케이션은
`docker/lab02-target/Dockerfile`을 사용합니다. 강사가 비공개 서버 파일로
Lab02 대상을 빌드하고 이미지를 제공합니다. Part 4–6에서는 2단계에서 해당
이미지를 시작하세요. 위의 공통 수업용 빌드는 여러분의 작업 환경만 준비합니다.

<a id="2-start-the-services-you-need"></a>
### 2. 필요한 서비스 시작

**Part 1–3과 7**에서는 저장소 루트의 **호스트 터미널**에서 공통 수업용
컨테이너만 시작한 뒤 3단계로 이동하세요.

```console
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml ps
```

이 명령은 공통 `docker/compose.yml`을 사용해 `course`를 백그라운드(`-d`)에서
시작하고 상태를 확인합니다. `ps` 출력에서 `course`가 실행 상태인 `Up`으로
표시되어야 합니다. `course`가 이미 실행 중이어도 `up` 명령을 실행하세요.
Compose는 필요할 때 컨테이너를 다시 생성하여 새로 빌드한 이미지나 변경된
서비스 설정을 적용합니다.

`lab02` 프로필은 `lab02-target` 서비스를 활성화합니다. 이 대상은 기본적으로
시작되지 않습니다. 아래 안내에 따라 Part 4–6에서만 시작하세요.

Part 4–6의 목표는 암호학 공격을 적용해 플래그를 복구하는 것입니다. 서버 소스
코드와 비밀 데이터를 읽으면 의도된 실습을 거치지 않고 플래그를 바로 알 수
있으므로, 해당 파일은 학생용 저장소에 포함하지 않습니다. 강사가
`lab02-target`을 미리 빌드하여 GitHub Container Registry(GHCR)에 게시합니다.
Docker Compose가 해당 이미지를 내려받아 실행하므로 학생은 대상을 로컬에서
빌드하지 않습니다.

이미지 자체는 로컬에서 조사할 수 있습니다. 이 실습에서는 이미지 안의 파일을
읽는 대신 제공된 클라이언트를 통해 플래그를 복구하세요.

대상은 다음 GHCR 이미지 이름을 사용합니다.

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

`docker/compose.yml`에는 `build` 항목 없이 이 이미지가 지정되어 있습니다.
Compose가 필요할 때 자동으로 가져오므로 수동 다운로드, `docker load`,
공개 패키지용 레지스트리 로그인은 필요하지 않습니다. Lab02 파일과 대상 이미지는
한 쌍의 **`2026-lab02-v1`** 릴리스입니다. Part 5의 암호문은 대상 이미지와
일치해야 하므로 갱신할 때도 같은 릴리스로 유지하세요.

**Part 4–6**에서는 저장소 루트의 **호스트 터미널**에서 다음 명령으로 수업용
컨테이너와 Lab02 대상을 시작하세요. Lab 01 Part 2를 완료했다면 SSH 대상을
시작할 때와 같은 Compose 절차이며, 이번에는 `lab02` 프로필과 `lab02-target`
서비스를 사용합니다.

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

첫 `up`은 대상 이미지 다운로드 때문에 더 오래 걸릴 수 있습니다. 이후 명령은
서비스가 준비될 때까지 기다립니다. `ps`에서 `lab02-target`이 `healthy`로
표시되어야 합니다. Docker Compose가 내부 네트워크를 자동으로 만듭니다.
대상은 여러분의 컴퓨터에서 실행되며 호스트에 공개하는 포트가 없습니다.
`lab02` 프로필이 추가 서비스를 활성화하며, 수업용 컨테이너는 다른 실습에서
사용하는 것과 동일합니다.

이미지를 가져올 때 `denied` 또는 `manifest unknown`이 나타나면 강사에게
해당 릴리스가 게시되었는지, GHCR 패키지가 공개되어 있는지 확인을 요청하세요.
클라이언트를 변경하거나 대상을 로컬에서 빌드할 필요는 없습니다.

<a id="3-open-the-common-course-container"></a>
### 3. 공통 수업용 컨테이너 접속

VS Code에서는 [공통 안내](../../README.md#use-vs-code-with-the-course-container)에
따라 저장소 루트를 연 상태에서 **Dev Containers: Reopen in Container**를
실행한 뒤, 해당 창에서 통합 터미널을 여세요.

터미널만 사용하는 경우 저장소 루트의 **호스트 터미널**에서 컨테이너에 접속합니다.

```console
docker compose -f docker/compose.yml exec course bash
```

이 명령은 컨테이너 셸을 엽니다. 호스트의 VS Code 창을 컨테이너에 연결하는
명령은 아닙니다.

이제 **컨테이너 안**입니다. Lab02 디렉토리로 이동하세요.

```console
cd /workspace/labs/lab02
```

저장소는 모든 실습에서 공유하는 `/workspace`에 마운트되어 있습니다.
그 안에서 파일을 변경하면 호스트 저장소에도 저장됩니다. 각 Part의 Python
명령은 이 셸에서 실행하거나, 컨테이너에 연결된 VS Code 창의 Python 실행 및
디버깅 기능을 사용하세요. Part 4–6의 클라이언트에는 로컬 서비스 이름
`lab02-target`이 이미 설정되어 있으므로 주소를 입력할 필요는 없습니다.

<a id="working-through-the-parts"></a>
## Part별 진행 방법

각 Part의 README를 순서대로 따라가세요. 먼저 해당 `samples/` 디렉토리의
독립적인 예제를 실행하고 문서에 설명된 출력을 확인합니다. 그런 다음 제공된
빈 실습 파일에 함수를 하나 구현하고 요구 사항 바로 아래의 작은 검사를
실행하세요. 검사가 통과한 뒤에만 다음 단계로 진행합니다. 개별 함수를 확인한
후에는 `main()`과 실행 가드를 작성하고 파일 입출력을 연결하여 제공된 문제를
실행합니다. 복구한 플래그, 측정값, 분석 질문의 답을 기록하세요.

실습 파일은 처음에는 0바이트입니다. import, 함수, 입력 처리, 프로그램
진입점을 직접 작성하세요. 예제는 공개된 입력으로 라이브러리와 클라이언트 사용법을
보여 주며, 실습을 구현하기 전에도 실행할 수 있습니다.

각 Part의 개별 검사와 프로그램 진입점 작성을 마쳤다면 **수업용 컨테이너 안**의
`/workspace/labs/lab02`에서 해당 명령을 실행하세요.

```console
python3 part1_des_bruteforce/des_bruteforce.py
python3 part2_double_des_mitm/double_des_mitm.py
python3 part3_aes_cbc_pkcs7/aes_cbc_pkcs7.py
python3 part4_cbc_bit_flipping/cbc_bit_flipping.py
python3 part5_padding_oracle/padding_oracle.py
python3 part6_mte_vs_etm/mte_vs_etm.py
python3 part7_aes_cpa/aes_cpa.py --all
```

Part 6 명령은 먼저 두 서비스의 동작을 탐색합니다. 해당 Part의 README에 따라
서비스를 선택하고 복구를 실행하세요. Part 7의 README에는 전체 키를 복구하기
전에 한 바이트를 먼저 복구하고 그래프를 저장하는 방법도 설명되어 있습니다.

<a id="report-and-execution-evidence"></a>
## 보고서 및 실행 증빙

채점은 보고서와 실행 스크린샷을 기준으로 합니다.

- **확인 질문:** 각 Part의 확인 질문에 답하세요.
- **구현:** 주요 코드 변경 사항을 포함하고 동작 방식을 설명하세요.
- **실행 증빙:** 명령, 관련 출력, 완료 결과를 읽을 수 있는 스크린샷을
  포함하세요. 복구한 FLAG가 보이도록 하세요.
- **측정값:** 검사한 후보 수, 소요 시간, 처리 속도, 오라클 질의 수 등 각
  Part에서 요구하는 값을 포함하세요. 제공된 입력과 요구된 방법으로 올바른
  최종 결과를 얻었다면 측정값이 강사의 참조 값과 일치할 필요는 없습니다.
- **가림 처리:** 개인정보와 비밀번호, API 토큰 등 실제 자격 증명을 가리세요.
- **불필요한 항목:** 하드웨어 사양과 컨테이너 정리 스크린샷은 제출하지 않아도
  됩니다.

이 실습에서 요구하는 합성 키도 수업 보고서에 포함할 수 있습니다. 복구한
FLAG나 키를 공개 저장소 또는 공개 보고서에 게시하지 마세요.

실제 자격 증명, 제3자의 캡처, 비공개 토큰, 제공된 수업 파일과 로컬 서비스
밖의 시스템에서 얻은 데이터는 제출하거나 사용하지 마세요. 대상 이미지의
내부를 조사하거나 복구한 FLAG 또는 키를 하드코딩하여 요구된 방법을 우회하지
마세요. 실제 비밀 노출, 허용된 수업 범위를 벗어난 작업, 의도된 실습 절차
우회는 표시된 결과가 올바르더라도 감점 사유가 될 수 있습니다.

<a id="finish-or-restart-a-session"></a>
## 세션 종료 또는 재시작

터미널만 사용하는 경우 다음 명령으로 수업용 셸에서 나갑니다.

```console
exit
```

셸에서 나가거나 Dev Containers 창을 닫아도 수업용 컨테이너와 대상은 계속
실행됩니다. 파일은 호스트 저장소에 남습니다. Part 4–6을 마쳤다면 저장소 루트의
**호스트 터미널**에서 Lab02 대상만 중지하세요.

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

수업용 컨테이너는 다른 Part와 실습을 위해 계속 사용할 수 있습니다. 다음에는
2단계의 적절한 시작 명령을 다시 실행하고 3단계처럼 셸에 접속하세요. 빌드하거나
내려받은 이미지는 컴퓨터에 남아 있습니다.

Lab02 세션을 마치고 대상, 수업용 컨테이너, 관련 네트워크를 제거하려면
**호스트 터미널**에서 다음을 실행하세요.

```console
docker compose -f docker/compose.yml --profile lab02 down
```

수업용 컨테이너에서 다른 실습을 계속하려면 위의 대상 전용 `stop` 명령을
사용하세요.

모든 실습을 마쳐 수업용 컨테이너가 더 이상 필요하지 않다면 **호스트 터미널**에서
다음 명령으로 컨테이너와 네트워크를 중지하고 제거하세요.

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 down
```

클라이언트가 연결하지 못하면 호스트 터미널에서 `ps`를 실행해 대상이 실행 중인지
확인하세요. Part 5–6 디버깅 중 질의 제한에 도달했다면 반복문을 수정한 뒤
**호스트 터미널**에서 카운터를 초기화하세요.

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

다시 시도하기 전에 `healthy` 상태가 될 때까지 기다리세요. 같은 이미지를
재시작하면 키가 유지되므로 제공된 Part 5 암호문을 계속 사용할 수 있습니다.

<a id="tests"></a>
## 테스트

수업용 컨테이너 안의 `/workspace/labs/lab02`에서 간단한 공개 검사를 실행하세요.

```console
make test
```

한 Part를 완료했다면 해당 Part의 구현 검사만 선택하세요. 예를 들어 Part 1을
완료했다면 다음을 실행합니다.

```console
make grade PART=1
```

`PART=1`부터 `PART=7`까지 사용할 수 있으며, 이후 Part를 먼저 구현할 필요는
없습니다. 일곱 Part를 모두 완료했다면 전체 구현 검사를 실행하세요.

```console
make grade
```

실습 파일이 비어 있을 때도 `make test`를 사용할 수 있습니다. 이 모드에서는
구현 검사를 건너뜁니다. `make grade`는 명확한 테스트용 값으로 Part 1–7의
구현 함수를 확인하며 실습 플래그를 공개하지 않습니다.

`tests/`의 다음 파일이 검사와 보조 코드를 제공합니다.

| 파일 | 역할 |
| --- | --- |
| [`test_des_primitives.py`](tests/test_des_primitives.py) | 공통 DES 키 생성, 홀수 패리티, 암호화·복호화, 잘못된 입력 처리를 검사합니다. |
| [`test_service_interface.py`](tests/test_service_interface.py) | 서버에 연결하지 않고 대상 서비스 이름과 포트 설정을 검사합니다. |
| [`test_exercises.py`](tests/test_exercises.py) | `make grade` 실행 시 Part 1–7에 구현한 함수를 검사합니다. |
| [`_load_impl.py`](tests/_load_impl.py) | 테스트할 Part의 학생 구현을 불러옵니다. 강사는 비공개 참조 구현을 선택할 수도 있습니다. |
| [`__init__.py`](tests/__init__.py) | `tests` 디렉토리를 Python 패키지로 만들어 보조 모듈을 import할 수 있게 합니다. |

이 검사는 공개 벡터와 합성 테스트 데이터를 사용합니다. Part 4–6의 자동 검사는
로컬 테스트 패킷과 메모리 안에서 동작하는 오라클 또는 서비스 대체물을 사용하므로
`lab02-target`을 시작하지 않아도 됩니다. 실제 Part 4–6 실습을 실행하려면
환경 준비에서 설명한 대상 컨테이너가 필요합니다.

테스트는 각 Part의 전체 명령행 프로그램을 실행하거나 문제 플래그를 검증하는
대신 개별 함수를 검사합니다. 완성한 실습은 테스트와 해당 Part의 README 안내를
함께 사용해 확인하세요. 실습을 완료하기 위해 테스트 파일을 수정할 필요는 없습니다.
