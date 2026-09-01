# tdd-plan Spec Anchored 전환 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/tdd-plan`을 얇은 앵커 문서 + 에이전트 1회 + 리뷰 1회의 경량 플로우로 교체하고, 구현 단계(tdd-rgb·tdd-feature)에 "배움 → 앵커 먼저 갱신 → 같은 커밋" 게이트를 연결한다. 현행 풀 플로우는 `--full`로 보존한다.

**Architecture:** 문서 편집만 있는 작업이다(코드 없음). 신규 에이전트 1개 + 신규 references 2개를 만들고, 스킬 2개(tdd-plan·tdd)를 재작성/수정하고, 구현 스킬·에이전트 5개에 앵커 게이트 인용을 추가한다. 플러그인의 no-restatement 원칙에 따라 게이트 본문은 `references/anchor-update.md` 한 곳에만 쓰고 나머지는 경로 인용한다.

**Tech Stack:** Markdown (Claude Code plugin: skills + agents + references)

**Spec:** `docs/superpowers/specs/2026-09-01-tdd-plan-spec-anchored-design.md`

## Global Constraints

- 이 저장소는 워크트리 없이 main에서 직접 작업한다 (memory: no-worktree-work-in-place)
- 커밋 메시지: 제목 1줄 + bullet 2~4줄, 한글은 임시 파일 + `git commit -F` (`msbaek-tdd/references/commit-style.md`)
- 에이전트/스킬이 다른 파일의 규율을 쓸 때는 재기술하지 않고 경로로 인용한다 (drift 방지)
- 앵커 문서 템플릿에 산문 계층(정본 선언·INVEST·제외 근거) 금지 — 규율은 에이전트 지침으로만
- 앵커 문서에 Gherkin 코드블록 사본 금지 — `.feature` 경로만 가리킨다
- 기존 3 에이전트(tdd-domain-modeler·tdd-example-designer·tdd-test-list)와 tdd-plan-critic은 삭제하지 않는다 (`--full` 전용)
- 검증 = grep 확인 (게이트 인용 wiring은 모든 완료 경로를 grep으로 확인 — memory: gate-wiring-check-all-completion-paths)
- 릴리스 시 `.claude-plugin/marketplace.json`과 `msbaek-tdd/.claude-plugin/plugin.json` 버전을 함께 bump

## File Structure

| 파일 | 작업 | 책임 |
|---|---|---|
| `msbaek-tdd/agents/tdd-anchor-drafter.md` | Create | 앵커 초안(규칙+예제표+미확정+.feature 초안) 1회 산출. 기존 3 에이전트의 규율 흡수 |
| `msbaek-tdd/references/anchor-update.md` | Create | 배움 반영 게이트 정본 (앵커 먼저 갱신·같은 커밋·규칙 변경만 질문) |
| `msbaek-tdd/skills/tdd-plan/references/full-plan.md` | Create | 현행 풀 플로우(단계 1~3 + critic) 명세 이동처 |
| `msbaek-tdd/skills/tdd-plan/SKILL.md` | Rewrite | 경량 앵커 플로우 기본 + `--full` 분기 |
| `msbaek-tdd/skills/tdd/SKILL.md` | Modify | 템플릿을 앵커 구조로 교체 (general 2단계, web-app 8단계), 상태 판단 문구 갱신 |
| `msbaek-tdd/skills/tdd-rgb/SKILL.md`, `skills/tdd-feature/SKILL.md`, `agents/tdd-red.md`, `agents/tdd-green.md`, `agents/tdd-blue.md` | Modify | 앵커 게이트 인용 + FAILURE CONDITIONS 1줄 |
| `msbaek-tdd/skills/tdd-plan/references/web-app-persistence.md`, `agents/tdd-skeleton-builder.md` | Modify | 단계 번호 재배열 반영 (6·7단계 → 4·5단계 등) |
| `README.md` | Modify | 워크플로우 표·mermaid·에이전트 목록 갱신 |
| `.claude-plugin/marketplace.json`, `msbaek-tdd/.claude-plugin/plugin.json` | Modify | 1.43.0 bump |

