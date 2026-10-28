**한국어** | [English](../en/docker/README.md)

# 수업용 Docker 환경

모든 실습은 하나의 학생용 환경을 사용합니다. `docker/Dockerfile`이
`modern-cryptography-2026` 이미지를 빌드하고, `docker/compose.yml`이 이를 `course`로
실행합니다. 실습에 필요한 프로그래밍 도구와 Python 의존성은 이 Dockerfile에서 관리합니다.
별도 서버가 필요한 Part는 자체 하위 디렉토리에 대상용 Dockerfile을 추가하고,
동일한 Compose 파일에 서비스를 등록합니다.

```text
docker/
├── Dockerfile                    # Shared environment for every lab
├── compose.yml                   # Course container and optional targets
├── lab01-ssh-target/
│   ├── Dockerfile                # Lab01 Part 2 SSH server
│   ├── README.md
│   └── sshd_config
├── lab02-target/
    ├── Dockerfile                # Lab02 Parts 4–6 server; staff build
    └── README.md
└── lab03-target/
    ├── Dockerfile                # Lab03 Parts 06/08 server; staff build
    └── README.md
```

## 한 번 빌드하여 모든 실습에서 사용하기

호스트 터미널의 저장소 루트에서 Docker 명령을 실행합니다.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course bash
```

셸 안에서 실습을 선택합니다. 예를 들어 `cd /workspace/labs/lab02`를 실행합니다.
저장소가 `/workspace`에 마운트되므로 수정 사항은 호스트에 저장됩니다.
`exit`로 셸에서 나와도 `course`는 다음 작업을 위해 계속 실행됩니다.
공통 Dockerfile이 변경되면 이미지를 다시 빌드한 뒤 `up -d course`를 다시 실행하여
갱신된 이미지를 적용합니다.

## VS Code를 수업용 컨테이너에 연결하기

[공통 VS Code 안내](../README.md#use-vs-code-with-the-course-container)에 따라
**저장소 루트**를 열고 **Dev Containers: Reopen in Container**를 실행합니다.
저장소의 `.devcontainer/devcontainer.json`은 동일한 `course` 서비스와 `/workspace`
마운트를 사용합니다. 컨테이너에 Python 확장을 설치하고 기본 인터프리터를
`/opt/course-venv/bin/python3`로 설정합니다. 모든 실습의 편집, Python 실행·디버깅,
통합 터미널 작업은 이 연결된 창에서 진행하세요. VS Code에 다른 인터프리터가 이미 저장되어
있다면 공통 안내에 따라 한 번 수정합니다.

`docker compose ... exec course bash`는 셸만 엽니다. 호스트의 VS Code 창을 컨테이너에
연결하지는 않습니다. Dev Containers는 `course`만 시작합니다. 선택적인 대상 서비스는
아래와 같이 **호스트 터미널**에서 별도로 시작하세요.
VS Code 창을 닫아도 공용 수업 컨테이너는 계속 실행됩니다.

## 필요할 때만 추가 서비스 시작하기

대상 서비스는 Compose 프로필을 사용하므로 기본 수업 컨테이너 명령으로는 시작되지 않습니다.
호스트에서 동일한 Compose 파일을 사용해 다음 명령을 실행합니다.

Lab01 Part 2에서는 제공된 SSH 서버를 빌드하고 시작합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh up -d --build --wait lab01-ssh-target
```

대상의 빌드 파일, 수업용 셸 진입, 종료 명령은
[lab01-ssh-target/README.md](lab01-ssh-target/README.md)를 참고하세요.

Lab02 Part 4–6에서는 공용 수업 컨테이너와 미리 빌드된 대상을 시작합니다.

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

필요하면 Compose가 공개 GHCR 이미지
`ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1`을 자동으로
내려받습니다. 처음 `up`을 실행할 때는 이미지 다운로드로 시간이 더 걸릴 수 있습니다.
수동 이미지 다운로드나 레지스트리 로그인은 필요하지 않습니다. 학생은 이 대상을 로컬에서
빌드하지 않습니다. Lab02 파일과 이미지는 같은 **`2026-lab02-v1`** 릴리스를 사용하세요.
Part 5의 암호문은 대상 이미지와 일치해야 합니다. `ps`에서 대상이 `healthy`로 표시되어야 합니다.

같은 `course` 셸로 두 실습을 모두 실행합니다. 각 대상에 서비스 이름으로 접근할 수 있습니다.
각 대상은 자체 내부 네트워크에 있으며 호스트 포트를 공개하지 않습니다.
서버 실행 데이터는 해당 대상 컨테이너에 저장됩니다.

Lab02 대상의 빌드 방법은 공개되어 있지만 Python 서버와 비밀 데이터는 학생용 소스 배포에서
제외됩니다. 이미지에는 실행에 필요한 비공개 구현과 비밀값이 포함되어 있으며,
이미지에 로컬 접근 권한이 있는 사람은 이를 살펴볼 수 있습니다.
실습은 제공된 클라이언트를 통해 해결하세요. 교직원의 이미지 게시 절차는
[lab02-target/README.md](lab02-target/README.md)를 참고하세요.

수업용 셸과 Lab01 서버를 유지하면서 Lab02 대상만 중지하려면 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

Lab02 작업을 마치고 대상, 수업 컨테이너와 해당 네트워크를 제거하려면 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab02 down
```

다른 실습을 위해 수업 컨테이너를 유지하려면 위의 대상 전용 `stop` 명령을 사용합니다.

**모든** 실습을 마쳤다면 수업 컨테이너, 세 대상과 해당 네트워크를 제거합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 --profile lab03 down
```

## Lab03 대상

Part06과 Part08은 같은 `course` 셸에서 `lab03-target:8080`에 접근합니다.
`lab03` 프로필은 별도 내부 네트워크를 사용하며 호스트 포트를 공개하지 않습니다.
공통 Dockerfile의 기존 의존성으로 실행하므로 추가 설치는 필요 없습니다.

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml --profile lab03 logs --tail 30 lab03-target
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
```

`ps`에서 대상이 `healthy`인지 확인하세요. 강의 이미지와 대상은
[Lab03 빌드 안내](lab03-target/README.md)에 따라 교수자가 먼저 검증합니다.
대상 이미지는 GHCR의 `2026-lab03-v1` 태그를 사용하며, 게시 여부는 별도 확인해야
합니다. 로컬 대상은 연습용입니다. 실제 평가용 비밀은 교수자 관리 서버에서 사용하고,
학생 클라이언트는 `LAB03_TARGET_URL`로 관리 서버에 연결할 수 있습니다.

## 이후 실습 추가하기

1. 학생에게 필요한 도구나 라이브러리를 공통 `Dockerfile`에 추가합니다.
2. Part에 서버가 필요하면 `labXX-target/Dockerfile`과 비밀이 아닌 필수 빌드 파일을
   추가합니다. 비공개 소스와 값은 `instructor/` 아래에 유지합니다.
3. `compose.yml`에 선택적인 대상 서비스와 내부 네트워크를 추가하고 `course`를 그
   네트워크에 연결합니다. 학생이 빌드할 수 있는 대상에는 `build:`를, 미리 빌드된 이미지로
   제공하는 대상에는 `image:`를 사용합니다.
4. Part README에 대상 시작 및 종료 방법을 설명합니다. 공통 이미지에서 새 실습과
   기존 실습을 모두 검증합니다.
