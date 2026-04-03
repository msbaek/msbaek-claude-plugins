# Tidy/Refactoring 스킬 분리 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** tdd-tidy/tdd-blue에서 Extract Method와 Domain Logic 이동을 제거하고, 이를 별도 브랜치/PR 기반의 system-wide-refactoring 스킬로 분리

**Architecture:** tdd-blue agent의 Tidying Process를 local tidying(6단계+품질게이트)으로 축소하고, tdd-tidy 스킬의 호출 메시지를 업데이트한다. 새로운 system-wide-refactoring 스킬은 대화형 워크플로우로 Extract Method / Domain Logic 이동을 수행하며, 별도 브랜치에서 기법별 커밋 후 PR을 생성한다.

**Tech Stack:** Claude Code plugin (markdown-based skills/agents)

---

## File Structure

| 파일 | 역할 | 변경 유형 |
|------|------|-----------|
| `msbaek-tdd/agents/tdd-blue.md` | Blue Phase agent — Tidying Process 정의 | Modify |
| `msbaek-tdd/skills/tdd-tidy/SKILL.md` | Standalone tidying 스킬 | Modify |
| `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` | 대화형 system-wide refactoring 스킬 | Create |
| `msbaek-tdd/.claude-plugin/plugin.json` | 플러그인 메타데이터 | Modify |

---

### Task 1: tdd-blue agent — Tidying Process 범위 축소

**Files:**
- Modify: `msbaek-tdd/agents/tdd-blue.md`

- [ ] **Step 1: frontmatter description 업데이트**

기존:
```
description: TDD Blue phase - Composed Method 지향 Tidying Process (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract → Domain Logic → Trimming).
```

변경:
```
description: TDD Blue phase - Composed Method 지향 Local Tidying Process (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming).
```

- [ ] **Step 2: 프로세스 흐름도에서 6번 제거, 5번을 Extract Variable로 한정**

기존 프로세스 흐름 (라인 77~103):
```
시작 (코드 리뷰)
  │
  ▼
0. Guard Clauses (중첩 제거)
  │
  ▼
조숙한 리팩터링으로 Composed Method 위배?
  ├─ Yes → 1. One Pile (inline method) ──┐
  │                                       │
  └─ No ──┐                              │
           ▼                              │
      2. Reorder (Slide Statements)       │
           ▼                              │
      3. Chunk Statements                 │
           ▼                              │
      4. Explaining Comment ← 필수1       │
           ▼                              │
      5. Extract Variable/Method ← 필수2  │
           │                              │
           ├→ 6. Domain Logic 이동 (Advanced)
           ├→ 7. Trimming (Advanced)      │
           ▼                              │
      8. 이해하기 어려워졌나?              │
           ├─ Yes ────────────────────────┘
           └─ No → 완료
```

변경:
```
시작 (코드 리뷰)
  │
  ▼
0. Guard Clauses (중첩 제거)
  │
  ▼
조숙한 리팩터링으로 Composed Method 위배?
  ├─ Yes → 1. One Pile (inline method) ──┐
  │                                       │
  └─ No ──┐                              │
           ▼                              │
      2. Reorder (Slide Statements)       │
           ▼                              │
      3. Chunk Statements                 │
           ▼                              │
      4. Explaining Comment ← 필수1       │
           ▼                              │
      5. Extract Variable ← 필수2         │
           │                              │
           ├→ 6. Trimming                 │
           ▼                              │
      7. 이해하기 어려워졌나?              │
           ├─ Yes ────────────────────────┘
           └─ No → 완료
```

- [ ] **Step 3: 5번 섹션 제목과 내용 수정**

기존 (라인 246~280):
```markdown
##### 5. Extract Variable/Method ← 필수2 — Composed Method 지향
**목적**: 복잡한 표현식과 중복 로직을 의미있는 변수/메서드로 추출하여 **Composed Method Pattern** 달성

> "좋은 이름을 붙일 수 있을 때" 추출한다. SLAP(Single Level of Abstraction Principle) 준수.
> 하나의 {} (loop, conditional) 에서는 한 가지 일만 하도록.

```java
// Before: 복잡한 조건식이 인라인
if (totalAmount > 100 && customer.getAddress().getCountry().equals("KOREA") &&
    !customer.getAddress().getCity().equals("SEOUL")) {
    return 0;
}

// After: 의미있는 변수/메서드로 추출
boolean qualifiesForFreeShipping = totalAmount > 100 &&
    isKoreanCustomerOutsideSeoul(customer);

if (qualifiesForFreeShipping) {
    return 0;
}

