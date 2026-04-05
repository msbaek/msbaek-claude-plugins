# Refactoring Skills 확장 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** tidy 필수 파이프라인에 Normalize Symmetries, Split Loop를 추가하고, system-wide에 SoC 3개 기법을 추가하며, 12개 선택 slash command 스킬을 생성한다.

**Architecture:** 기존 tdd-blue agent와 tdd-tidy/system-wide-refactoring 스킬을 수정하고, 12개 독립 SKILL.md 파일을 생성한다. 각 선택 스킬은 동일한 워크플로우(대상 식별 → 후보 제시 → 사용자 확인 → 실행 → 커밋)를 따른다. plugin.json에 새 스킬을 등록한다.

**Tech Stack:** Claude Code Plugin (SKILL.md markdown), tdd-blue agent (markdown)

**Plugin base:** `/Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins/msbaek-tdd`

---

## Task 1: tdd-blue agent에 Normalize Symmetries 추가 (단계 2.5)

**Files:**
- Modify: `msbaek-tdd/agents/tdd-blue.md`

- [ ] **Step 1: 프로세스 흐름 다이어그램에 2.5단계 삽입**

`msbaek-tdd/agents/tdd-blue.md`의 프로세스 흐름 ASCII 다이어그램(라인 77~101)에서, `2. Reorder` 이후 `3. Chunk Statements` 사이에 `2.5 Normalize Symmetries` 노드를 추가한다:

```
      2. Reorder (Slide Statements)
           ▼
      2.5 Normalize Symmetries (Canonical Order 포함)
           ▼
      3. Chunk Statements
```

- [ ] **Step 2: 2.5 Normalize Symmetries 상세 섹션 추가**

`##### 2. Reorder (Slide Statements)` 섹션과 `##### 3. Chunk Statements` 섹션 사이에 다음을 삽입:

```markdown
##### 2.5 Normalize Symmetries (Canonical Order 포함)
**목적**: 의미 없는 차이를 제거하여 코드 신뢰도 향상. "차이는 차이를 신호해야 한다"
- 동일한 로직이 다른 방식으로 표현된 곳을 하나의 방식으로 통일
- Canonical Order: 필드/변수/파라미터 선언 순서를 일관되게 유지

```java
// Before: 동일 패턴이 다른 방식으로 표현
if (user == null) return Optional.empty();
// ... 다른 코드 ...
if (order != null) {
    processOrder(order);
}

// After: 동일 패턴은 동일 방식으로
if (user == null) return Optional.empty();
// ... 다른 코드 ...
if (order == null) return Optional.empty();
processOrder(order);
```

```java
// Before: 선언 순서 불일치 (Canonical Order 위반)
void process(User user, Product product) { ... }
void validate(Product product, User user) { ... }  // 왜 순서가 다른가?

// After: 정규 순서 유지
void process(User user, Product product) { ... }
void validate(User user, Product product) { ... }
```

**핵심 원칙**:
- 다를 이유가 없다면 같아야 한다
- 알파벳 순서 같은 기계적 규칙보다 **의미 기반 순서**가 좋다
- 파라미터 순서 변경 시 호출자가 많으면 Parallel Change 패턴 사용 (별도 커밋)
```

- [ ] **Step 3: description 필드에 Normalize Symmetries 반영**

파일 상단 frontmatter의 `description` 필드를 업데이트:

```yaml
description: TDD Blue phase - Composed Method 지향 Local Tidying Process (Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming).
```

- [ ] **Step 4: Standalone 모드 작업 절차 업데이트**

`#### 2. Tidying Process 적용` 섹션(라인 310~318, 364~374 두 곳 모두)의 목록에 2.5 단계를 추가:

```markdown
0. Guard Clauses (중첩 제거 — 가장 먼저)
1. One Pile (조건부 — Composed Method 위배 시)
2. Reorder (Slide Statements)
2.5 Normalize Symmetries (Canonical Order 포함)
3. Chunk Statements
4. Explaining Comment ← 필수1
5. Extract Variable ← 필수2
5.5 Split Loop (루프가 2가지 이상 일을 하면 분리)
6. Trimming
7. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

- [ ] **Step 5: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/agents/tdd-blue.md
git commit -m "refactor: tdd-blue에 Normalize Symmetries(2.5단계) 추가"
```

---

## Task 2: tdd-blue agent에 Split Loop 추가 (단계 5.5)

**Files:**
- Modify: `msbaek-tdd/agents/tdd-blue.md`

- [ ] **Step 1: 프로세스 흐름 다이어그램에 5.5단계 삽입**

`5. Extract Variable` 이후 `6. Trimming` 사이에 `5.5 Split Loop` 노드를 추가:

```
      5. Extract Variable ← 필수2
           ▼
      5.5 Split Loop
           │
           ├→ 6. Trimming
```

- [ ] **Step 2: 5.5 Split Loop 상세 섹션 추가**

`##### 5. Extract Variable` 섹션과 `##### 6. Trimming` 섹션 사이에 다음을 삽입:

```markdown
##### 5.5 Split Loop (루프가 2가지 이상 일을 하면 분리)
**목적**: 하나의 루프가 여러 관심사를 처리하면 각각의 루프로 분리. Extract Variable/Method의 전제 조건.

```java
// Before: 하나의 루프가 2가지 일을 함
double totalSalary = 0;
int youngestAge = Integer.MAX_VALUE;
for (Person p : people) {
    totalSalary += p.getSalary();         // 관심사 1: 급여 합산
    youngestAge = Math.min(youngestAge, p.getAge()); // 관심사 2: 최소 나이
}

