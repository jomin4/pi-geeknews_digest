# 측정: GeekNews RSS 한 번 받은 저장본의 범위

- 목적: P1 "문제 원인"의 사실 확인. RSS 한 번에 몇 건, 몇 시간치가 들어 있는가
- 날짜·기간: 2026-09-29 21:51 KST, 1회 요청
- 명령: `curl -sS -A "gndigest/0.1 (+https://github.com/jomin4/pi-geeknews_digest)" https://news.hada.io/rss/news`
  - 집계: `parse_feed`(src/gndigest/rss.py)로 읽어 건수·게시 시각 범위·id 범위 계산 (L-20260929-1)
- 환경: 클라우드 세션(Claude Code), Python 3.12.3, feedparser 6
- 데이터 범위: 피드 항목 50건 전부. 제외 없음
- 결과 요약:
  - 항목 50건, 게시 시각 2026-09-28 22:59:58 ~ 2026-09-29 21:32:57 KST (22시간 32분 59초)
  - topic id 34433 ~ 34489 (57개 구간 중 50개 있음, 7개 없음)
  - `published`와 `updated`가 다른 항목 0건 (OPEN-4)
- 원본 파일: `2026-09-29-rss-snapshot.xml` (tests/fixtures/rss_sample.xml과 같은 파일, sha256 435a6914…aa125)
- 한계: 하루 한 번의 표본이다. 50건이 몇 시간치인지는 날마다 다르다. 없는 id 7개가 삭제 글인지 숨김 글인지 이 자료로는 알 수 없다