private boolean isKoreanCustomer(Customer customer) {
    return "KOREA".equals(customer.getAddress().getCountry());
}

private boolean isKoreanCustomerOutsideSeoul(Customer customer) {
    return isKoreanCustomer(customer) &&
           !"SEOUL".equals(customer.getAddress().getCity());
}
```

**추출 시 고려사항**:
- **Split Phase**: 서로 다른 추상화 수준(WEB, APP, Domain, Infra)을 분리
- **Split Unrelated Complexity**: 서로 다른 의존성을 가진 기능을 분리
- 중복이 있더라도 하나의 루프/조건문에서는 한 가지 일만 하도록 (리팩토링에 유리)
```

변경:
```markdown
##### 5. Extract Variable ← 필수2
**목적**: 복잡한 표현식을 의미있는 변수로 추출하여 가독성 향상

> 복잡한 조건식이나 계산식에 의도를 드러내는 이름을 붙인다.
> Extract Method는 system-wide-refactoring 스킬에서 수행한다.

```java
// Before: 복잡한 조건식이 인라인
if (totalAmount > 100 && customer.getAddress().getCountry().equals("KOREA") &&
    !customer.getAddress().getCity().equals("SEOUL")) {
    return 0;
}

// After: 의미있는 변수로 추출
boolean isKorean = "KOREA".equals(customer.getAddress().getCountry());
boolean isOutsideSeoul = !"SEOUL".equals(customer.getAddress().getCity());
boolean qualifiesForFreeShipping = totalAmount > 100 && isKorean && isOutsideSeoul;

if (qualifiesForFreeShipping) {
    return 0;
}
```
```

- [ ] **Step 4: 6번 Domain Logic 이동 섹션 제거**

라인 282~308의 "##### 6. Domain Logic 이동" 섹션 전체를 삭제하고, 다음 안내 문구로 대체:

```markdown
##### 6. Trimming
```

기존 7번 Trimming 내용을 6번으로 번호만 변경 (내용 동일).

- [ ] **Step 5: 품질 게이트 번호 변경**

기존 "##### 8. 품질 게이트" (라인 324~330)를 "##### 7. 품질 게이트"로 변경.

기존:
```markdown
##### 8. 품질 게이트: 이해하기 어려워졌나?
5번까지 진행한 결과 코드가 오히려 이해하기 어려워졌다면:
```

변경:
```markdown
##### 7. 품질 게이트: 이해하기 어려워졌나?
5번까지 진행한 결과 코드가 오히려 이해하기 어려워졌다면:
```

- [ ] **Step 6: Standalone 모드의 Tidying Process 목록 업데이트**

"#### 2. Tidying Process 적용" 섹션 (라인 352~361)을 업데이트:

기존:
```markdown
0. Guard Clauses (중첩 제거 — 가장 먼저)
1. One Pile (조건부 — Composed Method 위배 시)
2. Reorder (Slide Statements)
3. Chunk Statements
4. Explaining Comment ← 필수1
5. Extract Variable/Method ← 필수2
6. Domain Logic 이동 (Advanced)
7. Trimming (Advanced)
8. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

변경:
```markdown
0. Guard Clauses (중첩 제거 — 가장 먼저)
1. One Pile (조건부 — Composed Method 위배 시)
2. Reorder (Slide Statements)
3. Chunk Statements
4. Explaining Comment ← 필수1
5. Extract Variable ← 필수2
6. Trimming
7. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

- [ ] **Step 7: Document-Based Workflow의 Tidying Process 목록도 동일하게 업데이트**

"#### 2. Tidying Process 적용" (라인 408~417) — Standalone이 아닌 RGB 모드의 목록도 동일하게 업데이트:

기존:
```markdown
0. Guard Clauses (중첩 제거 — 가장 먼저)
1. One Pile (조건부 — Composed Method 위배 시)
2. Reorder (Slide Statements)
3. Chunk Statements
4. Explaining Comment ← 필수1
5. Extract Variable/Method ← 필수2
6. Domain Logic 이동 (Advanced)
7. Trimming (Advanced)
8. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

변경:
```markdown
0. Guard Clauses (중첩 제거 — 가장 먼저)
1. One Pile (조건부 — Composed Method 위배 시)
2. Reorder (Slide Statements)
3. Chunk Statements
4. Explaining Comment ← 필수1
5. Extract Variable ← 필수2
6. Trimming
7. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

- [ ] **Step 8: FAILURE CONDITIONS에 system-wide 리팩토링 금지 규칙 추가**

기존 FAILURE CONDITIONS (라인 443~454) 끝에 추가:

