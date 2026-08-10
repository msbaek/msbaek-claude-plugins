# Driving In Gears (기어 모델) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/tdd-rgb`에 기어(low/mid/high)를 도입해 사용자 검토 지점의 밀도를 확신·폭발 반경에 따라 조절한다.

**Architecture:** 오케스트레이터(tdd-rgb SKILL.md)만 기어 로직을 갖는다. R/G/B agent 3개는 무변경 — 검토 대기는 오케스트레이터 책임이고 phase별 커밋은 agent가 기어와 무관하게 수행한다. 기어 상태는 프로젝트 템플릿 문서의 진행 기록에 기록되고 `/tdd`(tdd SKILL.md)가 복원한다.

**Tech Stack:** Claude Code plugin skill (markdown SKILL.md). 자동 테스트 하네스 없음 — 검증은 편집 결과 확인과 실제 `/tdd-rgb` 실행 관찰.

**Spec:** `docs/superpowers/specs/2026-08-10-driving-in-gears-design.md`

## Global Constraints

- 기어는 검토 지점의 밀도만 바꾼다. TDD 3법칙, 한 번에 테스트 하나, phase별 커밋(`test:`/`feat:`/`refactor:`), 테스트 삭제 금지는 모든 기어에서 동일.
- 기어 전환 결정은 항상 사용자. 오케스트레이터는 제안만 한다.
- `agents/tdd-red.md`, `agents/tdd-green.md`, `agents/tdd-blue.md`는 수정 금지.
- `--gear` 미지정 = low = 현행 동작과 문자 그대로 동일. 기어 필드 없는 기존 문서는 low로 간주.
- 작업 브랜치: `feat/driving-in-gears` (클린룸 검증 종료 전 main 머지 금지).
- 커밋 메시지는 `~/.claude/docs/reviewable-commits.md` 표준, 한글 안전을 위해 temp 파일 + `git commit -F` 사용 (heredoc 금지).
- 이 계획의 모든 경로는 repo 루트 `~/.claude/plugins/marketplaces/msbaek-claude-plugins/` 기준.

---

### Task 1: tdd-rgb — 기어 정의 섹션 + 피드백 규칙 재정의

**Files:**
- Modify: `msbaek-tdd/skills/tdd-rgb/SKILL.md` (frontmatter `argument-hint`, GOAL, CONSTRAINTS의 피드백 규칙, 새 "기어(Gears)" 섹션)

**Interfaces:**
- Consumes: 없음 (첫 태스크)
- Produces: "기어(Gears)" 섹션의 기어 표·전환 신호·기록 형식 — Task 2·3이 실행 흐름에서 이 섹션을 참조한다. 기록 형식 문자열: `기어: {gear} ({전환 이력})`

- [ ] **Step 1: frontmatter argument-hint 수정**

`msbaek-tdd/skills/tdd-rgb/SKILL.md`에서:

```
old: argument-hint: "[plan-doc-path]"
new: argument-hint: "[plan-doc-path] [--gear=low|mid|high]"
```

- [ ] **Step 2: GOAL에 기어 문구 추가**

`- (Web Usecase의 경우) High Level Test 활성화, JPA Repository 전환, DSL 개선까지 완료` 줄 다음에 추가:

```markdown
- 검토 지점의 밀도는 기어(low/mid/high)가 정한다 — 아래 "기어(Gears)" 섹션 참조
```

- [ ] **Step 3: 피드백 규칙 재정의**

기존 Hard Rules의 피드백 규칙 블록:

```markdown
#### 피드백 규칙

- 한 단계에서 관련된 코드를 생성한 후에는 반드시 사용자에게 피드백을 요청
- 사용자가 명시적으로 다음 단계로 진행하는 것을 결정해야만 다음 단계로 진행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."
```

를 다음으로 교체:

```markdown
#### 피드백 규칙

- **기어가 정의하는 검토 지점에서 반드시 사용자 피드백을 요청하고 대기** ("기어(Gears)" 섹션의 검토 지점 표 참조)
- 검토 지점에서는 사용자가 명시적으로 다음 단계로 진행을 결정해야만 진행
- 검토 지점이 아닌 phase 경계(mid/high 기어)에서는 대기 없이 다음 phase로 진행하되, 커밋은 phase마다 정상 수행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."
```

