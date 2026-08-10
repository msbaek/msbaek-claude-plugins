# vault 기법 반영 (Getting Stuck 복구 + tdd-legacy) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Getting Stuck 2단계 복구 경로·테스트 목록 도출 절차를 기존 스킬에 추가하고, 레거시 코드 안전망 신규 스킬 `/tdd-legacy`를 신설한다.

**Architecture:** 설계 A는 기존 3개 파일의 텍스트 델타(agents/tdd-green.md, skills/tdd-rgb/SKILL.md, skills/tdd-plan/SKILL.md). 설계 B는 단일 신규 파일(skills/tdd-legacy/SKILL.md, agent 신설 없음) + README 동기화. 버전 범프는 이 계획 범위 밖(머지·배포 시점 별도).

**Tech Stack:** Claude Code plugin skill (markdown SKILL.md). 자동 테스트 하네스 없음 — 검증은 grep/Read 대조.

**Spec:** `docs/superpowers/specs/2026-08-10-vault-techniques-design.md`

## Global Constraints

- 스킬 이름 `tdd-legacy`, 범위는 안전망 구축 + 핸드오프까지 — seam 생성·의존성 깨기·리팩토링 실행은 범위 밖.
- mutation 도구: `mutate4java` agent 1순위, 없으면 내장 PIT(gradle/maven) 가이드 fallback.
- "ApprovalTests가 기본 선택" 단정 서술 금지 — 설계 품질 트레이드오프로 서술.
- 수정·생성 파일 외 기존 25개 스킬·agents 3개 무변경.
- 작업 브랜치 `feat/vault-techniques`. 커밋은 temp 파일 + `git commit -F`(heredoc 금지), 메시지 끝에 두 줄:
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` / `Claude-Session: https://claude.ai/code/session_0142iF2mAMrVyBK9ixSruQGz`
- 경로는 repo 루트 `~/git/msbaek-claude-plugins/` 기준.

---

### Task 1: Getting Stuck 2단계 복구 (tdd-green + tdd-rgb)

**Files:**
- Modify: `msbaek-tdd/agents/tdd-green.md:105`
- Modify: `msbaek-tdd/skills/tdd-rgb/SKILL.md:479-484` (Red 단계 블록)

**Interfaces:**
- Consumes: 없음
- Produces: tdd-green의 "Getting Stuck 복구 경로" 2단계 텍스트 — Task 2가 아니라 tdd-rgb Red 가드레일(이 태스크 내)이 참조. 참조 문구: "Getting Stuck 복구 경로"

- [ ] **Step 1: tdd-green.md의 단일 경로를 2단계로 교체**

`msbaek-tdd/agents/tdd-green.md`에서:

```
old: **주의사항**: Getting Stuck 위험 - 막히면 즉시 Fake it으로 전환
```

을 다음으로 교체:

```markdown
**주의사항 — Getting Stuck 복구 경로 (순서 준수)**:

1. **테스트가 너무 큰 도약인지 먼저 판단** — 그렇다면 **Write a simpler test**:
   현재 테스트를 잠시 치우고 더 단순한 테스트로 후퇴한다(Red로 복귀, tdd-red 인계).
   Getting Stuck의 원인은 잘못된(너무 구체적인) 테스트 또는 너무 일반적인 코드일 수
   있으므로 Fake it으로 해결되지 않는 경우가 있다.
2. **테스트 크기가 적절한데 구현이 안 보이면** — Fake it으로 전환한다.
```

- [ ] **Step 2: tdd-rgb Red 단계에 가드레일 추가**

`msbaek-tdd/skills/tdd-rgb/SKILL.md`의 Red 단계 블록에서:

```
old:
- 실패하는 테스트 작성
- approved.txt 파일 생성 (필요 시)

new:
- 실패하는 테스트 작성
- 테스트 추가 후 구현 방향이 즉시 떠오르지 않으면 Getting Stuck으로 간주 —
  tdd-green의 "Getting Stuck 복구 경로"(더 단순한 테스트로 후퇴 우선)를 따른다.
  후퇴 결정은 Red/Green 경계를 넘으므로 오케스트레이터가 인지하고 조율한다
- approved.txt 파일 생성 (필요 시)
```

- [ ] **Step 3: 편집 결과 확인**

Run: `grep -n "Getting Stuck" msbaek-tdd/agents/tdd-green.md msbaek-tdd/skills/tdd-rgb/SKILL.md`
Expected: tdd-green에 "Getting Stuck 복구 경로" 1건(단일 경로 "즉시 Fake it으로 전환" 문구는 0건), tdd-rgb에 가드레일 1건.

- [ ] **Step 4: Commit**