```markdown
- ❌ **Extract Method 수행 금지** - system-wide-refactoring 스킬 전담
- ❌ **Domain Logic 이동 금지** - system-wide-refactoring 스킬 전담
```

- [ ] **Step 9: 변경사항 diff 확인**

Run: `git diff msbaek-tdd/agents/tdd-blue.md`
Expected: description 변경, 프로세스 흐름도 업데이트, 5번 섹션 수정, 6번 삭제/재번호, 8→7번 변경, Tidying Process 목록 x2 업데이트, FAILURE CONDITIONS 추가 확인

- [ ] **Step 10: 커밋**

```bash
git add msbaek-tdd/agents/tdd-blue.md
```

Write tool로 커밋 메시지 파일 생성:
```
refactor(tdd): tdd-blue Tidying Process에서 Extract Method/Domain Logic 제거

local tidying만 수행하도록 범위 축소:
- 5번을 Extract Variable로 한정 (Extract Method 제거)
- 6번 Domain Logic 이동 제거
- 7번 Trimming → 6번, 8번 품질 게이트 → 7번으로 재번호
- Extract Method/Domain Logic은 system-wide-refactoring 스킬로 분리 예정
```

```bash
git commit -F /tmp/commit-msg.txt && rm /tmp/commit-msg.txt
```

---

### Task 2: tdd-tidy 스킬 — 단계 목록 및 호출 메시지 업데이트

**Files:**
- Modify: `msbaek-tdd/skills/tdd-tidy/SKILL.md`

- [ ] **Step 1: GOAL 섹션에서 "8단계" → 축소된 단계로 변경**

기존 (라인 9):
```markdown
git diff로 최근 변경된 Java 파일을 자동 탐지하여, tdd-blue agent의 8단계 Tidying Process를 TDD 사이클 없이 독립 실행합니다.
```

변경:
```markdown
git diff로 최근 변경된 Java 파일을 자동 탐지하여, tdd-blue agent의 Local Tidying Process를 TDD 사이클 없이 독립 실행합니다.
```

기존 (라인 15):
```markdown
- 8단계 Tidying Process가 적용됨
```

변경:
```markdown
- Local Tidying Process가 적용됨 (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming)
```

- [ ] **Step 2: tdd-blue agent 호출 메시지 업데이트**

기존 (라인 64~69):
```markdown
[standalone] 다음 파일에 Composed Method 지향 Tidying Process를 적용해주세요:
- src/main/java/com/example/OrderService.java
- src/main/java/com/example/PaymentProcessor.java

8단계 Tidying Process (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract → Domain Logic → Trimming)를 순서대로 적용하고,
변경이 있으면 하나의 refactor: 커밋으로 완료해주세요.
```

변경:
```markdown
[standalone] 다음 파일에 Local Tidying Process를 적용해주세요:
- src/main/java/com/example/OrderService.java
- src/main/java/com/example/PaymentProcessor.java

Local Tidying Process (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming)를 순서대로 적용하고,
변경이 있으면 하나의 refactor: 커밋으로 완료해주세요.
Extract Method와 Domain Logic 이동은 수행하지 마세요 (system-wide-refactoring 스킬 전담).
```

- [ ] **Step 3: 변경사항 diff 확인**

Run: `git diff msbaek-tdd/skills/tdd-tidy/SKILL.md`
Expected: "8단계" → "Local Tidying Process", 호출 메시지에서 Extract Method/Domain Logic 제외 명시 확인

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/tdd-tidy/SKILL.md
```

Write tool로 커밋 메시지 파일 생성:
```
refactor(tdd): tdd-tidy 스킬에서 Local Tidying으로 범위 한정

- "8단계 Tidying Process" → "Local Tidying Process"로 명칭 변경
- tdd-blue 호출 메시지에 Extract Method/Domain Logic 제외 명시
```

```bash
git commit -F /tmp/commit-msg.txt && rm /tmp/commit-msg.txt
```

---

### Task 3: system-wide-refactoring 스킬 생성

**Files:**
- Create: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

- [ ] **Step 1: 디렉토리 확인**

Run: `ls msbaek-tdd/skills/`
Expected: tdd, tdd-plan, tdd-rgb, tdd-tidy 디렉토리 존재 확인

- [ ] **Step 2: SKILL.md 작성**

Create: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

```markdown
---
name: system-wide-refactoring
description: 대화형 System-wide Refactoring — Extract Method, Domain Logic 이동을 별도 브랜치에서 기법별 커밋 후 PR 생성. /system-wide-refactoring으로 호출.
argument-hint: "[commit-ref]"
---

# System-wide Refactoring Skill

코드 분석 → 리팩토링 후보 제시 → 사용자 확인 → 별도 브랜치에서 기법별 커밋 → PR 생성.

