# Refactoring Catalog Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** refactoring.com/catalog/ 기반으로 신규 스킬 4개 생성 + 기존 스킬 2개 보완 + 추천 연결 업데이트

**Architecture:** 각 신규 스킬은 `msbaek-tdd/skills/<name>/SKILL.md`에 기존 패턴(decompose-conditional 또는 introduce-parameter-object)을 따라 생성. 기존 스킬은 섹션 추가/수정으로 보완. 모든 작업은 독립적이며 병렬 실행 가능.

**Tech Stack:** Markdown (SKILL.md frontmatter + body), Git

**Spec:** `docs/superpowers/specs/2026-04-05-refactoring-catalog-enhancement-design.md`

---

## File Structure

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `msbaek-tdd/skills/consolidate-conditional/SKILL.md` | 동일 결과 조건문 통합 스킬 |
| Create | `msbaek-tdd/skills/introduce-assertion/SKILL.md` | 암묵적 가정 assertion 명시 스킬 |
| Create | `msbaek-tdd/skills/introduce-special-case/SKILL.md` | Null Object 패턴 스킬 |
| Create | `msbaek-tdd/skills/replace-loop-with-pipeline/SKILL.md` | 루프→Stream 변환 스킬 |
| Modify | `msbaek-tdd/skills/introduce-parameter-object/SKILL.md` | Preserve Whole Object 통합 |
| Modify | `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` | Hide Delegate 추가 + 신규 스킬 추천 |
| Modify | `msbaek-tdd/skills/tdd-tidy/SKILL.md` | 신규 스킬 추천 추가 |
| Modify | `msbaek-tdd/.claude-plugin/plugin.json` | description 업데이트 |

---

### Task 1: Consolidate Conditional Expression 스킬 생성

**Files:**
- Create: `msbaek-tdd/skills/consolidate-conditional/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p msbaek-tdd/skills/consolidate-conditional
```

- [ ] **Step 2: SKILL.md 작성**

Create: `msbaek-tdd/skills/consolidate-conditional/SKILL.md`

```markdown
---
name: consolidate-conditional
description: 동일한 결과를 내는 여러 조건문을 하나로 통합하고 의미 있는 메서드로 추출. /consolidate-conditional로 호출.
argument-hint: "[commit-ref]"
---

# Consolidate Conditional Expression

## GOAL

동일한 결과를 내는 여러 조건문을 하나로 통합하여:
- 흩어진 조건들의 관계를 명확히 표현
- 통합된 조건을 의미 있는 메서드로 추출
- 코드 의도 파악 용이

decompose-conditional과 상호 보완:
- **Consolidate**: 흩어진 조건을 **모으는** 방향 (여러 if → 하나의 if)
- **Decompose**: 복잡한 조건을 **쪼개는** 방향 (하나의 복잡한 if → 여러 메서드)
- 실전: Consolidate → Decompose 순서로 적용하는 경우가 많음

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료
- **Extract Method 포함**: 단일 클래스 내 완결 시에만 적용

## 적용 패턴

### Before: OR 패턴 — 동일 결과를 내는 조건들이 분산
```java
if (employee.getSeniority() < 2) return 0;
if (employee.getMonthsDisabled() > 12) return 0;
if (employee.isPartTime()) return 0;
```

### After: 조건 통합 + 메서드 추출
```java
if (isNotEligibleForDisability(employee)) return 0;

private boolean isNotEligibleForDisability(Employee employee) {
    return employee.getSeniority() < 2
        || employee.getMonthsDisabled() > 12
        || employee.isPartTime();
}
```

### 추가 예시: AND 패턴 — 중첩 조건 통합
```java
// Before
if (employee.onVacation()) {
    if (employee.getSeniority() > 10) {
        return 1;
    }
}

// After
if (employee.onVacation() && employee.getSeniority() > 10) {
    return 1;
}
```

### 추가 예시: 삼항 연산자 통합
```java
// Before
if (isSpecialDeal()) {
    total = price * 0.95;
} else {
    total = price * 0.98;
}
if (isLoyalCustomer()) {
    total = price * 0.95;
}

