**한국어** | [English](../../../../en/labs/lab01/part3_password_kdfs/data/README.md)

# Part 3 데이터

이 디렉토리의 모든 계정과 비밀번호는 가상의 수업용 데이터입니다.

- `lab01-small.txt`: 현재 Part 3 실습에 사용하는 의도적으로 작은 단어 목록입니다.
- `unsalted_hashes.csv`: `account,sha256` 대상 데이터입니다.
- `salted_hashes.csv`: `account,salt_hex,sha256` 대상 데이터이며 검증값은
  `SHA256(salt || UTF8(password))`입니다.
- `passwords.txt`와 `sha256_targets.txt`: 후보 목록과 솔트 없는 SHA-256 해시값을
  비교하기 위한 선택 실습용 추가 공개 데이터입니다.