// After: 관심사별로 루프 분리
double totalSalary = 0;
for (Person p : people) {
    totalSalary += p.getSalary();
}

int youngestAge = Integer.MAX_VALUE;
for (Person p : people) {
    youngestAge = Math.min(youngestAge, p.getAge());
}
```

**핵심 원칙**:
- 성능 걱정은 하지 않는다 — 현대 컴파일러/JIT이 최적화한다
- 분리 후 각 루프는 Extract Variable이나 Replace Loop with Pipeline(stream)이 가능해진다
- 조건문도 동일: if문이 2가지 이상 일을 하면 각각의 if문으로 분리
```

- [ ] **Step 3: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/agents/tdd-blue.md
git commit -m "refactor: tdd-blue에 Split Loop(5.5단계) 추가"
```

---

## Task 3: tdd-tidy SKILL.md 업데이트

**Files:**
- Modify: `msbaek-tdd/skills/tdd-tidy/SKILL.md`

- [ ] **Step 1: GOAL 섹션의 단계 목록 업데이트**

라인 15의 `Local Tidying Process가 적용됨 (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming)` 을 다음으로 변경:

```markdown
- Local Tidying Process가 적용됨 (Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming)
```

- [ ] **Step 2: tdd-blue 호출 메시지 업데이트**

라인 64~71의 tdd-blue agent 호출 메시지를 다음으로 변경:

```markdown
```
[standalone] 다음 파일에 Local Tidying Process를 적용해주세요:
- src/main/java/com/example/OrderService.java
- src/main/java/com/example/PaymentProcessor.java

Local Tidying Process (Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming)를 순서대로 적용하고,
변경이 있으면 하나의 refactor: 커밋으로 완료해주세요.
Extract Method와 Domain Logic 이동은 수행하지 마세요 (system-wide-refactoring 스킬 전담).
```
```

- [ ] **Step 3: 완료 후 선택 기법 제안 섹션 추가**

`#### 4. 결과 보고` 섹션 내용을 다음으로 교체:

```markdown
#### 4. 결과 보고

tdd-blue agent 완료 후 사용자에게 결과 보고:
- 적용된 tidying 단계
- 변경된 파일과 주요 개선 사항
- 커밋 해시 (변경이 있는 경우)

tidying 과정에서 발견된 징후에 따라 선택 기법 제안:

```
추가로 적용 가능한 기법이 발견되었습니다:
[발견 시에만 해당 항목 표시]
- /decompose-conditional — [파일명]의 if/then/else가 복잡합니다
- /replace-temp-with-query — [파일명]에서 임시 변수가 반복 계산됩니다
- /explicit-parameters — [파일명]에서 암묵적 필드 의존이 발견되었습니다
- /naming-process — 의도가 불분명한 이름이 [N]건 있습니다
- /encapsulate-collection — [파일명]에서 컬렉션이 직접 노출됩니다
적용할 기법을 선택하세요 (slash command 또는 skip)
```
```

- [ ] **Step 4: description 필드 업데이트**

frontmatter의 description을 업데이트:

```yaml
description: git diff 기준 변경 파일을 자동 탐지하여 Composed Method 지향 Tidying Process를 독립 실행. 완료 후 선택 기법 제안. /tdd-tidy로 호출.
```

- [ ] **Step 5: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/skills/tdd-tidy/SKILL.md
git commit -m "refactor: tdd-tidy 단계 목록 업데이트 및 선택 기법 제안 추가"
```

---

## Task 4: system-wide-refactoring SKILL.md에 SoC 3개 기법 추가

**Files:**
- Modify: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

- [ ] **Step 1: GOAL 섹션 업데이트**

라인 14의 `Extract Method / Domain Logic 이동 후보가 식별됨` 을 다음으로 변경:

```markdown
- Extract Method / Extract Delegate / Domain Logic 이동 / SoC(Split Phase, Split by Abstraction Layer, Split by Unrelated Complexity) 후보가 식별됨
```

- [ ] **Step 2: 코드 분석 섹션에 SoC 패턴 추가**

라인 62~65의 `#### 2. 코드 분석 — 리팩토링 후보 식별` 섹션에서 기존 **Domain Logic 이동 후보** 다음에 다음 블록을 추가:

```markdown
**Split by Abstraction Layer 후보**:
- High-level 비즈니스 로직과 Low-level 인프라 코드(DB, I/O)가 한 메서드에 혼재
- App 계층과 Domain 계층이 분리되지 않은 경우

**Split by Unrelated Complexity 후보**:
- 서로 관계없는 복잡성(예: 사용자 처리 로직과 상품 처리 로직)이 한 메서드/클래스에 혼재
- 서로 다른 변경 이유를 가진 코드가 결합된 경우

**Split Phase 후보** (Functional Core & Imperative Shell 포함):
- 서로 다른 계산 단계가 한 메서드에 혼재 (예: 파싱 → 처리 → 포매팅)
- 순수 로직과 부수효과(I/O)가 분리되지 않은 경우 (빵속빵 패턴)
  - 패턴: I/O(impure) → 비즈니스 로직(pure) → I/O(impure)
- 중간 데이터 구조(Intermediate Data Structure)로 단계를 연결
```

- [ ] **Step 3: 후보 제시 예시에 SoC 추가**

라인 72~84의 `#### 3. 리팩토링 후보 제시` 섹션에 SoC 후보 제시 예시를 추가:

```markdown
```
## 리팩토링 후보 N: Split Phase (Functional Core & Imperative Shell)

**파일**: OrderService.java
**대상**: processOrder() 메서드 (35줄)