// After (동일 결과를 내는 조건 통합)
if (isSpecialDeal() || isLoyalCustomer()) {
    total = price * 0.95;
} else {
    total = price * 0.98;
}
```

## 적용 기준

### ✅ 적용 대상
- 2개 이상의 조건문이 동일한 결과(return/throw/assign)를 냄
- 조건들이 논리적으로 OR 또는 AND로 결합 가능
- 각 조건이 독립적 (부수효과 없음)
- 통합 후 의미 있는 이름을 부여할 수 있음

### ❌ 적용 제외
- **다른 결과**: 조건들이 서로 다른 결과를 냄
- **부수효과 사이**: 조건 사이에 부수효과 코드가 있음
- **의도적 분리**: 각 조건이 서로 다른 비즈니스 규칙을 표현 (분리가 의도적)
- **단일 조건**: 통합할 조건이 1개뿐

## OUTPUT FORMAT

### 실행 절차

1. **대상 파일 수집**
   ```bash
   # commit-ref 제공 시
   git diff <commit-ref> --name-only '*.java'
   
   # 미제공 시 현재 변경사항
   git diff --name-only '*.java'
   ```

2. **후보 식별 및 제시**
   - 동일 결과(return/throw/assign)를 내는 연속 조건문 탐지
   - 동일 결과를 내는 중첩 조건문 탐지 (AND 패턴)
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - Before/After 코드 미리보기
     - 통합 유형 (OR / AND)

3. **사용자 확인**
   ```
   발견된 후보 2개:
   
   1. DisabilityService.java:15-17
      OR 패턴: 3개 조건 → 동일 return 0
      → isNotEligibleForDisability() 메서드 추출
   
   2. VacationPolicy.java:30-34
      AND 패턴: 중첩 if 2단계
      → 단일 조건으로 플래트닝
   
   적용하시겠습니까? (yes / no / 수정)
   ```

4. **리팩토링 적용**
   - 조건문을 OR 또는 AND로 통합
   - 통합된 조건을 boolean 반환 메서드로 추출
   - (선택) 통합 후 복잡하면 decompose-conditional 제안

5. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

6. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: consolidate conditional in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Consolidate Conditional Expression 완료

변경 내용:
- DisabilityService.java:15-17
  OR 통합: 3개 조건 → isNotEligibleForDisability() 메서드 추출

- VacationPolicy.java:30-34
  AND 통합: 중첩 if → 단일 조건으로 플래트닝

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: consolidate conditional in DisabilityService, VacationPolicy

💡 제안: DisabilityService.java의 통합된 조건이 복잡합니다.
   /decompose-conditional 적용을 고려해보세요.
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (리팩토링 후)
- [ ] 다른 결과를 내는 조건들을 억지로 통합함
- [ ] 부수효과가 있는 조건 사이의 코드를 무시함
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
```

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/skills/consolidate-conditional/SKILL.md
git commit -m "feat: consolidate-conditional 스킬 생성"
```

---

### Task 2: Introduce Assertion 스킬 생성

**Files:**
- Create: `msbaek-tdd/skills/introduce-assertion/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p msbaek-tdd/skills/introduce-assertion
```

- [ ] **Step 2: SKILL.md 작성**

Create: `msbaek-tdd/skills/introduce-assertion/SKILL.md`

```markdown
---
name: introduce-assertion
description: 암묵적 가정을 Assert/Validate로 명시하여 가정 위반 시 즉시 발견. /introduce-assertion으로 호출.
argument-hint: "[commit-ref]"
---

# Introduce Assertion

## GOAL

코드가 암묵적으로 가정하는 조건을 assertion으로 명시하여:
- 가정 위반 시 즉시 발견 (원인과 증상의 거리 단축)
- 주석보다 강력한 실행 가능한 문서
- 계약 기반 프로그래밍의 경량 버전

## CONSTRAINTS

- **동작 변경 금지**: assertion 추가만 수행 (기존 로직 변경 없음)
- **테스트 수정 금지**: assertion 추가가 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

### Assertion 도구 선택 (프로젝트 의존성 자동 감지)

프로젝트의 빌드 파일(build.gradle 또는 pom.xml)을 확인하여 자동 선택:

1. **Spring 의존성 있음** → `org.springframework.util.Assert`
2. **Apache Commons 있음** → `org.apache.commons.lang3.Validate`
3. **둘 다 없음** → `java.util.Objects.requireNonNull` + `IllegalArgumentException`

> Java `assert` 키워드는 `-ea` 플래그가 필요하여 프로덕션에서 비활성화될 수 있으므로 사용하지 않음

## 적용 패턴

### Before: 암묵적 가정 (Spring Assert)
```java
public double calculateDiscount(double price, double rate) {
    // price는 양수, rate는 0~1 사이여야 함 (주석 또는 아무것도 없음)
    return price * rate;
}
```

### After: assertion으로 가정 명시
```java
import org.springframework.util.Assert;

public double calculateDiscount(double price, double rate) {
    Assert.isTrue(price > 0, "price must be positive: " + price);
    Assert.isTrue(rate >= 0 && rate <= 1, "rate must be between 0 and 1: " + rate);
    return price * rate;
}
```

### 추가 예시: Apache Commons Validate
```java
import org.apache.commons.lang3.Validate;

public String formatName(Customer customer) {
    Validate.notNull(customer, "customer must not be null");
    Validate.notBlank(customer.getFirstName(), "firstName must not be blank");
    return customer.getFirstName() + " " + customer.getLastName();
}
```

### 추가 예시: 사후 조건 (결과 검증)
```java
public int allocateSlots(int requested, int available) {
    int allocated = Math.min(requested, available);
    Assert.isTrue(allocated >= 0, "allocated slots must not be negative: " + allocated);
    Assert.isTrue(allocated <= available, "allocated exceeds available: " + allocated + " > " + available);
    return allocated;
}
```

## 적용 기준

### ✅ 적용 대상
- 메서드가 특정 조건을 가정하지만 명시하지 않은 경우
- 내부 메서드(private/package-private)의 전제 조건
- 계산 결과의 사후 조건 (결과값 범위 검증)
- 알고리즘의 불변식 (invariant)
- null이 아닌 것을 암묵적으로 가정하는 경우

