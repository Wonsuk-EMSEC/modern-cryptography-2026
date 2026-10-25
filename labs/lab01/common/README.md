**한국어** | [English](../../../en/labs/lab01/common/README.md)

# Lab 01 완료 플래그

각 Part는 `data/flag_challenge.json`에 인증 암호화된 플래그를 제공합니다.
실험을 완료하고 해당 Part README에 지정된 증명값을 구성한 뒤, 제공된
`unlock_flag(path, proof)` 유틸리티를 호출하세요. 인증에 성공하면 `FLAG{...}` 문자열을
반환하고, 증명값이 틀리거나 암호화 봉투가 유효하지 않으면 `ValueError`를 발생시킵니다.
제공된 플래그 파일을 수정하지 마세요.

번호별 Part의 학생 실습 파일에서는 공통 유틸리티를 가져오기 전에 저장소 루트를
모듈 검색 경로에 추가합니다.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`canonical_account_proof(accounts)`는 계정 이름을 사전순으로 정렬하고, 불필요한 공백 없이
유니코드를 텍스트로 유지한 간결한 JSON을 반환합니다. 계정 문자열을 복구한 비밀번호 문자열에
대응시키는 비어 있지 않은 매핑이 필요합니다. 공개 매핑
`{"b": "public-two", "a": "public-one"}`을 입력하면 `{"a":"public-one","b":"public-two"}`를
반환합니다. 정확한 인코딩은 다음과 같습니다.

```python
json.dumps(accounts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

어느 Part에서든 `python3 samples/flag_unlock_demo.py`를 실행하면 잘못된 공개 증명값이
거부되고 명시적으로 공개된 데모 증명값으로는 성공하는 것을 관찰할 수 있습니다.
데모는 `common/samples/public_flag_challenge.json`만 엽니다. 수업용 계정, SSH 인증 정보,
캡처된 네트워크의 암호문구 또는 Part 플래그는 사용하지 않습니다.

예상 데모 출력:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

도우미는 AES-256-GCM 복호화와 인증을 처리합니다. 도메인을 분리한 SHA-256 유도 과정이
UTF-8 증명값을 암호화 봉투의 Part 식별자에 결합하며, 공개된 챌린지 메타데이터도 인증됩니다.
실제 실험은 직접 구현해야 합니다. 이 유틸리티는 후보 탐색이나 비밀번호 복구 기능을 제공하지 않습니다.