**현재 코드**:
[해당 코드 블록 — DB 조회, 비즈니스 로직, DB 저장이 혼재]

**제안 변경**:
1. DB 조회를 메서드 상단으로 모음 (Imperative Shell — 빵)
2. 순수 비즈니스 로직을 별도 메서드로 추출 (Functional Core — 속)
3. DB 저장을 메서드 하단으로 모음 (Imperative Shell — 빵)

**적용할까요?** (yes / no / 수정 요청)
```
```

- [ ] **Step 4: 커밋 메시지 형식에 SoC 추가**

라인 112~118의 커밋 메시지 형식 섹션에 추가:

```markdown
- `refactor: split phase [설명] in [클래스명]`
- `refactor: split by abstraction layer [설명] in [클래스명]`
- `refactor: split unrelated complexity [설명] from [클래스명]`
```

- [ ] **Step 5: 완료 후 선택 기법 제안 섹션 추가**

`#### 7. 원래 브랜치로 복귀 및 결과 보고` 섹션 말미에 추가:

```markdown
리팩토링 과정에서 발견된 추가 개선 기회를 제안:

```
추가로 발견된 개선 기회:
[발견 시에만 해당 항목 표시]
- /extract-method-object — [파일명]에서 지역 변수 얽힘으로 Extract Method 불가
- /replace-conditional-with-poly — [파일명]에 반복 switch/if-else [N]곳
- /introduce-parameter-object — [파일명]에 3개 이상 파라미터 그룹 반복
- /discover-value-object — [파일명]에 primitive 타입에 로직 집중
- /first-class-collection — [파일명]에 컬렉션+관련 로직 산재
- /lift-up-conditional — [파일명]에 동일 조건문 중복
- /separate-query-modifier — [파일명]에 값 반환과 부수효과 혼재
적용할 기법을 선택하세요 (slash command 또는 skip)
```
```

- [ ] **Step 6: FAILURE CONDITIONS에 SoC 관련 추가**

기존 failure conditions 목록에 추가:

```markdown
- ❌ Split Phase 적용 시 중간 데이터 구조 없이 단계만 분리 (단계 간 결합 유발)
```

- [ ] **Step 7: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/skills/system-wide-refactoring/SKILL.md
git commit -m "refactor: system-wide에 SoC 3개 기법 추가 및 선택 기법 제안"
```

---

## Task 5: 선택 스킬 생성 — tidy 계열 5개

**Files:**
- Create: `msbaek-tdd/skills/replace-temp-with-query/SKILL.md`
- Create: `msbaek-tdd/skills/explicit-parameters/SKILL.md`
- Create: `msbaek-tdd/skills/decompose-conditional/SKILL.md`
- Create: `msbaek-tdd/skills/naming-process/SKILL.md`
- Create: `msbaek-tdd/skills/encapsulate-collection/SKILL.md`

모든 tidy 계열 선택 스킬은 동일한 구조를 따른다:

```yaml
---
name: <skill-name>
description: <설명>. /<skill-name>으로 호출.
argument-hint: "[commit-ref]"
---
```

### 공통 워크플로우 (모든 tidy 계열 선택 스킬)

```
1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 해당 기법 적용 후보 식별 및 제시
3. 사용자 확인 (yes / no / 수정 요청)
4. 적용 → 테스트 실행
5. 테스트 통과 시 커밋 (refactor: 접두사)
6. 실패 시 되돌리기
```

### 공통 제약조건

```
- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가
- 하나의 refactor: 커밋으로 완료
```

- [ ] **Step 1: /replace-temp-with-query 스킬 생성**

파일 `msbaek-tdd/skills/replace-temp-with-query/SKILL.md`:

```markdown
---
name: replace-temp-with-query
description: 임시 변수를 메서드 호출로 치환하여 정보 재사용 및 중복 제거. /replace-temp-with-query로 호출.
argument-hint: "[commit-ref]"
---

# Replace Temp with Query

임시 변수(temp)가 여러 곳에서 반복 계산되거나, Extract Method를 방해할 때 메서드 호출로 치환한다.

## GOAL

- **성공 = 식별된 임시 변수가 메서드로 치환되고, 모든 테스트가 통과하며, refactor: 커밋 완료됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가

## 적용 패턴

```java
// Before: 임시 변수에 계산 결과 저장
double basePrice = quantity * itemPrice;
if (basePrice > 1000) {
    return basePrice * 0.95;
} else {
    return basePrice * 0.98;
}

// After: 메서드로 치환
if (basePrice() > 1000) {
    return basePrice() * 0.95;
} else {
    return basePrice() * 0.98;
}

private double basePrice() {
    return quantity * itemPrice;
}
```

## 적용 기준

- 임시 변수에 한 번만 대입되고 여러 곳에서 사용됨
- 변수 제거 후 메서드 추출이 가능해짐
- **주의**: 루프 내에서 누적되는 변수(accumulator)에는 적용하지 않음

## OUTPUT FORMAT

### 실행 절차

1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 파일 분석 → 치환 가능한 임시 변수 후보 식별
3. 후보 하나씩 제시 (현재 코드 → 제안 변경)
4. 사용자 확인 후 적용
5. 테스트 실행 → 통과 확인
6. 변경된 파일만 git add → `refactor: replace temp with query [변수명] in [클래스명]` 커밋

## FAILURE CONDITIONS

- ❌ 루프 내 누적 변수에 적용 (동작 변경)
- ❌ 부수효과가 있는 표현식을 메서드로 추출 (호출 횟수 변경으로 동작 변경)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 2: /explicit-parameters 스킬 생성**