### ❌ 적용 제외
- **public API의 입력 검증**: assertion이 아니라 명시적 예외(IllegalArgumentException 등)를 사용해야 함
- **비즈니스 규칙 검증**: 도메인 로직으로 처리해야 할 것
- **이미 Guard Clause나 예외로 처리된 조건**: 중복
- **외부 입력(사용자, API 응답)**: 시스템 경계는 명시적 검증 필요

### ⚠️ 주의사항
- assertion 실패 = 프로그래머의 버그 (예상치 못한 상황)
- 예외(Exception) = 예상 가능한 오류 상황 (사용자 입력 오류 등)
- 이 구분이 모호하면 사용자에게 질문

## OUTPUT FORMAT

### 실행 절차

1. **프로젝트 의존성 확인**
   ```bash
   # Gradle 프로젝트
   grep -l "spring" build.gradle 2>/dev/null || grep -l "commons-lang3" build.gradle 2>/dev/null
   
   # Maven 프로젝트
   grep -l "spring" pom.xml 2>/dev/null || grep -l "commons-lang3" pom.xml 2>/dev/null
   ```
   결과에 따라 assertion 도구를 선택하고 사용자에게 안내:
   ```
   프로젝트에서 Spring 의존성이 감지되었습니다.
   org.springframework.util.Assert를 사용합니다.
   ```

2. **대상 파일 수집**
   ```bash
   # commit-ref 제공 시
   git diff <commit-ref> --name-only '*.java'
   
   # 미제공 시 현재 변경사항
   git diff --name-only '*.java'
   ```

3. **후보 식별 및 제시**
   - 암묵적 가정 패턴 탐지:
     - null 참조 없이 메서드 호출하는 경우
     - 범위 가정 (양수, 0~1, 비어있지 않음 등)
     - 상태 가정 (초기화 완료, 특정 상태 등)
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - 가정 내용 설명
     - 추가할 assertion 코드

4. **사용자 확인**
   ```
   발견된 후보 3개 (Spring Assert 사용):
   
   1. PricingService.java:20
      가정: price > 0, rate는 0~1
      → Assert.isTrue(price > 0, ...)
      → Assert.isTrue(rate >= 0 && rate <= 1, ...)
   
   2. OrderProcessor.java:45
      가정: order != null, order.getItems() 비어있지 않음
      → Assert.notNull(order, ...)
      → Assert.notEmpty(order.getItems(), ...)
   
   적용하시겠습니까? (yes / no / 수정)
   ```

5. **리팩토링 적용**
   - import 문 추가
   - 메서드 시작 부분에 assertion 추가
   - (사후 조건인 경우) return 직전에 assertion 추가

6. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

7. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: introduce assertions in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Introduce Assertion 완료 (Spring Assert)

변경 내용:
- PricingService.java:20
  전제 조건: Assert.isTrue(price > 0), Assert.isTrue(rate >= 0 && rate <= 1)

- OrderProcessor.java:45
  전제 조건: Assert.notNull(order), Assert.notEmpty(order.getItems())

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: introduce assertions in PricingService, OrderProcessor
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (assertion 추가 후)
- [ ] public API의 입력 검증에 assertion을 사용함 (예외를 써야 함)
- [ ] Java `assert` 키워드를 사용함 (프로덕션 비활성화 위험)
- [ ] 이미 Guard Clause로 보호된 조건에 중복 assertion 추가
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
```

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/skills/introduce-assertion/SKILL.md
git commit -m "feat: introduce-assertion 스킬 생성"
```

---

### Task 3: Introduce Special Case (Null Object) 스킬 생성

**Files:**
- Create: `msbaek-tdd/skills/introduce-special-case/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p msbaek-tdd/skills/introduce-special-case
```

- [ ] **Step 2: SKILL.md 작성**

Create: `msbaek-tdd/skills/introduce-special-case/SKILL.md`

```markdown
---
name: introduce-special-case
description: 반복되는 null 검사를 Special Case(Null Object) 클래스로 대체하여 다형성으로 처리. /introduce-special-case로 호출.
argument-hint: "[commit-ref]"
---

# Introduce Special Case (Null Object)

## GOAL

- **성공 = 반복 null 검사가 Special Case 클래스로 대체되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 동일 타입에 대한 null 검사가 3곳 이상 반복됨
- null일 때의 기본 동작이 Special Case 클래스에 캡슐화됨
- 호출처의 null 검사가 제거됨
- 모든 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 단계별 커밋 (Special Case 생성 → 소스 수정 → 호출처 정리)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

## 적용 패턴

### Before: null 검사가 여러 곳에 산재
```java
public String getCustomerName(Site site) {
    Customer customer = site.getCustomer();
    if (customer == null) {
        return "occupant";
    }
    return customer.getName();
}

public BillingPlan getBillingPlan(Site site) {
    Customer customer = site.getCustomer();
    if (customer == null) {
        return BillingPlan.basic();
    }
    return customer.getBillingPlan();
}