- [ ] **Step 4: "기어(Gears)" 섹션 신설**

CONSTRAINTS의 `### Principles` 표제 **바로 앞**에 삽입:

```markdown
### 기어(Gears) — 검토 밀도 조절

Kent Beck의 "driving in gears": 이론에 대한 확신(confidence)이 검토 지점의 밀도를 정한다.
**기어는 검토 지점의 밀도만 바꾼다** — TDD 3법칙, 한 번에 테스트 하나, phase별 커밋,
테스트 삭제 금지는 모든 기어에서 동일하다. phase별 커밋이 남으므로 어떤 기어에서도
테스트 단위 revert가 가능하다.

#### 기어별 검토 지점

| 기어 | 검토 지점(사용자 피드백 대기) | 대응 상황 |
|---|---|---|
| **low** (기본) | Red 후 · Green 후 · Blue 후 | 이론에 확신 없음, 낯선 도메인·기술, 학습 목적 |
| **mid** | 테스트 1개의 R→G→B 사이클 완료 후 1회 | 유사 문제 경험 있음, 작동하는 이론을 빠르게 확보할 것으로 기대 |
| **high** | 전체 테스트 목록 완료 + 적대적 리뷰 통과 후 최종 1회 | 이론이 상용구(boilerplate) 수준으로 명확 |

`--gear` 미지정 시: 템플릿 문서 진행 기록에 기어 기록이 있으면 그 기어로 복원, 없으면 low.

#### 기어 전환 — 신호와 제안

사이클 사이에 아래 신호를 점검하고, 감지 시 전환을 **제안**한다. 결정은 항상 사용자.

**업시프트 신호** (low→mid, mid→high):

- 최근 2~3 사이클 연속 사용자 피드백이 "그대로 진행"뿐이었음
- Blue phase에서 새로운 통찰이 더 이상 나오지 않음 (설계 안정)
- 남은 테스트가 기존 패턴의 반복

업시프트 제안 문구에 반드시 포함: "지루함은 업시프트를 얻어냈다는 정직한 신호지만, 조급함은 그렇지 않습니다."

**다운시프트 신호** (high→mid, mid→low):

- revert 발생
- 예상과 다른 이유의 테스트 실패 반복
- 구현이 불투명 — 사용자 이견·질문 반복
- Green phase에서 최소 구현 범위를 넘는 코드 생성 감지

#### 폭발 반경(blast radius) 경고

시작 시와 업시프트 제안 전에 대상 코드 영역에서 high-stakes 신호를 점검한다:
인증/인가, 결제/금액 계산, 데이터 삭제·변경(마이그레이션), 외부 API 호출, 동시성.

감지 시 경고: "이 작업은 폭발 반경이 큽니다({영역}). 확신이 높아도 한 단 낮은 기어를
권장합니다. 틀릴 확률이 낮아도 틀렸을 때 비용이 큽니다." 경고 후 결정은 사용자.
high-stakes 영역에서는 업시프트 제안을 억제한다 (다운시프트 제안은 정상 동작).

#### 기어 기록

템플릿 문서 진행 기록 섹션에 현재 기어와 전환 이력을 남긴다:

```
기어: mid (사이클 7에서 low→mid, 사유: 설계 안정)
```

기어 변경(시작 지정 포함) 시마다 갱신한다. high 기어 자율 진행 시작 시에는 현재 HEAD
해시도 함께 기록한다 (적대적 리뷰 diff 기준점):

```
기어: high (사이클 12에서 mid→high, 사유: 남은 테스트가 패턴 반복) / 시작 커밋: abc1234
```
```

- [ ] **Step 5: 편집 결과 확인**