파일 `msbaek-tdd/skills/explicit-parameters/SKILL.md`:

```markdown
---
name: explicit-parameters
description: 암묵적 의존성(전역변수, 클래스 필드)을 명시적 파라미터로 전환. /explicit-parameters로 호출.
argument-hint: "[commit-ref]"
---

# Explicit Parameters

메서드가 전역변수나 클래스 필드에 암묵적으로 의존할 때, 명시적 파라미터로 전환하여 테스트 용이성과 가독성을 향상시킨다.

## GOAL

- **성공 = 암묵적 의존성이 명시적 파라미터로 전환되고, 모든 테스트가 통과하며, refactor: 커밋 완료됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가

## 적용 패턴

```java
// Before: 필드에 암묵적 의존
class OrderProcessor {
    private DiscountPolicy discountPolicy;
    private TaxCalculator taxCalculator;

    double calculateTotal(Order order) {
        double subtotal = order.getSubtotal();
        double discount = discountPolicy.calculate(subtotal);  // 암묵적 의존
        double tax = taxCalculator.calculate(subtotal - discount);  // 암묵적 의존
        return subtotal - discount + tax;
    }
}

// After: 명시적 파라미터
double calculateTotal(Order order, DiscountPolicy discountPolicy, TaxCalculator taxCalculator) {
    double subtotal = order.getSubtotal();
    double discount = discountPolicy.calculate(subtotal);
    double tax = taxCalculator.calculate(subtotal - discount);
    return subtotal - discount + tax;
}
```

## 적용 기준

- 메서드가 필드에 의존하지만 필드가 변경 가능(mutable)이거나 테스트 시 주입이 어려움
- 메서드를 다른 클래스로 이동할 준비 단계
- **주의**: 파라미터가 3개 이상 되면 Introduce Parameter Object 적용 고려

## OUTPUT FORMAT

### 실행 절차

1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 파일 분석 → 암묵적 의존성 후보 식별
3. 후보 하나씩 제시 (현재 코드 → 제안 변경)
4. 사용자 확인 후 적용
5. 테스트 실행 → 통과 확인
6. 변경된 파일만 git add → `refactor: explicit parameters [메서드명] in [클래스명]` 커밋

## FAILURE CONDITIONS

- ❌ 모든 필드를 파라미터로 전환 (과도한 적용)
- ❌ 호출자 수정 없이 시그니처만 변경 (컴파일 에러)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 3: /decompose-conditional 스킬 생성**

파일 `msbaek-tdd/skills/decompose-conditional/SKILL.md`:

```markdown
---
name: decompose-conditional
description: 복잡한 if/then/else의 조건식과 분기를 의미 있는 이름의 메서드로 추출. /decompose-conditional로 호출.
argument-hint: "[commit-ref]"
---

# Decompose Conditional

복잡한 조건식 자체와 then/else 분기를 각각 의미 있는 이름의 메서드로 추출한다. Guard Clauses가 중첩을 해결한다면, Decompose Conditional은 조건 표현식 자체의 복잡성을 해결한다.

## GOAL

- **성공 = 복잡한 조건문이 의미 있는 이름의 메서드로 분해되고, 모든 테스트가 통과하며, refactor: 커밋 완료됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가

## 적용 패턴

```java
// Before: 조건식과 분기 모두 복잡
if (date.isBefore(SUMMER_START) || date.isAfter(SUMMER_END)) {
    charge = quantity * winterRate + winterServiceCharge;
} else {
    charge = quantity * summerRate;
}

// After: 조건/then/else 각각을 의미 있는 이름으로
if (isWinter(date)) {
    charge = winterCharge(quantity);
} else {
    charge = summerCharge(quantity);
}
```

## 적용 기준

- 조건식이 복합 논리 연산자(&&, ||)로 구성됨
- then/else 분기가 각각 3줄 이상의 로직을 포함
- Guard Clauses로 해결되지 않는 복잡성 (조건 자체가 복잡한 경우)
- **주의**: 이 기법은 Extract Method를 포함하므로, 메서드 추출이 단일 클래스 내에서 완결되는 경우에만 적용

## OUTPUT FORMAT

### 실행 절차

1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 파일 분석 → 복잡한 조건문 후보 식별
3. 후보 하나씩 제시 (현재 코드 → 제안 변경)
4. 사용자 확인 후 적용
5. 테스트 실행 → 통과 확인
6. 변경된 파일만 git add → `refactor: decompose conditional in [클래스명]` 커밋

## FAILURE CONDITIONS

- ❌ 단순한 조건문에 과도하게 적용 (over-engineering)
- ❌ 추출된 메서드가 다른 클래스에 속해야 하는데 현재 클래스에 남김 (→ system-wide 영역)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 4: /naming-process 스킬 생성**

파일 `msbaek-tdd/skills/naming-process/SKILL.md`:

