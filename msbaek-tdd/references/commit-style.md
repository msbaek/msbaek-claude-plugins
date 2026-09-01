# 커밋 메시지 간결성 규칙 (플러그인 정본)

`reviewable-commits.md` 표준은 **무엇을 담는가**(Why·버린 대안·결정)의 정본이고,
이 문서는 **얼마나 담는가**(길이)의 정본이다. 두 규칙이 충돌하면 이 문서가 이긴다 —
표준의 채널들을 장문 서술로 풀지 않는다.

## 규칙

- **제목 1줄** (Conventional Commits type + 한글) + 빈 줄 + **핵심 bullet 2~4줄**.
- bullet은 각각 1줄 — Why의 핵심만. 배경 설명·경위 서술·문단형 산문 금지.
- 버린 대안·결정은 리뷰어가 diff만 보고 오해할 수 있는 경우에만 1줄로 남긴다.
- 제목만으로 Why가 명백한 작은 커밋은 body 생략 가능.
- 한글 메시지는 임시 파일 + `git commit -F` (heredoc·`-m "한글"` 금지 — 깨짐).

## 예시

좋은 예 (제목 + bullet 3줄):

```
docs(msbaek-tdd): tmpl 세션 실측 결과를 web-app 정본 references에 편입

- skeleton·계약 테스트 예시를 tmpl 실측 코드로 교체 (raw body 승인, TestTransaction guard)
- docker-compose scope를 testAndDevelopmentOnly로 수정, Boot 4 함정은 별도 절로 격리
- 정본 인용을 github.com/msbaek/tmpl URL로 통일
```

나쁜 예: 같은 커밋을 bullet마다 3~5줄 문단으로 풀어 20줄+ body를 만드는 것 —
Why의 세부 근거·검증 경위는 커밋이 아니라 plan 문서·PR 본문(`/compose-pr`)의 몫이다.