public int getWeeksDelinquent(Site site) {
    Customer customer = site.getCustomer();
    if (customer == null) {
        return 0;
    }
    return customer.getPaymentHistory().getWeeksDelinquent();
}
```

### After: Special Case 객체 도입
```java
// Step 1: Special Case 클래스 생성
public class UnknownCustomer extends Customer {
    @Override
    public String getName() { return "occupant"; }

    @Override
    public BillingPlan getBillingPlan() { return BillingPlan.basic(); }

    @Override
    public PaymentHistory getPaymentHistory() {
        return PaymentHistory.empty();
    }

    @Override
    public boolean isUnknown() { return true; }
}

// Step 2: 소스에서 null 대신 Special Case 반환
public class Site {
    public Customer getCustomer() {
        return (customer == null) ? new UnknownCustomer() : customer;
    }
}

// Step 3: 호출처 — null 검사 제거
public String getCustomerName(Site site) {
    return site.getCustomer().getName();
}

public BillingPlan getBillingPlan(Site site) {
    return site.getCustomer().getBillingPlan();
}

public int getWeeksDelinquent(Site site) {
    return site.getCustomer().getPaymentHistory().getWeeksDelinquent();
}
```

### 추가 예시: 인터페이스 기반
```java
// 대상이 인터페이스인 경우
public interface PaymentMethod {
    String charge(int amount);
    String getDescription();
}

public class NullPaymentMethod implements PaymentMethod {
    @Override
    public String charge(int amount) { return "no-op"; }

    @Override
    public String getDescription() { return "No payment method on file"; }
}
```

## 적용 기준

### ✅ 적용 대상
- 동일 타입에 대한 null 검사가 **3곳 이상** 반복
- null일 때의 기본값/기본 동작이 **일관됨**
- 대상 타입이 **상속 또는 인터페이스 구현 가능** (final 아님)
- null 처리 로직이 흩어져 있어 일관성 유지가 어려운 경우

### ❌ 적용 제외
- **null 검사 1-2곳**: 과도한 추상화
- **동작이 호출처마다 다름**: 일관된 기본 동작이 없으면 Special Case 불가
- **외부 라이브러리 클래스**: 상속 불가
- **Optional로 충분**: Optional로 이미 처리되거나 Optional이 더 적합한 경우
- **final 클래스**: 상속 불가능

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

#### 2. null 검사 반복 패턴 탐지

대상 파일에서 다음 패턴을 찾는다:

- 동일 타입에 대한 `== null` 또는 `!= null` 검사가 3곳 이상
- null일 때 반환하는 기본값이 일관됨
- 대상 타입이 상속/구현 가능

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Introduce Special Case

**대상 타입**: Customer
**null 검사 위치** (4곳):
1. OrderService.java:30 → null이면 "occupant" 반환
2. BillingService.java:45 → null이면 BillingPlan.basic() 반환
3. ReportService.java:20 → null이면 0 반환
4. NotificationService.java:55 → null이면 스킵

**기본 동작 일관성**: ✅ (1-3은 일관된 기본값, 4는 스킵)

**제안**:
1. UnknownCustomer extends Customer 생성
2. Site.getCustomer()에서 null 대신 UnknownCustomer 반환
3. 호출처 4곳의 null 검사 제거

**적용할까요?** (yes / no / 수정 요청)
```

#### 4. 브랜치 생성

```bash
CURRENT_BRANCH=$(git branch --show-current)
git checkout -b "refactor/${CURRENT_BRANCH}"
```

#### 5. 단계별 커밋 실행

**커밋 1: Special Case 클래스 생성**
1. Special Case 클래스 작성 (상속 또는 인터페이스 구현)
2. 기본값을 반환하는 메서드 오버라이드
3. isUnknown() 메서드 추가
4. 테스트 실행
5. 커밋: `refactor: introduce special case <클래스명>`

**커밋 2: 소스에서 null 대신 Special Case 반환**
1. null을 반환하던 곳에서 Special Case 인스턴스 반환
2. 테스트 실행
3. 커밋: `refactor: return <Special Case> instead of null in <소스클래스>`

**커밋 3: 호출처 null 검사 제거**
1. null 검사 코드 제거
2. 직접 메서드 호출로 대체
3. 테스트 실행
4. 커밋: `refactor: remove null checks for <타입> in callers`

한글 커밋 메시지가 필요한 경우 Write tool로 임시 파일 생성 후 `git commit -F <파일>` 사용.

테스트 실패 시:
- 해당 리팩토링 변경사항 되돌리기 (`git checkout -- [파일]`)
- 사용자에게 실패 사유 안내
- 다음 단계로 진행 또는 중단

#### 6. PR 생성