**단계 번호 확정 (web-app, 10 → 8단계):**

| 새 번호 | 내용 | 이전 번호 |
|---|---|---|
| 1 | 앵커 작성 (규칙 + 예제 검산표 + 미확정) | 1·2·4 통합 |
| 2 | 인수 테스트 셋업 (.feature + Runner, @pending) | 3 |
| 3 | Walking Skeleton 구현 | 5 |
| 4 | 테스트 구현 (RGB 사이클) | 6 |
| 5 | JPA Repository 완성 | 7 |
| 6 | DSL 개선 | 8 |
| 7 | 적대적 리뷰 | 9 |
| 8 | 하드닝 게이트 | 10 |

General은 4 → 2단계: 1. 앵커 작성, 2. 테스트 구현 (RGB 사이클).

---

### Task 1: 배움 반영 게이트 정본 `references/anchor-update.md`

**Files:**
- Create: `msbaek-tdd/references/anchor-update.md`

**Interfaces:**
- Produces: 상대경로 인용 대상 — agents에서 `../references/anchor-update.md`, skills에서 `../../references/anchor-update.md`

- [ ] **Step 1: 파일 작성**

```markdown
# 배움 반영 게이트 (anchor update)

구현 중 앵커 문서(템플릿 *.md의 규칙·예제)와 어긋나는 배움을 발견했을 때의 절차.
Spec Anchored의 핵심 규약 — 앵커는 살아 있는 문서이고, 코드보다 먼저 갱신된다.

## 절차

1. **멈춘다** — 어긋난 채 코드를 먼저 고치지 않는다
2. **앵커를 먼저 갱신한다** — 해당하는 곳에:
   - 규칙이 틀렸거나 부족 → `## 규칙` 수정/추가 + `## 배움 로그`에 "규칙 N 변경: [한 줄]"
   - 예제 값이 틀림 → `## 예제` 표 수정 + 배움 로그 한 줄
   - 규칙·예제와 무관한 발견(구현 세부·기술 선택) → `## 배움 로그`에 한 줄만
3. **코드를 변경한다**
4. **같은 커밋에 담는다** — 앵커 갱신과 코드 변경을 분리하지 않는다
   (체크박스-커밋 동기화 규칙의 일반형)

## 사용자 질문 기준

- **규칙이 바뀌는 배움만** 사용자에게 질문한다 — 동작 계약이 바뀌므로
  (예: "취소 가능 기한이 명세와 달리 D+7이어야 할 것 같습니다")
- 나머지(배움 로그만 추가되는 발견)는 질문 없이 자율 기록한다

## Gherkin과의 관계

- `.feature` 파일이 시나리오의 실행되는 정본이다 — 시나리오가 바뀌는 배움이면
  `.feature`를 갱신하고, 앵커에는 배움 로그 한 줄만 남긴다
- 앵커 문서에 Gherkin 사본을 만들지 않는다

## FAILURE CONDITIONS

- 앵커와 어긋난 코드 변경을 앵커 갱신 없이 커밋
- 앵커 갱신과 코드 변경을 다른 커밋으로 분리
- 규칙이 바뀌는 배움을 질문 없이 자율 반영
```

- [ ] **Step 2: 커밋**

```bash
git add msbaek-tdd/references/anchor-update.md
git commit -m "docs(msbaek-tdd): 배움 반영 게이트 정본 references/anchor-update.md 추가"
```

---

### Task 2: 신규 에이전트 `tdd-anchor-drafter`

**Files:**
- Create: `msbaek-tdd/agents/tdd-anchor-drafter.md`

**Interfaces:**
- Consumes: 없음 (plan-input 문서 경로 + 템플릿 문서 경로를 prompt로 받음)
- Produces: 템플릿 문서의 `## 규칙`·`## 예제 (검산표)`·`## 미확정` 채움 + `.feature` 초안 텍스트를 산출(파일 저장은 E-1의 cucumber-acceptance 몫). Task 3의 tdd-plan SKILL.md가 이 에이전트를 1회 호출

