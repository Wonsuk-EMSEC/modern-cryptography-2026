# 현대 암호 응용 2026

**한국어** | [English](en/README.md)

암호 기술을 직접 구현하고 실험하는 실습 중심의 강의 저장소입니다.

## 실습 윤리와 허용 범위

보안 실습은 제공된 합성 데이터, 로컬 컨테이너, 명시적으로 허가받은
교수자 관리 시스템에서만 수행합니다. 실제 계정 정보, 공개 서비스,
제3자의 네트워크를 대상으로 실험하지 마세요. 실습별 제한 사항은 각
실습의 README에 안내되어 있습니다.

## 저장소 구조

- `docker/`: Docker 기반 공통 실습 환경
- `labs/`: 한국어 실습 안내와 공통 코드·데이터
- `en/`: 동일한 구조의 영어 안내 문서
- `instructor/`: 교수자용 자료

실습 안내: [Lab 01](labs/lab01/README.md) · [Lab 02](labs/lab02/README.md)

한국어와 영어 문서는 같은 실습 코드, 데이터, Docker 환경을 사용합니다.
영어 문서를 읽더라도 실행 경로는 `/workspace/labs/...`입니다.
문서를 수정할 때의 번역·동기화 절차는 [기여 안내](CONTRIBUTING.md)를 참고하세요.

## 실행 환경

모든 실습은 제공된 Docker 환경 안에서 실행합니다.

## Docker 환경

강의 Docker 이미지에는 실습에 사용하는 프로그램과 라이브러리가 포함되어
있습니다. 작업 파일은 이 Git 저장소에 보관하고, 실행은 Docker 환경에서
진행합니다.

모든 실습은 공통 `docker/Dockerfile`과 `docker/compose.yml`의 `course`
서비스를 사용합니다. 추가 서버가 필요한 Part는 `docker/` 아래의
`lab01-ssh-target/`, `lab02-target/` 같은 디렉토리에 있는 대상 서버용
Dockerfile을 사용합니다. 해당 Part에서 요구할 때만 추가 서비스를 시작하세요.
자세한 내용은 [Docker 구조와 서비스 명령](docker/README.md)을 참고하세요.
Lab02의 대상 서버 이미지는 교수자가 제공하며 Compose가 공개 GHCR에서
자동으로 내려받습니다. 서버 구현과 비밀 데이터는 학생용 소스 배포본에서는
제외되지만, 로컬에서 확인할 수 있는 실행 이미지에는 포함되어 있습니다.

<a id="0-prerequisites"></a>

### 0. 사전 준비