subject: `feat(tdd-green): Getting Stuck 복구를 2단계 경로로 — simpler test 우선`
body 요지: 단일 경로(즉시 Fake it)는 잘못된 테스트가 원인인 경우를 못 다룸(Uncle Bob §6.4). ① 더 단순한 테스트로 후퇴 ② Fake it 순서로 정렬, tdd-rgb Red에 오케스트레이터 가드레일 연결.

---

### Task 2: tdd-plan 테스트 목록 도출 절차

**Files:**
- Modify: `msbaek-tdd/skills/tdd-plan/SKILL.md` (단계 3 본문, "RGB 구현 순서는 ... 정렬한다." 단락 뒤)

**Interfaces:**
- Consumes: 없음
- Produces: 없음 (말단)

- [ ] **Step 1: 도출 절차 삽입**

`msbaek-tdd/skills/tdd-plan/SKILL.md` 단계 3에서 아래 단락:

```
**RGB 구현 순서는 Gherkin 시나리오 + unit test를 합쳐 Degenerate → General로
정렬한다.**
```

바로 뒤에 삽입:

```markdown
**Degenerate → General 순서의 도출 절차** (결과가 아니라 만드는 방법):

1. 가장 중요한 테스트(핵심 시나리오)를 먼저 적는다
2. 거기 도달하기 위한 징검다리(stair-step) 테스트를 거슬러 내려간다
3. most degenerate 테스트를 발견할 때까지 반복한다
4. 목록을 **reverse order로 정렬**해 degenerate-first 순서를 만든다
```

- [ ] **Step 2: 편집 결과 확인**

Run: `grep -n "도출 절차\|reverse order" msbaek-tdd/skills/tdd-plan/SKILL.md`
Expected: 도출 절차 1건 + reverse order 1건, 삽입 위치가 "RGB 구현 순서는" 단락 직후.

- [ ] **Step 3: Commit**

subject: `feat(tdd-plan): 테스트 목록 degenerate-first 도출 절차 추가`
body 요지: 결과(Degenerate→General 정렬)만 있고 도출 방법이 없던 공백을 절차화 — 중요 테스트에서 stair-step으로 역추적 후 reverse order 정렬 (Uncle Bob §6.5).

---

### Task 3: /tdd-legacy 스킬 신설

**Files:**
- Create: `msbaek-tdd/skills/tdd-legacy/SKILL.md`

**Interfaces:**
- Consumes: 없음
- Produces: `/tdd-legacy` 스킬 — Task 4의 README가 이 이름·3단계 구성을 참조

- [ ] **Step 1: SKILL.md 생성**

`msbaek-tdd/skills/tdd-legacy/SKILL.md`를 아래 내용 그대로 생성:

````markdown
---
name: tdd-legacy
description: 테스트 없는 기존 코드에 행위 보존 안전망(Characterization → Approval → Mutation)을 구축한 뒤 개선 스킬로 핸드오프. "레거시에 테스트 추가", "안전망 구축", "characterization test" 요청 시 사용. /tdd-legacy로 호출.
argument-hint: "<대상 클래스 FQCN 또는 파일 경로>"
---

# TDD Legacy — 레거시 코드 안전망 구축

테스트 없는 기존 코드의 현재 행위를 고정하는 안전망을 만들고, 개선은 기존 스킬로 넘깁니다.

## GOAL

- **성공 = 대상 코드의 현재 행위가 테스트로 고정되고, mutation 검증으로 안전망의
  실효성이 확인되며, 개선 스킬로 핸드오프됨**
- characterization 테스트가 현재 행위(옳은 행위가 아니라)를 기록함
- 모든 어설션이 sabotage 검증을 통과함 (동어반복 어설션 없음)
- mutation score가 합의된 임계값에 도달함 (기본: 대상 메소드 기준 100%)
- `/tdd-tidy` 또는 `/system-wide-refactoring` 핸드오프 안내로 종료

## CONSTRAINTS

### Hard Rules

- **현재 행위를 기록한다** — 버그로 보이는 동작도 일단 고정한다. 수정은 안전망
  완성 후 별도 작업 (발견한 의심 동작은 사용자에게 보고만).
- **프로덕션 코드를 변경하지 않는다** — 이 스킬의 산출물은 테스트뿐이다.
  sabotage로 일시 변경한 코드는 반드시 원복하고 커밋에 포함하지 않는다.
- 단계(1→2→3) 경계마다 사용자 검토 후 진행 (레거시는 확신이 낮은 상황 —
  기어 모델의 low 상당 밀도로 고정).
- 리팩토링·seam 생성·의존성 깨기는 범위 밖 — 필요하면 핸드오프 후 진행.