- [ ] **Step 1: 파일 작성**

```markdown
---
name: tdd-anchor-drafter
description: TDD Plan 경량 모드 전담 — 원천 자료에서 앵커 문서(규칙·예제 검산표·미확정)와 .feature용 Gherkin 초안을 1회 호출로 작성한다. tdd-plan 스킬 기본 플로우가 호출, 초안 후 메인이 사용자 리뷰 1회를 받는다.
tools: Read, Write, Edit, Grep, Glob
---

# TDD Anchor Drafter

원천 자료(plan-input 문서·사용자 요구)를 읽고 얇은 앵커를 초안한다.
산출은 템플릿 문서의 세 섹션 + `.feature` 초안 — 그 이상 쓰지 않는다.

## GOAL

- **성공 = 템플릿 문서의 `## 규칙`·`## 예제 (검산표)`·`## 미확정`이 채워지고,
  `.feature`용 Gherkin 초안이 응답으로 반환됨**
- 규칙: 도메인 규칙을 한 줄씩 번호 목록으로 (계산·절사·상태·검증 순서 불변식 포함)
- 예제: 값의 정본인 검산표 — 대표 입력의 단계별 계산 결과를 표로, 각 행에 걸리는 규칙 번호
- 미확정: 원천 자료로 결정할 수 없는 항목을 질문 형태로
- Gherkin 초안: 핵심 예시만 (happy path·경계·대표 예외) — 응답 텍스트로 반환하고
  문서에는 쓰지 않는다

## CONSTRAINTS

### 흡수한 규율 (산출은 얇게, 규율은 지킨다)

1. **검산 전개** — 계산 도메인이면 대표 입력 1건의 단계별 계산을 예제 표에 담는다.
   표의 값이 곧 정본이다 (별도 산문 선언은 쓰지 않는다)
2. **경계 조건 5종 스캔** — 수치·크기·상태·시간·집계 경계를 훑고, 해당하는 것만
   규칙/예제/Gherkin에 반영한다. 집계 경계(같은 키가 여러 항목으로 나뉘어 항목별
   통과·합산 위반)는 합산되는 자원(재고·한도·쿠폰·포인트)이 있으면 반드시 예제로 만든다
3. **Degenerate → General** — Gherkin 시나리오를 가장 단순한 특수 케이스부터
   일반 케이스 순으로 정렬한다
4. **invent 금지** — 원천 자료에 없는 값·규칙·인터페이스를 지어내지(invent) 않는다.
   불명확하면 `## 미확정`에 질문으로 남긴다
5. **핵심 예시만** — 망라적 edge 나열 금지. Gherkin에 없는 세밀 분기는 목록으로
   만들지 않는다 — 구현 중 발견 시 배움 반영 게이트(`../references/anchor-update.md`)로
   규칙에 추가된다

### 쓰지 않는 것

- 산문 계층: 정본 선언, 파생 뷰 선언, INVEST 점검, 제외 근거 나열, User Story 서식
- Gherkin 코드블록을 앵커 문서에 복사 (drift 원천 — `.feature`가 정본)
- 커밋 (메인이 사용자 리뷰 후 커밋한다)

## OUTPUT FORMAT

응답 구조:

1. 문서에 쓴 규칙·예제·미확정 요약 (섹션당 1~2줄)
2. `.feature`용 Gherkin 초안 전문 (코드블록)
3. "확인 필요" — 미확정 항목을 사용자 질문 형태로

## FAILURE CONDITIONS

- 원천 자료에 없는 값·규칙을 지어냄 (미확정으로 남기지 않고)
- 앵커 문서에 Gherkin 사본·산문 계층을 씀
- 세밀 분기 목록(unit test 목록)을 만듦 — 경량 모드에 그 단계는 없다
- 커밋을 수행함
```

- [ ] **Step 2: 검증 — 산문 계층·Gherkin 사본 금지 규율이 파일에 있는지 grep**

Run: `grep -c "산문 계층\|invent\|사본" msbaek-tdd/agents/tdd-anchor-drafter.md`
Expected: 3 이상

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/agents/tdd-anchor-drafter.md
git commit -m "feat(msbaek-tdd): tdd-anchor-drafter 에이전트 — 경량 plan 앵커 초안 1회 산출"
```