```markdown
---
name: naming-process
description: Arlo Belshee의 6단계 네이밍 프로세스와 Clean Code 네이밍 규칙을 적용하여 점진적으로 이름을 개선. /naming-process로 호출.
argument-hint: "[commit-ref]"
---

# Naming as a Process

네이밍을 단일 단계가 아닌 점진적 프로세스로 접근. 코드의 이름을 체계적으로 개선하여 의도가 산문처럼 읽히도록 만든다.

## GOAL

- **성공 = 식별된 나쁜 이름이 개선되고, 모든 테스트가 통과하며, refactor: 커밋 완료됨**

## CONSTRAINTS

- 동작 변경 금지 — 이름 변경만 수행
- 테스트 수정 금지 — IDE의 Rename 리팩터링만 사용하여 안전하게 변경
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가

## 네이밍 프로세스 (Arlo Belshee)

### 6단계 점진적 개선

| 단계 | 이름 | 설명 | 예시 |
|------|------|------|------|
| 1 | Obvious Nonsense | 명백히 무의미한 이름으로 시작 | `Applesauce()` |
| 2 | Honest | 코드가 하는 일에 정직한 이름 | `probably_doSomethingEvil_AndStuff()` |
| 3 | Completely Honest | 모든 작업을 이름에 포함 | `parseXMLAndAddFlightToDBAndLocalCache()` |
| 4 | Does the Right Thing | SRP 기반 책임 분리 | `parseXML()`, `saveFlight()`, `showFlight()` |
| 5 | Intent Revealing | 왜 중요한지 드러내기 | `beginTrackingFlight(flight)` |
| 6 | Domain Abstraction | 도메인 개념 반영 | `FlightTracker.track(flight)` |

## 네이밍 규칙 체계

### The Scope Rule (Robert C. Martin)

| 대상 | 규칙 | 예시 |
|------|------|------|
| **변수** | scope 길수록 → 긴 이름 | 짧은: `i`, `tr` / 긴: `elapsedTimeInDays` |
| **함수** | scope 넓을수록 → 짧은 이름 | public: `serve()` / private: `closeEnclosingServiceInSeparateThread()` |
| **클래스** | scope 넓을수록 → 짧은 이름 | 기반: `Employee` / 파생: `PartTimeHourlyEmployee` |

### Parts of Speech — Well-Written Prose (Grady Booch)

| 요소 | 품사 | 좋은 예 | 나쁜 예 |
|------|------|---------|---------|
| 클래스 | 명사 | `Customer`, `WikiPage` | `Manager`, `Processor`, `Data` |
| 메소드 | 동사 | `postPayment()`, `deletePage()` | `payment()`, `page()` |
| boolean | 서술어 | `isEmpty`, `isPostable()` | `flag`, `check()` |

### System of Names (Clean Code 2nd Ed.)

개별 이름이 아닌 이름들의 **체계**가 도메인을 전달해야 한다. `gameBoard`, `cell`, `FLAGGED`, `flaggedCells`가 모여서 "상태를 가진 셀의 보드 게임"이라는 컨텍스트를 만든다.

### Naming Smells (탐지 기준)

| 징후 | 대응 |
|------|------|
| 라이프사이클 이벤트 이름 (`PreLoad`) | what/why를 드러내도록 변경 |
| 타입 이름 반복 (`nameString`) | 타입 정보 제거 |
| -er/-Utils 접미사 (`MemberManager`) | 책임 분리 후 도메인 이름 부여 |
| 중요 정보 생략 (`process()`, `handle()`) | 구체적 동작 명시 |
| 불용어 (`ProductInfo`, `ProductData`) | 의미 있는 구분 또는 제거 |

### 추가 실천 규칙

- 동일 개념에 한 단어만 사용 (Ubiquitous Language)
- 검색 가능한 이름 (매직 넘버 → 상수)
- 인코딩 금지 (HN, m_, I 접두사)
- Solution Domain Names (CS 용어) vs Problem Domain Names (비즈니스 용어)

## OUTPUT FORMAT

### 실행 절차

1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. Collapse All로 클래스 구조 파악
3. Naming Smells 탐지 → 나쁜 이름 후보 목록 작성
4. 후보 하나씩 제시 (현재 이름 → 개선 이유 → 제안 이름)
5. 사용자 확인 후 IDE Rename 수행
6. 테스트 실행 → 통과 확인
7. 변경된 파일만 git add → `refactor: rename [요약]` 커밋

## FAILURE CONDITIONS

- ❌ 이름 변경 외의 구조 변경 수행
- ❌ 한 번에 완벽한 이름을 강요 (점진적 개선 원칙 위반)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 5: /encapsulate-collection 스킬 생성**

파일 `msbaek-tdd/skills/encapsulate-collection/SKILL.md`:

```markdown
---
name: encapsulate-collection
description: 컬렉션 직접 노출을 방지하고 add/remove 메서드로 캡슐화. First Class Collection의 첫 단계. /encapsulate-collection으로 호출.
argument-hint: "[commit-ref]"
---

# Encapsulate Collection

컬렉션 getter가 내부 상태를 직접 노출하면, unmodifiable 반환 + add/remove 메서드로 캡슐화한다. First Class Collection으로 가는 첫 단계.

## GOAL

- **성공 = 컬렉션이 캡슐화되고, 모든 테스트가 통과하며, refactor: 커밋 완료됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 적용 금지
- git add -A 금지 — 변경된 파일만 명시적으로 추가

## 적용 패턴

```java
// Before: 컬렉션 직접 노출
class Course {
    private List<Student> students = new ArrayList<>();

    public List<Student> getStudents() {
        return students;  // 외부에서 직접 수정 가능
    }
}
// 호출부: course.getStudents().add(student);

// After: 캡슐화
class Course {
    private List<Student> students = new ArrayList<>();

    public List<Student> getStudents() {
        return Collections.unmodifiableList(students);
    }

    public void addStudent(Student student) {
        students.add(student);
    }

    public void removeStudent(Student student) {
        students.remove(student);
    }
}
```

## 관련 기법

- 이 기법 적용 후 컬렉션 관련 로직이 많아지면 → `/first-class-collection`으로 전용 클래스 추출

## OUTPUT FORMAT

### 실행 절차

