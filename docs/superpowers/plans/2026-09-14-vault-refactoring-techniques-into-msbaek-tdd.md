# vault 리팩터링 기법 → msbaek-tdd 편입 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** vault 조사에서 검증된 리팩터링 기법 20건(T1~T9, S1~S9, O2, O3)을 msbaek-tdd 플러그인의 tidying 정본·system-wide-refactoring 스킬·references에 편입하고 1.47.0으로 릴리스한다.

**Architecture:** tidying은 단계 수(0~7, 11개 `##` 절)를 늘리지 않고 기존 절의 항목만 보강한다. system-wide-refactoring은 후보 유형·적용 순서·커밋 형식을 추가한다. Chaining 표와 Parallel Change는 별도 reference 파일로 분리해 본문 비대화를 막는다. 모든 편입 내용은 vault 원문에 근거하며, 원문에 절차가 없는 항목(S8 유사 기능 추가)은 이름과 3단계만 기재하고 절차를 지어내지 않는다.

**Tech Stack:** Markdown(플러그인 스킬·에이전트·references), git, grep 검증. 코드 없음.

**Spec:** `.claude/plans/2026-09-13-vault-refactoring-techniques/report.md` (검증 리포트, confirmed 14 · weaken 10 · reject 1). 리뷰 결정: 23항목 전부 권장안 채택(2026-09-14).

## Global Constraints

- 문체: CLAUDE.md "생성 markdown" 규칙 — 전문 용어, 모호하면 `한글(english)` 병기(괄호 앞 공백 없음), 구어·비유 동사 금지(터진다·흐려진다·붙다·막다·태우다 금지), 정의→절차→출력→제약 순, 한 문장에 사실 하나.
- 코드 예시 주석은 한글, 모호 용어는 `한글(english)` 병기 (`msbaek-tdd/agents/references/code-comment-style.md`).
- tidying-process.md의 `## ` 절 수는 편집 전후 **11개로 동일**해야 한다 (`grep -c "^## " == 11`).
- tdd-blue.md·tdd-tidy/SKILL.md의 단계 요약 문자열(`Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming`)은 변경하지 않는다.
- 커밋: 1 Task = 1 커밋. 메시지는 `feat(msbaek-tdd): 1.47.0 — <한 줄>` 형식(기존 히스토리 `fix(msbaek-tdd): 1.46.10 — ...`과 동일 패턴). 한글 메시지는 임시 파일 + `git commit -F`. `git add -A` 금지. 커밋 말미에 세션 attribution 2줄 추가.
- 버전: `msbaek-tdd/.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 msbaek-tdd `version` **두 곳** 모두 `1.46.10` → `1.47.0` (마지막 Task).
- 범위 밖: O1(WEWLC 의존성 깨뜨리기 24기법 → 새 스킬)은 이 계획에 포함하지 않는다. 별도 브레인스토밍.
- 이 저장소는 worktree 없이 main에서 직접 작업한다 (memory: no-worktree-work-in-place).

---

## File Structure

| 파일 | 작업 | 책임 |
|---|---|---|
| `msbaek-tdd/agents/references/tidying-process.md` | Modify | tidying 각 절의 항목 보강 (T1~T7), 참조 링크 2건 |
| `msbaek-tdd/agents/references/tidying-chaining.md` | Create | Chaining 표(T9) + 참조 전용 기법 New Interface, Old Implementation(T8) |
| `msbaek-tdd/references/parallel-change.md` | Create | Expand → Migrate → Contract 절차, Branch by Abstraction (O2) |
| `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` | Modify | 후보 유형 6건(S1·S4·S5·S6·S7·S8), 적용 순서 절(S2·S3), Mikado 대화형 절차(S9), 커밋 형식 |
| `msbaek-tdd/agents/tdd-blue.md` | Modify | 작업 원칙에 Preparatory Refactoring 한 줄(O3) |
| `msbaek-tdd/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Modify | 1.47.0 |
| `.claude/plans/2026-09-13-vault-refactoring-techniques/INDEX.md`, `.claude/plans/INDEX.md` | Modify | Status: completed |

---

### Task 1: tidying-process.md — Reorder(2)·Chunk Statements(3) 보강 (T3, T5)