Run: `grep -n "기어(Gears)\|--gear=low\|검토 지점의 밀도만" msbaek-tdd/skills/tdd-rgb/SKILL.md`
Expected: frontmatter 1건, GOAL 1건, 기어 섹션 표제 포함 3건 이상 매치. `### Principles`가 기어 섹션 뒤에 그대로 존재.

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/skills/tdd-rgb/SKILL.md
# temp 파일로 커밋: "feat(tdd-rgb): 기어(low/mid/high) 정의와 검토 지점 규칙 도입"
# body: Why — 검토 밀도를 확신·폭발 반경에 따라 조절(driving in gears). 기어는 검토 지점 밀도만 변경, TDD Hard Rule 불변.
```

---

### Task 2: tdd-rgb — 실행 흐름에 기어 반영

**Files:**
- Modify: `msbaek-tdd/skills/tdd-rgb/SKILL.md` (OUTPUT FORMAT의 Step 1~3)

**Interfaces:**
- Consumes: Task 1의 "기어(Gears)" 섹션 (기어 표·신호·기록 형식)
- Produces: 실행 흐름의 "Step 2.5: 기어 전환 점검"과 high 기어 분기 — Task 3의 적대적 리뷰 단계가 이 분기에 연결된다.

- [ ] **Step 1: Step 1(현재 상태 확인)에 기어 결정 추가**

기존:

```markdown
#### Step 1: 현재 상태 확인

1. 템플릿 문서(*.md)에서 unit test 목록 확인 (Cucumber 미사용 시 Gherkin 시나리오도 포함되어 programmer test와 섞임)
2. 첫 미완성 테스트(`- [ ]`) 식별
3. 현재 테스트 실행 상태 확인
```

를 다음으로 교체:

```markdown
#### Step 1: 현재 상태 확인

1. 템플릿 문서(*.md)에서 unit test 목록 확인 (Cucumber 미사용 시 Gherkin 시나리오도 포함되어 programmer test와 섞임)
2. 첫 미완성 테스트(`- [ ]`) 식별
3. 현재 테스트 실행 상태 확인
4. **기어 결정**: `--gear` 파라미터 > 템플릿 문서의 기어 기록 > 기본 low 순으로 결정.
   폭발 반경 점검("기어(Gears)" 섹션)을 수행하고, high-stakes 영역이면 한 단 낮은 기어를
   권장하는 경고를 출력. 결정된 기어를 템플릿 문서 진행 기록에 기록.
```

- [ ] **Step 2: RGB 사이클의 phase별 대기를 기어 조건부로 수정**

Red/Green/Blue 각 단계 끝의 `- **사용자 피드백 대기**` 3곳을 모두 다음으로 교체:

```markdown
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)
```

- [ ] **Step 3: 사이클 완료 지점에 mid 검토·전환 점검 추가**

`#### Step 3: 완료 처리` 표제 **바로 앞**에 삽입:

```markdown
##### 사이클 완료 시 (테스트 1개의 R→G→B 종료)

- **mid 기어**: 여기가 검토 지점 — 사이클 요약(테스트·구현·리팩토링)을 보고하고 사용자 피드백 대기
- **high 기어**: 대기 없이 다음 테스트로 진행
- **기어 전환 점검** (모든 기어): "기어(Gears)" 섹션의 업/다운시프트 신호를 점검하고,
  감지 시 전환을 제안. 사용자가 수락하면 템플릿 문서의 기어 기록을 갱신하고 다음
  사이클부터 새 기어 적용
```

- [ ] **Step 4: Step 3(완료 처리)에 high 기어 분기 추가**

기존:

```markdown
#### Step 3: 완료 처리
- 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 작업 내역을 마크다운 파일에 반영
- 다음 테스트 안내 또는 전체 완료
```

를 다음으로 교체:

```markdown
#### Step 3: 완료 처리
- 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 작업 내역을 마크다운 파일에 반영
- 다음 테스트 안내 또는 전체 완료
- **전체 완료 시 high 기어였다면**: 최종 사용자 검토 전에 적대적 리뷰를 실행
  (아래 "high 기어: 적대적 리뷰" 섹션). green 스위트 + 적대적 리뷰 통과가
  high 기어의 Definition of Done
```

- [ ] **Step 5: 편집 결과 확인**

