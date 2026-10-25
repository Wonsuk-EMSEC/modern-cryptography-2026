**한국어** | [English](../../en/docker/lab02-target/README.md)

# Lab02 대상 이미지

이 디렉토리에는 Lab02 Part 4–6의 추가 서비스를 위한 빌드 방법이 있습니다.
공통 학생용 환경은 `docker/Dockerfile`로 빌드합니다.
두 컨테이너 모두 `docker/compose.yml`을 통해 실행합니다.

학생은 [Lab02 환경 설정 안내](../../labs/lab02/README.md#setup)에 따라 대상을 시작합니다.
아래 고정 릴리스가 로컬에 없으면 Compose가 GitHub Container Registry(GHCR)에서
내려받습니다.

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

학생은 이 대상을 빌드하지 않습니다. 서버 소스와 비공개 대상 데이터는 교수용 저장소에만
있으므로 학생용 저장소만으로는 빌드할 수 없습니다.
수업용 이미지는 교수용 파일 없이도 빌드할 수 있습니다.

## 교수용 빌드 및 게시

비공개 저장소 루트에서 `docker/Dockerfile`로 수업용 기본 이미지를 빌드하고,
기존 Lab02 데이터가 일치하는지 검증한 다음 `docker/lab02-target/Dockerfile`로 대상을
빌드합니다.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml run --rm course \
  python3 -m instructor.lab02.generators.build_data --check
docker build -f docker/lab02-target/Dockerfile -t ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1 .
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

Dockerfile은 기존 `instructor/lab02/targets/` 디렉토리를 이미지에 복사합니다.
이 디렉토리를 공개 저장소나 학생용 소스 압축 파일에 포함하지 마세요.
일상적인 빌드 과정에서는 데이터를 다시 생성하지 않습니다. `2026-lab02-v1`의 Lab02 학생용
파일과 같은 릴리스 태그의 이미지를 함께 사용하세요. Part 5의 암호문은 대상의 대응 데이터에
의존합니다. 데이터가 변경되면 새 릴리스 태그를 정하고 Compose와 학생용 파일을 함께
갱신합니다. 게시된 버전 태그를 변경된 데이터로 덮어쓰지 말고, Lab02 대상에는 `latest`를
사용하지 마세요.

로컬 검증을 마친 뒤 `wonsuk-emsec` 아래에 게시 권한이 있는 GitHub 계정으로 인증합니다.
비밀번호 입력란에는 `write:packages` 권한을 가진 개인용 액세스 토큰(classic)을 입력합니다.

```console
docker login ghcr.io
docker push ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

학생이 익명으로 내려받을 수 있도록 **Public** 패키지를 권장합니다. 첫 push는 보통 비공개
패키지를 생성합니다. push 후 GitHub 패키지 페이지에서
**Package settings → Change visibility → Public**을 엽니다. 저장소가 이미 공개되어 있어도
이 설정은 대개 수동으로 변경해야 합니다.
[GitHub 패키지 공개 범위 안내](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)를 참고하세요.

비공개 패키지를 사용한다면 학생에게 읽기 권한을 부여하고, 각자 `read:packages` 권한의
개인용 액세스 토큰(classic)으로 `docker login ghcr.io`를 실행하게 합니다.
계정 자체에도 해당 패키지 권한이 있어야 합니다.
[GitHub Container registry 인증 안내](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic)를 참고하세요.

GHCR 인증 정보가 없는 깨끗한 Docker 클라이언트에서 명시적으로 pull하여 익명 접근을
검증합니다.

```console
docker pull ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

캐시된 로컬 빌드를 실행하는 것은 컨테이너 동작만 검증합니다. 게시 여부나 공개 pull 접근은
검증하지 않습니다. 단일 플랫폼 빌드 역시 모든 학생 CPU 아키텍처와의 호환성을 보장하지
않습니다. 배포 전에 지원할 각 플랫폼을 테스트하세요. 여러 플랫폼을 지원하는 릴리스에는
플랫폼별 수업용 기본 이미지와 하나의 릴리스 매니페스트가 필요합니다.

교수용 `scripts/build_student_release.sh OUTPUT_DIRECTORY`는 소스 압축 파일만 생성합니다.
대응하는 대상 이미지는 GHCR에서 제공합니다.
로컬 검증을 마치면 호스트 터미널에서 정리합니다.

```console
docker compose -f docker/compose.yml --profile lab02 down
```