```bash
gh pr create \
  --base "${CURRENT_BRANCH}" \
  --title "refactor: introduce special case for <대상 타입>" \
  --body "$(cat <<'EOF'
## Summary
- Introduce Special Case 적용: <Special Case 클래스명>
- null 검사 <N>곳 제거

## Changes
- Special Case 클래스 생성 (기본값 캡슐화)
- 소스에서 null 대신 Special Case 반환
- 호출처 null 검사 제거

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
- 생성된 Special Case 클래스
- 제거된 null 검사 위치
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ null일 때 동작이 호출처마다 다른데 억지로 통합
- ❌ null 검사가 1-2곳뿐인데 적용 (과도한 추상화)
- ❌ final 클래스에 적용 시도
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
```

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/skills/introduce-special-case/SKILL.md
git commit -m "feat: introduce-special-case 스킬 생성"
```

---

### Task 4: Replace Loop with Pipeline 스킬 생성

**Files:**
- Create: `msbaek-tdd/skills/replace-loop-with-pipeline/SKILL.md`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p msbaek-tdd/skills/replace-loop-with-pipeline
```

- [ ] **Step 2: SKILL.md 작성**

Create: `msbaek-tdd/skills/replace-loop-with-pipeline/SKILL.md`

```markdown
---
name: replace-loop-with-pipeline
description: 명령형 루프를 Stream API/Collection Pipeline으로 변환하여 데이터 흐름 의도 명확화. /replace-loop-with-pipeline로 호출.
argument-hint: "[commit-ref]"
---

# Replace Loop with Pipeline

## GOAL

명령형 루프를 Stream API/Collection Pipeline으로 변환하여:
- **what** vs **how**: Pipeline은 "무엇을" 하는지, 루프는 "어떻게" 하는지 표현
- 필터링/변환/집계의 의도가 메서드 체인으로 드러남
- 중간 변수/플래그 변수 제거

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

## 적용 패턴

### 패턴 1: 필터링 + 변환
```java
// Before
List<String> result = new ArrayList<>();
for (Order order : orders) {
    if (order.isActive()) {
        result.add(order.getCustomerName());
    }
}

// After
List<String> result = orders.stream()
    .filter(Order::isActive)
    .map(Order::getCustomerName)
    .toList();
```

### 패턴 2: 집계
```java
// Before
int total = 0;
for (LineItem item : items) {
    if (item.getQuantity() > 0) {
        total += item.getPrice() * item.getQuantity();
    }
}

// After
int total = items.stream()
    .filter(item -> item.getQuantity() > 0)
    .mapToInt(item -> item.getPrice() * item.getQuantity())
    .sum();
```

### 패턴 3: 검색 (첫 번째 매칭)
```java
// Before
Employee found = null;
for (Employee e : employees) {
    if (e.getDepartment().equals("Engineering")) {
        found = e;
        break;
    }
}

// After
Optional<Employee> found = employees.stream()
    .filter(e -> e.getDepartment().equals("Engineering"))
    .findFirst();
```

### 패턴 4: 존재 여부 확인
```java
// Before
boolean hasOverdue = false;
for (Invoice invoice : invoices) {
    if (invoice.isOverdue()) {
        hasOverdue = true;
        break;
    }
}

// After
boolean hasOverdue = invoices.stream()
    .anyMatch(Invoice::isOverdue);
```

### 패턴 5: 그룹핑
```java
// Before
Map<String, List<Employee>> byDept = new HashMap<>();
for (Employee e : employees) {
    byDept.computeIfAbsent(e.getDepartment(), k -> new ArrayList<>()).add(e);
}