Run: `grep -n "기어 결정\|검토 지점이면 사용자\|사이클 완료 시\|high 기어였다면" msbaek-tdd/skills/tdd-rgb/SKILL.md`
Expected: 기어 결정 1건, "검토 지점이면 사용자" 3건(R/G/B), 사이클 완료 시 1건, high 분기 1건. `- **사용자 피드백 대기**` 단독 표기는 0건.

- [ ] **Step 6: Commit**

```bash
git add msbaek-tdd/skills/tdd-rgb/SKILL.md
# 커밋: "feat(tdd-rgb): 실행 흐름에 기어별 검토 지점·전환 점검 반영"
# body: Why — 기어 결정(파라미터>문서>low), phase 대기의 조건부화, 사이클 경계에서 전환 제안.
```

---

### Task 3: tdd-rgb — high 기어 적대적 리뷰 단계

**Files:**
- Modify: `msbaek-tdd/skills/tdd-rgb/SKILL.md` (`### Web Usecase 추가 단계` 표제 바로 앞에 섹션 삽입, FAILURE CONDITIONS에 체크 추가)

**Interfaces:**
- Consumes: Task 1의 기어 기록 형식(시작 커밋 해시), Task 2의 Step 3 high 분기 문구 "high 기어: 적대적 리뷰"
- Produces: 없음 (말단 태스크)

- [ ] **Step 1: "high 기어: 적대적 리뷰" 섹션 삽입**

`### Web Usecase 추가 단계` 표제 바로 앞에 삽입:

```markdown
### high 기어: 적대적 리뷰

high 기어에서 전체 테스트 목록이 green이 되면, 최종 사용자 검토 **전에** 반드시 실행한다.

#### 리뷰어 선택

1. 환경에 `adversarial-reviewer` agent가 있으면 그것으로 dispatch (1순위)
2. 없으면 general-purpose sub-agent에 아래 내장 프롬프트로 dispatch

내장 프롬프트 (fallback):

> 당신은 이 diff를 깨뜨리려는 적대적 리뷰어입니다. 평가하지 말고 공격하세요.
> 다음을 찾아 심각도(critical/major/minor)와 함께 보고하세요:
> 1. 테스트가 검증하지 않는 동작 (green이지만 커버되지 않은 경로)
> 2. 테스트 목록 문서와 구현의 표류(drift)
> 3. 최소 구현을 가장한 과잉 구현 (테스트가 요구하지 않는 코드)
> 4. 코드 스멜 (중복, 불명확한 이름, 긴 메소드)
> 각 지적에 구체적 실패 시나리오("이게 일어나면 → 저게 깨진다")를 붙이세요.

#### 입력

- 진행 기록의 시작 커밋..HEAD diff (`git diff {시작커밋}..HEAD`)
- 테스트 목록 문서 (intent 요약 — 리뷰어의 depth 보정에 사용)

#### 결과 처리

1. 지적 사항을 심각도별로 분류해 사용자에게 보고
2. 수정이 필요한 항목은 사용자 승인 후 반영 — 반영도 RGB 규칙 준수 (실패 테스트 먼저)
3. 리뷰 통과 후에야 최종 사용자 검토를 요청
```

- [ ] **Step 2: FAILURE CONDITIONS에 high 기어 체크 추가**

`#### 4. 전체 과정 후 확인` 체크리스트에 항목 추가:

```markdown
- [ ] (high 기어) 적대적 리뷰를 실행하고 결과를 보고했는가?
- [ ] (high 기어) 시작 커밋 해시가 진행 기록에 있는가?
```

- [ ] **Step 3: 편집 결과 확인**

Run: `grep -n "high 기어: 적대적 리뷰\|adversarial-reviewer\|시작 커밋 해시" msbaek-tdd/skills/tdd-rgb/SKILL.md`
Expected: 섹션 표제 2건(Step 3 분기 참조 + 섹션), adversarial-reviewer 1건 이상, 체크리스트 1건. 섹션이 `### Web Usecase 추가 단계` 앞에 위치.

- [ ] **Step 4: Commit**

```bash
git add msbaek-tdd/skills/tdd-rgb/SKILL.md
# 커밋: "feat(tdd-rgb): high 기어 적대적 리뷰 단계 추가"
# body: Why — high 기어 DoD = green 스위트 + 적대적 리뷰 통과. adversarial-reviewer 우선, 이식성 위한 내장 프롬프트 fallback.
```

