# Lab03 대상 이미지

**한국어** | [English](../../en/docker/lab03-target/README.md)

Part06·08은 공통 `course` 컨테이너에서 HTTP로 접근하는 대상 하나를 사용합니다.
`lab03` 프로필의 대상은 `lab03-internal` 네트워크에서만 접근할 수 있으며
호스트 포트는 공개하지 않습니다. 공개 배포 태그는 다음과 같습니다.

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1
```

학생 배포본에는 서버 소스가 없으므로 학생이 대상을 빌드하지 않습니다.
교수자가 이미지를 빌드하고 검증한 뒤 게시해야 합니다. 저장소 파일을 추가하는 것만으로
해당 태그가 게시되지는 않습니다. `manifest unknown`이면 교수자에게 게시 상태를 확인하거나
제공된 관리 서버 주소를 사용하세요.

## 교수용 빌드와 검증

비공개 교수용 저장소의 호스트 터미널에서 실행합니다.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml run --rm course python3 -m instructor.lab03.generators.build_data --check
docker build -f docker/lab03-target/Dockerfile -t ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1 .
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml --profile lab03 logs --tail 30 lab03-target
docker compose -f docker/compose.yml exec course python3 -m instructor.lab03.solve_all --url http://lab03-target:8080
```

검증 기준은 대상의 `healthy` 상태와 여덟 Part의 `PASS` 결과입니다.
이 작업 환경에서는 Docker가 없어 위 컨테이너 검증은 실행하지 못했습니다.
실행한 호스트 검증과 남은 항목은 교수용 `instructor/lab03/TEST_REPORT.md`에 기록합니다.

빌드한 이미지에는 서버 구현만 복사하며 평가용 개인 키나 플래그를 넣지 않습니다.
기본 실행은 Part별 독립된 RSA-2048 연습 키와 연습 플래그를 메모리에서 새로 만듭니다.
대상을 재시작하면 키·세션·플래그가 바뀝니다. 학생이 Docker를 제어하면 이미지와
프로세스 메모리를 조사할 수 있으므로 로컬 연습 비밀은 평가용 비밀이 아닙니다.

## 교수자 관리 서버

교수자는 학생에게 접근 권한이 없는 호스트에서 비공개 설정을 생성하고,
서버의 `--config /PRIVATE/PATH/config.json` 또는 `LAB03_TARGET_CONFIG`로 읽습니다.
설정 생성기는 `python3 -m instructor.lab03.generators.part06_08 --help`로 확인합니다.
평가에는 비공개 고엔트로피 seed와 서로 다른 두 플래그를 사용하고 설정 파일을
학생 배포나 이미지에 포함하지 마세요. 재현을 위해 같은 비공개 seed를 보관합니다.
Part별 키·세션·완료 조건은 분리되어 있습니다.

컨테이너 배포에서는 비공개 파일을 읽기 전용으로 마운트하고 `LAB03_TARGET_CONFIG`에
컨테이너 내 경로를 설정합니다. 파일은 컨테이너의 `student` UID가 읽을 수 있어야 합니다.
평가용 서버는 학생이 제어하는 Docker에서 실행하지 마세요. 외부 접근이 필요하면
교수자가 별도 배포 설정으로 HTTPS와 수업 접근 제어를 제공합니다. 기본 Compose의
내부 네트워크 설정은 로컬 연습용입니다. 학생은 `LAB03_TARGET_URL`로 연결합니다.

## 게시와 종료

위 검증을 완료한 뒤 게시 권한이 있는 계정으로 별도 게시합니다.

```console
docker login ghcr.io
docker push ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1
```

게시 후 공개 접근 권한과 지원 CPU 플랫폼을 별도로 검증하세요. 이미 게시한 태그를
다른 내용으로 덮어쓰지 말고 변경 시 새 버전으로 배포합니다. 로컬 실행 성공은
레지스트리 공개 pull 성공을 의미하지 않습니다.

```console
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
docker compose -f docker/compose.yml --profile lab03 down
```

첫 명령은 대상만 중지하고 두 번째 명령은 이 Compose 프로젝트를 정리합니다.
