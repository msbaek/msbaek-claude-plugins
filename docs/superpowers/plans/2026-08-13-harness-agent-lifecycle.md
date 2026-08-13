# 하네스 관점 에이전트 재편 — Phase P(Plan) + I(Implement)

> 작성: 2026-08-13 · 대상: `msbaek-tdd` 1.33.0 → 1.34.0
> 근거: 황민호 『하네스 엔지니어링 with 클로드 코드』 3·4·6·8·9장
> 기준 문서: `~/.claude/docs/harness-delta.md` (gap·충돌) + `harness` 플러그인 references(정본)

## 배경 — 왜 이 작업을 하나

플러그인이 **스킬(어떻게) 편중**이다. 스킬 28개 대 에이전트 3개(tdd-red/green/blue).
라이프사이클 13개 단계 중 에이전트가 있는 건 RGB 3개뿐이고, 나머지 10개는 메인 컨텍스트가
직접 수행한다 — 책의 **안티패턴 3(리더가 직접 일을 처리)**.

가장 아픈 곳은 **Plan Phase**다. 경계 조건 누락(tdd-plan이 직접 경고하는 "집계 경계" 사례)이나
"숫자의 정본 부재" 같은 결함은 **같은 관점이 다시 봐서는 잡히지 않는** 종류다 — 책 1장의
자기 검증 실패 모드. 현재 이 단계에 검증 축이 아예 없다.

두 번째는 **에이전트 파일의 절차 비대** — `tdd-blue.md` 532줄 중 360줄이 Tidying 절차다.
책의 **안티패턴 4(에이전트 파일에 절차 지식을 다 넣는다)**이며, `tdd-tidy` 스킬과 중복이다.

세 번째는 **확실한 결함** — `tdd-red`의 `tools`에 테스트 실행 도구가 없다. Red 단계 핵심 규칙인
"TEST SHOULD FAIL WHEN YOU ADD IT"을 검증할 수단이 도구 목록에서 빠져 있다(green/blue에는 있음).
책 4장이 경고한 "도구를 너무 적게 줘서 조용히 실패하는" 케이스.

## GOAL (testable)

- **성공 = 에이전트 8개가 7섹션 역할 계약서로 존재하고, 검증 축 2개가 읽기 전용 `tools`로
  강제되며, `tdd-blue`가 200줄 이하이고, `tdd-red`가 테스트 실행 도구를 가진다**
- Plan Phase 4개 신설 + Implement Phase 3개 재작성 + 검증 에이전트 1개 신설
- 각 에이전트가 입출력 프로토콜(`_workspace` 또는 plan 문서 경로)을 파일로 선언
- 기존 워크플로(`/tdd-plan`, `/tdd-rgb`, `/tdd-feature`)가 회귀 없이 동작

## CONSTRAINTS (non-negotiable)

1. **초안은 에이전트, 승인은 메인** — 에이전트가 초안 생성 + 교차검증까지 하고, 메인이 결과를
   묶어 사용자에게 제시·승인받는다. tdd-plan의 단계별 "사용자 승인 대기" 피드백 루프를 끊지 않는다.
   (책: 리더 = 지시자가 아니라 통합자·결정자)
2. **검증 에이전트는 쓰기 도구를 갖지 않는다** — `Write`/`Edit` 없음. 자연어 "수정 금지"는
   안전장치가 아니다(delta A-2).
3. **실행 모드는 1차에서 서브에이전트** — Plan Phase는 책 기준 팀 모드가 정석(팬아웃·팬인)이나,
   팀 프리미티브가 이 플러그인에서 검증된 적이 없다. 서브 병렬 + 메인 통합으로 시작하고
   효과 확인 후 팀 전환을 판단한다. (오버엔지니어링 경계)
4. **절차 지식은 에이전트가 아니라 스킬·references에 둔다** — 에이전트는 역할·판단 기준·프로토콜만.
5. **버전은 두 곳을 함께 bump** — `plugin.json` + `marketplace.json`.
6. **기존 스킬의 정본 참조 관계를 깨지 않는다** — tdd-rgb의 references 4개는 tdd-feature·tdd-plan·tdd가
   참조하는 정본이다. 이관 시 참조 경로를 함께 갱신한다.

## FAILURE CONDITIONS (plan 전체)

