# 공개 배포 후속 작업 (2026-09-14 감사 잔여분)

> 2026-09-14 5각도 감사에서 발견됐으나 이번 릴리스(1.48.0)에서 처리하지 않은 항목.
> 원본 리뷰: `~/git/kt4u/review-explain/raw/claude-review-2026-09-14-msbaek-tdd-public-release-audit.html`
> 처리 시 이 문서에서 항목을 지운다.

## A. 개인 환경 누출 문구 (사용자 결정: 지금 변경하지 않음)

| 위치 | 내용 | 조치안 |
|---|---|---|
| `msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md` (Uncle Bob 근거 줄) | Obsidian vault 경로 `001-INBOX/LIVE Uncle Bob on Software Fundamentals in the Age of AI.md [18:01-24:03]` | YouTube URL + 타임스탬프로 치환 |
| `skills/introduce-parameter-object/SKILL.md:260-283` | "실전 리팩토링 경로 (Vault 사례)" SequenceKey — 코드 없는 사내 사례 | 삭제 또는 공개 코드로 일반화 |
| `skills/naming-process/SKILL.md:325` | 더 읽을거리에 vault 내부 경로 `999-MOC/…` | 공개 출처(Bache·Martin)만 남김 |
| `skills/intent-revealing-names/SKILL.md:274` | 더 읽을거리 vault 경로 | 동일 |
| `references/commit-style.md:28` | `/compose-pr` 개인 스킬 언급 | "PR 본문" 일반 표현 |
| `references/reviewable-commits.md` 상단 | `/commit`·`reconstruct-commits`·`/compose-pr` 세 도구가 공유한다는 서문 — 외부 사용자에게는 없는 도구 | "커밋·PR 작성 시 참조하는 표준" 일반 표현 |
| `skills/tdd-feature/SKILL.md:3,101` | "superpowers의 장황한 spec/plan 대신" | 삭제 |
| `hooks/observe-agent-end.sh:6` | `harness-delta.md B-4` 개인 문서 인용 | 삭제 |
| `hooks/block-hunk-reviewer.sh`, `skills/tdd-profile/SKILL.md:29-30` | hunk-reviewer·IntelliJ Local Changes 언급 | "작성자 환경 전용, 없으면 no-op" 한 줄 |
| `references/commit-style.md:24`, `skills/tdd-plan/references/web-app-*.md`, `skills/tdd-rgb/references/web-app-finish.md` (7곳) | `github.com/msbaek/tmpl` 정본 인용 | 공개 유지 확인. 핵심 코드는 references에 인라인 |

## B. docs/superpowers/ 18개 파일 (사용자 결정: 현 상태 유지)

- `/Users/msbaek/…` 절대 경로 27곳 — hardening-gate-proposal:255, vault-refactoring-techniques 9곳, harness-agent-lifecycle:225·234, refactoring-skills-expansion 8곳, crap4java-gradle 4곳, specs 2곳
- claude.ai 세션 URL 8곳 — vault-techniques:20, vault-refactoring-techniques 7곳
- 조치안: 유지 + 치환(절대 경로 → 상대 표현, 세션 URL 삭제), README에 "설계 이력" 절로 링크. 또는 vault로 이관 후 삭제

## C. 1.48.0 이후 백로그 (Important)

| # | 항목 | 조치안 |
|---|---|---|
| I1 | `agents/references/*.md`가 유령 에이전트로 등록(`msbaek-tdd:references:tidying-process`) | `msbaek-tdd/references/`로 이동, `agents/tdd-blue.md:52,109`·`tidying-process.md:229` 경로 갱신 |
| I2 | `jq` 부재 시 hook 4개 조용히 무력화 | README 요구사항에 jq 추가 + hook 첫 줄 1회 경고 |
| I3 | `observe-agent-end.sh:39` BSD 전용 `sed -i ''` | `mktemp` 경유로 이식성 확보 |
| I5 잔여 | `intent-revealing-names:214-256,265` 정본 미인용·브랜치/PR 규칙 충돌 | 공통 절차 인용 + 정본에 관통형 예외 기재 |
| I7 잔여 | `tdd-plan-input:10,21,347`·`references/template.md:16-22` 소비 매핑이 `--full` 단계 기준 | 기본 경량 플로우 기준으로 재작성 |
| I8 | README: 에이전트 9→10, `/tdd-plan-input` 사용법 절 없음, 디렉토리 트리에 hooks/bin/references 없음, 요구사항(jq·Docker·python3·gh·Cucumber) 누락, 설치가 user settings 수정 미고지 | README 정비 |
| I9 | PUBLISHING-GUIDE 사용자·유지보수자 혼재, §4.4 구 시그니처 | 유지보수자 절만 CONTRIBUTING.md로, 사용자 절은 README 링크 |
| I11 | `.claude/plans/2026-02-14-…/{INDEX,design}.md` gitignore 이전 커밋으로 추적 중 | `git rm --cached -r .claude/plans` |
| I12 | `docs/architecture-map.html` 1.40.1 기준 정지 | 1.47.0+ 기준 갱신 |
| I13 | tdd-rgb·tdd-feature high 기어 3-phase 절차 중복(tdd-rgb 408줄) | `tdd-rgb/references/high-gear-3phase.md` 추출 |
| I15 | hook 마커 파일 누적, `mark-tdd-active.sh:28` stderr 누출 | `.gitignore` 자동 추가 또는 `$TMPDIR`, 리다이렉션 순서 수정 |

## D. Minor

- M1 CHANGELOG 없음, 태그 1.31.0까지, `marketplace.json` `metadata.version` 1.2.0 혼동
- M2 tdd-red/green/blue 첫 줄 persona 영어, tdd-blue description 호출자 표기
- M3 `refactoring-procedure.md:21-22` 문장 파손, `encapsulate-collection:166` 참조 제목 없음, `replace-conditional-with-poly:53-66` 컴파일 불가 예제
- M4 `tdd:28,30` 로케일 고정, `cucumber-acceptance` JapanDdp 예제 도메인
- M5 reference 내부 형제 경로 표기 불일치
- M7 `models/` 빈 디렉토리, `.junie/`·`.superpowers/` gitignore, `docs/plans/2026-03-30-tdd-tidy.md` 구 위치
- M8 `msbaek-tdd/README.md` 없음 · M9 에이전트 color·example · M10 `block-hunk-reviewer.sh` "26개 스킬" → 28
