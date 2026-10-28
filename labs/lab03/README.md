# Lab03: 공개키 암호 — CTF 실습

**한국어** | [English](../../en/labs/lab03/README.md)

## 학습 목표

공개키 암호의 수학적 연산을 구현하고 성능을 측정합니다. 취약한 난수 생성,
작은 RSA 매개변수, 교과서 RSA의 가변성, 서명 검증 오류와 CRT 결함을 실험한 뒤
안전한 API 사용 및 대응책을 검증합니다. 정확히 아래 여덟 Part를 수행합니다.

| Part | 주제 | 완료 목표 |
|---|---|---|
| [Part01](part01/README.md) | Modular Exponentiation and Primality Testing | 구현·성능·128비트 합성수 검증 |
| [Part02](part02/README.md) | Predictable Key Recovery and Secure Random Generation | PDF 복구와 RNG 오류 처리 |
| [Part03](part03/README.md) | RSA Key Generation, Encryption, and CRT | C BIGNUM RSA와 CRT 최적화 |
| [Part04](part04/README.md) | RSA Factorization Attack | 약한 모듈러스 인수분해 및 복호화 |
| [Part05](part05/README.md) | RSA Low Public Exponent Attack | 정확한 정수 세제곱근과 공격 조건 |
| [Part06](part06/README.md) | Textbook RSA Malleability and RSA-OAEP | 서버 공격과 OAEP 비교 |
| [Part07](part07/README.md) | RSA-PSS Signatures and Secure Verification | 정상 서명 수락과 오류 시 거부 |
| [Part08](part08/README.md) | RSA-CRT Fault Attack | 새 메시지 서명과 결과 검증 대응책 |

## 챌린지 시나리오

각 Part는 독립된 장치나 서비스를 감사하는 CTF입니다. 구현 문제는 올바른 결과뿐
아니라 지정된 연산과 성능 조건을 만족해야 합니다. 공격 문제는 제공된 공개 데이터와
명시적으로 허가된 실습 대상만 사용합니다.

## 제공 자료

각 `partNN/`에는 `README.md`, `starter/`, `data/`, `tests/`가 있습니다.
문서는 한국어·영어로 제공되며 코드와 데이터는 공통입니다.
교수용 해답, 생성기와 평가 자료는 학생 배포본에 포함되지 않습니다.
보고서 양식은 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md)입니다.

## 과제

각 Part의 TODO를 구현하고 공개 검사와 분석 질문을 수행하세요. Python 실험에는
Python 3, C 구현에는 GCC와 OpenSSL을 사용합니다. 코드, 재현 가능한 측정 결과,
공격 증거와 대응책 검증을 제출합니다. 공개 검사는 로컬 피드백이며 최종 점수가 아닙니다.

<a id="setup"></a>

## 실행 방법

[공통 환경 안내](../../docker/README.md)를 따라 호스트의 저장소 루트에서 실행합니다.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course bash
```

컨테이너 안에서 환경을 확인합니다. 추가 `pip install`이나 `apt install`은 필요 없습니다.

```console
cd /workspace
python3 -c "import Crypto, cryptography; print('Lab03 Python imports: OK')"
gcc --version
openssl version
make -C labs/lab03 test
```

첫 명령의 예상 출력은 `Lab03 Python imports: OK`이며 도구 버전은 환경에 따라
다릅니다. `make test`는 자료와 도구 검사입니다. 과제 완료 여부는 확인하지 않습니다.

Part06과 Part08은 호스트에서 추가 대상을 시작합니다.

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml --profile lab03 logs --tail 30 lab03-target
```

`ps`의 대상 상태는 `healthy`여야 합니다. 이미지는
`ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1`을 사용합니다.
교수자가 이 버전을 빌드·검증·게시한 뒤 사용할 수 있습니다. 이 소스 작업만으로
레지스트리 게시나 익명 pull이 완료되지는 않습니다. `manifest unknown`이면 교수자가
안내한 이미지 게시 상태 또는 관리 서버 주소를 확인하세요.