| 증상 | 대처 |
|---|---|
| 에이전트가 7섹션 중 입출력 프로토콜을 비운 채 완성 | 다음 에이전트가 산출물 위치를 매번 즉흥 결정 — 경로를 파일에 명시하고 재작성 |
| 검증 에이전트에 Write/Edit가 남음 | 검증 루프 붕괴 — tools에서 제거 |
| tdd-blue가 여전히 300줄 초과 | 절차가 덜 이관됨 — references로 마저 이관 |
| 이관 후 tdd-tidy·tdd-rgb에서 참조가 끊김 | 정본 드리프트 — 참조 경로 갱신 후 실제 Read 경로 검증 |
| 에이전트만 늘고 스킬이 그대로 호출 | 위임 구조 미반영 — 스킬 본문에 위임 지점 명시 |

---

## Task 목록

### Task 1. `agents/references/tidying-process.md` 신설 + `tdd-blue` 축소

**작업**: `tdd-blue.md`(532줄)의 Principles 구간(46~406행, Tidying Process 절차 360줄)을
`agents/references/tidying-process.md`로 이관. 에이전트 본문에는 **판단 기준만** 남긴다
(언제 어떤 기법을 고르는가, 80% 규칙, 중단 조건).

**Output Format**
- `agents/references/tidying-process.md` (신설) — Guard Clauses → One Pile → Reorder →
  Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming 절차 전문
- `agents/tdd-blue.md` — 200줄 이하, 절차는 `references/tidying-process.md`를 Read로 참조

**Failure Conditions**
- 이관 후 `tdd-tidy` 스킬이 참조하던 내용이 사라짐 → 줄 단위 대조로 실손실 확인(이전 tdd-rgb
  축소 때 실손실 2건이 나온 전례가 있다)
- 판단 기준까지 references로 밀려나 에이전트가 껍데기만 남음 → 판단은 본문에 유지

---

### Task 2. `agents/tdd-red.md` 재작성

**작업**: 7섹션 역할 계약서로 재작성 + `tools` 결함 수정.

**Output Format** — 프론트매터
```yaml
name: tdd-red
description: <무엇을 / 어떤 기준으로 / 언제 호출> 3요소 한 줄
model: sonnet
tools: Edit, MultiEdit, Write, Read, Bash(gradle test:*), Bash(mvn test:*),
       Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*)
```
본문 7섹션: 핵심 역할 / 작업 원칙 / 입출력 프로토콜 / 팀 통신 프로토콜(서브 모드이므로 생략 가능) /
에러 핸들링 / 협업 / 품질 자체 검증

- 입출력 프로토콜: 입력 = plan 문서의 미완료 test 항목, 출력 = 테스트 코드 + `test:` 커밋
- 품질 자체 검증: "추가 시점에 실제로 실패하는가"를 **테스트 실행으로 확인**했는지 체크박스

**Failure Conditions**
- 테스트 실행 도구가 여전히 없음 → Red의 핵심 규칙을 검증할 수 없음
- 절차(TPP·Test Desiderata 등)를 본문에 재기술 → tdd-rgb references가 정본이므로 경로 참조만

---

### Task 3. `agents/tdd-green.md` 재작성

**작업**: 7섹션화. 입출력 프로토콜·협업·품질 자체 검증 신설.

**Output Format**
- `model: sonnet`, tools는 현행 유지(테스트 실행 도구 이미 보유)
- 입출력: 입력 = tdd-red가 남긴 실패 테스트, 출력 = 최소 구현 + `feat:` 커밋
- 협업: 상류 tdd-red / 하류 tdd-blue·tdd-impl-critic / Getting Stuck 후퇴 시 오케스트레이터에 보고
- 품질 자체 검증: 최소 구현 초과 여부, 테스트 수정 여부

**Failure Conditions**
- Getting Stuck 후퇴 경로가 프로토콜에서 빠짐 → tdd-feature가 이 신호를 소비하므로 계약 유지 필수

---

### Task 4. ~~`agents/tdd-impl-critic.md` 신설~~ → **스킵 (이미 충족됨, 구현 중 발견)**

**정정**: `skills/tdd-rgb/references/adversarial-review.md`를 실제로 읽어보니, "리뷰어 선택"
절이 이미 "1순위: 전역 `adversarial-reviewer` agent가 있으면 dispatch, 2순위: general-purpose
sub-agent + 내장 프롬프트"를 명시하고 있었다. 전역 `adversarial-reviewer`는 이미
`Tools: Read, Grep, Glob, Bash`(쓰기 없음)의 읽기 전용 적대적 리뷰어다 — Task 4가 만들려던
것과 동일한 설계가 **환경 적응형**(env-adaptive)으로 이미 존재한다.

