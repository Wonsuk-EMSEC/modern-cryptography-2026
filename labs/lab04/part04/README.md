# Part04: 실습용 CA 신뢰와 HTTPS 중간자 프록시

**한국어** | [English](../../../en/labs/lab04/part04/README.md)

내 PC의 브라우저가 어떤 CA를 신뢰하느냐에 따라 같은 HTTPS 접속을 다르게 판단하는지
확인합니다. Docker 안의 실습용 프록시는 `lab04.local.test`로 가는 연결만 받습니다.
브라우저와 프록시, 프록시와 원래 서버 사이에는 각각 TLS 연결이 만들어집니다.

## 학습 목표

1. 인증서 경고가 나타나는 이유를 신뢰 목록과 인증서 발급자에서 찾습니다.
2. 실습용 CA 인증서를 브라우저에 추가한 뒤 프록시가 중계한 HTTPS 요청을 관찰합니다.
3. 원래 서버 인증서와 브라우저에 제시된 인증서를 비교하고 신뢰 설정을 복구합니다.

이 Part의 대상은 Docker가 제공하는 **합성 실습 사이트**입니다. 일반 웹사이트의
계정이나 데이터를 사용하지 마세요. 실습용 CA는 이 PC에서 임시로만 신뢰합니다.
가능하면 실습 전용 브라우저 프로필에 인증서를 등록하세요. 브라우저가 운영체제의
신뢰 목록을 사용한다면 현재 사용자 영역에 등록하고, 종료할 때 같은 위치에서
제거하세요.

## 제공 자료

- [compare_certificates.py](compare_certificates.py): 두 인증서의 Subject, Issuer,
  SHA-256 지문, DNS SAN을 읽는 TODO와 직접 실행하는 `main()`.
- [check.py](check.py): 원본 인증서와 프록시 인증서의 차이를 확인하는 선택적 검사.
- [data/protocol.json](data/protocol.json): 실습 호스트 이름과 프록시 주소.
- `lab04-proxy` 컨테이너: 실습 사이트와 중간자 프록시. 실행할 때마다 새 실습용
  CA를 생성합니다.

이 Part를 완료하려면 `compare_certificates.py`의 미완성 `describe()`를 직접 구현해야
합니다. 프록시 로그에서 Flag를 찾는 것과 코드 완성은 별개의 과제입니다. 프록시의
구현은 실습 환경이 제공하며, 브라우저에서 보내는 요청과 컨테이너 로그를 통해
동작을 확인합니다.

## 실행 방법

먼저 [Lab04의 공통 Docker 준비](../README.md)를 마칩니다. 아래 Docker 명령은
**호스트 터미널의 저장소 루트**에서 실행합니다. 브라우저도 개인 PC에서 엽니다.

```console
docker compose -f docker/compose.yml --profile lab04 up -d --wait course lab04-proxy
docker compose -f docker/compose.yml --profile lab04 ps
```

`lab04-proxy`가 `healthy`인지 확인하세요. 프록시는 호스트의
`127.0.0.1:18080`에서만 접근할 수 있습니다. 실습 이름 `lab04.local.test`는
브라우저가 프록시에 보내는 요청 이름이며 PC의 DNS나 hosts 파일을 수정할 필요가
없습니다.

1. **인증서 신뢰 전:** 브라우저의 HTTPS 프록시를 `127.0.0.1`, 포트 `18080`으로
   설정하고 `https://lab04.local.test/`에 접속하세요. 인증서 신뢰 경고가
   나타나야 합니다. 경고를 무시하고 계속 진행하지 마세요.
2. **실습용 CA 등록:** 호스트 브라우저에서
   `http://127.0.0.1:18080/lab04-proxy-ca.pem`을 열어 CA의 **공개 인증서**만
   내려받으세요. 브라우저의 인증 기관 관리 화면에서 이 인증서를 웹사이트
   식별용으로 신뢰하도록 추가합니다. 표시 이름은 `Lab04 MITM Practice Root`입니다.
   개인키를 PC로 복사할 필요는 없습니다. 브라우저별 메뉴는 다를 수 있으므로
   인증 기관을 추가한 뒤 필요하면 브라우저를 다시 시작하세요.
3. **다시 접속:** 같은 실습 URL을 새 탭에서 여세요. 정상 연결 뒤 제목이
   `Observed Through Proxy`로 표시됩니다. 브라우저의 인증서 보기에서 발급자와
   대상 이름을 확인하세요.
