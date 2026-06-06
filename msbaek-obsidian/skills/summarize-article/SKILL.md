---
name: summarize-article
description: 기술 문서·블로그·뉴스레터 URL을 백그라운드로 번역·정리하여 상세한 한국어 Obsidian 노트(001-INBOX)를 생성. wikilink·atomic note·related notes·이미지를 자동 포함. "이 글 정리해줘 <URL>", "아티클 요약", "이 블로그 옵시디안에 저장", "summarize this article", URL을 주며 정리·요약·번역을 요청하거나, 이전 요약을 다시 실행·재실행·업데이트·보완하려 할 때 반드시 이 skill을 사용. (YouTube 영상은 summarize-youtube 사용)
argument-hint: "[url]"
---

# Article Summarize — $ARGUMENTS

기술 문서 URL을 받아 번역/정리하여 Obsidian 문서를 생성한다.

## 실행 모델 (필수)

URL → 추출 → 번역 → 문서 생성은 수 분이 걸리므로 **백그라운드 sub-agent에 위임**한다.
main context에서 직접 실행하지 말 것 — 즉시 progress 파일을 만들고 사용자에게 알린 뒤 반환한다.

위임 방법:

1. progress 파일을 먼저 생성: `.claude/summarize-progress/YYYYMMDD-HHMMSSfff-article-{url-slug}.json`
   (스키마는 agent 정의의 "백그라운드 실행" 섹션 참조)
2. `Agent`(Task) 도구로 **`msbaek-obsidian:article-obsidian-summarizer` agent에 위임**한다
   (`subagent_type`을 이 namespaced 형식으로 지정):
   - `model: "sonnet"` — main 세션 모델과 무관하게 비용 최적화
   - `run_in_background: true`
   - `prompt`: `$ARGUMENTS`(URL) + progress 파일 경로 전달
3. 사용자에게 "처리 시작" 알림 후 즉시 반환

추출 절차·번역 규칙·출력 구조·wikilink/atomic/related/이미지 규칙은 **모두 agent가 정의(SSOT)**한다.
이 skill은 트리거와 위임만 책임진다.

## 동기 실행 예외

`OBSIDIAN_EXEC=1` 환경변수가 설정됐거나(obsidian-summarize.sh 경유) 다른 subagent 내부에서 호출되면
**동기 모드**로 동작한다 — 백그라운드 위임 없이 agent의 작업 절차를 그대로 수행하고 결과를 반환한다.

## 사용 예시

```
/msbaek-obsidian:summarize-article https://martinfowler.com/articles/...
```

$ARGUMENTS가 비어 있으면 사용법을 안내한다.
