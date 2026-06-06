---
name: summarize-youtube
description: YouTube URL 또는 트랜스크립트를 백그라운드로 번역·정리하여 타임스탬프 기반 상세 한국어 Obsidian 노트(001-INBOX)를 생성. 첫 인자로 언어 지정(kr|en, 기본 en). wikilink·atomic note·related notes를 자동 포함. "이 영상 정리해줘 <URL>", "유튜브 요약", "이 영상 옵시디안에 저장", "summarize this video", YouTube URL/트랜스크립트를 주며 정리·요약·번역을 요청하거나, 이전 요약을 다시 실행·재실행·업데이트·보완하려 할 때 반드시 이 skill을 사용. (일반 웹 article은 summarize-article 사용)
argument-hint: "[kr|en] [transcript or YouTube URL]"
---

# YouTube Summarize — $ARGUMENTS

YouTube URL 또는 트랜스크립트를 받아 번역/정리하여 Obsidian 문서를 생성한다.

## 언어 옵션

첫 번째 인자로 언어를 확인한다 (기본값: `en`):
- `kr` 또는 `ko`: 한글 트랜스크립트 우선
- `en`: 영어 트랜스크립트 우선 (기본값)
- 첫 단어가 언어 옵션이 아니면 전체를 내용(트랜스크립트)으로 처리

## 실행 모델 (필수)

트랜스크립트 추출 → 번역 → 문서 생성은 수 분이 걸리므로 **백그라운드 sub-agent에 위임**한다.
main context에서 직접 실행하지 말 것 — 즉시 progress 파일을 만들고 사용자에게 알린 뒤 반환한다.

위임 방법:

1. progress 파일을 먼저 생성: `.claude/summarize-progress/YYYYMMDD-HHMMSSfff-youtube-{video-id}.json`
   (스키마는 agent 정의의 "백그라운드 실행" 섹션 참조)
2. `Agent`(Task) 도구로 **`msbaek-obsidian:youtube-obsidian-summarizer` agent에 위임**한다
   (`subagent_type`을 이 namespaced 형식으로 지정):
   - `model: "sonnet"` — main 세션 모델과 무관하게 비용 최적화
   - `run_in_background: true`
   - `prompt`: `$ARGUMENTS`(언어 옵션 + URL/트랜스크립트) + progress 파일 경로 전달
3. 사용자에게 "처리 시작" 알림 후 즉시 반환

트랜스크립트 추출·번역 규칙·출력 구조·wikilink/atomic/related 규칙은 **모두 agent가 정의(SSOT)**한다.
이 skill은 트리거와 위임만 책임진다.

## 동기 실행 예외

`OBSIDIAN_EXEC=1` 환경변수가 설정됐거나(obsidian-summarize.sh 경유) 다른 subagent 내부에서 호출되면
**동기 모드**로 동작한다 — 백그라운드 위임 없이 agent의 작업 절차를 그대로 수행하고 결과를 반환한다.

## 사용 예시

```
/msbaek-obsidian:summarize-youtube en https://www.youtube.com/watch?v=...
/msbaek-obsidian:summarize-youtube kr https://youtu.be/...
```

$ARGUMENTS가 비어 있으면 사용법을 안내한다.