---

### Task 3: 풀 플로우 이동 + tdd-plan SKILL.md 재작성

**Files:**
- Create: `msbaek-tdd/skills/tdd-plan/references/full-plan.md`
- Rewrite: `msbaek-tdd/skills/tdd-plan/SKILL.md`

**Interfaces:**
- Consumes: Task 2의 `tdd-anchor-drafter` (기본 플로우에서 1회 호출)
- Produces: `/tdd-plan` 기본 = 앵커 플로우, `/tdd-plan --full` = 풀 플로우. Task 4의 tdd/SKILL.md가 안내 문구에서 이 계약을 인용

- [ ] **Step 1: `references/full-plan.md` 생성 — 현행 SKILL.md 내용 이동**

현행 `skills/tdd-plan/SKILL.md`의 다음 블록을 **그대로 복사**해 담는다 (내용 수정 없음, 도입부만 추가):

- 단계 1 (요구사항 — 도메인 규칙 + User Story, tdd-domain-modeler 절차 포함): 현행 185~253행
- 단계 2 (Gherkin Scenario, tdd-example-designer 절차 포함): 현행 256~316행
- 단계 3 (Unit Test 목록, tdd-test-list 절차 + tdd-plan-critic 교차검증 포함): 현행 319~404행
- (조건부) Use Case 추가: 현행 407~432행
- 품질 체크리스트: 현행 482~491행

파일 도입부:

```markdown
# 풀 plan 플로우 (--full)

`/tdd-plan --full`이 따르는 현행 3단계 플로우의 정본. high-stakes(폭발 반경 큰 도메인)·
대형·다팀 작업에서 무거운 명세가 정당화될 때만 쓴다. 기본 경량 플로우는
`../SKILL.md`가 정본이다.

에이전트: tdd-domain-modeler(단계 1) → tdd-example-designer(단계 2) →
tdd-test-list(단계 3) → tdd-plan-critic(교차검증). 각 단계 승인 후 커밋.

풀 모드에서는 템플릿 문서에 `## 요구사항`·`## Gherkin Scenario`·`## Unit Test 목록`
섹션을 추가해 산출을 담는다 (앵커 섹션과 공존).
```

- [ ] **Step 2: `SKILL.md` 재작성**

frontmatter의 name·argument-hint·allowed-tools는 유지하되 description 갱신, 본문 전체 교체:

```markdown
---
name: tdd-plan
description: TDD Planning (Spec Anchored) - 얇은 앵커 문서(규칙 + 예제 검산표 + 미확정)를 에이전트 1회 + 사용자 리뷰 1회로 작성. --full로 현행 3단계 풀 플로우. /tdd-plan으로 호출.
argument-hint: "[plan-doc-path] [--full]"
allowed-tools: Write, Edit, Read, Bash(git add:*), Bash(git commit:*), Bash(git status:*)
---

# TDD Planning Skill (Spec Anchored)

얇은 앵커를 만들고, 구현 내내 살아 있게 유지한다. 앵커 = 규칙(한 줄씩) +
예제 검산표(값의 정본) + 미확정. 시나리오의 실행되는 정본은 `.feature`다
(`/cucumber-acceptance`) — 앵커 문서에 Gherkin 사본을 두지 않는다.

구현 중 배움은 `../../references/anchor-update.md`의 게이트로 앵커에 먼저
반영된다 — plan은 변경 가능함이 최우선 원칙이다.

## GOAL

- **성공 = 템플릿 문서의 앵커 섹션(규칙·예제·미확정)이 채워지고 사용자 리뷰 1회를
  통과하며, (web-app) E-1 인수 셋업·E-2 Walking Skeleton으로 이어짐**