**Files:**
- Modify: `msbaek-tdd/agents/references/tidying-process.md:140-176` (## 2. Reorder), `:213-239` (## 3. Chunk Statements)

**Interfaces:**
- Consumes: 없음
- Produces: 절 제목 문자열 불변 (`## 2. Reorder (Slide Statements)`, `## 3. Chunk Statements (빈 라인으로 그룹핑)`). Task 2·3이 같은 파일의 다른 절을 편집하므로 절 제목을 앵커로 쓴다.

- [ ] **Step 1: Reorder 절에 "선언과 초기화" 항목 추가**

`## 2. Reorder (Slide Statements)` 절에서 아래 두 줄(현재 144~145행)을 찾는다:

```markdown
- **Reading Order**: 변수 선언을 사용 위치 가까이로 이동 (`Move declaration closer to usages`)
- **Cohesion Order**: 관련된 로직끼리 함께 배치 (Step Down Rule 적용)
```

다음으로 교체한다:

```markdown
- **Reading Order**: 변수 선언을 사용 위치 가까이로 이동 (`Move declaration closer to usages`)
- **Cohesion Order**: 관련된 로직끼리 함께 배치 (Step Down Rule 적용)
- **선언과 초기화 결합(Move Declaration and Initialization Together)**: 선언과 초기화가
  떨어져 있으면 초기화 지점에 도달했을 때 변수의 맥락을 잊는다. 초기화를 선언 위치로
  이동하거나, 선언을 초기화 직전으로 이동한다. 반대 방향(선언과 할당을 분리)은
  Extract Method 등 후속 리팩터링 준비가 목적일 때만 적용한다(`Join Declaration and Assignment`).

```java
// Before: 선언과 초기화가 떨어져 있음
int discountRate;
List<OrderItem> items = order.getItems();
validateInventory(items);
discountRate = calculateDiscountRate(customer);

// After: 초기화를 선언 위치로 이동
List<OrderItem> items = order.getItems();
validateInventory(items);
int discountRate = calculateDiscountRate(customer);
```
```

- [ ] **Step 2: Chunk Statements 절에 "문단 식별 기준" 추가**

`## 3. Chunk Statements (빈 라인으로 그룹핑)` 절의 첫 줄 `**목적**: 빈 줄을 삽입하여 관련된 코드 블록을 논리적으로 그룹화` 바로 아래(코드 블록 앞)에 다음을 삽입한다:

```markdown
**문단(code paragraph) 식별 기준** — 코드를 정독하지 않아도 다음 시각적 단서 중 하나 이상이
있으면 하나의 문단이다:
- 다음 줄의 기능을 설명하는 짧은 주석으로 시작한다
- 중괄호 한 쌍 안에 있거나 같은 들여쓰기 수준에 있다
- `for`, `if`, `try`, `switch`, `while`로 시작한다
- 앞뒤에 공백 라인이 있다
- 동일한 변수명 또는 반복되는 단어를 사용하는 문장 군집이다

**식별 순서**: 메서드의 **끝부분부터** 문단을 식별한다. 끝부분은 반환할 결과 값을 준비하므로
단일 값을 반환하는 메서드로 추출될 확률이 높다. 상단은 여러 값을 만들어 내는 경우가 많아
추출이 어렵다. 인자 목록 정리는 모든 문단을 추출한 뒤로 미룬다.

```

- [ ] **Step 3: 검증**

Run:
```bash
cd msbaek-tdd/agents/references && grep -c "^## " tidying-process.md && grep -c "Move Declaration and Initialization Together\|code paragraph\|끝부분부터" tidying-process.md
```
Expected: `11` 그리고 `3` (각 키워드 1회 이상, 합계 3줄)

- [ ] **Step 4: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — tidying Reorder·Chunk 보강 (선언·초기화 결합, 문단 식별 기준)\n\nvault 근거: Tidy First Ch07, Reduce Method Sprawl with Code Paragraphs\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/agents/references/tidying-process.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 2: tidying-process.md — Extract Variable(5)·Split Loop(5.5)·Trimming(6) 보강 (T1, T6, T7, T4, T2)

**Files:**
- Modify: `msbaek-tdd/agents/references/tidying-process.md` — `## 5. Extract Variable ← 필수2`, `## 5.5 Split Loop`, `## 6. Trimming` 절

**Interfaces:**
- Consumes: Task 1 완료 후 파일(절 제목 불변)
- Produces: 절 제목 불변. Task 3이 `## 7. 품질 게이트` 절 뒤에 참조 링크를 추가한다.

- [ ] **Step 1: Extract Variable 절에 Explaining Constants·Split Variable·Extract Helper 추가**

`## 5. Extract Variable ← 필수2` 절의 코드 블록(`// After: 의미있는 변수로 추출` 블록) 종료 직후, `## 5.5 Split Loop` 제목 앞에 다음을 삽입한다:

```markdown
**같은 단계에서 함께 적용하는 항목**:

- **Explaining Constants(설명 상수)**: 코드를 읽다가 의미를 알 수 없는 숫자를 발견하거나
  같은 문자열 상수가 여러 곳에 반복되면 심볼릭 상수(symbolic constant)로 추출한다.
  이해한 것을 코드에 기록하는 행위이며, 함께 변경되는 상수를 묶으면 Cohesion Order가 드러난다.

```java
// Before
if (response.code == 404) { ... }

// After
private static final int PAGE_NOT_FOUND = 404;
if (response.code == PAGE_NOT_FOUND) { ... }
```

- **Split Variable(변수 분리)**: 루프 변수·수집 변수가 아닌 임시 변수가 두 번 이상
  할당되면 할당마다 별도 변수로 분리한다. 하나의 변수는 하나의 의미만 가진다.

```java
// Before: temp가 두 가지 의미로 재할당됨
double temp = 2 * (height + width);   // 둘레(perimeter)
System.out.println(temp);
temp = height * width;                // 면적(area)
System.out.println(temp);

// After
final double perimeter = 2 * (height + width);
System.out.println(perimeter);
final double area = height * width;
System.out.println(area);
```

- **Extract Helper(같은 클래스 내 Extract Method)**: 메서드 내 코드 블록이 명확한 목적을
  갖고 나머지 코드와 상호작용이 제한적이면 private 메서드로 추출한다. 이름은 **어떻게**가
  아니라 **의도**를 드러낸다. 두 가지 특수 사례:
  - **변경 준비 추출**: 큰 메서드에서 몇 줄만 변경해야 하면 그 줄들을 헬퍼로 먼저 추출하고,
    헬퍼를 변경한다(추출된 메서드는 TDD 가능). 동작이 확인되면 inline해도 되지만 대개
    헬퍼를 유지하게 된다.
  - **시간적 결합(temporal coupling)**: `foo.a(); foo.b();`처럼 항상 같은 순서로 함께 호출되는
    두 호출은 `ab()`로 묶는다.
  - 다른 클래스로 옮기는 이동(Domain Logic 이동)은 `system-wide-refactoring` 스킬이 수행한다.

```

- [ ] **Step 2: Split Loop 절의 조건문 한 줄을 절차로 확장**

`## 5.5 Split Loop` 절의 `**핵심 원칙**:` 목록 마지막 항목:

```markdown
- 조건문도 동일: if문이 2가지 이상 일을 하면 각각의 if문으로 분리
```

다음으로 교체한다:

```markdown
- **조건문도 동일 — Duplicate If**: if문이 2가지 이상 일을 하면 if를 **복제**하여 각 if가
  한 가지 일만 하게 만든다. 복제 직후는 조건 평가가 중복되지만 각 블록이 독립적으로
  Extract Method 가능해진다.
- **Add Else Branch(대칭화 준비)**: if-else 두 분기의 공통 부분을 추출하려면 else가 없는
  if에 의도적으로 빈 else 분기를 추가해 구조를 대칭으로 만든 뒤 공통 부분을 추출한다.
- **Consolidate Duplicate Conditional Fragments**: if/else 각 분기에 동일한 코드 조각이
  있으면 조건문 바깥(앞 또는 뒤)으로 이동한다.

```java
// Before: 하나의 if가 두 가지 일(재고 차감 + 알림)을 함
if (order.isPaid()) {
    inventory.deduct(order.getItems());
    notifier.send(order.getCustomer(), "결제 완료");
}

// After: Duplicate If — 각 if가 한 가지 일만
if (order.isPaid()) {
    inventory.deduct(order.getItems());
}
if (order.isPaid()) {
    notifier.send(order.getCustomer(), "결제 완료");
}
```
```

- [ ] **Step 3: Trimming 절에 중복 주석 삭제 추가**

`## 6. Trimming` 절의 `**목적**: 사용하지 않는 변수, 메서드, 조건문 등 불필요한 코드 제거`를 다음으로 교체한다:

```markdown
**목적**: 사용하지 않는 변수, 메서드, 조건문 등 불필요한 코드 제거. **코드와 완전히
중복되는 주석**(Delete Redundant Comments)도 여기서 삭제한다 — 주석이 코드가 말하는 것과
동일하면 혜택 없이 비용(동기화 실패, 독자 시간)만 발생한다. 완전히 중복되는 주석만
삭제하며, 의도(WHY)를 담은 주석(4단계)은 유지한다.

```java
// Before: 코드와 동일한 내용의 주석
// X를 반환한다
return x;

// After: 주석 삭제
return x;
```
```

- [ ] **Step 4: 검증**

Run:
```bash
cd msbaek-tdd/agents/references && grep -c "^## " tidying-process.md && grep -c "Explaining Constants\|Split Variable\|Extract Helper\|Duplicate If\|Add Else Branch\|Consolidate Duplicate Conditional Fragments\|Delete Redundant Comments" tidying-process.md
```
Expected: `11` 그리고 `7` 이상

- [ ] **Step 5: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — tidying Extract Variable·Split Loop·Trimming 보강 (설명 상수, 변수 분리, Extract Helper, Duplicate If, 중복 주석 삭제)\n\nvault 근거: Tidy First Ch09·Ch12·Ch15, 기법-인덱스-통합(Duplicate If·Add Else Branch·Consolidate Duplicate Conditional Fragments·Split Variable)\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/agents/references/tidying-process.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 3: tidying-chaining.md 신규 + tidying-process.md 참조 링크 (T8, T9)

**Files:**
- Create: `msbaek-tdd/agents/references/tidying-chaining.md`
- Modify: `msbaek-tdd/agents/references/tidying-process.md` — `## 7. 품질 게이트` 절 끝(파일 끝)

**Interfaces:**
- Consumes: Task 2 완료 후 파일
- Produces: 파일명 `tidying-chaining.md` (Task 4·7이 참조하지 않음)

- [ ] **Step 1: tidying-chaining.md 작성**

```markdown
# Tidying Chaining — 정리가 정리를 유발하는 연쇄

> `tidying-process.md`의 보조 자료. 절차 순서를 대체하지 않는다. 한 단계를 마친 뒤
> "다음에 무엇이 가능해졌는가"를 확인하는 용도다.

정리 단계의 크기는 최대한 작게 유지한다. 하나의 정리는 다른 정리를 가능하게 하며,
정리하고 싶은 충동을 관리하는 것이 핵심 기술이다(80% 규칙).

## 연쇄 표

| 이 정리를 하면 | 다음이 가능해진다 |
|---|---|
| Guard Clause | 남은 조건문을 Explaining Variable / Extract Helper로 전환 |
| Dead Code(Trimming) | Reading Order / Cohesion Order로 재배치(Slide Statements) |
| Normalize Symmetries | 유사해진 병렬 코드를 Reading Order로 그룹화 (파일 상단이 목차가 된다) |
| New Interface, Old Implementation | 호출자를 하나씩 새 인터페이스로 전환 (팬아웃) |
| Reading Order | 멀리 떨어져 있어 보이지 않던 유사성이 드러나 Normalize Symmetries 가능 |
| Cohesion Order | 함께 묶인 요소가 Extract Helper / 하위 요소 추출 후보가 된다 |
| Explaining Variable | 할당의 우변이 Extract Helper 후보. 변수 이름이 중복 주석을 대체 |
| Explaining Constant | 함께 변경되는 상수를 묶어 Cohesion Order 도출 |
| Explicit Parameters | 파라미터 집합을 Parameter Object로 묶고 코드를 그 객체로 이동(system-wide 범위) |
| Chunk Statements | 각 블록에 Explaining Comment 추가 또는 Extract Helper |
| Extract Helper | 헬퍼 내부에 Guard Clause, Explaining Constant/Variable, Delete Redundant Comment |
| One Pile | 합친 뒤 Chunk Statements → Explaining Comment → Extract Helper로 재정리 |
| Explaining Comment | 주석 정보를 Explaining Variable / Constant / Helper로 코드에 이전 |
| Delete Redundant Comment | 잡음이 사라져 Reading Order와 Explicit Parameters 기회가 보인다 |

## 참조 전용 기법 — New Interface, Old Implementation

**정의**: 호출해야 하는 루틴의 인터페이스가 복잡하거나 혼란스러울 때, 원하는 형태의
새 인터페이스를 만들고 그 구현이 기존 인터페이스를 호출하게 한다(pass-through).
호출자를 새 인터페이스로 전환한 뒤 필요하면 inline한다.

**절차**:
1. 호출자 관점에서 원하는 시그니처로 새 메서드를 선언한다
2. 새 메서드 본문에서 기존 메서드를 호출한다
3. 호출자를 하나씩 새 메서드로 전환한다 (커밋 단위: 호출자 그룹별)
4. 기존 메서드의 호출자가 0이 되면 기존 메서드를 inline하거나 삭제한다

**제약**: tidying 기본 절차에 포함하지 않는다. pass-through 메서드는 Middle Man 냄새
(불필요한 간접 호출, 의미 없는 계층)를 만들 수 있다. 3단계에서 전환이 멈추면 4단계 대신
`system-wide-refactoring`의 Remove Middle Man을 적용한다.
```

- [ ] **Step 2: tidying-process.md 파일 끝에 참조 링크 추가**

파일 마지막 줄(`> 이때는 억지로 고치지 말고 One Pile로 합친 후 올바르게 재추출한다.`) 뒤에 추가한다:

```markdown

## 참조

- `tidying-chaining.md` — 정리 연쇄 표, New Interface·Old Implementation(참조 전용)
```

- [ ] **Step 3: 검증**

Run:
```bash
cd msbaek-tdd/agents/references && test -f tidying-chaining.md && grep -c "^| " tidying-chaining.md && grep -c "^## " tidying-process.md && grep -n "tidying-chaining.md" tidying-process.md
```
Expected: 표 행 `16`(헤더 2 + 본문 14), 절 수 `12`, 링크 1행. **주의**: 이 Task에서 `## 참조` 절이 추가되어 절 수 기준이 11 → 12가 된다. Global Constraints의 "11개 동일"은 0~7 단계 절에 대한 제약이며 `## 참조`는 단계가 아니다.

- [ ] **Step 4: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — tidying-chaining.md 신규 (연쇄 표, New Interface·Old Implementation 참조)\n\nvault 근거: Tidy First Ch04·Ch17\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/agents/references/tidying-chaining.md msbaek-tdd/agents/references/tidying-process.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 4: parallel-change.md 신규 + 링크 (O2)

**Files:**
- Create: `msbaek-tdd/references/parallel-change.md`
- Modify: `msbaek-tdd/agents/references/tidying-process.md:211` (`- 파라미터 순서 변경 시 호출자가 많으면 Parallel Change 패턴 사용 (별도 커밋)`)

**Interfaces:**
- Consumes: Task 3 완료 후 파일
- Produces: `references/parallel-change.md`. Task 5가 system-wide SKILL.md에서 이 경로를 참조한다 (`../../references/parallel-change.md`).

- [ ] **Step 1: parallel-change.md 작성**

```markdown
# Parallel Change (Expand → Migrate → Contract)

> 리팩터링 스킬 공통 참조. 호환성을 깨는 변경(breaking change)을 호환성을 유지하는 여러
> 작은 단계로 분해한다. 시그니처·파라미터 순서·필드·API·스키마 변경에 적용한다.

## 절차

1. **Expand(확장)**: 새 요소(메서드·파라미터·필드·컬럼·API)를 추가한다. 기존 요소는
   삭제하지 않고 유지한다. 두 요소가 공존하며 기존 호출자는 영향을 받지 않는다.
2. **Migrate(전환)**: 호출자를 새 요소로 하나씩 옮긴다. 데이터가 있으면 dual-write(신·구
   양쪽 기록)와 read fallback(신규 없으면 기존 읽기)으로 정합성을 유지한다. 커밋 단위는
   호출자 그룹별로 나눈다.
3. **Contract(수축)**: 기존 요소의 사용처가 0임을 확인한 뒤 기존 요소를 제거한다.
   Migrate 없이 Expand → Contract로 직행하지 않는다.

## Contract 진입 판단

- 기존 요소를 참조하는 코드가 0건이다 (IDE Find Usages, 컴파일)
- 배포 단위가 여러 개면 기존 요소 접근 카운터가 관측 기간 동안 0이다

## 코드 수준 예 — 파라미터 순서 정규화(Canonical Order)

```java
// Expand: 정규 순서(needle, haystack)의 새 메서드 추가. 기존 find(haystack, needle) 유지
int find(Haystack haystack, Needle needle) { return find2(needle, haystack); }
int find2(Needle needle, Haystack haystack) { ... }

// Migrate: 호출자를 find2로 하나씩 전환 (그룹별 커밋)

// Contract: find 삭제 후 find2 → find로 rename
```

## 대규모 교체 — Branch by Abstraction

모듈·라이브러리·프레임워크 등 공급자(provider) 교체에 적용한다. 트렁크 기반 개발을
유지하면서 점진적으로 전환한다.

1. 클라이언트 코드와 현재 공급자 사이에 추상화 계층(interface)을 만든다
2. 클라이언트를 한 섹션씩 추상화 계층 호출로 전환한다
3. 새 공급자 구현을 추상화 계층 뒤에 만든다. feature flag로 전환·검증한다
4. 기존 공급자와 (필요하면) 추상화 계층을 제거한다

공통 원칙: 추상화 계층으로 다중 구현이 공존한다. 항상 빌드·정상 실행 상태를 유지한다.

## 제약

- 한 커밋에 Expand와 Contract를 함께 넣지 않는다
- Migrate 중 테스트가 실패하면 그 호출자 전환만 되돌린다
```

- [ ] **Step 2: tidying-process.md의 Parallel Change 한 줄에 경로 추가**

```markdown
- 파라미터 순서 변경 시 호출자가 많으면 Parallel Change 패턴 사용 (별도 커밋)
```
을 다음으로 교체한다:
```markdown
- 파라미터 순서 변경 시 호출자가 많으면 Parallel Change 패턴 사용 (별도 커밋) —
  절차는 `../../references/parallel-change.md`
```

- [ ] **Step 3: 검증**

Run:
```bash
cd msbaek-tdd && test -f references/parallel-change.md && grep -c "^## " references/parallel-change.md && grep -n "parallel-change.md" agents/references/tidying-process.md
```
Expected: `5`, 링크 1행

- [ ] **Step 4: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — references/parallel-change.md 신규 (Expand→Migrate→Contract, Branch by Abstraction)\n\nvault 근거: Expand-Contract-Pattern(Parallel-Change), Branch-By-Abstraction, Tidying-Canonical-Order\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/references/parallel-change.md msbaek-tdd/agents/references/tidying-process.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 5: system-wide-refactoring — 후보 유형·커밋 형식 추가 (S1, S4, S5, S6, S7, S8)

**Files:**
- Modify: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` — GOAL 절, `#### 코드 분석` 절(39~70행), `#### 후보 제시 예시` 절, `**커밋 메시지 형식**` 목록(139~144행), FAILURE CONDITIONS

**Interfaces:**
- Consumes: Task 4의 `references/parallel-change.md`
- Produces: 후보 유형명 `Pull Up Method`, `Push Down → Delegate`, `Train Wreck`, `Remove Middle Man`, `Programming by Difference`. Task 6이 같은 파일에 절을 추가하므로 절 제목(`#### ...`)을 유지한다.

- [ ] **Step 1: GOAL 두 번째 항목 확장**

```markdown
- Extract Method / Extract Delegate / Domain Logic 이동 / SoC(Split Phase, Split by Abstraction Layer, Split by Unrelated Complexity) 후보가 식별됨
```
을 다음으로 교체한다:
```markdown
- Extract Method / Extract Delegate / Domain Logic 이동 / SoC(Split Phase, Split by Abstraction Layer, Split by Unrelated Complexity) / 상속 계층(Pull Up Method, Push Down → Delegate) / 유사 기능 통합(Programming by Difference) 후보가 식별됨
```

- [ ] **Step 2: Extract Delegate 후보에 Fat Class 3기준 추가 (S7)**

```markdown
**Extract Delegate 후보**:
- 한 클래스가 과다한 책임을 가진 경우
- 관련 필드와 메서드가 그룹을 이루는 경우
```
을 다음으로 교체한다:
```markdown
**Extract Delegate 후보** (Fat Class 분리 3기준):
- **ISP 기준**: 클라이언트마다 사용하는 메서드 집합이 다르면 클라이언트별 인터페이스 단위로 분리한다
- **관련 필드·메서드 기준**: 함께 읽고 쓰는 필드와 메서드가 그룹을 이루면 그 그룹을 클래스로 추출한다
- **관련 협력자(collaborator) 기준**: 테스트 setUp에서 함께 mock되는 협력자 그룹이 있으면
  그 그룹을 사용하는 메서드들이 하나의 클래스 경계 후보다 (Split by Unrelated Complexity와 같은 신호)
```

- [ ] **Step 3: Domain Logic 이동 후보에 Train Wreck·Remove Middle Man 추가 (S1, S5)**

`**Domain Logic 이동 후보**:` 목록의 마지막 항목 `- Domain Service, Value Object, First Class Collection 추출 가능` 뒤에 추가한다:

```markdown
- **Train Wreck 제거** — `a.getB().getC().doSomething()` 연쇄 호출(Law of Demeter 위반)을
  2단계로 해소한다: ① 연쇄 호출을 포함한 로직을 Extract Method → ② 추출한 메서드를
  연쇄의 시작 객체(`a` 또는 `B`)로 Move Method. Hide Delegate가 위임 메서드를 추가하는 것과
  달리 로직 자체를 옮긴다
- **Remove Middle Man** (Hide Delegate의 역) — 단순 위임만 하는 메서드가 많아져 클라이언트가
  위임 객체를 직접 다루는 편이 자연스러우면 위임 메서드를 제거하고 위임 객체를 노출한다.
  Hide Delegate와 Remove Middle Man은 같은 축의 양 끝이며, 위임 메서드 수를 기준으로 판단한다
```

- [ ] **Step 4: Split by Abstraction Layer 후보에 Push Down → Delegate 절차 추가 (S6)**

`**Split by Abstraction Layer 후보**:` 목록 뒤(`**Split by Unrelated Complexity 후보**:` 앞)에 추가한다:

```markdown
- **낮은 수준 기능이 높은 수준 클래스에 섞였을 때의 절차** (Push Down → Delegate → 상속 제거):
  ① 낮은 수준 기능을 담을 새 클래스를 **임시로 원본 클래스의 하위 클래스**로 만든다
  ② 옮길 필드·메서드를 Push Members Down으로 하위 클래스에 내린다
  ③ 테스트가 통과하도록 원본 클래스가 하위 클래스 인스턴스에 위임(delegate)하게 바꾼다
  ④ 상속 관계를 제거해 합성(composition)으로 확정한다. 각 단계마다 테스트를 실행한다
```

- [ ] **Step 5: 상속 계층·유사 기능 후보 절 신설 (S4, S8)**

`**Split Phase 후보** (Functional Core & Imperative Shell 포함):` 목록 뒤(`#### 후보 제시 예시` 제목 앞)에 추가한다:

```markdown
**Pull Up Method 후보** (서브클래스 간 중복):
- 여러 서브클래스가 같은 메서드를 동일하게 override한 경우. 절차(IDE 자동 리팩터링 활용):
  ① superclass의 abstract 메서드에서 `abstract`를 제거한다
  ② 각 서브클래스의 override 메서드를 같은 이름으로 rename하고 Pull Members Up한다.
     IDE가 다른 서브클래스의 중복도 바꾸겠느냐고 물으면 "Skip"을 선택한다 (서브클래스 간
     중복은 자동으로 제거되지 않으므로 모든 서브클래스에 대해 rename → pull up을 반복한다)
  ③ pull up된 메서드 하나를 골라 본문을 Extract Method하며 IDE의 "All"(전체 치환)을 선택해
     나머지 중복도 한 번에 치환한다
  ④ superclass 구현을 추출한 메서드 호출로 바꾼다
  ⑤ 사용되지 않는 서브클래스 메서드를 제거한다

**유사 기능 통합 후보** (Programming by Difference):
- 새 기능이 기존 기능과 대부분 같고 일부만 다를 때. 순서: ① 복사·붙여넣기로 동작시킨다 →
  ② 차이점만 남기고 공통 부분을 추출한다(Programming by Difference) → ③ Template Method
  패턴으로 수렴한다(상속 또는 위임). vault에는 ①~③ 목록만 있고 세부 절차는 없으므로
  후보 제시 시 차이점 목록을 사용자에게 먼저 확인한다
```

- [ ] **Step 6: 후보 제시 예시에 Pull Up Method 예시 추가**

`## 리팩토링 후보 N: Hide Delegate (Domain Logic 이동)` 예시 코드 블록 종료 직후(`- 사용자가 **yes** → 실행 목록에 추가` 앞)에 추가한다:

````markdown
```
## 리팩토링 후보 N: Pull Up Method (서브클래스 중복 제거)

**파일**: CardPayment.java, BankTransferPayment.java, PointPayment.java
**대상**: validate() — 3개 서브클래스가 동일 구현으로 override

**현재 코드**:
[각 서브클래스의 validate() 본문 — 동일]

**제안 변경**:
1. Payment.validate()의 abstract 제거
2. 각 서브클래스 validate()를 rename → Pull Members Up (Skip 선택), 3회 반복
3. pull up된 메서드 본문을 Extract Method(All) → 나머지 중복 치환
4. 사용되지 않는 서브클래스 메서드 제거

**적용할까요?** (yes / no / 수정 요청)
```
````

- [ ] **Step 7: 커밋 메시지 형식 추가**

`- `refactor: split unrelated complexity [설명] from [클래스명]`` 뒤에 추가한다:

```markdown
- `refactor: pull up [메서드명] to [상위클래스명]`
- `refactor: push down [설명] to [하위클래스명] and delegate`
- `refactor: remove middle man [메서드명] in [클래스명]`
- `refactor: extract common part of [기능A]/[기능B] into [템플릿 메서드명]`
```

- [ ] **Step 8: FAILURE CONDITIONS 추가**

FAILURE CONDITIONS 목록 마지막 `- Split Phase 적용 시 중간 데이터 구조 없이 단계만 분리 (단계 간 결합 유발)` 뒤에 추가한다:

```markdown
- Push Down → Delegate 절차에서 상속을 제거하지 않고 종료 (임시 상속이 영구화됨)
- Pull Up 시 IDE 중복 치환에 "Replace"를 선택해 서브클래스 본문이 superclass 호출로 바뀐 채 중복 확인을 건너뜀
- 시그니처·파라미터 순서 변경을 한 커밋에 Expand와 Contract를 함께 넣어 수행 (절차는 `../../references/parallel-change.md`)
```

- [ ] **Step 9: 검증**

Run:
```bash
cd msbaek-tdd/skills/system-wide-refactoring && grep -c "Train Wreck\|Remove Middle Man\|Pull Up Method 후보\|Push Members Down\|Programming by Difference\|ISP 기준\|parallel-change.md" SKILL.md && grep -c "^- \`refactor:" SKILL.md
```
Expected: `7` 이상, `10`

- [ ] **Step 10: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — system-wide 후보 유형 추가 (Train Wreck, Remove Middle Man, Pull Up, Push Down→Delegate, Fat Class 3기준, Programming by Difference)\n\nvault 근거: 기법-인덱스-통합, Refactoring-II #19, Cases/서브클래스들의 중복 제거, 하위 수준의 추가 기능이 상위 수준에 있을 때, Fat Class를 나누는 3가지 방법, 유사한-기능을-추가하는-절차\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/skills/system-wide-refactoring/SKILL.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 6: system-wide-refactoring — 적용 순서 절 + Mikado 대화형 절차 (S2, S3, S9)

**Files:**
- Modify: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` — `#### 코드 분석` 절 앞에 새 `#### 적용 순서` 절, `#### 기별 적용 실행` 절에 Mikado 분기

**Interfaces:**
- Consumes: Task 5 완료 후 파일
- Produces: 절 제목 `#### 적용 순서 — 후보 제시의 기본 순서`, `**대규모 범위 — Mikado Method 분기**`

- [ ] **Step 1: 적용 순서 절 삽입**

`#### 코드 분석 — 리팩토링 후보 식별 (공통 절차 2단계)` 제목 **앞**에 삽입한다:

```markdown
#### 적용 순서 — 후보 제시의 기본 순서

후보를 제시할 때 아래 순서를 기본으로 정렬한다. 사용자가 순서를 바꾸면 그에 따른다.

**A. TDD 직후(테스트에 로직이 모여 있는 상태) — 초기 리팩터링 7단계**:
1. 모든 로직을 테스트에 구현한 상태에서 시작한다 (이 전제가 없으면 2~7의 순서가 성립하지 않는다)
2. AAA 구조의 테스트에서 Act 부분을 Extract Method한다
3. Act가 의존성 객체를 쓰면: ① Introduce Parameter로 의존성을 파라미터로 → ② Introduce
   Parameter Object로 파라미터들을 객체(Application Service)로 묶는다 (Application Service에
   그대로 전달될 파라미터는 제외) → ③ Move Instance Method to Application Service.
   의존성이 Application Service 생성자로 전달되어 의존성 주입(DI)이 가능해진다
4. Act가 의존성 객체를 쓰지 않으면: Extract Delegate로 Application Service를 추출한다
5. Application Service에서 Slide Statements로 I/O → 계산 → I/O 구조(Functional Core /
   Imperative Shell)를 확보한다
6. Application Service에서 Extract Method로 도메인 로직을 메서드로 추출한다
7. 추출된 도메인 로직을 Extract Delegate·Move Instance Method로 domain 계층에 옮긴다

**B. 기존 트랜잭션 스크립트 → 도메인 모델 (Jimmy Bogard 9단계)**:
1. Composed Method — 긴 메서드를 같은 추상화 수준의 작은 메서드로 분해
2. Extract Methods — 주석 기준으로 블록 추출
3. Introduce Parameter — 의존성 명시화
4. Extract Class — seam 생성
5. Extract Interface — 테스트 용이성
6. Make Method Non-Static — Feature Envy 해소를 위한 인스턴스 메서드 전환
7. Move Method — 데이터를 가진 객체로 이동
8. Inline (Undo) — 이동 결과가 불균형하면 되돌리고 재추출한다. 리팩터링은 되돌릴 수 있어야 한다
9. Reduce Setter Scope — private setter로 캡슐화 강화

A와 B는 출발 상태가 다르다(A: 테스트에 로직 집중, B: 기존 서비스 코드). 둘을 섞지 않는다.

```

- [ ] **Step 2: Mikado 분기 추가**

`#### 기법별 적용 실행 (공통 절차 4단계)` 절의 `1. 리팩토링 적용` 줄 뒤, `**커밋 메시지 형식**:` 앞에 추가한다:

```markdown

**대규모 범위 — Mikado Method 분기**: 하나의 후보를 적용했을 때 컴파일 오류·테스트 실패가
연쇄적으로 발생하고 30분(타임박스) 안에 수습되지 않으면 강행하지 않고 다음 절차로 전환한다.
사용자와 대화형으로 진행하며 자동 실행하지 않는다.
1. 변경을 되돌린다(`git checkout -- <파일>`). 컴파일이 깨진 상태에서는 IDE 자동 리팩터링이
   동작하지 않으므로 항상 컴파일 가능한 상태로 복귀한다
2. 실패 원인을 "이 변경의 **전제 조건**"으로 기록한다 (예: "OrderService가 Repository를
   직접 생성함 → 생성자 주입으로 바꿔야 함")
3. 전제 조건과 목표의 의존 관계를 목록 또는 그래프로 사용자에게 제시한다
4. 전제 조건 중 안전하게 완료할 수 있는 것부터 하나씩 적용·커밋한다 (각각이 독립 후보가 된다)
5. 전제 조건이 모두 해결되면 원래 후보로 돌아가 다시 적용한다. 다시 실패하면 2로 돌아간다

```

- [ ] **Step 3: 검증**

Run:
```bash
cd msbaek-tdd/skills/system-wide-refactoring && grep -n "^#### " SKILL.md && grep -c "Mikado Method 분기\|초기 리팩터링 7단계\|Jimmy Bogard 9단계\|Inline (Undo)" SKILL.md
```
Expected: `#### 적용 순서` 가 `#### 코드 분석` 앞에 위치, 카운트 `4`

- [ ] **Step 4: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — system-wide 적용 순서 절 (TDD 직후 7단계, Bogard 9단계) + Mikado 대화형 분기\n\nvault 근거: Refactoring Techniques(TDD에서의 초기 Refactoring), 리팩터링 기법 목록 §5, Exploratory Refactoring(미카도 메소드)\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/skills/system-wide-refactoring/SKILL.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

### Task 7: tdd-blue 작업 원칙 한 줄(O3) + 버전 1.47.0 + 플랜 INDEX 완료 처리

**Files:**
- Modify: `msbaek-tdd/agents/tdd-blue.md:29` (80% 규칙 줄 뒤)
- Modify: `msbaek-tdd/.claude-plugin/plugin.json:3`, `.claude-plugin/marketplace.json:15`
- Modify: `.claude/plans/2026-09-13-vault-refactoring-techniques/INDEX.md`, `.claude/plans/INDEX.md`

**Interfaces:**
- Consumes: Task 1~6 완료
- Produces: 릴리스 1.47.0

- [ ] **Step 1: tdd-blue.md 작업 원칙에 Preparatory Refactoring 추가**

```markdown
- **80% 규칙** — 80% 이하로 리팩토링한다. 기준은 **의도 전달 가능한 가독성**이다
```
뒤에 추가한다:
```markdown
- **준비 리팩터링(Preparatory Refactoring)** — tidying의 목적은 다음 변경을 쉽게 만드는
  것이다("변경을 쉽게 만들고, 그다음 쉬운 변경을 하라"). 다음 변경과 무관한 개선은
  이 단계의 대상이 아니다. 이해를 위한 리팩터링(Comprehension)과 중복 통합(Consolidation)은
  변경 영향 범위(blast radius) 안에서만 수행한다
```

- [ ] **Step 2: 버전 두 곳 bump**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
sed -i '' 's/"version": "1.46.10"/"version": "1.47.0"/' msbaek-tdd/.claude-plugin/plugin.json
python3 - <<'EOF'
import json,pathlib
p=pathlib.Path('.claude-plugin/marketplace.json'); d=json.loads(p.read_text())
for pl in d['plugins']:
    if pl['name']=='msbaek-tdd': pl['version']='1.47.0'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
EOF
grep -n '"version"' msbaek-tdd/.claude-plugin/plugin.json .claude-plugin/marketplace.json
```
Expected: plugin.json `1.47.0`, marketplace.json msbaek-tdd 항목 `1.47.0` (marketplace 자체 버전 `1.2.0`은 그대로)

- [ ] **Step 3: 플랜 INDEX 완료 처리**

`.claude/plans/2026-09-13-vault-refactoring-techniques/INDEX.md`의 `Status: active` → `Status: completed`, `Phase:` 줄을 `Phase: 완료 (2026-09-14, 1.47.0 릴리스)`로 교체. `.claude/plans/INDEX.md`에서 해당 줄을 `## Active`에서 `## Completed` 첫 줄로 이동하고 끝에 ` | completed: 2026-09-14`를 붙인다.

- [ ] **Step 4: 검증**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
grep -c "Preparatory Refactoring" msbaek-tdd/agents/tdd-blue.md
grep -c "^## " msbaek-tdd/agents/references/tidying-process.md
grep -A1 "^## Completed" .claude/plans/INDEX.md | grep -c "2026-09-13-vault-refactoring"
```
Expected: `1`, `12`(단계 11 + 참조 1), `1`

- [ ] **Step 5: 커밋**

```bash
cd /Users/msbaek/git/msbaek-claude-plugins
printf 'feat(msbaek-tdd): 1.47.0 — tdd-blue 준비 리팩터링 원칙 + 버전 bump + 플랜 완료\n\nvault 조사(2026-09-13) 편입 완료: tidying 항목 보강 9건, system-wide 후보·순서 9건, references 2건\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01C6dsUkY9itmLM5MjkPoCNn\n' > /tmp/cm.txt
git add msbaek-tdd/agents/tdd-blue.md msbaek-tdd/.claude-plugin/plugin.json .claude-plugin/marketplace.json .claude/plans/2026-09-13-vault-refactoring-techniques/INDEX.md .claude/plans/INDEX.md
git commit -F /tmp/cm.txt && rm /tmp/cm.txt
```

---

## Self-Review

**Spec coverage** — report.md 항목 대조:
- T1 Explaining Constants → Task 2 / T2 Delete Redundant Comments → Task 2 / T3 Move Declaration → Task 1 / T4 Duplicate If·Add Else → Task 2 / T5 Code Paragraph → Task 1 / T6 Extract Helper → Task 2 / T7 Split Variable·Consolidate Fragments → Task 2 / T8 New Interface → Task 3(참조 전용) / T9 Chaining → Task 3
- S1 Train Wreck → Task 5 / S2 Bogard 9단계 → Task 6 / S3 TDD 7단계 → Task 6 / S4 Pull Up 5단계 → Task 5 / S5 Remove Middle Man → Task 5 / S6 Push Down→Delegate → Task 5 / S7 Fat Class 3기준 → Task 5 / S8 Programming by Difference → Task 5 / S9 Mikado → Task 6
- O2 Parallel Change → Task 4 / O3 Refactoring-Types 인용 → Task 7 / O1 → 범위 밖(Global Constraints 명시) / X1·X2 현행 유지 → 변경 없음
- 제외 항목(Move Return closer to computation) → 어느 Task에도 없음 ✓

**Placeholder scan**: "TBD/TODO/적절히/Similar to Task N" 없음. 모든 편집 단계에 삽입 본문 포함.

**Consistency**: `references/parallel-change.md` 경로는 Task 4 생성, Task 4(tidying-process.md `../../references/parallel-change.md`)·Task 5(system-wide `../../references/parallel-change.md`)에서 참조 — 두 파일 모두 `msbaek-tdd/<x>/<y>/` 깊이 2이므로 상대 경로 동일 ✓. 후보 유형명 "Pull Up Method"는 Task 5 GOAL·후보 절·예시·커밋 형식에서 동일 표기 ✓. 절 수 기준: Task 1·2는 11, Task 3 이후 12(`## 참조` 추가) — Task 7 검증도 12로 기재 ✓.