1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 파일 분석 → 컬렉션 직접 노출 후보 식별
3. 후보 하나씩 제시 (현재 코드 → 제안 변경)
4. 사용자 확인 후 적용
5. 테스트 실행 → 통과 확인
6. 변경된 파일만 git add → `refactor: encapsulate collection in [클래스명]` 커밋

## FAILURE CONDITIONS

- ❌ 컬렉션을 사용하는 모든 호출부를 수정하지 않음 (컴파일 에러)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 6: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/skills/replace-temp-with-query/SKILL.md \
        msbaek-tdd/skills/explicit-parameters/SKILL.md \
        msbaek-tdd/skills/decompose-conditional/SKILL.md \
        msbaek-tdd/skills/naming-process/SKILL.md \
        msbaek-tdd/skills/encapsulate-collection/SKILL.md
git commit -m "feat: tidy 계열 선택 스킬 5개 생성"
```

---

## Task 6: 선택 스킬 생성 — system-wide 계열 7개

**Files:**
- Create: `msbaek-tdd/skills/extract-method-object/SKILL.md`
- Create: `msbaek-tdd/skills/replace-conditional-with-poly/SKILL.md`
- Create: `msbaek-tdd/skills/introduce-parameter-object/SKILL.md`
- Create: `msbaek-tdd/skills/discover-value-object/SKILL.md`
- Create: `msbaek-tdd/skills/first-class-collection/SKILL.md`
- Create: `msbaek-tdd/skills/lift-up-conditional/SKILL.md`
- Create: `msbaek-tdd/skills/separate-query-modifier/SKILL.md`

모든 system-wide 계열 선택 스킬은 system-wide-refactoring과 동일한 워크플로우를 따른다:

```
1. 대상 파일 수집 (git diff 기반 또는 사용자 지정)
2. 해당 기법 적용 후보 식별 및 제시 (현재 코드 → 제안 변경)
3. 사용자와 질의응답 (yes / no / 수정 요청)
4. 모든 후보 확인 후 최종 실행 목록 제시
5. refactor/<현재브랜치> 브랜치 생성
6. 기법별 커밋 (1파일 x 1기법 = 1커밋)
7. 각 커밋 후 테스트 통과 확인
8. 원래 브랜치로 PR 생성
9. 결과 보고
```

### 공통 제약조건

```
- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지 — 구조 변경이 테스트를 깨면 되돌리기
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋 (논리적으로 연결된 파일은 함께)
- git add -A 금지 — 변경된 파일만 명시적으로 추가
```

- [ ] **Step 1: /extract-method-object 스킬 생성**

파일 `msbaek-tdd/skills/extract-method-object/SKILL.md`:

```markdown
---
name: extract-method-object
description: 지역 변수가 얽힌 거대 메서드를 별도 클래스로 추출하여 분해. /extract-method-object로 호출.
argument-hint: "[commit-ref]"
---

# Extract Method Object

많은 지역 변수가 얽혀서 Extract Method가 어려운 거대 메서드를, 별도 클래스로 추출하여 분해한다.

## GOAL

- **성공 = 거대 메서드가 별도 클래스로 추출되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 많은 지역 변수가 얽힌 거대 메서드
public List<RefundDiff> refundDiff() {
    // 50+ lines with many local variables
    // Extract Method가 어려움 — 변수 의존성이 복잡
}

// After: Method Object로 추출
public List<RefundDiff> refundDiff() {
    return new RefundDifferenceCalculator(
        costsByTigerLogic,
        acmeCostsForClaimByAcmeLogic()
    ).invoke(orderItems);
}

// RefundDifferenceCalculator 클래스에서 작은 메서드로 분해
class RefundDifferenceCalculator {
    private final CostData costsByTiger;
    private final CostData acmeCosts;

    List<RefundDiff> invoke(List<OrderItem> items) {
        return items.stream()
            .map(this::createRefundDiff)
            .collect(toList());
    }

    private RefundDiff createRefundDiff(OrderItem item) {
        return new RefundDiff(
            getDeliveryFeeDiff(item),
            getServiceFeeDiff(item)
        );
    }
}
```

## 적용 단계

1. 메서드 전체를 별도 클래스로 이동
2. 지역 변수를 필드로 전환
3. 외부 의존성을 생성자 파라미터로 전환
4. 클래스 내에서 작은 메서드들로 분해
5. 원래 메서드는 새 클래스를 호출하도록 변경

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 지역 변수가 적은 메서드에 적용 (Extract Method로 충분한 경우)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 2: /replace-conditional-with-poly 스킬 생성**

파일 `msbaek-tdd/skills/replace-conditional-with-poly/SKILL.md`:

```markdown
---
name: replace-conditional-with-poly
description: 반복되는 switch/if-else를 서브클래스 다형성으로 치환. /replace-conditional-with-poly로 호출.
argument-hint: "[commit-ref]"
---

# Replace Conditional with Polymorphism

타입에 따라 다른 동작을 선택하는 조건문이 반복될 때, 서브클래스 다형성으로 치환한다.

## GOAL

- **성공 = 반복 조건문이 다형성으로 치환되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 반복되는 조건문
switch (play.type) {
    case "tragedy": return tragedyAmount();
    case "comedy": return comedyAmount();
}

// After: 다형성
abstract class PerformanceCalculator {
    abstract int amount();
    abstract int volumeCredits();
}

class TragedyCalculator extends PerformanceCalculator {
    int amount() { return tragedyAmount(); }
}