- 승인 왕복은 기본 1회 — 앵커 초안 리뷰. 미확정 항목 질문은 그 리뷰에 함께 담는다
- CancelOrder급 도메인에서 앵커 문서 100줄 이하

## 기본 플로우 (경량)

1. **`tdd-anchor-drafter` 에이전트 1회 호출** — plan-input 문서(있으면)·템플릿 문서
   경로를 전달. 규칙·예제 검산표·미확정을 문서에 채우고 `.feature`용 Gherkin 초안을
   반환받는다
2. **사용자 리뷰 1회** — 앵커 내용 + Gherkin 초안 + 미확정 질문을 한 번에 제시.
   수정 요청이면 에이전트 재호출 또는 메인이 직접 반영
3. **커밋** — `git add [변경 파일]` (git add -A 금지) →
   `git commit -m "docs: 앵커 작성 - [기능명]"` → 체크박스 갱신
4. **(web-app) E-1: 인수 테스트 셋업** — `/cucumber-acceptance` 호출. 승인된 Gherkin
   초안이 `.feature`가 된다 (미구현 시나리오 `@pending`)
5. **(web-app) E-2: Walking Skeleton** — `tdd-skeleton-builder` 위임 (아래 참조)
6. **다음 단계 안내** — 기어에 맞는 `/tdd-rgb` 또는 `/tdd-feature` 호출 안내.
   구현 중 배움 반영 규약은 `../../references/anchor-update.md`가 정본

### 경량 모드에 없는 것

- Unit test 목록 단계 — Gherkin이 못 덮는 세밀 분기는 구현 중 발견 시
  앵커 `## 규칙`에 한 줄 추가로 대체 (배움 반영 게이트)
- critic 검증 — 사용자 리뷰 1회가 그 역할
- 단계별 승인 왕복 — 리뷰는 1회다

## --full 플로우

high-stakes(인증·결제·데이터 삭제·외부 API·동시성 등 폭발 반경 큰 도메인)·대형·
다팀 작업에서 사용자가 명시적으로 선택한다. 절차는
`references/full-plan.md`가 정본 — tdd-domain-modeler → tdd-example-designer →
tdd-test-list → tdd-plan-critic, 단계별 승인.

## Web App 추가 단계

(현행 SKILL.md의 "단계 E-1"·"단계 E-2" 섹션을 그대로 유지 — cucumber-acceptance
위임, tdd-skeleton-builder 위임, OSIV·트랜잭션 경계·LAZY·DTO 불변 규칙 포함)

## FAILURE CONDITIONS

- 앵커 문서에 산문 계층(정본 선언·INVEST·제외 근거)이나 Gherkin 사본을 씀
- 경량 모드에서 3 에이전트(domain-modeler·example-designer·test-list) 또는
  critic을 호출함
- 사용자가 --full을 선택하지 않았는데 unit test 목록 단계를 진행함
- 승인 왕복이 리뷰 1회 + 미확정 질문을 초과함 (사용자가 수정을 요청한 경우 제외)
```

주의: "Web App 추가 단계" 자리에는 위 괄호 설명이 아니라 **현행 SKILL.md 437~478행의 E-1·E-2 섹션 전문을 그대로 붙인다**. 단, E-2 내 "승인된 단계 2 문서 경로" 문구는 "승인된 앵커 문서 경로"로 바꾼다.

또한 현행 SKILL.md의 CONSTRAINTS 중 다음은 경량 SKILL.md에 유지한다 (구현·skeleton 단계가 계속 참조하는 내용): "조용한 실패" 섹션, "도구는 최초로 필요해진 시점에 추가한다" 섹션, "Act-Assert 동일 추상화 수준 규칙". 나머지(Test Addition Rule, FIRST 원칙, 요구사항 작성 원칙, 경계 조건 식별 가이드)는 full-plan.md와 tdd-anchor-drafter가 흡수했으므로 본체에서 제거한다. 단 경계 조건 식별 가이드(집계 경계 예시 포함, 현행 84~106행)는 tdd-anchor-drafter와 tdd-example-designer 둘 다 쓰므로 **full-plan.md로 옮기고** tdd-anchor-drafter에서는 요약(경계 5종 + 집계 경계 규칙)이 이미 Task 2에 있으니 추가로 `자세한 예시는 ../skills/tdd-plan/references/full-plan.md의 "경계 조건 식별 가이드" 참조` 한 줄을 붙인다.

- [ ] **Step 3: 검증**

Run: `grep -n "tdd-anchor-drafter\|--full\|anchor-update" msbaek-tdd/skills/tdd-plan/SKILL.md && grep -c "tdd-domain-modeler" msbaek-tdd/skills/tdd-plan/references/full-plan.md`
Expected: SKILL.md에 세 키워드 모두 존재, full-plan.md에 tdd-domain-modeler 1 이상

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/tdd-plan/SKILL.md msbaek-tdd/skills/tdd-plan/references/full-plan.md
git commit -F <임시파일>   # 제목: "feat(msbaek-tdd): tdd-plan을 Spec Anchored 경량 플로우로 재작성 — 풀 플로우는 --full로 이동"
```