### Principles

- 테스트하기 어려운 의존성(DB·시간·랜덤)이 있으면 값을 고정할 수 있는 가장 얇은
  방법(고정 입력, 시스템 프로퍼티, 테스트 전용 설정)을 먼저 찾고, 그걸로 안 되면
  그 지점을 사용자에게 보고한다 — 의존성 깨기는 이 스킬이 하지 않는다.
- unit test vs approval test는 트레이드오프다: 설계가 매우 나쁠 때는 approval이
  효율적이고, 설계가 좋아지면 composable한 unit test가 낫다. 둘은 공존 가능하다.

## OUTPUT FORMAT

### 호출 형식

```
/tdd-legacy <대상 클래스 FQCN 또는 파일 경로>
```

### 1단계: Characterization — 현재 행위 고정

1. **대상 선정**: 인자의 클래스에서 변경 예정 지점(사용자에게 확인) 우선.
   public 메소드부터, 입력 조합이 단순한 것부터.
2. **golden master 작성**: 대표 입력으로 현재 출력을 그대로 어설션에 고정.
   기대값을 추측하지 말고 실제 실행 결과를 기록한다.
3. **어설션 정확성 검증 — SUT sabotage**: 통과하는 어설션마다
   - SUT를 일시적으로 깨서(값 하나 변경 등) 테스트를 실행
   - 해당 어설션이 실제로 실패하는지 확인
   - 원복 후 다시 통과 확인
   - 실패하지 않는 어설션 = 동어반복 — 어설션을 고친다
4. **비결정 출력 정규화 — scrubber**: 타임스탬프·랜덤·해시·순서 등 실행마다
   변하는 부분은 정규화(치환) 후 비교한다.
5. 커밋: `test: <대상> characterization 테스트 추가` (reviewable-commits 표준 —
   body에 어떤 행위를 고정했고 sabotage 검증 결과를 기록)
6. **사용자 검토 대기** — 고정한 행위 목록과 의심 동작 보고

### 2단계: Approval — 조합 커버리지 확장

1. 입력 조합이 많은 메소드는 `CombinationApprovals.verifyAllCombinations()`로
   조합 전체를 승인 파일에 고정 (approvaltests 의존성 필요 — 없으면 추가를
   사용자에게 확인).
2. 조합이 적거나 설계가 깨끗한 부분은 1단계의 unit 스타일을 유지 —
   전환은 트레이드오프 판단이며 전부 approval로 바꾸지 않는다.
3. 승인 파일(approved.txt)도 scrubber 적용.
4. 커밋: `test: <대상> combination approval 추가`
5. **사용자 검토 대기** — 커버한 조합 범위 보고

### 3단계: Mutation 검증 — 안전망 실효성 확인

1. **도구 선택**:
   - 환경에 `mutate4java` agent가 있으면 그것으로 dispatch (1순위)
   - 없으면 PIT를 직접 설정:
     - Gradle: `plugins { id "info.solidsoft.pitest" version "1.15.0" }` +
       `pitest { targetClasses = ["<대상 FQCN>"] }` → `./gradlew pitest`
     - Maven: `org.pitest:pitest-maven` 플러그인 `<targetClasses>` 설정 →
       `mvn test-compile org.pitest:pitest-maven:mutationCoverage`
2. 대상 클래스에 mutation 실행 → 살아남은 뮤턴트 = 안전망의 구멍
3. 뮤턴트를 죽이는 테스트를 보강하고 재실행 (반복)
4. **DoD**: 대상 메소드 기준 mutation score 100% 또는 사용자가 합의한 임계값
5. 커밋: `test: <대상> 뮤턴트 킬 테스트 보강`
6. **사용자 검토 대기** — mutation score 전/후 보고

### 완료: 핸드오프

안전망 완료를 보고하고 종료한다:

> 안전망 완료 (characterization N개 + approval M개, mutation score X%).
> 이제 개선을 진행하세요: 코드 정리는 `/tdd-tidy`, 구조 개선은
> `/system-wide-refactoring`. 새 기능 추가는 `/tdd-feature`.

개선 실행은 이 스킬 범위 밖이다.

## FAILURE CONDITIONS

- [ ] characterization 어설션 중 sabotage 검증을 거치지 않은 것이 있다
- [ ] 프로덕션 코드 변경이 커밋에 포함됐다 (sabotage 원복 누락)
- [ ] "현재 행위"가 아니라 "옳다고 생각하는 행위"를 어설션에 넣었다
- [ ] mutation 검증 없이 안전망 완료를 선언했다
- [ ] 단계 경계에서 사용자 검토 없이 다음 단계로 진행했다
- [ ] 리팩토링/의존성 깨기를 이 스킬 안에서 수행했다
````