// After
Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));
```

## 적용 기준

### ✅ 적용 대상
- 컬렉션 순회 + 필터링/변환/집계/검색 패턴
- 중간 변수(`result`, `total`, `found`)에 결과를 누적하는 루프
- 플래그 변수(`boolean found = false`)로 제어하는 루프
- 중첩 루프에서 내부 루프가 독립적 검색/필터인 경우
- `computeIfAbsent` + `add` 패턴의 그룹핑 루프

### ❌ 적용 제외
- **부수효과가 핵심인 루프**: DB 저장, 로깅 등 각 요소마다 side effect 수행 (forEach로만 바꾸는 것은 가치 없음)
- **인덱스 기반 접근 필수**: `list.get(i-1)` 비교, 인접 요소 참조 등
- **break/continue 조건이 복잡**: Stream으로 변환하면 오히려 난해
- **성능 크리티컬 루프**: primitive 배열 대량 처리 등 Stream 오버헤드가 문제
- **Java 8 미만 프로젝트**: Stream API 사용 불가
- **단순 forEach 전환**: `for → stream().forEach()`는 가독성 이점 없음

## OUTPUT FORMAT

### 실행 절차

1. **대상 파일 수집**
   ```bash
   # commit-ref 제공 시
   git diff <commit-ref> --name-only '*.java'
   
   # 미제공 시 현재 변경사항
   git diff --name-only '*.java'
   ```

2. **후보 식별 및 제시**
   - 루프 패턴 탐지:
     - `new ArrayList<>()` + for + `add()` → filter/map + toList
     - `int/long sum = 0` + for + `+=` → mapToInt + sum
     - `T found = null` + for + break → filter + findFirst
     - `boolean flag = false` + for + break → anyMatch/noneMatch
     - `computeIfAbsent` + for → groupingBy
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - 변환 유형 (필터링/집계/검색/존재확인/그룹핑)
     - Before/After 코드 미리보기

3. **사용자 확인**
   ```
   발견된 후보 3개:
   
   1. OrderService.java:30-36
      유형: 필터링 + 변환
      → orders.stream().filter(...).map(...).toList()
   
   2. ReportService.java:50-55
      유형: 집계 (합계)
      → items.stream().mapToInt(...).sum()
   
   3. UserService.java:20-27
      유형: 검색
      → users.stream().filter(...).findFirst()
   
   적용하시겠습니까? (yes / no / 수정)
   ```

4. **리팩토링 적용**
   - 루프를 해당 Stream Pipeline으로 변환
   - 중간 변수/플래그 변수 제거
   - 필요시 import 추가 (java.util.stream.Collectors 등)

5. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

6. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: replace loop with pipeline in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Replace Loop with Pipeline 완료

변경 내용:
- OrderService.java:30-36
  필터링+변환: for+if+add → stream().filter().map().toList()

- ReportService.java:50-55
  집계: for+if+= → stream().filter().mapToInt().sum()

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: replace loop with pipeline in OrderService, ReportService
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (리팩토링 후)
- [ ] 부수효과가 핵심인 루프를 단순 forEach로 변환함
- [ ] Stream으로 변환하여 오히려 가독성이 떨어짐
- [ ] 인덱스 기반 접근이 필요한 루프를 억지로 변환함
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
```

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/skills/replace-loop-with-pipeline/SKILL.md
git commit -m "feat: replace-loop-with-pipeline 스킬 생성"
```

---

### Task 5: introduce-parameter-object 스킬에 Preserve Whole Object 통합

**Files:**
- Modify: `msbaek-tdd/skills/introduce-parameter-object/SKILL.md`

- [ ] **Step 1: 스킬 설명(description) 업데이트**

`msbaek-tdd/skills/introduce-parameter-object/SKILL.md` frontmatter의 description을 변경:

Before:
```
description: 반복되는 파라미터 그룹을 객체로 치환하여 Value Object 발견. /introduce-parameter-object로 호출.
```

After:
```
description: 반복되는 파라미터 그룹을 객체로 치환(IPO)하거나, 객체에서 꺼낸 값 대신 객체 자체를 전달(PWO). /introduce-parameter-object로 호출.
```

- [ ] **Step 2: 스킬 제목과 GOAL 업데이트**

제목 변경:
```
# Introduce Parameter Object / Preserve Whole Object
```

GOAL 섹션 변경:

Before:
```markdown
반복되는 파라미터 그룹을 객체로 치환하여 응집도 높은 Value Object 발견.

## GOAL

- **성공 = 반복 파라미터 그룹이 Parameter Object로 치환되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 3개 이상의 파라미터가 함께 전달되는 패턴이 2회 이상 반복됨
- 논리적으로 관련 있는 파라미터 그룹이 식별됨
- 사용자 확인 후 Parameter Object 적용
- 모든 테스트 통과
- 원래 브랜치로 PR 생성
```

After:
```markdown
상황에 따라 두 가지 기법 중 적합한 것을 선택:

- **Introduce Parameter Object (IPO)**: 파라미터에 행위를 추가해야 할 때 → 새 객체 생성 → 행위 이동 → Value Object 발견
- **Preserve Whole Object (PWO)**: 기존 객체에서 값을 꺼내 전달할 때 → 객체 자체를 전달하여 파라미터 수 감소

## GOAL

- **성공 = 반복 파라미터가 IPO 또는 PWO로 정리되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- IPO: 파라미터 그룹이 Parameter Object로 치환되고 관련 행위가 이동됨
- PWO: 객체에서 꺼낸 값들이 객체 자체 전달로 대체됨
- 사용자 확인 후 적용
- 모든 테스트 통과
- 원래 브랜치로 PR 생성
```

- [ ] **Step 3: 선택 기준 섹션 추가**

"## CONSTRAINTS" 바로 앞에 새 섹션 추가:

```markdown
## 기법 선택 기준

| 상황 | 적용 기법 | 이유 |
|---|---|---|
| 파라미터들이 이미 하나의 객체에서 꺼내져 전달됨 | **Preserve Whole Object** | 객체가 이미 존재 — 꺼내지 말고 그대로 전달 |
| 파라미터에 대한 행위를 추가해야 하는 경우 | **Introduce Parameter Object** | 새 객체 생성 → 행위 이동 → Value Object 발견 |

### IPO의 진짜 목적

> "더 큰 혜택은 파라미터 그룹에 대해서 동작하는 행위들을 파라미터 객체로 이동시킬 수 있는 것" — Fowler, Ch10

IPO는 파라미터 묶기 자체가 목적이 아니라, **Value Object를 발견하는 시작점**:

```
Introduce Parameter Object
  → Move Instance Method (관련 로직을 Parameter Object로 이동)
    → Value Object 탄생 (데이터 + 행위를 가진 객체)
```

### 적용하면 안 되는 경우

