# Part 06: MD5 충돌로 위조된 중간 CA 복원하기

**한국어** | [English](../../../en/labs/lab04/part06/README.md)

2008년 연구진은 정상 서버 인증서와 위조 중간 CA 인증서의 서명 대상 본문을 서로 다르게 만들면서 MD5 값은 같게 했습니다. 이 Part에서는 공개된 정상 인증서의 서명을 위조 CA 인증서 템플릿에 옮겨 인증서를 복원하고, 당시 이미 발급된 서버 인증서가 그 CA를 거쳐 검증되는지 살펴봅니다.

연구진은 **위조 CA의 개인키를 공개하지 않았습니다.** 따라서 이 자료로 새 서버 인증서를 발급하는 실습은 할 수 없습니다. 제공된 `historical_server.der`는 연구진이 당시 이미 발급한 인증서입니다.

## 학습 목표

1. 두 인증서의 `TBSCertificate`가 서로 다르지만 MD5는 같은지 검사합니다.
2. 같은 서명으로 `CA:FALSE` 인증서와 `CA:TRUE` 인증서가 검증되는 원리를 확인합니다.
3. 역사적 검증 시점과 약한 서명을 허용하는 정책을 적용했을 때의 결과를 현재의 강한 검증 정책과 비교합니다.
4. 위조 CA 인증서와 그 개인키가 서로 다른 역할을 한다는 점을 설명합니다.

## 제공 자료

| 경로 | 내용 |
| --- | --- |
| [investigate.py](investigate.py) | 구현할 `collision_evidence()`와 `transplant_signature()` 및 체인 검사 실습 코드 |
| [data/legitimate.der](data/legitimate.der) | CA가 실제로 서명한 정상 인증서 |
| [data/rogue_template.der](data/rogue_template.der) | 서명 바이트가 비어 있는 위조 중간 CA 인증서 템플릿 |
| [data/template.json](data/template.json) | 템플릿의 서명 바이트 위치와 길이 |
| [data/historical_server.der](data/historical_server.der) | 위조 CA가 당시에 발급한 서버 인증서 |
| [data/historical_root.crt](data/historical_root.crt) | 오프라인 검증을 위한 역사적 루트 인증서 |
| [test_part06_materials.py](test_part06_materials.py) | 파일 형식과 템플릿 메타데이터를 확인하는 공개 검사 |

이 Part를 완료하려면 `investigate.py`의 두 TODO 함수를 직접 구현해야 합니다.

## 수행 과제

1. `collision_evidence()`에서 두 DER 인증서를 읽어 각각의 `TBSCertificate`를 비교하세요. 본문 자체와 SHA-256은 다르고 MD5가 같을 때만 `True`를 반환합니다.
2. `transplant_signature()`에서 정상 인증서의 서명을 읽고, `template.json`에 기록된 위치의 비어 있는 서명 바이트만 교체한 DER 바이트를 반환하세요. 다른 인증서 필드는 바꾸지 마세요.
3. 완성한 프로그램을 실행하세요. 정상 인증서는 `CA:FALSE`, 복원된 인증서는 `CA:TRUE`인지 살펴보고, 두 검증 정책의 결과를 비교하세요.

`investigate.py`는 복원된 인증서를 `/tmp/lab04-rogue-reconstructed.der`에 저장합니다. OpenSSL 검사에서 `historical_root.crt`는 **명령 한 번의 `-CAfile` 입력**으로만 사용합니다. 개인 PC의 운영체제나 브라우저 신뢰 목록에 이 역사적 루트를 설치하지 마세요.

## 실행 방법

[Lab04 공통 Docker 환경](../README.md)을 시작한 뒤 **course 컨테이너의 `/workspace`**에서 실행하세요. 네트워크 서버나 추가 패키지는 필요하지 않습니다.

```console
cd /workspace
python3 labs/lab04/part06/investigate.py
python3 labs/lab04/part06/test_part06_materials.py
```

TODO가 남아 있으면 첫 번째 명령은 `NotImplementedError`로 끝납니다. 공개 검사는 **자료 구성만** 확인하므로 구현 전에도 통과할 수 있습니다. 구현이 맞으면 프로그램은 다음 요지를 출력합니다.

```text
legitimate CA role: False
rogue CA role: True
legacy chain: accepted
modern chain: rejected
LAB04{...}
```

검증 시점은 자료의 유효기간 안인 **2004-08-05 00:00 UTC**로 고정되어 있습니다. `legacy chain`은 OpenSSL `-auth_level 0`으로 약한 서명을 허용한 오프라인 재현이며, `modern chain`은 `-auth_level 1`에서 MD5 서명을 약하다고 거부합니다. 이 명령은 **인증서 체인만** 검사하며 호스트 이름, 실제 TLS 연결, 오늘날 브라우저의 신뢰 여부는 검사하지 않습니다.

## 생각해 볼 질문

1. 서명 바이트는 같은데 인증서의 CA 역할이 달라질 수 있었던 이유는 무엇인가요?
2. 정상 인증서의 서명을 위조 템플릿에 옮겨도 `TBSCertificate`를 바꾸면 안 되는 이유는 무엇인가요?
3. 복원된 CA 인증서만 있고 대응하는 개인키가 없다면, 새 서버 인증서를 발급할 수 없는 이유는 무엇인가요?
4. 검증 시점과 `-auth_level`을 바꾸면 결과가 달라지는 이유는 무엇인가요?

## 자료 출처와 범위

정상·위조 CA 인증서와 미리 발급된 서버 인증서는 Marc Stevens 등 연구진의 [MD5 considered harmful today](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html) 공개 자료입니다. 역사적 루트 인증서는 [Android 인증서 저장소의 보관본](https://android.googlesource.com/platform/system/ca-certificates/+/a0de1e8ae3654572ec4f87074bb13b8ff3a04670/files/74c26bd0.0)에서 가져왔습니다. 이 Part는 공개된 인증서를 오프라인으로 분석하며, 새로운 MD5 충돌 계산이나 서버 인증서 발급은 수행하지 않습니다.