- [ ] **Step 2: 생성 결과 확인**

Run: `grep -n "name: tdd-legacy\|sabotage\|scrubber\|CombinationApprovals\|mutate4java\|핸드오프" msbaek-tdd/skills/tdd-legacy/SKILL.md | head`
Expected: 전부 1건 이상. `grep -c "기본 선택" → 0` (ApprovalTests 단정 서술 없음).

- [ ] **Step 3: Commit**

subject: `feat(tdd-legacy): 레거시 안전망 스킬 신설 — characterization/approval/mutation`
body 요지: 기존 25개 스킬이 모두 신규 코드 전제 — 테스트 없는 기존 코드 진입점 공백을 메움. sabotage 어설션 검증 + scrubber + 트레이드오프 서술 + mutate4java 우선/PIT fallback. 개선은 tdd-tidy·system-wide-refactoring 핸드오프.

---

### Task 4: README 동기화

**Files:**
- Modify: `README.md` (핵심 워크플로우 절, 디렉토리 트리, Skills·Agents 관계도)

**Interfaces:**
- Consumes: Task 3의 스킬 이름 `tdd-legacy`와 3단계 구성
- Produces: 없음 (말단)

- [ ] **Step 1: 핵심 워크플로우에 /tdd-legacy 절 추가**

`#### /tdd-tidy — 독립 Tidying` 절 **바로 앞**에 삽입:

```markdown
#### `/tdd-legacy` — 레거시 코드 안전망 구축

테스트 없는 기존 코드의 현재 행위를 고정하는 안전망을 만들고, 개선은 기존 스킬로 넘깁니다.

```
/tdd-legacy <대상 클래스 FQCN 또는 파일 경로>
```

- **1단계 Characterization** — golden master로 현재 행위 고정, SUT sabotage로 어설션 검증, scrubber로 비결정 출력 정규화
- **2단계 Approval** — 조합 폭발 구간은 CombinationApprovals로 확장 (unit vs approval은 설계 품질 트레이드오프)
- **3단계 Mutation 검증** — mutate4java(있으면) 또는 PIT로 안전망 실효성 확인
- 완료 후 `/tdd-tidy`·`/system-wide-refactoring`으로 핸드오프 (개선은 범위 밖)
```

- [ ] **Step 2: 디렉토리 트리·관계도 갱신**

디렉토리 트리의 `│   │   ├── cucumber-acceptance/      # /cucumber-acceptance 인수 테스트 구축` 다음 줄에:

```
│   │   ├── tdd-legacy/               # /tdd-legacy 레거시 안전망 구축
```

Skills과 Agents 관계도의 `/cucumber-acceptance` 블록 뒤에:

```
/tdd-legacy (레거시 안전망)
 ├── Characterization (sabotage 검증 + scrubber)
 ├── Approval (CombinationApprovals)
 └── Mutation 검증 (mutate4java/PIT) → tdd-tidy·system-wide-refactoring 핸드오프
```

- [ ] **Step 3: 편집 결과 확인**

Run: `grep -n "tdd-legacy" README.md`
Expected: 워크플로우 절·트리·관계도 3곳 이상.

- [ ] **Step 4: Commit**

subject: `docs: README에 /tdd-legacy 사용법 추가`
body 요지: 신규 스킬의 사용자 진입점 문서화 — 3단계 요약과 핸드오프 경계 명시.

---

### Task 5: 스펙 대조 최종 검증

**Files:**
- Read: `docs/superpowers/specs/2026-08-10-vault-techniques-design.md`, 수정·생성된 4개 파일

**Interfaces:**
- Consumes: Task 1~4 전체
- Produces: 검증 보고

- [ ] **Step 1: 승인 조건 5개 대조**

스펙 "검증(승인 조건)" 1~5 각각에 해당 파일 구절을 인용해 대조표 작성:
1. tdd-green 2단계 복구 + "즉시 Fake it" 단일 경로 부재
2. tdd-plan 4단계 도출 절차
3. tdd-legacy의 3단계 + sabotage + scrubber + 트레이드오프 + fallback + 핸드오프
4. "ApprovalTests가 기본" 단정 서술 없음 (`grep "기본 선택"` 0건)
5. 대상 외 파일 무변경: `git diff main --stat`가 4개 파일 + 스펙/플랜 문서만 보여야 함

- [ ] **Step 2: 최종 보고**

대조표 + `git log main..feat/vault-techniques --oneline` 보고. 버전 범프·머지는 이 계획 범위 밖(사용자 결정).