## GOAL

- **성공 = 사용자가 확인한 리팩토링이 별도 브랜치에서 기법별 커밋으로 완료되고, 원래 브랜치로 PR이 생성됨**
- Extract Method / Domain Logic 이동 후보가 식별됨
- 사용자와 질의응답으로 방향이 확정됨
- 별도 브랜치에서 기법별 커밋 완료
- 모든 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 1파일 x 1기법 = 1커밋 (논리적으로 연결된 파일은 함께)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

## OUTPUT FORMAT

### 실행 절차

#### 1. 대상 파일 수집

인자가 전달된 경우 해당 commit ref와 비교, 없으면 unstaged + staged 변경 파일 수집:

```bash
# 인자 없음: unstaged + staged 변경 파일
git diff --name-only -- '*.java'
git diff --cached --name-only -- '*.java'

# 인자 있음: 특정 commit과 비교
git diff --name-only <commit-ref> -- '*.java'
```

- 테스트 파일(`*Test.java`, `*Tests.java`, `*Spec.java`)은 **제외**
- 변경 파일이 없으면: "리팩토링 대상 Java 파일이 없습니다." 안내 후 종료

#### 2. 코드 분석 — 리팩토링 후보 식별

대상 파일을 읽고 다음 패턴을 찾는다:

**Extract Method 후보**:
- 긴 메서드 (20줄 이상)에서 독립적인 로직 블록
- 여러 곳에서 반복되는 코드 패턴
- 서로 다른 추상화 수준이 섞인 메서드

**Extract Delegate 후보**:
- 한 클래스가 너무 많은 책임을 가진 경우
- 관련 필드와 메서드가 그룹을 이루는 경우

**Domain Logic 이동 후보**:
- Feature Envy — Service에서 도메인 객체의 데이터를 직접 조작
- Tell, Don't Ask 위반 — getter 체이닝으로 로직 수행
- Domain Service, Value Object, First Class Collection 추출 가능

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Extract Method

**파일**: OrderService.java
**대상**: processOrder() 메서드 (45줄)

**현재 코드**:
[해당 코드 블록]

**제안 변경**:
- calculateDiscount() 메서드 추출 (라인 23-35)
- validateInventory() 메서드 추출 (라인 37-42)

**적용할까요?** (yes / no / 수정 요청)
```

- 사용자가 **yes** → 실행 목록에 추가
- 사용자가 **no** → 스킵
- 사용자가 **수정 요청** → 요청 반영 후 재제시

모든 후보 확인 후 최종 실행 목록을 보여주고 진행 여부 확인.

#### 4. 브랜치 생성

```bash
# 현재 브랜치 이름 확인
CURRENT_BRANCH=$(git branch --show-current)

# refactor 브랜치 생성 및 전환
git checkout -b "refactor/${CURRENT_BRANCH}"
```

#### 5. 기법별 커밋 실행

확정된 리팩토링을 하나씩 수행:

1. 리팩토링 적용
2. 테스트 실행 (gradle test 또는 mvn test)
3. 테스트 통과 확인
4. 해당 파일만 git add
5. 커밋

**커밋 메시지 형식**:
- `refactor: extract method [메서드명] from [클래스명]`
- `refactor: extract delegate [클래스명] from [원본클래스명]`
- `refactor: move [설명] to [대상 클래스]`

한글 커밋 메시지가 필요한 경우 Write tool로 임시 파일 생성 후 `git commit -F <파일>` 사용.

테스트 실패 시:
- 해당 리팩토링 변경사항 되돌리기 (`git checkout -- [파일]`)
- 사용자에게 실패 사유 안내
- 다음 리팩토링으로 진행

#### 6. PR 생성

모든 리팩토링 커밋 완료 후:

```bash
# 원래 브랜치로 PR 생성
gh pr create \
  --base "${CURRENT_BRANCH}" \
  --title "refactor: system-wide refactoring for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- [적용된 기법 1]: [설명]
- [적용된 기법 2]: [설명]

## Commits
각 커밋은 하나의 리팩토링 기법을 적용합니다.
Commits 탭에서 개별 리뷰할 수 있습니다.

## Test
- [x] 모든 기존 테스트 통과 확인

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

#### 7. 원래 브랜치로 복귀 및 결과 보고

```bash
git checkout "${CURRENT_BRANCH}"
```