class ComedyCalculator extends PerformanceCalculator {
    int amount() { return comedyAmount(); }
}
```

## 리팩토링 경로

1. Replace Type Code with Subclasses
2. Replace Constructor with Factory Function
3. Replace Conditional with Polymorphism
4. Factory에만 switch 남기기

## 적용 기준

- 동일 switch/if-else가 2곳 이상 반복될 때 (Repeated Switches)
- 새 타입 추가 시 여러 곳을 수정해야 할 때 (OCP 위반)
- **주의**: 조건문이 1곳에만 있으면 과도한 적용일 수 있음

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 1곳에만 있는 단순 조건문에 적용
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 3: /introduce-parameter-object 스킬 생성**

파일 `msbaek-tdd/skills/introduce-parameter-object/SKILL.md`:

```markdown
---
name: introduce-parameter-object
description: 반복되는 파라미터 그룹을 객체로 치환. Value Object 발견의 시작점. /introduce-parameter-object로 호출.
argument-hint: "[commit-ref]"
---

# Introduce Parameter Object

함께 전달되는 파라미터 그룹을 하나의 객체로 치환한다. 종종 이 객체가 Value Object로 발전하고, 관련 로직이 이동한다.

## GOAL

- **성공 = 파라미터 그룹이 객체로 치환되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 파라미터 그룹이 반복
void processPrice(int originalPrice, int discountedPrice, String currency) { ... }
void formatPrice(int originalPrice, int discountedPrice, String currency) { ... }
void validatePrice(int originalPrice, int discountedPrice, String currency) { ... }

// After: Parameter Object로 치환
record Price(int original, int discounted, String currency) {
    boolean isDiscounted() {
        return discounted > 0 && discounted < original;
    }
}

void processPrice(Price price) { ... }
void formatPrice(Price price) { ... }
void validatePrice(Price price) { ... }
```

## 적용 기준

- 3개 이상의 파라미터가 함께 전달되는 패턴이 2회 이상 반복
- 파라미터 간에 논리적 관계가 있음 (예: start/end, x/y, amount/currency)

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 논리적 관계가 없는 파라미터를 억지로 묶음
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 4: /discover-value-object 스킬 생성**

파일 `msbaek-tdd/skills/discover-value-object/SKILL.md`:

```markdown
---
name: discover-value-object
description: Primitive Obsession을 제거하여 Value Object를 발견. Entity 필드, 반복 파라미터, 기능이 많은 primitive에서 추출. /discover-value-object로 호출.
argument-hint: "[commit-ref]"
---

# Discover Value Object

Primitive Obsession(기본형 집착)을 제거하여 숨겨진 Value Object를 발견하고 추출한다.

## GOAL

- **성공 = Primitive가 Value Object로 치환되고, 관련 로직이 이동되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## Value Object 발견 후보

1. **Entity의 필드들**: `String email`, `int price` → `Email`, `Money`
2. **메서드 인자로 함께 전달되는 데이터**: `(int amount, String currency)` → `Money`
3. **특정 primitive에 많은 기능이 있는 경우**: `String`에 대한 validation, formatting이 산재

## 적용 패턴

```java
// Before: Primitive Obsession
class Order {
    private int amount;
    private String currency;

    boolean isExpensive() { return amount > 10000; }
    String formattedPrice() { return currency + " " + amount; }
}

// After: Value Object 추출
record Money(int amount, String currency) {
    boolean isOver(int threshold) { return amount > threshold; }
    String formatted() { return currency + " " + amount; }
}

class Order {
    private Money price;

    boolean isExpensive() { return price.isOver(10000); }
    String formattedPrice() { return price.formatted(); }
}
```

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 모든 primitive를 무조건 객체로 감쌈 (관련 로직이 없으면 과도한 적용)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 5: /first-class-collection 스킬 생성**

파일 `msbaek-tdd/skills/first-class-collection/SKILL.md`:

```markdown
---
name: first-class-collection
description: 컬렉션을 감싸는 전용 클래스를 생성하고 컬렉션 관련 로직을 이동. /first-class-collection으로 호출.
argument-hint: "[commit-ref]"
---

# First Class Collection

컬렉션과 관련 로직이 여러 클래스에 산재할 때, 컬렉션을 감싸는 전용 클래스를 생성하고 관련 로직을 이동한다.

## GOAL

- **성공 = 컬렉션이 전용 클래스로 추출되고, 관련 로직이 이동되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 컬렉션 + 로직이 서비스에 산재
class OrderService {
    List<Order> orders;

    double totalAmount() {
        return orders.stream().mapToDouble(Order::getAmount).sum();
    }

    List<Order> expensiveOrders() {
        return orders.stream().filter(o -> o.getAmount() > 10000).toList();
    }
}

// After: First Class Collection
class Orders {
    private final List<Order> items;

    Orders(List<Order> items) { this.items = List.copyOf(items); }

    double totalAmount() {
        return items.stream().mapToDouble(Order::getAmount).sum();
    }

    Orders expensive() {
        return new Orders(items.stream().filter(o -> o.getAmount() > 10000).toList());
    }
}
```

## 관련 기법

- `/encapsulate-collection` → 이 기법의 전 단계 (getter 캡슐화)
- `/discover-value-object` → 컬렉션 내 요소가 Value Object 후보일 수 있음

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 컬렉션 관련 로직이 1~2개뿐인데 적용 (과도한 추상화)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 6: /lift-up-conditional 스킬 생성**

파일 `msbaek-tdd/skills/lift-up-conditional/SKILL.md`:

```markdown
---
name: lift-up-conditional
description: 여러 곳에 중복된 조건문을 상위로 끌어올려 중복 제거. /lift-up-conditional로 호출.
argument-hint: "[commit-ref]"
---

# Lift Up Conditional

동일 조건문이 여러 메서드에 중복될 때, 조건문을 상위로 끌어올려 중복을 제거한다.

## GOAL

- **성공 = 중복 조건문이 상위로 통합되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 동일 조건이 여러 메서드에 중복
double calculatePrice(Product product) {
    if (product.isOnSale()) {
        return product.getPrice() * 0.9;
    }
    return product.getPrice();
}

String formatLabel(Product product) {
    if (product.isOnSale()) {
        return "SALE: " + product.getName();
    }
    return product.getName();
}

// After: 조건을 상위로 끌어올림
void processProduct(Product product) {
    if (product.isOnSale()) {
        double price = product.getPrice() * 0.9;
        String label = "SALE: " + product.getName();
        display(price, label);
    } else {
        double price = product.getPrice();
        String label = product.getName();
        display(price, label);
    }
}
```

## 리팩토링 단계

1. 중복 조건을 변수로 추출
2. 해당 조건을 메서드로 추출
3. surround with if-else
4. 각 분기 내에서 불필요해진 조건문 inline

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 논리적으로 다른 조건을 동일하다고 판단
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 7: /separate-query-modifier 스킬 생성**

파일 `msbaek-tdd/skills/separate-query-modifier/SKILL.md`:

```markdown
---
name: separate-query-modifier
description: 값 반환과 부수효과가 혼재된 메서드를 query(값 반환)와 modifier(부수효과)로 분리. CQS 원칙. /separate-query-modifier로 호출.
argument-hint: "[commit-ref]"
---

# Separate Query from Modifier (CQS)

값을 반환하면서 동시에 부수효과를 일으키는 메서드를 query(값 반환, 순수)와 modifier(부수효과, void)로 분리한다.

## GOAL

- **성공 = query/modifier가 분리되고, 모든 테스트가 통과하며, 별도 브랜치에서 PR이 생성됨**

## CONSTRAINTS

- 동작 변경 금지 — 구조 개선만 수행
- 테스트 수정 금지
- 사용자 확인 없이 리팩토링 금지
- 커밋 단위: 1파일 x 1기법 = 1커밋
- git add -A 금지

## 적용 패턴

```java
// Before: 값 반환 + 부수효과 혼재
double getTotalAndApplyDiscount(Order order) {
    double total = order.calculateTotal();
    if (total > 1000) {
        order.setDiscount(0.1);  // 부수효과
    }
    return total;  // 값 반환
}

// After: CQS 분리
// Query: 값 반환, 부수효과 없음
double getTotal(Order order) {
    return order.calculateTotal();
}

// Modifier: 부수효과, void 반환
void applyDiscountIfEligible(Order order) {
    if (order.calculateTotal() > 1000) {
        order.setDiscount(0.1);
    }
}
```

## 적용 기준

- 메서드가 값을 반환하면서 동시에 상태를 변경
- 호출자가 반환값과 부수효과를 동시에 기대
- **주의**: 원자적 연산(예: CAS, pop)은 CQS를 적용하면 thread-safety 문제 발생 가능

## OUTPUT FORMAT

system-wide-refactoring과 동일한 워크플로우 (브랜치 생성 → 기법별 커밋 → PR).

## FAILURE CONDITIONS

- ❌ 원자적 연산에 적용 (thread-safety 파괴)
- ❌ 호출자 수정을 누락 (분리 후 호출부도 업데이트 필요)
- ❌ 사용자 확인 없이 적용
```

- [ ] **Step 8: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/skills/extract-method-object/SKILL.md \
        msbaek-tdd/skills/replace-conditional-with-poly/SKILL.md \
        msbaek-tdd/skills/introduce-parameter-object/SKILL.md \
        msbaek-tdd/skills/discover-value-object/SKILL.md \
        msbaek-tdd/skills/first-class-collection/SKILL.md \
        msbaek-tdd/skills/lift-up-conditional/SKILL.md \
        msbaek-tdd/skills/separate-query-modifier/SKILL.md
git commit -m "feat: system-wide 계열 선택 스킬 7개 생성"
```

---

## Task 7: plugin.json 업데이트

**Files:**
- Modify: `msbaek-tdd/.claude-plugin/plugin.json`

- [ ] **Step 1: 버전 범프 및 설명 업데이트**

```json
{
  "name": "msbaek-tdd",
  "version": "1.5.0",
  "description": "Java + Spring Boot TDD workflow plugin with RGB cycle, local tidying, system-wide refactoring, and 12 optional refactoring skills",
  "author": {
    "name": "msbaek"
  },
  "keywords": ["tdd", "java", "spring-boot", "red-green-blue", "tidying", "refactoring", "split-phase", "value-object", "naming"]
}
```

- [ ] **Step 2: 커밋**

```bash
cd /Users/msbaek/.claude/plugins/marketplaces/msbaek-claude-plugins
git add msbaek-tdd/.claude-plugin/plugin.json
git commit -m "chore: plugin.json 버전 1.5.0으로 범프 및 설명 업데이트"
```

---

## 요약

| Task | 설명 | 파일 수 |
|------|------|---------|
| 1 | tdd-blue에 Normalize Symmetries 추가 | 1 modify |
| 2 | tdd-blue에 Split Loop 추가 | 1 modify |
| 3 | tdd-tidy SKILL.md 업데이트 | 1 modify |
| 4 | system-wide SKILL.md에 SoC 추가 | 1 modify |
| 5 | tidy 계열 선택 스킬 5개 생성 | 5 create |
| 6 | system-wide 계열 선택 스킬 7개 생성 | 7 create |
| 7 | plugin.json 업데이트 | 1 modify |
| **합계** | | **4 modify, 12 create** |
