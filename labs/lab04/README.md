# Lab04: TLS 인증서와 신뢰

**한국어** | [English](../../en/labs/lab04/README.md)

## 학습 목표

OpenSSL로 RSA 키 쌍을 만들고 PBKDF2 기반 암호화 PKCS#8 개인키를 코드로
열어 봅니다. 이후 인증서 발급 요청부터 서버 인증서 검증까지 직접 실행합니다.
개인 PC의 브라우저를 실습용 HTTPS 프록시에 연결한 뒤,
프록시 CA를 신뢰 목록에 추가하기 전에는 인증서 경고가 나타나고 추가한 뒤에는
연결이 허용되는 과정을 비교합니다. 프록시가 실습 사이트의 요청·응답을 읽고
변경할 수 있는 이유와 역사적인 MD5 인증서 충돌의 영향을 분석합니다. 약한
비밀번호로 보호한 개인키 파일을 사전으로 복구하고, CRL로 인증서 폐기를 확인합니다.

| Part | 주제 | 시작 파일 | 완료 후 확인할 결과 |
|---|---|---|---|
| [01](part01/README.md) | OpenSSL 키 생성, 개인키 복호화와 OID 확인 | `part01/decrypt_key.py` | 개인키·공개키 일치와 완료 표식 |
| [02](part02/README.md) | CA 컨테이너에 CSR 제출 | `part02/enroll.py` | 발급 인증서 파일과 CSR·인증서 공개키 일치 |
| [03](part03/README.md) | 체인과 DNS 이름 검증 | `part03/verify_chain.py` | 올바른 체인·이름 수락, 오류 사례 거부 |
| [04](part04/README.md) | PC의 CA 신뢰와 로컬 HTTPS 중계 | `part04/compare_certificates.py` | 원본·프록시 인증서 비교와 프록시 로그의 Flag |
| [05](part05/README.md) | 제공 파일에서 MD5 충돌쌍 찾기 | `part05/find_collision.py` | 서로 다른 파일의 동일한 MD5와 다른 SHA-256 |
| [06](part06/README.md) | 역사적 가짜 중간 CA 복원과 체인 검증 | `part06/investigate.py` | 복원 파일, 과거 정책 수락과 현대 정책 거부 |
| [07](part07/README.md) | 암호화된 개인키 파일 사전 공격 | `part07/attack.py` | 시도 횟수·시간과 복호화한 Flag |
| [08](part08/README.md) | CRL을 이용한 인증서 폐기 확인 | `part08/revoke.py` | 폐기 전 수락, 갱신 CRL 적용 시 거부, 새 인증서 수락 |

각 Part 디렉토리에 학생이 수정하는 실습 코드와 직접 실행되는 `main()`이 있습니다.
**각 Part를 완료하려면 해당 Python 파일의 TODO를 직접 구현해야 합니다.** 먼저
실습 코드를 실행해 입력·출력 흐름을 살펴보고, 구현 후 다시 실행하세요.
같은 디렉토리의 `check.py` 또는 `test_...py`는 선택적인 공개 확인용입니다.
완료 표식 `LAB04{...}`로 각 Part의 진행 결과를 스스로 확인할 수 있습니다.
Part04의 Flag는 실습용 HTTPS 통신에서
찾고, Part07의 Flag는 개인키 복구 후 제공 암호문에서 찾습니다. Part04는 Flag
관찰과 `compare_certificates.py` 완성을 모두 수행합니다.
각 Part의 README에는 실행 화면의 구체적인 확인 항목을 적었습니다.

## 필요한 Docker 이미지

| 이미지 (Compose 서비스) | 준비 방법 | 사용하는 Part |
|---|---|---|
| `modern-cryptography-2026` (`course`) | `docker/Dockerfile`로 직접 빌드 | 모든 Part |
| `modern-cryptography-2026-lab04-ca` (`lab04-ca`) | 공통 이미지 위에 `docker/lab04-ca/Dockerfile`로 직접 빌드 | Part02·08, Part03에 사용할 인증서 발급 |
| `modern-cryptography-2026-lab04-proxy` (`lab04-proxy`) | 공통 이미지 위에 `docker/lab04-proxy/Dockerfile`로 직접 빌드 | Part04 |

Part01·05·06·07은 `course` 이미지만 사용합니다. Part03의 체인 검증도
`course`에서 실행하지만 Part02에서 만든 인증서 파일이 먼저 필요합니다.
Lab04의 대상 이미지는 외부 레지스트리에서 따로 받지 않습니다.

## 환경 시작

호스트의 저장소 루트에서 Docker를 실행합니다. **Lab04 전체를 진행한다면** 공통
이미지를 먼저 빌드하고 CA·프록시 이미지를 빌드한 뒤 세 서비스를 시작하세요.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml --profile lab04 build lab04-ca lab04-proxy
docker compose -f docker/compose.yml --profile lab04 up -d --wait course lab04-ca lab04-proxy
docker compose -f docker/compose.yml exec course bash
```

이후 **course 컨테이너**에서 `/workspace`를 기준으로 각 Part의 README와 실행 명령을
따릅니다. Part01에서 생성한 키 파일은 Part02에서 사용하므로 자신의 비밀번호를
기억하세요. 생성된 개인키는 `part01/output/`, 발급받은 인증서는
`part02/output/`에 저장되며 Git에서 제외됩니다. CA 컨테이너를 재시작하면
실습용 CA 키가 새로 생성되므로 Part02의 인증서를 다시 발급해야 합니다.
Part08에서는 Part02의 CSR을 이용해 새 인증서를 발급받고 폐기 상태를 확인합니다.

Part04는 학생 개인 PC의 브라우저 설정도 사용합니다. 프록시는 자신의 PC에서만
접속할 수 있도록 `127.0.0.1:18080`에 연결됩니다. 해당 Part의 안내에 따라
실습용 CA를 등록하고, 종료할 때 반드시 그 CA와 프록시 설정을 제거하세요.
제공된 합성 자료와 로컬 실습 서비스만 대상으로 사용합니다.

실습을 마친 뒤 컨테이너 셸에서 `exit`하고 호스트에서 다음을 실행합니다.

```console
docker compose -f docker/compose.yml --profile lab04 down
```

## MD5 실습 범위

Part05는 여러 파일 중 실제 선택 접두어 MD5 충돌쌍을 찾아 비교합니다. Part06은 공개된
2008년 실제 인증서 자료로, 정상 인증서의 서명을 가짜 중간 CA 인증서에 옮기고
**당시 이미 발급된** 서버 인증서의 체인을 검증합니다. 연구진은 가짜 CA의 개인키를
공개하지 않았으므로 이 자료로 새 서버 인증서를 발급하는 과제는 아닙니다.
공격 재현에는 과거 시각과 명시적인 레거시 검증 정책을 사용하며, 현대 정책의
거부 결과도 확인합니다. 역사적 Root 인증서는 개인 PC의 신뢰 목록에 등록하지
마세요. [원 연구 자료](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html)