4. **Flag 관찰:** 페이지의 **Send practice token** 버튼을 클릭한 다음,
   **호스트 터미널**에서 로그를 읽습니다.

   ```console
   docker compose -f docker/compose.yml --profile lab04 logs --tail 50 lab04-proxy
   ```

   `Lab04 proxy observed token response` 또는 `Lab04 proxy observed submitted body`
   줄에서 실습용 `LAB04{...}` 값을 찾으세요. 이 값은 실행 시 생성됩니다.

브라우저의 프록시를 설정하는 것과 CA를 신뢰 목록에 넣는 것은 별개의 단계입니다.
CA만 추가해도 트래픽이 프록시를 통과하지는 않습니다.

## 인증서 비교 코드

**course 컨테이너 터미널**에서 다음을 실행합니다. 제공된 두 PEM은 공개
인증서이며, 개인키가 아닙니다.

```console
cd /workspace/labs/lab04/part04
curl -fsS http://lab04-proxy:8080/lab04-target-cert.pem -o /tmp/lab04-target-cert.pem
curl -fsS http://lab04-proxy:8080/lab04-intercept-cert.pem -o /tmp/lab04-intercept-cert.pem
openssl x509 -in /tmp/lab04-target-cert.pem -noout -subject -issuer -ext subjectAltName -sha256 -fingerprint
openssl x509 -in /tmp/lab04-intercept-cert.pem -noout -subject -issuer -ext subjectAltName -sha256 -fingerprint
python3 compare_certificates.py /tmp/lab04-target-cert.pem /tmp/lab04-intercept-cert.pem
python3 check.py
```

`compare_certificates.py`는 `describe()` TODO를 구현하기 전까지 `NotImplementedError`를
보입니다. 구현 후에는 두 인증서의 Subject, Issuer, SHA-256 지문, DNS SAN을
나란히 출력하세요. 브라우저에서 본 인증서와 가로챈 인증서의 발급자가 같은지도
확인합니다. `check.py`는 구현 후 실행하는 선택적 검사입니다.

### TODO 완료 후 확인할 결과

- `compare_certificates.py`는 JSON의 `original`과 `intercepted` 항목에 각각
  `subject`, `issuer`, `fingerprint`, `dns_names`를 출력합니다. 두 항목 모두
  `dns_names`에 `lab04.local.test`가 있고, `fingerprint`는 64자리 16진수입니다.
- 원본과 프록시 인증서의 `issuer` 및 `fingerprint`는 서로 달라야 합니다.
  `check.py`가 이를 확인하면
  `Part04: original and intercepted certificate identities: OK`를 출력합니다.
- 코드의 JSON 출력에는 Flag가 없습니다. `LAB04{...}`는 위 브라우저 단계에서
  실습 토큰을 전송한 뒤 **프록시 로그**에서 확인합니다.

## 실습 종료

**호스트 PC**에서 `Lab04 MITM Practice Root`를 브라우저 또는 사용자 신뢰
목록에서 제거하고, HTTPS 프록시 설정을 실습 전 값으로 되돌리세요. 필요하면
브라우저를 다시 시작합니다. 그다음 **호스트 터미널의 저장소 루트**에서 프록시를
중지합니다.

```console
docker compose -f docker/compose.yml --profile lab04 stop lab04-proxy
```

프록시를 다시 시작하면 새로운 CA가 생성되므로 이전에 내려받은 인증서는 새
프록시 인증서를 신뢰하는 데 사용할 수 없습니다. 종료 후에도 기존 CA가 PC에
남지 않았는지 확인하세요.

## 완료 및 기록

신뢰 전의 오류, 신뢰 후 접속 성공, 두 인증서의 발급자·지문 차이, 프록시 로그의
Flag를 기록하세요. 실습용 CA 개인키나 실제 계정 정보는 제출하지 않습니다.

1. 브라우저가 원래 서버 대신 프록시의 인증서를 받아들인 이유는 무엇인가요?
2. 같은 DNS 이름을 가진 두 인증서의 발급자와 지문은 어떻게 다른가요?
3. 프록시에서 응답 문구와 전송 토큰을 볼 수 있었던 이유는 무엇인가요?
4. CA를 신뢰 목록에서 제거한 뒤에는 왜 새 접속이 실패하나요?