실습을 시작하기 전에 다음 프로그램을 설치하세요.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- Windows 사용자는 WSL2와 Ubuntu가 필요합니다.
- [Visual Studio Code](https://code.visualstudio.com/)는 선택 사항입니다.
  강의 컨테이너 안에서 편집·실행·디버깅하려면
  [VS Code에서 강의 컨테이너 사용하기](#use-vs-code-with-the-course-container)를
  참고하세요.

Windows에서는 저장소를 복제하기 전에 PowerShell에서 Ubuntu로 들어가세요.

```powershell
wsl -d Ubuntu
```

이후 Git과 Docker 명령은 Ubuntu 안에서 실행합니다. Docker Desktop의 WSL
통합 설정에서 Ubuntu가 활성화되어 있어야 합니다. macOS와 Linux에서는
터미널에서 바로 실행하면 됩니다.

<a id="1-clone-the-course-repository"></a>

### 1. 강의 저장소 복제

강의 파일을 보관할 디렉토리에서 터미널을 열고 저장소를 복제한 뒤,
저장소 루트 디렉토리로 이동하세요.

```console
git clone https://github.com/Wonsuk-EMSEC/modern-cryptography-2026.git
cd modern-cryptography-2026
```

이후 명령은 별도 안내가 없는 한 저장소 루트 디렉토리에서 실행합니다.

### 2. 강의 Docker 이미지 빌드

```console
docker compose -f docker/compose.yml build course
```

이 명령은 `modern-cryptography-2026` 이미지를 빌드하고 강의에 필요한
프로그램과 라이브러리를 설치합니다. 처음 빌드할 때는 몇 분이 걸릴 수 있습니다.

### 3. 강의 컨테이너를 백그라운드에서 시작

`course` 서비스를 백그라운드 모드로 시작하세요.

```console
docker compose -f docker/compose.yml up -d course
```

`course`는 Docker Compose 서비스 이름이며, `-d` 옵션은 컨테이너를
백그라운드에서 실행한다는 뜻입니다.

실행 상태는 다음 명령으로 확인할 수 있습니다.

```console
docker compose -f docker/compose.yml ps
```

실행 중인 강의 컨테이너의 대화형 셸로 들어가려면 다음 명령을 실행하세요.

```console
docker compose -f docker/compose.yml exec course bash
```

Git 저장소는 컨테이너의 `/workspace`에 마운트됩니다. 이 경로 아래에서
파일을 생성하거나 수정하면 호스트 컴퓨터의 저장소에도 반영됩니다.

대화형 셸에서 나갈 때는 다음 명령을 실행하세요.

```console
exit
```

강의 컨테이너는 백그라운드에서 실행 중이므로 셸에서 나가도 중지되지 않습니다.
다음 명령으로 언제든 다시 들어갈 수 있습니다.

```console
docker compose -f docker/compose.yml exec course bash
```

모든 실습을 마친 뒤에는 다음 명령으로 강의 컨테이너, 선택적으로 실행한
대상 서버, 관련 네트워크를 중지하고 제거하세요.

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 down
```

### 4. 환경 확인

강의 컨테이너의 셸에 들어간 뒤 다음 명령을 실행하세요.

```console
whoami
pwd
python3 --version
python3 -c "import sys; print(sys.executable)"
gcc --version
openssl version
```

출력 예시는 다음과 같습니다.

```text
student
/workspace
Python 3.12.3
/opt/course-venv/bin/python3
gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
OpenSSL 3.0.13 30 Jan 2024
```

사용자는 `student`, 작업 디렉토리는 `/workspace`여야 합니다. Python 실행
파일은 강의 공통 라이브러리를 설치한 `/opt/course-venv/bin/python3`여야 합니다.

위 버전 번호는 예시이며 이미지가 갱신되면 달라질 수 있습니다. 각 명령이
정상적으로 실행되고 버전 정보가 출력되는지 확인하세요.

<a id="use-vs-code-with-the-course-container"></a>

### VS Code에서 강의 컨테이너 사용하기

VS Code에서도 강의 터미널과 같은 환경에서 Python 파일을 편집·실행·디버깅할
수 있습니다. 먼저 1~3단계를 완료한 뒤 다음 절차를 따르세요.

1. VS Code에 Microsoft의 **Dev Containers** 확장
   (`ms-vscode-remote.remote-containers`)을 설치하세요.
2. 개별 Part 디렉토리가 아닌 `.devcontainer/`, `docker/`, `labs/`가 있는
   **저장소 루트**를 여세요. Windows에서는 Ubuntu/WSL에서 `code .`으로 엽니다.
3. 명령 팔레트(`Ctrl+Shift+P`, macOS는 `Cmd+Shift+P`)에서
   **Dev Containers: Reopen in Container**를 실행하세요. VS Code가
   `.devcontainer/devcontainer.json`을 읽고 기존 `docker/compose.yml`의
   `course` 서비스에 연결합니다. 처음 연결할 때는 VS Code 서버와 Python
   확장을 설치하므로 몇 분이 걸릴 수 있습니다.
4. 왼쪽 아래 상태 표시가 **Dev Container**이고 탐색기에 `/workspace`가
   열려 있는지 확인하세요. Lab01과 Lab02 모두 이 작업 공간에서 진행하고,
   탐색기를 통해 파일을 여세요.
5. 연결된 창에서 **Terminal → New Terminal**을 열고 확인하세요.

   ```console
   python3 -c "import sys; print(sys.executable)"
   python3 -c "import Crypto, numpy, matplotlib; print('Course Python imports: OK')"
   ```

   실행 파일은 `/opt/course-venv/bin/python3`여야 합니다. 저장소 설정이 이
   인터프리터를 기본값으로 지정하고, 같은 환경의 경로를 VS Code 터미널의
   `PATH` 앞에 둡니다.

처음 확인할 때는 `labs/lab02/part1_des_bruteforce/samples/des_roundtrip.py`를
열고 명령 팔레트에서 **Python: Run Python File in Terminal**을 선택하세요.
`Padding round-trip check: OK`가 출력되어야 합니다. 예제 실행에는 Python
확장의 실행 명령을 사용하고, 디버깅에는 **Python Debugger: Debug Python File**을
사용하세요. 인자가 필요한 실습 명령은 통합 터미널에서 실행하며, 각 Part가
안내하는 작업 디렉토리를 사용합니다.

기본 인터프리터는 공통 작업 공간 전체에 적용됩니다. 파일이나 실습마다 Python을
다시 선택할 필요가 없습니다. 목록에 Ubuntu의 시스템 Python이 보일 수도 있지만,
강의 라이브러리는 `/opt/course-venv`에 설치되어 있습니다.

VS Code에 다른 인터프리터 선택이 이미 저장되어 있다면 연결된 컨테이너 창에서
한 번 수정하세요.

1. **Python: Select Interpreter**를 실행합니다.
2. **Enter interpreter path...**를 선택하고 `/opt/course-venv/bin/python3`를
   입력합니다.
3. 기존 통합 터미널을 닫고 새로 연 뒤 위 확인 명령을 다시 실행합니다.
   Python 파일을 열면 상태 표시줄에도 선택한 인터프리터가 표시됩니다.

VS Code는 새 기본값보다 기존의 명시적인 선택을 우선할 수 있습니다.
자세한 내용은 [Python 설정 안내](https://code.visualstudio.com/docs/python/settings-reference)를
참고하세요. 강의에서 안내하는 연결 방식은 **Reopen in Container**입니다.
`docker compose ... exec course bash`는 터미널 셸만 열며 편집기를 연결하지 않습니다.

Docker 빌드, 대상 서버 시작, 종료 명령은 별도의 **호스트 터미널**에서
실행하세요. 연결된 VS Code 터미널은 이미 컨테이너 안에 있습니다.
Dev Containers 설정은 `course`만 시작하므로, 추가 대상 서버는 해당 Part에서
필요할 때 따로 시작합니다. VS Code 창을 닫아도 강의 컨테이너는 계속 실행됩니다.
`.devcontainer/devcontainer.json`을 수정했다면
**Dev Containers: Rebuild Container**로 변경 사항을 적용하세요.

### 5. 실습 실행

예를 들어 Lab01을 열려면 다음 명령을 실행하세요.

```console
cd /workspace/labs/lab01
ls
```

추가 준비, 과제, 테스트 절차는 각 실습의 `README.md`를 참고하세요.

Lab01 테스트는 다음과 같이 실행합니다.

```console
cd /workspace/labs/lab01
pytest -q
```

### 6. 컨테이너 셸에서 나가기

```console
exit
```

셸만 종료되며 강의 컨테이너는 계속 실행됩니다. `/workspace` 아래의 파일은
호스트 Git 저장소에 유지됩니다. 모든 컨테이너 사용을 마쳤다면 3단계의
종료 명령을 실행하세요.

### 7. 환경 다시 빌드하기

`docker/Dockerfile`이 변경되었다면 이미지를 다시 빌드하세요.

```console
docker compose -f docker/compose.yml build course
```

문제를 해결하기 위해 모든 계층을 새로 빌드해야 한다면 다음 명령을 사용합니다.

```console
docker compose -f docker/compose.yml build --no-cache course
```

`--no-cache` 옵션은 보통 필요하지 않으며 빌드 시간이 늘어납니다.
빌드 후 `docker compose -f docker/compose.yml up -d course`를 실행해
갱신된 이미지로 강의 컨테이너를 다시 생성하세요.

### 8. JupyterLab 실행하기 (선택 사항)

JupyterLab은 강의 이미지에 포함되어 있습니다. 저장소 루트에서 다음 명령으로
공통 강의 컨테이너 안에 실행하세요.

```console
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course \
  jupyter lab --ip=0.0.0.0 --no-browser
```

`docker/compose.yml` 설정에 따라 강의 컨테이너의 8888번 포트가 호스트에
공개됩니다. JupyterLab이 출력한 URL을 접근 토큰까지 포함해 브라우저에서
여세요. 터미널에서 `Ctrl+C`를 누르면 JupyterLab이 종료되며 강의 컨테이너는
계속 실행됩니다.

### 9. 유의 사항

- 실습이나 교수자의 명시적인 안내가 없으면 `apt`나 `pip`로 강의 의존성을
  직접 설치하지 마세요. 필요한 의존성은 Docker 이미지에 포함되어야 합니다.
- 중요한 강의 파일은 `/workspace` 아래에 저장하세요. 컨테이너의 다른 경로에
  둔 파일은 컨테이너를 삭제하거나 다시 생성할 때 사라집니다.
- 일반적으로 호스트 Git 저장소에서 파일을 편집하고 Docker에서 실행·테스트합니다.