| 상황 | 이유 |
|---|---|
| 파라미터 간에 논리적 관계가 없음 | 억지로 묶으면 이상한 객체가 탄생 |
| 한 메서드에서만 사용되는 파라미터 조합 | 반복이 없으면 추상화의 가치 없음 |
| 파라미터 객체에 이동할 행위가 없음 | 단순 DTO가 되어 Anemic Domain Model 유발 (이 경우 PWO가 더 적합할 수 있음) |
```

- [ ] **Step 4: Preserve Whole Object 적용 패턴 추가**

기존 "## 적용 패턴" 섹션 끝에 PWO 패턴 추가:

```markdown
### Preserve Whole Object 패턴

```java
// Before: 객체에서 값을 꺼내서 전달
int low = temperatureRange.getLow();
int high = temperatureRange.getHigh();
boolean withinRange = plan.isWithinRange(low, high);

// After: 객체 자체를 전달
boolean withinRange = plan.isWithinRange(temperatureRange);
```

```java
// Before: DTO에서 여러 값을 꺼내서 전달
String name = request.getName();
String email = request.getEmail();
int age = request.getAge();
User user = createUser(name, email, age);

// After: 객체 자체를 전달
User user = createUser(request);
```
```

- [ ] **Step 5: 후보 식별 섹션에 PWO 패턴 추가**

"#### 2. 반복 파라미터 그룹 후보 식별" 섹션을 변경:

Before:
```markdown
대상 파일에서 다음 패턴을 찾는다:

- 3개 이상의 파라미터를 받는 메서드
- 동일한 파라미터 조합이 2곳 이상에서 반복
- 파라미터들이 논리적으로 관련 있음 (같은 도메인 개념)
- 파라미터 순서가 일관됨
```

After:
```markdown
대상 파일에서 다음 패턴을 찾는다:

**패턴 A: Introduce Parameter Object**
- 3개 이상의 파라미터를 받는 메서드
- 동일한 파라미터 조합이 2곳 이상에서 반복
- 파라미터들이 논리적으로 관련 있음 (같은 도메인 개념)
- 파라미터에 대한 계산/검증 로직이 여러 곳에서 중복
- Move Method의 전 단계로 파라미터를 묶어야 하는 경우

**패턴 B: Preserve Whole Object**
- 하나의 객체에서 여러 값을 꺼내어 다른 메서드에 전달
- `obj.getX()`, `obj.getY()`, `obj.getZ()`를 꺼낸 뒤 `method(x, y, z)` 호출
- 객체 자체를 전달하면 파라미터 수가 줄어드는 경우
```

- [ ] **Step 6: 후보 제시 예시에 PWO 패턴 추가**

기존 후보 제시 형식 뒤에 PWO 예시 추가:

```markdown
```
## 리팩토링 후보 2: Preserve Whole Object

**파일**: HeatingPlan.java
**현재**: temperatureRange에서 low, high를 꺼내어 isWithinRange(low, high) 호출
**제안**: isWithinRange(temperatureRange)로 변경

적용할까요? (yes / no / 수정 요청)
```
```

- [ ] **Step 7: 실전 사례 섹션 추가**

FAILURE CONDITIONS 바로 앞에 추가:

```markdown
## 실전 리팩토링 경로 (Vault 사례)

### 사례 1: SequenceKey
```
Extract Method → Introduce Parameter Object → Move Instance Method → Convert Record to Class
```
효과: sequenceKey가 String → Value Object로 승격. format, increase 로직이 Value Object로 이동.

### 사례 2: ProductPrice
```
Split Conditional → Extract Method → Introduce Parameter Object → Move Instance Method
```
효과: isDiscounted, getFinalPrice가 ProductPrice로 이동. 독립 테스트 가능.

### 사례 3: StockChecker (빵속빵 패턴)
```
빵속빵(FCIS) 구조 만들기 → DTO 의존성을 파라미터로 전환 → Parameter Object 생성 → 관련 메서드 이동
```
패턴: Move Method 전 단계로 파라미터를 먼저 묶음.

### 공통 패턴
```
IPO → Move Instance Method → Value Object 탄생
```
```

- [ ] **Step 8: 테스트 실행 및 커밋**

```bash
./gradlew test  # 또는 mvn test (프로젝트가 있는 경우)
git add msbaek-tdd/skills/introduce-parameter-object/SKILL.md
git commit -m "refactor: introduce-parameter-object에 Preserve Whole Object 통합"
```

---

### Task 6: system-wide-refactoring에 Hide Delegate 추가 + 신규 스킬 추천

**Files:**
- Modify: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

- [ ] **Step 1: Domain Logic 이동 후보에 Hide Delegate 추가**

`msbaek-tdd/skills/system-wide-refactoring/SKILL.md`의 "**Domain Logic 이동 후보**" 섹션(line 63-65 부근) 끝에 추가:

Before:
```markdown
**Domain Logic 이동 후보**:
- Feature Envy — Service에서 도메인 객체의 데이터를 직접 조작
- Tell, Don't Ask 위반 — getter 체이닝으로 로직 수행
- Domain Service, Value Object, First Class Collection 추출 가능
```

After:
```markdown
**Domain Logic 이동 후보**:
- Feature Envy — Service에서 도메인 객체의 데이터를 직접 조작
- Tell, Don't Ask 위반 — getter 체이닝으로 로직 수행
- Hide Delegate — getter 체이닝으로 내부 객체를 노출 (디미터 법칙 위반)
  - 징후: `obj.getA().getB().doSomething()` 형태의 체이닝
  - 해결: 중간 객체를 숨기고 위임 메서드 제공, 또는 로직 자체를 obj로 이동
  - Tell Don't Ask와의 관계: 둘 다 Feature Envy의 증상. 해결 방향 동일 — 로직을 데이터가 있는 곳으로 이동
