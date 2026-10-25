**한국어** | [English](../../en/docker/lab01-ssh-target/README.md)

# Lab01 SSH 대상 이미지

이 디렉토리에는 Lab01 Part 2의 추가 SSH 서비스를 위한 빌드 파일이 있습니다.
공통 학생용 환경은 `docker/Dockerfile`로 빌드합니다.
두 컨테이너 모두 `docker/compose.yml`을 통해 실행합니다.

- `Dockerfile`은 SSH 서버를 설치하고 시작합니다.
- `sshd_config`는 격리된 수업용 서비스를 설정합니다.

학생은 제공된 파일로 이 대상을 빌드할 수 있습니다.
호스트 터미널의 저장소 루트에서 다음 명령을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh build course lab01-ssh-target
docker compose -f docker/compose.yml --profile lab01-ssh up -d --wait course lab01-ssh-target
docker compose -f docker/compose.yml exec course bash
```

수업용 셸 안에서 Part 디렉토리로 이동합니다.

```console
cd /workspace/labs/lab01/part2_dictionary_attack
```

[Part 2 안내](../../labs/lab01/part2_dictionary_attack/README.md)에 따라 실습을 진행합니다.
클라이언트는 내부 Docker 네트워크를 통해 `lab01-ssh-target`의 22번 포트에 연결합니다.
대상은 호스트 포트를 공개하지 않습니다.

`exit`로 셸에서 나온 뒤 호스트에서 SSH 대상만 중지합니다.

```console
docker compose -f docker/compose.yml --profile lab01-ssh stop lab01-ssh-target
```

공용 수업 컨테이너와 다른 실습 대상은 계속 사용할 수 있습니다.
모든 실습 서비스를 종료하는 방법은 [공통 Docker 안내](../README.md)를 참고하세요.