교수자 관리 서버를 사용하는 경우, 컨테이너 안에서 제공받은 주소를 설정합니다.

```console
export LAB03_TARGET_URL=https://INSTRUCTOR-PROVIDED-HOST
```

위 주소는 예시이며 실제 주소로 바꾸세요. 기본 주소는 `http://lab03-target:8080`입니다.
대상은 기본적으로 호스트 포트를 공개하지 않습니다. 서버 상태를 확인하려면:

```console
python3 -c "from labs.lab03.common.service_client import TargetClient; print(TargetClient().request('GET', '/health'))"
```

정확한 응답 스키마와 Part별 클라이언트 명령은 각 Part 안내를 참고하세요.
과제를 구현한 뒤 저장소 루트에서 Part별 검사 명령을 실행합니다.

```console
python3 -m labs.lab03.check --part 1
python3 -m labs.lab03.check --part 2
python3 -m labs.lab03.check --part 3
python3 -m labs.lab03.check --part 4
python3 -m labs.lab03.check --part 5
python3 -m labs.lab03.check --part 6
python3 -m labs.lab03.check --part 7
python3 -m labs.lab03.check --part 8
```

미구현 스타터는 실패해야 합니다. 구현 후 성공 출력과 추가 옵션은 각 Part의 안내를
따르세요. `make -C labs/lab03 grade PART=1`로도 같은 검사를 선택할 수 있습니다.
성능 측정은 다른 부하를 줄인 같은 컨테이너에서 준비 실행 후 반복 측정한 중앙값을
사용하세요. Docker 시작, 키 생성, 파일 입출력을 측정 구간에 포함하지 마세요.

대상만 중지하거나 모든 작업을 마치고 정리하려면 호스트에서 각각 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
docker compose -f docker/compose.yml --profile lab03 down
```

연결 오류가 나면 대상의 상태와 로그, `LAB03_TARGET_URL`, 실행 위치를 확인하세요.
컨테이너 안에서는 `localhost`가 대상 서버를 가리키지 않습니다. `/workspace`를 찾을 수
없으면 호스트가 아닌 `course` 셸에 진입했는지 확인하세요.

## 성공 조건

완료 표식은 `LAB03{...}` 형식입니다. 로컬 검사 표식은 공개된 비밀이 아닌 피드백입니다.
Part02·04·05의 복구한 데이터는 공격 성공 증거입니다. 최종 평가는 독립적으로 생성된
입력과 소스 검토를 사용하며, 분석 답변은 교수자가 평가합니다. 정해진 문자열을 출력하는
것만으로는 통과하지 않습니다.

로컬 Docker를 제어하는 사용자는 이미지와 메모리를 조사할 수 있습니다. 로컬 연습 키와
플래그의 비밀성은 보장하지 않습니다. 실제 평가용 키·플래그는 교수자 관리 서버나 격리된
평가 환경에서만 사용합니다. OAEP는 송신자 인증이나 송금 권한 검사를 제공하지 않으며,
Part08 대응책은 실습의 단일 CRT 분기 결함 모델을 대상으로 합니다.

## 제출 요구 사항

각 Part의 구현 소스, 실행 명령·출력, 복구 증거 또는 서버 완료 결과를 제출합니다.
Part01·03에는 연산 수, 반복 수, 중앙값, 상대 속도와 실행 환경을 포함하세요.
Part02의 복구 PDF와 SHA-256, Part07의 정상·오류 검증 결과도 포함합니다.
교수자가 요청하지 않은 서버 키나 교수용 파일은 제출하지 마세요.

## 분석 질문

1. 수학적으로 올바른 RSA 연산만으로 안전한 시스템을 만들 수 없는 이유는 무엇인가요?
2. 지역 실행 시간과 연산 수를 함께 검증하는 이유는 무엇인가요?
3. 난수 API 오류와 서명 검증 API 오류는 각각 어떻게 처리해야 하나요?
4. 로컬 완료 표식, 공격으로 복구한 자료, 관리 서버의 완료 플래그는 어떤 증거를 제공하나요?