`tdd-rgb/SKILL.md`·`tdd-feature/SKILL.md` 모두 이 references를 정본으로 올바르게 참조하고
있어 스킬 쪽 수정도 불필요했다. 플러그인 로컬 에이전트를 새로 만들면 전역 에이전트와
같은 트리거 조건을 두고 경쟁·중복하게 되므로 **만들지 않는 것이 맞는 판단**이다.

계획 수립 시점에 이 references 파일의 "리뷰어 선택" 절을 읽지 않고 "references 문서로만
있어 검증 축이 없다"고 오판한 것이 원인 — plan 작성 전 기존 자산 대조가 부족했다.

---

### Task 5. Plan Phase 에이전트 4개 신설 ⭐

| 파일 | 책임 | model | tools |
|---|---|---|---|
| `agents/tdd-domain-modeler.md` | 0층 도메인 규칙(계산·절사·상태) + 검산 전개 = **숫자의 정본** | opus | Read, Write, Edit, Grep |
| `agents/tdd-example-designer.md` | Gherkin 핵심예시 + 경계조건 5종 스캔(수치·크기·상태·시간·**집계**) | opus | Read, Write, Edit, Grep |
| `agents/tdd-test-list.md` | unit test 목록, Degenerate→General 정렬, 두 계층 중복 금지 | sonnet | Read, Write, Edit |
| `agents/tdd-plan-critic.md` ⭐ | plan 품질 체크리스트 검증 — 정본 부재·모순·중복·누락 탐지 | opus | Read, Grep, Glob |

**Output Format** — 공통
- 모두 7섹션. 입출력 프로토콜은 **plan 템플릿 문서의 해당 절**을 경로로 명시
  (예: 입력 = `<topic>-plan-input.md` §2, 출력 = 템플릿 문서 `## 1. 요구사항` 절)
- `tdd-plan-critic`은 tdd-plan의 FAILURE CONDITIONS 품질 체크리스트 6항목을 검증 기준으로 삼는다
- 각 에이전트는 **커밋하지 않는다** — 승인 후 메인이 커밋(승인 게이트 유지)

**Failure Conditions**
- 에이전트가 사용자 승인 없이 커밋 → 피드백 루프 우회. 커밋 도구를 주지 않는다
- domain-modeler와 example-designer가 수치를 각자 계산 → 정본 이중화. Examples 표는
  0층 검산 전개의 **파생 뷰**임을 프로토콜에 명시
- 4명이 같은 문서를 동시 편집해 충돌 → 1차는 순차 실행 또는 절 단위 분리

---

### Task 6. 스킬 위임 구조 반영

**작업**
- `skills/tdd-plan/SKILL.md` — 단계 1a/2/3 작업 절차에 "① 에이전트에 초안 위임 → ② 메인이
  결과 통합·제시 → ③ 사용자 승인 → ④ 메인이 커밋" 구조 명시. `tdd-plan-critic` 호출 지점 추가
- `skills/tdd-rgb/SKILL.md`·`skills/tdd-feature/SKILL.md` — 적대적 리뷰 절차 직접 실행 →
  `tdd-impl-critic` 위임으로 교체 (references는 정본으로 유지)

**Failure Conditions**
- 위임만 추가하고 승인 게이트가 사라짐 → Constraint 1 위반
- tdd-rgb references 참조가 끊김 → 정본 경로 유지 확인

---

### Task 7. 릴리스

- `msbaek-tdd/.claude-plugin/plugin.json` 1.33.0 → **1.34.0**
- 루트 `marketplace.json` 동일 bump (**두 곳 모두** — 과거 누락 전례)
- `README.md` 에이전트 섹션 갱신 (3개 → 8개, 역할·model·tools 표)
- reviewable-commits 표준으로 커밋 (Why + 버린 대안 + 결정 순서)

---

## 진행 기록

- [x] Task 1 — tidying-process.md 이관(349줄) + tdd-blue 축소(532→126줄)
- [x] Task 2 — tdd-red 재작성 (7섹션 + `Bash(gradle test:*)`·`Bash(mvn test:*)` 추가)
- [x] Task 3 — tdd-green 재작성 (7섹션)
- [x] Task 4 — **스킵**: 전역 `adversarial-reviewer` 에이전트로 이미 충족 (위 정정 참조)
- [x] Task 5 — Plan Phase 4개 신설 (tdd-domain-modeler·tdd-example-designer·tdd-test-list·
  tdd-plan-critic) — YAML frontmatter 콜론 이스케이프 버그 1건, 상대경로 깊이 오류 1건
  (`../../skills` → `../skills`) 검증 중 발견해 수정
