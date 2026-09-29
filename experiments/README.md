# 측정 실험

포트폴리오 결과 수치를 만드는 스크립트를 둔다 (T13).

- 테스트가 아니다. CI에서 돌리지 않는다.
- 실제 API를 부르는 실험은 사용자 승인 후 로컬에서 실행한다.
- 결과는 `portfolio/evidence/후보ID/`에 원본 CSV와 측정 설명 파일로 남긴다 (`portfolio/evidence/README.md` 형식).
- 파일 이름: `p1_coverage.py`, `p2_naive_gemini.py`, `p3_labels_export.py`, `p4_weekly.py`, `r1_order_bias.py`, `r2_delay.py`
