# Lab03 제출 보고서

**한국어** | [English](../../en/labs/lab03/REPORT_TEMPLATE.md)

- 이름 / 학번:
- 제출 소스 경로 및 버전:
- 실행 환경: CPU, Docker 이미지, Python, GCC, OpenSSL 버전
- 재현 명령:

## Part01: Modular Exponentiation and Primality Testing

- 정확성·경계값 검사 결과:
- 지수별 비트 길이·모듈러 곱셈 수:
- 준비 실행 / 반복 횟수 / 중앙값 (naive, square-and-multiply, built-in):
- 16·20·24·28·32비트 소수/작은 인수 합성수/큰 인수 합성수 측정:
- 생성한 128비트 합성수와 t, 세 소인수, 검증 기록:
- Fermat 통과가 소수성을 보장하지 않는 이유:

## Part02: Predictable Key Recovery and Secure Random Generation

- 시간대 / 탐색 구간 / 복구 절차:
- 복구한 PDF 파일과 SHA-256, 완료 증거:
- 수정한 RNG 호출과 반환값 처리:
- 정상 암·복호화 및 각 RNG 실패 주입 결과:
- 원래 공격의 제한된 재시도 결과와 그 해석:

## Part03: RSA Key Generation, Encryption, and CRT

- 키 계산·암호화·직접 복호화·CRT 복호화 검사:
- RSA 비트 길이 / 반복 수 / 직접·CRT 중앙값 / 상대 속도:
- 측정에서 제외한 작업 / 기준 구현 보정 기록:

## Part04: RSA Factorization Attack

- 인수분해·개인 지수 복구·복호화 증거:
- 복구한 값과 재암호화 검증:

## Part05: RSA Low Public Exponent Attack

- 정수근 알고리즘과 정확성 판정:
- 복구와 재암호화 증거:
- 직접 정수근 공격이 적용되지 않는 입력의 처리:

## Part06: Textbook RSA Malleability and RSA-OAEP

- 대상 주소 / 세션 / 곱셈 변조 요청과 결과:
- 정상 OAEP 처리와 변조 거부 결과:
- 완료 결과 / OAEP와 송신자 인증·권한 검사의 차이:

## Part07: RSA-PSS Signatures and Secure Verification

- 구현한 서명·검증과 PSS 매개변수:
- 정상·변조 메시지·변조 서명·잘못된 키 검사 결과:
- 잘못된 입력·API 오류·검증 반환값 처리:

## Part08: RSA-CRT Fault Attack

- 결함 서명에서 얻은 인수와 개인 지수의 검증:
- 새 메시지 서명에 대한 서버 검증 결과:
- 보호된 경로의 결함 거부와 정상 서명 결과:
- 완료 결과 / 대응책이 적용되는 결함 모델:

## 분석과 한계

각 Part의 분석 질문에 답하고 실패한 검사와 재현하지 못한 항목을 기록하세요.
로컬 표식은 비밀이 아니며, 교수자 관리 서버의 평가 결과와 구분하세요.