사용자에게 보고:
- PR URL
- 적용된 리팩토링 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 동작이 변경되어 테스트가 실패 (되돌리기 필수)
- ❌ 기법별 커밋 없이 한꺼번에 커밋
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
- ❌ Local Tidying 기법 수행 (Guard Clauses, Reorder 등은 tdd-tidy 전담)
```

- [ ] **Step 3: 파일 생성 확인**

Run: `head -5 msbaek-tdd/skills/system-wide-refactoring/SKILL.md`
Expected: frontmatter의 `name: system-wide-refactoring` 확인

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/system-wide-refactoring/SKILL.md
```

Write tool로 커밋 메시지 파일 생성:
```
feat(tdd): system-wide-refactoring 스킬 추가

대화형 워크플로우로 Extract Method / Domain Logic 이동 수행:
- 코드 분석 → 후보 제시 → 사용자 확인
- 별도 브랜치에서 기법별 커밋
- 원래 브랜치로 PR 생성
```

```bash
git commit -F /tmp/commit-msg.txt && rm /tmp/commit-msg.txt
```

---

### Task 4: plugin.json 버전 범프

**Files:**
- Modify: `msbaek-tdd/.claude-plugin/plugin.json`

- [ ] **Step 1: 버전 및 description 업데이트**

기존:
```json
{
  "name": "msbaek-tdd",
  "version": "1.3.0",
  "description": "Java + Spring Boot TDD workflow plugin with RGB cycle orchestration and standalone tidying",
  "author": {
    "name": "msbaek"
  },
  "keywords": ["tdd", "java", "spring-boot", "red-green-blue", "tidying"]
}
```

변경:
```json
{
  "name": "msbaek-tdd",
  "version": "1.4.0",
  "description": "Java + Spring Boot TDD workflow plugin with RGB cycle, local tidying, and system-wide refactoring",
  "author": {
    "name": "msbaek"
  },
  "keywords": ["tdd", "java", "spring-boot", "red-green-blue", "tidying", "refactoring"]
}
```

- [ ] **Step 2: 커밋**

```bash
git add msbaek-tdd/.claude-plugin/plugin.json
```

Write tool로 커밋 메시지 파일 생성:
```
chore(tdd): 버전 1.4.0으로 범프 — system-wide-refactoring 스킬 추가 반영
```

```bash
git commit -F /tmp/commit-msg.txt && rm /tmp/commit-msg.txt
```

---

### Task 5: 검증

- [ ] **Step 1: 전체 파일 구조 확인**

Run: `find msbaek-tdd -name "*.md" -o -name "*.json" | sort`
Expected:
```
msbaek-tdd/.claude-plugin/plugin.json
msbaek-tdd/agents/tdd-blue.md
msbaek-tdd/agents/tdd-green.md
msbaek-tdd/agents/tdd-red.md
msbaek-tdd/skills/system-wide-refactoring/SKILL.md
msbaek-tdd/skills/tdd/SKILL.md
msbaek-tdd/skills/tdd-plan/SKILL.md
msbaek-tdd/skills/tdd-rgb/SKILL.md
msbaek-tdd/skills/tdd-tidy/SKILL.md
```

- [ ] **Step 2: tdd-blue.md에서 "Extract Method" 가 FAILURE CONDITIONS에만 존재하는지 확인**

Run: `grep -n "Extract Method" msbaek-tdd/agents/tdd-blue.md`
Expected: FAILURE CONDITIONS 섹션의 금지 규칙에서만 매치 (Tidying Process 단계에서는 없어야 함)

- [ ] **Step 3: tdd-blue.md에서 "Domain Logic" 이 FAILURE CONDITIONS에만 존재하는지 확인**

Run: `grep -n "Domain Logic" msbaek-tdd/agents/tdd-blue.md`
Expected: FAILURE CONDITIONS 섹션의 금지 규칙에서만 매치

- [ ] **Step 4: tdd-tidy SKILL.md에서 "Extract Method" 제외가 명시되었는지 확인**

Run: `grep -n "Extract Method" msbaek-tdd/skills/tdd-tidy/SKILL.md`
Expected: "Extract Method와 Domain Logic 이동은 수행하지 마세요" 문구 매치

- [ ] **Step 5: system-wide-refactoring SKILL.md frontmatter 확인**

Run: `head -4 msbaek-tdd/skills/system-wide-refactoring/SKILL.md`
Expected:
```
---
name: system-wide-refactoring
description: 대화형 System-wide Refactoring — Extract Method, Domain Logic 이동을 별도 브랜치에서 기법별 커밋 후 PR 생성. /system-wide-refactoring으로 호출.
argument-hint: "[commit-ref]"
```

- [ ] **Step 6: plugin.json 버전 확인**

Run: `cat msbaek-tdd/.claude-plugin/plugin.json`
Expected: version이 "1.4.0", keywords에 "refactoring" 포함