---

### Task 4: `/tdd` 템플릿 앵커 구조로 교체 + 단계 번호 재배열

**Files:**
- Modify: `msbaek-tdd/skills/tdd/SKILL.md` (General 템플릿 129~149행, Web App 템플릿 153~196행, Case B 안내 96~104행)
- Modify: `msbaek-tdd/skills/tdd-plan/references/web-app-persistence.md` ("6단계"·"7단계"·"10단계" 표기)
- Modify: `msbaek-tdd/agents/tdd-skeleton-builder.md` ("단계 7" 표기)

**Interfaces:**
- Consumes: Task 3의 단계 계약 (앵커 작성이 1단계)
- Produces: File Structure의 "단계 번호 확정" 표 — 이후 모든 파일이 이 번호를 쓴다

- [ ] **Step 1: General 템플릿 교체 (4단계 → 2단계)**

```markdown
### General TDD 템플릿 (2단계)

​```markdown
# {ClassName} TDD 구현

## 절차
- [ ] 1. 앵커 작성 (규칙 + 예제 검산표 + 미확정)
- [ ] 2. 테스트 구현 (RGB 사이클)

## 규칙

## 예제 (검산표)

## 미확정

## 진행 기록

기어: low

## 배움 로그
​```
```

- [ ] **Step 2: Web App 템플릿 교체 (10단계 → 8단계)**

```markdown
### Web App TDD 템플릿 (8단계)

​```markdown
# AI와 Pair로 {ClassName}을 TDD로 구현하기 (Web App)

## 전체적인 절차
- [ ] 1. 앵커 작성 (규칙 + 예제 검산표 + 미확정)
- [ ] 2. 인수 테스트 셋업 (.feature + Runner, 미구현은 @pending — .feature가 시나리오의 실행되는 정본)
- [ ] 3. Walking Skeleton 구현
- [ ] 4. 테스트 구현 (RGB 사이클 — 각 Green이 자기 시나리오 @pending 해제)
- [ ] 5. JPA Repository 완성 (계약 테스트로 InMemory와 동등성 검증)
- [ ] 6. DSL 개선 (Steps·Protocol Driver·Test Data Builder)
- [ ] 7. 적대적 리뷰 (high 기어 또는 폭발 반경 high-stakes 시 — 5·6을 마친 뒤 실행, diff가 전체 구현을 포함해야 함)
- [ ] 8. 하드닝 게이트 (① CRAP·DRY 분석 → ② /system-wide-refactoring → ③ mutation 대표 파일 1개 — 제안만, 실행은 사용자 결정)

## 규칙

## 예제 (검산표)

## 미확정

## 진행 기록

기어: low

## 배움 로그
​```
```

기존 blockquote(Web App은 `/cucumber-acceptance` 필수...)는 그대로 유지한다.

- [ ] **Step 3: Case B 안내 문구 갱신 (tdd/SKILL.md 96~104행)**