- [x] Task 6 — tdd-plan/SKILL.md 단계 1·2·3에 위임 구조 반영. tdd-rgb·tdd-feature는
  Task 4 정정에 따라 변경 불필요
- [x] Task 7 — plugin.json·marketplace.json 1.33.0→1.34.0(양쪽), README.md 에이전트 섹션 갱신
- [ ] **커밋** — 아직 수행 안 됨. reviewable-commits 표준으로 Task 단위 분리 또는 통합 커밋
  여부는 다음 세션에서 사용자와 확인

**Resume Point**: 파일 작업은 모두 완료. 다음은 커밋 — `git status`로 변경 파일 확인 후
reviewable-commits.md 표준(Why + 버린 대안 + 결정 순서)으로 작성. 커밋 단위는 Task별 분리
(7개)와 논리적 묶음(에이전트 재작성 3개 + Plan 신설 4개 + 릴리스 1개) 중 다음 세션에서 결정.

## 크로스세션 실증 검증 (2026-08-13, Phase P+I 완료 후)

`tdd-agent-verifiyer` 저장소에서 두 피어 세션(`tdd-agent-verifier`→`tdd-spec-review-fixes`,
CouponUsageLimit 도메인)에 위임해 Plan Phase 4개·RGB 3개 전부 실제 호출을 확인했다.
집계 경계 스캔이 승인 반영 폭 결함(`+= 1`)까지 발견, `tdd-red`의 `tools` 결함 수정이
우연히 통과하는 테스트를 실전에서 잡아냄, `tdd-blue`가 80% 규칙을 diff로 실증(2줄
변경만). 모든 보고는 커밋 히스토리·diff 직접 대조로 독립 검증했다(추측 없음).
인덱스: `~/git/kt4u/review-explain/session-names.md` `harness-plan-phase-agent-delegation`.

## 다음 단계 (이 plan 범위 밖)

- Phase A(acceptance-builder·skeleton-builder), L(characterization-builder·safety-net-verifier),
  R(refactoring-scout) — Phase P+I 효과 확인 후 판단
- Plan Phase 팀 모드 전환 — 실증 결과 서브에이전트만으로 충분함이 확인됨(집계 경계
  스캔·`tools` 결함 잡기·80% 규칙 전부 순차 위임으로 달성). 지금 바꿀 근거가 약함
  (오버엔지니어링 경계) — 보류
- ~~관측 계층~~ → **완료 (1.35.0)**. `hooks/observe-agent-start.sh`(PreToolUse)·
  `observe-agent-end.sh`(PostToolUse)가 토큰 비용 0으로 에이전트 이름·소요 시간·성공
  여부를 `.claude/tdd-observability/agent-log.jsonl`에 기록. 책 원안의 토큰 필드는
  PostToolUse 입력에 없고 서브에이전트 격리 컨텍스트라 신뢰성 있게 못 얻어 제외

## 결정 로그

| 결정 | 채택 | 버린 대안 | 이유 |
|---|---|---|---|
| 실행 모드 | 서브에이전트 병렬 + 메인 통합 | 팀 모드(TeamCreate/SendMessage) | 책 기준 팬아웃은 팀이 정석이나, 팀 프리미티브가 이 플러그인에서 미검증. 효과 확인 후 전환 |
| 승인 구조 | 초안=에이전트, 승인=메인 | 에이전트에 전 단계 위임 | tdd-plan의 단계별 승인 게이트가 피드백 루프의 핵심 |
| 범위 | Phase P + I (8개) | 전체 라이프사이클(11~12개) | 검증되지 않은 설계를 대량 적용하는 위험 회피 |
| 검증 에이전트 tools | 읽기 전용 | 자연어로 "수정 금지" 선언 | 자연어는 안전장치가 아니다(delta A-2) |
| RGB 모드 | 서브 유지 | 팀 전환 | 패턴이 파이프라인(순차 의존)이라 팀 이점 제한적 |
| 적대적 리뷰 에이전트 | 신설 안 함(전역 `adversarial-reviewer` 사용) | `tdd-impl-critic` 신설(Task 4 원안) | 구현 중 `adversarial-review.md`를 실제로 읽어보니 이미 전역 에이전트로 위임하는 env-adaptive 구조가 있었음. plan 수립 시 이 파일을 읽지 않고 오판 |