---

### Task 4: tdd — 템플릿·상태 분석에 기어 기록·복원

**Files:**
- Modify: `msbaek-tdd/skills/tdd/SKILL.md` (두 템플릿의 진행 기록 섹션, Case B 상태 분석)

**Interfaces:**
- Consumes: Task 1의 기어 기록 형식 `기어: {gear} (...)`
- Produces: 없음 (말단 태스크)

- [ ] **Step 1: General TDD 템플릿에 기어 필드 추가**

General 템플릿의 `## 4. 진행 기록`을 다음으로 교체:

```markdown
## 4. 진행 기록

기어: low
```

- [ ] **Step 2: Web Usecase 템플릿에 기어 필드 추가**

Web Usecase 템플릿의 `## 6. 진행 기록`을 다음으로 교체:

```markdown
## 6. 진행 기록

기어: low
```

- [ ] **Step 3: Case B 상태 분석에 기어 안내 추가**

기존:

```markdown
#### Case B: 템플릿 있음 → 진행 상황 분석

1. 체크박스 분석으로 현재 단계 파악
2. 완료된 단계와 다음 단계 안내
```

의 1~2 사이에 항목을 추가해 다음으로 교체:

```markdown
#### Case B: 템플릿 있음 → 진행 상황 분석

1. 체크박스 분석으로 현재 단계 파악
2. 진행 기록의 기어 상태 확인 — 있으면 현재 기어와 전환 이력을 함께 안내, 없으면 low로 간주
3. 완료된 단계와 다음 단계 안내
```

(기존 3번 "적절한 다음 명령어 안내"는 4번으로 번호가 밀린다.)

- [ ] **Step 4: 편집 결과 확인**

Run: `grep -n "기어: low\|기어 상태 확인" msbaek-tdd/skills/tdd/SKILL.md`
Expected: `기어: low` 2건(두 템플릿), 기어 상태 확인 1건.

- [ ] **Step 5: Commit**

```bash
git add msbaek-tdd/skills/tdd/SKILL.md
# 커밋: "feat(tdd): 템플릿·상태 분석에 기어 기록/복원 추가"
# body: Why — 세션 재개 시 기어 복원. 기어 필드 없는 기존 문서는 low 간주(하위 호환).
```

---

### Task 5: 스펙 대조 최종 검증

**Files:**
- Read: `docs/superpowers/specs/2026-08-10-driving-in-gears-design.md`, 수정된 SKILL.md 2개

**Interfaces:**
- Consumes: Task 1~4 전체 결과
- Produces: 검증 보고 (승인 조건 1~5 대조표)

- [ ] **Step 1: 승인 조건 문서 대조**

스펙의 성공 기준 1~5 각각에 대해 수정된 SKILL.md의 해당 구절을 인용해 대조표 작성:

1. `--gear` 미지정 = low = 현행 동일 → tdd-rgb Step 1의 기어 결정 우선순위와 low 행 확인
2. mid의 대기 위치 → "사이클 완료 시" 블록 확인
3. high의 자율 진행 + 적대적 리뷰 → Step 3 분기와 "high 기어: 적대적 리뷰" 섹션 확인
4. 전환 제안이 신호 기반인가 → "기어 전환 점검" + 신호 목록 확인
5. 기어 기록·복원 → 기록 형식 + tdd SKILL.md Case B 확인

- [ ] **Step 2: agents 무변경 확인**

Run: `git diff main --stat -- msbaek-tdd/agents/`
Expected: 출력 없음 (agents 3개 무변경).

- [ ] **Step 3: 실행 관찰 검증 안내**

실제 `/tdd-rgb --gear=mid` 등의 동작 검증은 별도 세션(또는 클린룸 검증 다음 회차)에서
수행함을 사용자에게 보고. 이 계획의 범위는 문서 대조까지.

- [ ] **Step 4: 최종 보고**

대조표와 함께 브랜치 상태(`git log main..feat/driving-in-gears --oneline`)를 보고.
main 머지는 클린룸 검증 종료 후 — 머지하지 않는다.