"요구사항(도메인 규칙 + User Story)/Gherkin Scenario/unit test 목록 미완성" →
"앵커(규칙·예제·미확정) 미완성". `--full` 언급 1줄 추가: "high-stakes·대형 작업이면
`/tdd-plan --full`(3 에이전트 + critic 풀 플로우) 안내".

- [ ] **Step 4: 단계 번호 참조 전수 갱신**

Run: `grep -rn "단계 7\|단계 6\|6단계\|7단계\|8단계\|9단계\|10단계\|단계 9\|단계 10" msbaek-tdd/ README.md`

발견되는 각 참조를 "단계 번호 확정" 표의 새 번호로 바꾼다. 알려진 위치:
- `skills/tdd-plan/references/web-app-persistence.md` — "6단계 RGB" → "4단계 RGB", "7단계 JPA" → "5단계 JPA", "10단계" → "8단계"
- `agents/tdd-skeleton-builder.md:84` — "단계 7" → "단계 5"
- README.md 113행 워크플로우 표 — Task 6에서 처리 (여기서는 목록만 확인)

- [ ] **Step 5: 검증 — 옛 번호 잔존 없음**

Run: `grep -rn "10단계\|단계 10" msbaek-tdd/skills/tdd/ msbaek-tdd/skills/tdd-plan/ msbaek-tdd/agents/`
Expected: 결과 없음

- [ ] **Step 6: 커밋**

```bash
git add msbaek-tdd/skills/tdd/SKILL.md msbaek-tdd/skills/tdd-plan/references/web-app-persistence.md msbaek-tdd/agents/tdd-skeleton-builder.md
git commit -F <임시파일>   # 제목: "feat(msbaek-tdd): /tdd 템플릿을 앵커 구조로 교체 — web-app 8단계·general 2단계"
```

---

### Task 5: 배움 반영 게이트 연결 (tdd-rgb · tdd-feature · R/G/B 에이전트)

**Files:**
- Modify: `msbaek-tdd/skills/tdd-rgb/SKILL.md` (본문 규칙 1곳 + FAILURE CONDITIONS 372행 이하)
- Modify: `msbaek-tdd/skills/tdd-feature/SKILL.md` (본문 1곳 + FAILURE CONDITIONS 285행 이하)
- Modify: `msbaek-tdd/agents/tdd-red.md` (본문 1곳 + FAILURE CONDITIONS 191행 이하)
- Modify: `msbaek-tdd/agents/tdd-green.md` (본문 1곳 + FAILURE CONDITIONS 163행 이하)
- Modify: `msbaek-tdd/agents/tdd-blue.md` (본문 1곳 + FAILURE CONDITIONS 117행 이하)

**Interfaces:**
- Consumes: Task 1의 `references/anchor-update.md`

- [ ] **Step 1: 스킬 2개에 게이트 인용 추가**

tdd-rgb·tdd-feature SKILL.md 각각의 진행 규칙 섹션(커밋 규칙 인근)에:

```markdown
### 배움 반영 게이트 (Spec Anchored)

구현 중 앵커 문서(규칙·예제)와 어긋나는 배움을 발견하면 코드보다 앵커를 먼저
갱신하고 같은 커밋에 담는다. 규칙이 바뀌는 배움만 사용자에게 질문한다.
절차·기준은 `../../references/anchor-update.md`가 정본.
```

FAILURE CONDITIONS에 1줄 추가:

```markdown
- 앵커와 어긋난 코드 변경을 앵커 갱신 없이(또는 다른 커밋으로) 커밋함
```

- [ ] **Step 2: 에이전트 3개에 게이트 인용 추가**

tdd-red·tdd-green·tdd-blue 각각의 작업 규칙 섹션에 (에이전트는 stage만 하고 커밋은 오케스트레이터 몫인 high 기어 경로가 있으므로 "커밋"이 아니라 "보고"로 쓴다):