- Domain Service, Value Object, First Class Collection 추출 가능
```

- [ ] **Step 2: 후보 제시 예시에 Hide Delegate 추가**

line 96-99 부근의 후보 제시 예시 뒤에 추가:

```markdown
```
## 리팩토링 후보 N: Hide Delegate (Domain Logic 이동)

**파일**: OrderService.java
**대상**: order.getCustomer().getAddress().getCity() (3단계 체이닝)

**현재 코드**:
String city = order.getCustomer().getAddress().getCity();
if (city.equals("Seoul")) { applyLocalDiscount(); }

**제안 변경**:
1. Order에 getCustomerCity() 위임 메서드 추가
   또는
2. 판단 로직 자체를 Order로 이동: order.isLocatedIn("Seoul")

**적용할까요?** (yes / no / 수정 요청)
```
```

- [ ] **Step 3: 완료 후 추가 제안에 신규 스킬 추가**

line 196-208 부근의 "추가로 발견된 개선 기회" 섹션에 추가:

Before:
```markdown
- /separate-query-modifier — [파일명]에 값 반환과 부수효과 혼재
적용할 기법을 선택하세요 (slash command 또는 skip)
```

After:
```markdown
- /separate-query-modifier — [파일명]에 값 반환과 부수효과 혼재
- /introduce-special-case — [파일명]에 동일 타입 null 검사가 [N]곳 반복
적용할 기법을 선택하세요 (slash command 또는 skip)
```

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/system-wide-refactoring/SKILL.md
git commit -m "refactor: system-wide-refactoring에 Hide Delegate + introduce-special-case 추천 추가"
```

---

### Task 7: tdd-tidy 완료 후 추천에 신규 스킬 추가

**Files:**
- Modify: `msbaek-tdd/skills/tdd-tidy/SKILL.md`

- [ ] **Step 1: 추천 목록에 신규 스킬 추가**

`msbaek-tdd/skills/tdd-tidy/SKILL.md`의 line 85-91 부근, 기존 추천 목록에 추가:

Before:
```markdown
- /naming-process — 의도가 불분명한 이름이 [N]건 있습니다
- /encapsulate-collection — [파일명]에서 컬렉션이 직접 노출됩니다
적용할 기법을 선택하세요 (slash command 또는 skip)
```

After:
```markdown
- /naming-process — 의도가 불분명한 이름이 [N]건 있습니다
- /encapsulate-collection — [파일명]에서 컬렉션이 직접 노출됩니다
- /consolidate-conditional — [파일명]에서 동일 결과 조건문이 분산됩니다
- /introduce-assertion — [파일명]에서 암묵적 가정이 발견되었습니다
- /replace-loop-with-pipeline — [파일명]에서 명령형 루프를 Stream으로 변환 가능합니다
적용할 기법을 선택하세요 (slash command 또는 skip)
```

- [ ] **Step 2: 커밋**

```bash
git add msbaek-tdd/skills/tdd-tidy/SKILL.md
git commit -m "refactor: tdd-tidy 추천 목록에 신규 스킬 3개 추가"
```

---

### Task 8: plugin.json 설명 업데이트

**Files:**
- Modify: `msbaek-tdd/.claude-plugin/plugin.json`

- [ ] **Step 1: description과 version 업데이트**

`msbaek-tdd/.claude-plugin/plugin.json` 변경:

Before:
```json
{
  "name": "msbaek-tdd",
  "version": "1.5.0",
  "description": "Java + Spring Boot TDD workflow plugin with RGB cycle, local tidying, system-wide refactoring, and 12 optional refactoring skills",
```

After:
```json
{
  "name": "msbaek-tdd",
  "version": "1.6.0",
  "description": "Java + Spring Boot TDD workflow plugin with RGB cycle, local tidying, system-wide refactoring, and 16 optional refactoring skills",
```

- [ ] **Step 2: keywords에 신규 스킬 관련 키워드 추가**

Before:
```json
  "keywords": ["tdd", "java", "spring-boot", "red-green-blue", "tidying", "refactoring", "split-phase", "value-object", "naming"]
```

After:
```json
  "keywords": ["tdd", "java", "spring-boot", "red-green-blue", "tidying", "refactoring", "split-phase", "value-object", "naming", "null-object", "stream-pipeline", "assertion"]
```

- [ ] **Step 3: 커밋**

```bash
git add msbaek-tdd/.claude-plugin/plugin.json
git commit -m "chore: plugin.json v1.6.0 — 스킬 16개로 업데이트"
```
