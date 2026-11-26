# Part 05: MD5 충돌쌍 찾기

**한국어** | [English](../../../en/labs/lab04/part05/README.md)

서로 다른 인증서 본문이 같은 MD5 해시를 가질 수 있을까요? 제공된 바이너리 표본에서 실제 충돌쌍을 찾아 비교합니다. 이 Part는 충돌을 새로 계산하는 과제가 아닙니다. 다음 Part에서 그 충돌이 인증서 서명에 어떤 영향을 주는지 확인합니다.

## 학습 목표

1. 서로 다른 바이트열의 MD5 해시가 같아도 내용이 같다고 결론 내릴 수 없는 이유를 설명합니다.
2. 같은 두 바이트열의 SHA-256 해시도 비교합니다.
3. 인증서의 서명 대상인 `TBSCertificate`와 전체 인증서를 구분합니다.

## 제공 자료

| 경로 | 내용 |
| --- | --- |
| [find_collision.py](find_collision.py) | 구현할 `find_collision(samples)`와 실행 가능한 실습 코드 |
| [data/](data/) | 바이너리 표본 12개. 이 중 한 쌍은 역사적 X.509 인증서의 서로 다른 `TBSCertificate`입니다. |
| [test_part05_materials.py](test_part05_materials.py) | 표본 구성만 확인하는 공개 검사 |

이 Part를 완료하려면 `find_collision.py`의 미완성 `find_collision()`을 직접 구현해야 합니다.

## 수행 과제

1. `find_collision.py`의 `find_collision(samples)`를 구현하세요. 각 `Path`의 파일을 읽고, **파일 내용이 서로 다르면서 MD5 값이 같은** 두 경로를 반환합니다. 입력 순서나 파일명으로 답을 정하지 마세요.
2. 완성한 프로그램을 실행해 두 파일의 MD5와 SHA-256을 비교하세요. 출력된 `LAB04{...}`는 이 Part의 완료 표식입니다.
3. 바이너리 표본이 인증서 전체가 아닌 서명 대상 본문이라는 점을 확인하고, 왜 서명 검증에서 해시 충돌이 중요한지 기록하세요.

## 1. 제공된 표본과 실행 환경 준비하기

[Lab04 공통 준비](../README.md)를 마쳤다면 **기존 course 터미널의 `/workspace`**에서
진행하세요. `part05/data/`에 제공된 표본 12개를 사용합니다.
이 Part는 로컬 파일만 읽으므로 CA·프록시 접속이나 별도 패키지 설치는 필요하지 않습니다.

## 2. 코드로 충돌쌍 찾기

`find_collision.py`의 `find_collision()` TODO를 완성한 뒤 실행합니다.

```console
cd /workspace
python3 labs/lab04/part05/find_collision.py
python3 labs/lab04/part05/test_part05_materials.py
```

TODO가 남아 있으면 첫 번째 명령은 `NotImplementedError`로 끝납니다. 공개 검사는 **자료의 구성만** 확인하므로 TODO가 남아 있어도 통과할 수 있습니다.

### TODO 완료 후 확인할 결과

- `find_collision.py`는 찾은 두 파일명과 MD5·SHA-256 해시, 완료 표식을 출력합니다.
  실제 파일명과 해시값은 직접 실행한 결과에서 확인하세요.

  ```text
  files: <첫 번째 파일명> <두 번째 파일명>
  MD5: <두 파일에 공통인 해시>
  SHA-256 #1: <첫 번째 파일의 해시>
  SHA-256 #2: <두 번째 파일의 해시>
  LAB04{...}
  ```

  `files:`에는 **서로 다른 내용의 두 파일**이 나와야 합니다. 두 파일의 MD5는
  같고 SHA-256은 달라야 합니다. 이 조건이 틀리면 완료 표식 출력 전에 오류가 발생합니다.

- `test_part05_materials.py`는 표본 파일의 개수와 구성을 확인한 뒤 다음과 같이 출력합니다.
  실행 시간은 환경에 따라 달라집니다.

  ```text
  .
  ----------------------------------------------------------------------
  Ran 1 test in <실행 시간>s

  OK
  ```

  이 `OK`는 자료 검사 통과를 뜻합니다. **충돌쌍을 찾는 TODO의 정답 여부는 검사하지 않습니다.**

## Checkpoint Questions

1. 두 파일의 MD5가 같고 SHA-256이 다르다는 결과는 무엇을 보여주나요?
2. 인증서 서명은 인증서 전체의 어떤 부분에 적용되나요?
3. 임의의 두 파일 사이에서 충돌을 찾는 일과, 먼저 정한 서로 다른 내용을 가진 두 파일을 충돌시키는 일은 어떻게 다른가요?

## 자료 출처

충돌쌍의 인증서 본문은 Marc Stevens 등 연구진이 공개한 [역사적 위조 CA 인증서 실험](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html)의 인증서에서 추출했습니다. 나머지 표본은 이 실습을 위해 생성했습니다. 실제 인증서와 위조 CA의 역할 비교는 [Part 06](../part06/README.md)에서 이어집니다.