```markdown
### 배움 반영 (Spec Anchored)

작업 중 앵커 문서(규칙·예제)와 어긋나는 발견이 있으면 코드만 고치지 말고
앵커 문서를 먼저 갱신한 뒤 코드를 변경하고, 완료 보고에 "앵커 갱신: [내용]"을
명시한다 — 오케스트레이터가 같은 커밋에 담는다. 규칙이 바뀌는 발견은 갱신하지
말고 보고만 한다 (사용자 질문은 오케스트레이터 몫).
절차는 `../references/anchor-update.md`가 정본.
```

FAILURE CONDITIONS에 1줄 추가:

```markdown
- 앵커와 어긋난 발견을 앵커 갱신(또는 보고) 없이 코드에만 반영함
```

- [ ] **Step 3: 검증 — 모든 완료 경로 wiring 확인**

Run: `grep -rln "anchor-update" msbaek-tdd/skills/tdd-rgb/ msbaek-tdd/skills/tdd-feature/ msbaek-tdd/agents/tdd-red.md msbaek-tdd/agents/tdd-green.md msbaek-tdd/agents/tdd-blue.md msbaek-tdd/skills/tdd-plan/SKILL.md`
Expected: 6개 파일 모두 출력 (memory: gate-wiring-check-all-completion-paths)

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/tdd-rgb/SKILL.md msbaek-tdd/skills/tdd-feature/SKILL.md msbaek-tdd/agents/tdd-red.md msbaek-tdd/agents/tdd-green.md msbaek-tdd/agents/tdd-blue.md
git commit -F <임시파일>   # 제목: "feat(msbaek-tdd): 구현 스킬·에이전트에 배움 반영 게이트 연결"
```

---

### Task 6: README·문서 동기화

**Files:**
- Modify: `README.md` (워크플로우 mermaid 다이어그램, 113행 워크플로우 표, 에이전트 목록, tdd-plan 스킬 설명)

- [ ] **Step 1: README 갱신**

1. 워크플로우 표(113행 인근): "10단계" → "8단계", plan 구간을 "앵커 작성(에이전트 1회 + 리뷰 1회)"으로
2. mermaid 다이어그램: plan 구간 노드를 `tdd-anchor-drafter → 사용자 리뷰 → E-1 → E-2`로 교체, `--full` 분기 노드 추가 (tdd-domain-modeler → example-designer → test-list → critic)
3. 에이전트 목록에 `tdd-anchor-drafter` 추가, 기존 3 에이전트 + critic에 "(--full 전용)" 표기
4. Spec Anchored 원칙 1문단 추가: 앵커는 살아 있는 문서, 배움 → 앵커 먼저 → 같은 커밋 (`msbaek-tdd/references/anchor-update.md` 인용)

- [ ] **Step 2: 검증**

Run: `grep -n "anchor-drafter\|--full\|8단계" README.md && grep -rn "10단계" README.md`
Expected: 앞 3개 키워드 존재, "10단계" 결과 없음

- [ ] **Step 3: 커밋**

```bash
git add README.md
git commit -F <임시파일>   # 제목: "docs(msbaek-tdd): README를 Spec Anchored 플로우로 동기화"
```

---

### Task 7: 릴리스 1.43.0

**Files:**
- Modify: `.claude-plugin/marketplace.json` (msbaek-tdd version)
- Modify: `msbaek-tdd/.claude-plugin/plugin.json` (version)

- [ ] **Step 1: 두 파일의 버전을 1.43.0으로 bump** (memory: plugin-release-version-sync — 두 곳 함께)

- [ ] **Step 2: 검증**

Run: `grep -n "1.43.0" .claude-plugin/marketplace.json msbaek-tdd/.claude-plugin/plugin.json`
Expected: 두 파일 모두 1건씩

- [ ] **Step 3: 커밋**

```bash
git add .claude-plugin/marketplace.json msbaek-tdd/.claude-plugin/plugin.json
git commit -F <임시파일>   # 제목: "chore(msbaek-tdd): 1.43.0 릴리스 — Spec Anchored plan 전환"
```
