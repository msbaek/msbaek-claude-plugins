# Refactoring Catalog Enhancement Design

> refactoring.com/catalog/ 기반 기존 tidy/system-wide 스킬 보완 및 누락 기법 추가

## 배경

Martin Fowler의 Refactoring 2nd Edition 카탈로그(refactoring.com/catalog/)와 기존 msbaek-tdd 플러그인의 17개 스킬을 비교 분석하여, 누락된 기법 추가와 기존 기법 보완을 수행한다.

## 접근 방식

- **B 중심 + 선별적 A**: 기존 스킬 보완 중심, 독립 가치가 높은 기법만 신규 추가
- 스킬 수 증가에 따른 선택 부담을 고려하여 최소한의 추가만 수행

---

## 신규 스킬 (4개)

### 1. Consolidate Conditional Expression

- **목적**: 동일한 결과를 내는 여러 개의 조건문을 하나로 통합하고, 통합된 조건을 의미 있는 메서드로 추출
- **커밋 전략**: 단일 커밋 (decompose-conditional 패턴)
- **decompose-conditional과의 관계**:
  - Consolidate = 흩어진 조건들을 **모으는** 방향 (여러 if → 하나의 if)
  - Decompose = 복잡한 조건을 **쪼개는** 방향 (하나의 복잡한 if → 여러 메서드)
  - 실전에서는 Consolidate → Decompose 순서로 적용하는 경우가 많음

**적용 패턴:**

```java
// Before: 동일 결과를 내는 조건들이 분산
if (employee.getSeniority() < 2) return 0;
if (employee.getMonthsDisabled() > 12) return 0;
if (employee.isPartTime()) return 0;

// After: 조건 통합 + 메서드 추출
if (isNotEligibleForDisability(employee)) return 0;

private boolean isNotEligibleForDisability(Employee employee) {
    return employee.getSeniority() < 2
        || employee.getMonthsDisabled() > 12
        || employee.isPartTime();
}
```

```java
// Before: 동일 결과를 내는 중첩 조건 (AND 패턴)
if (employee.onVacation()) {
    if (employee.getSeniority() > 10) {
        return 1;
    }
}

// After: AND로 통합
if (employee.onVacation() && employee.getSeniority() > 10) {
    return 1;
}
```

**적용 기준:**
- 2개 이상의 조건문이 동일한 결과(return/throw/assign)를 냄
- 조건들이 논리적으로 OR 또는 AND로 결합 가능
- 각 조건이 독립적 (부수효과 없음)

**적용 제외:**
- 조건들이 서로 다른 결과를 냄
- 조건 사이에 부수효과 코드가 있음
- 의도적으로 분리한 경우 (각 조건이 서로 다른 비즈니스 규칙)

---

### 2. Introduce Assertion

- **목적**: 코드가 암묵적으로 가정하는 조건을 assertion으로 명시하여, 가정 위반 시 즉시 발견 가능하게 함
- **커밋 전략**: 단일 커밋 (decompose-conditional 패턴)
- **핵심 가치**: 주석보다 강력한 실행 가능한 문서, 디버깅 시간 단축

**assertion 도구 선택 (프로젝트 의존성 자동 감지):**
- Spring 의존성 → `org.springframework.util.Assert`
- Apache Commons → `org.apache.commons.lang3.Validate`
- 둘 다 없음 → `java.util.Objects.requireNonNull` + `IllegalArgumentException`

> Java `assert` 키워드는 `-ea` 플래그 필요로 프로덕션에서 비활성화될 수 있으므로 사용하지 않음

**적용 패턴:**

```java
// Before: 암묵적 가정
public double calculateDiscount(double price, double rate) {
    return price * rate;
}

// After: Spring Assert 사용
public double calculateDiscount(double price, double rate) {
    Assert.isTrue(price > 0, "price must be positive: " + price);
    Assert.isTrue(rate >= 0 && rate <= 1, "rate must be between 0 and 1: " + rate);
    return price * rate;
}
```

**적용 기준:**
- 메서드가 특정 조건을 가정하지만 명시하지 않은 경우
- 내부 메서드(private/package-private)의 전제 조건
- 계산 결과의 사후 조건 (결과값 범위 검증)
- 알고리즘의 불변식 (invariant)

**적용 제외:**
- public API의 입력 검증 (예외를 사용해야 함)
- 비즈니스 규칙 검증 (도메인 로직으로 처리)
- 이미 Guard Clause나 예외로 처리된 조건
- 외부 입력 (시스템 경계는 명시적 검증 필요)

---

### 3. Introduce Special Case (Null Object)

- **목적**: 반복되는 null 검사를 특수 케이스 객체로 대체하여, null 처리 로직을 한 곳에 캡슐화
- **커밋 전략**: 브랜치 + PR (introduce-parameter-object 패턴)
- **핵심 가치**: 다형성으로 정상/특수 케이스를 동일 취급, null 처리 일관성 보장

**적용 패턴:**

```java
// Before: null 검사가 여러 곳에 산재
Customer customer = site.getCustomer();
String name = (customer == null) ? "occupant" : customer.getName();
BillingPlan plan = (customer == null) ? BillingPlan.basic() : customer.getBillingPlan();

// After: Special Case 객체 도입
public class UnknownCustomer extends Customer {
    @Override public String getName() { return "occupant"; }
    @Override public BillingPlan getBillingPlan() { return BillingPlan.basic(); }
    @Override public boolean isUnknown() { return true; }
}

// Site에서 null 대신 Special Case 반환
public Customer getCustomer() {
    return (customer == null) ? new UnknownCustomer() : customer;
}

// 호출처: null 검사 제거
String name = site.getCustomer().getName();
```

**적용 기준:**
- 동일 객체에 대한 null 검사가 3곳 이상 반복
- null일 때의 기본값/기본 동작이 일관됨
- 대상 타입이 상속 또는 인터페이스 구현 가능 (final 아님)

**적용 제외:**
- null 검사가 1-2곳뿐 (과도한 추상화)
- null일 때 동작이 호출처마다 다름
- 외부 라이브러리의 클래스 (상속 불가)
- Optional로 이미 충분히 처리되는 경우

**실행 절차:**
1. 대상 파일 수집 (git diff)
2. null 검사 반복 패턴 탐지 (동일 타입 3곳+)
3. 후보 제시 + 사용자 확인
4. 브랜치 생성 (`refactor/현재브랜치`)
5. Special Case 클래스 생성 → 커밋 1
6. 소스에서 null 대신 Special Case 반환 → 커밋 2
7. 호출처 null 검사 제거 → 커밋 3
8. 테스트 실행 → PR 생성

---

### 4. Replace Loop with Pipeline

- **목적**: 명령형 루프를 Stream API/Collection Pipeline으로 변환하여 데이터 흐름의 의도를 명확히 표현
- **커밋 전략**: 단일 커밋 (decompose-conditional 패턴)
- **핵심 가치**: what vs how — Pipeline은 "무엇을" 하는지 표현, 중간 변수/플래그 변수 제거

**적용 패턴:**

```java
// Before: 필터링 + 변환
List<String> result = new ArrayList<>();
for (Order order : orders) {
    if (order.isActive()) {
        result.add(order.getCustomerName());
    }
}

// After: Stream Pipeline
List<String> result = orders.stream()
    .filter(Order::isActive)
    .map(Order::getCustomerName)
    .toList();
```

```java
// Before: 집계
int total = 0;
for (LineItem item : items) {
    if (item.getQuantity() > 0) {
        total += item.getPrice() * item.getQuantity();
    }
}

// After: Stream Pipeline
int total = items.stream()
    .filter(item -> item.getQuantity() > 0)
    .mapToInt(item -> item.getPrice() * item.getQuantity())
    .sum();
```

```java
// Before: 검색
Employee found = null;
for (Employee e : employees) {
    if (e.getDepartment().equals("Engineering")) {
        found = e;
        break;
    }
}

// After: Stream Pipeline
Optional<Employee> found = employees.stream()
    .filter(e -> e.getDepartment().equals("Engineering"))
    .findFirst();
```

**적용 기준:**
- 컬렉션 순회 + 필터링/변환/집계/검색 패턴
- 중간 변수에 결과를 누적하는 루프
- 플래그 변수로 제어하는 루프
- 중첩 루프에서 내부 루프가 독립적 검색/필터인 경우

**적용 제외:**
- 부수효과가 핵심인 루프 (forEach로만 바꾸는 것은 가치 없음)
- 인덱스 기반 접근이 필수인 루프
- break/continue 조건이 복잡한 루프 (Stream으로 변환 시 오히려 난해)
- 성능 크리티컬 루프 (primitive 배열 대량 처리)
- Java 8 미만 프로젝트

---

## 기존 스킬 보완 (2개)

### 5. introduce-parameter-object — Preserve Whole Object 통합

**변경 파일**: `msbaek-tdd/skills/introduce-parameter-object/SKILL.md`

**선택 기준:**

| 상황 | 적용 기법 | 이유 |
|---|---|---|
| 파라미터들이 이미 하나의 객체에서 꺼내져 전달됨 | **Preserve Whole Object** | 객체가 이미 존재 — 꺼내지 말고 그대로 전달 |
| 파라미터에 대한 행위를 추가해야 하는 경우 | **Introduce Parameter Object** | 새 객체 생성 → 행위 이동 → Value Object 발견 |

**Introduce Parameter Object의 진짜 목적:**

> 파라미터 묶기 자체가 아니라, Value Object를 발견하는 시작점
> IPO → Move Instance Method → Value Object 탄생

**Preserve Whole Object 추가 패턴:**

```java
// Before: 객체에서 값을 꺼내서 전달
int low = temperatureRange.getLow();
int high = temperatureRange.getHigh();
boolean withinRange = plan.isWithinRange(low, high);

// After: 객체 자체를 전달
boolean withinRange = plan.isWithinRange(temperatureRange);
```

**보완 내용:**
- 후보 식별 단계에 패턴 A (IPO) / 패턴 B (PWO) 구분 추가
- vault 실전 사례 4개 반영 (SequenceKey, ProductPrice, StockChecker, Gms)
- 리팩토링 경로: IPO → Move Instance Method → Value Object
- 적용하면 안 되는 경우 보강:
  - 파라미터 간 논리적 관계 없음 → 억지 객체
  - 한 메서드에서만 사용 → 반복 없으면 가치 없음
  - 이동할 행위가 없음 → Anemic DTO (이 경우 PWO가 더 적합)

---

### 6. system-wide-refactoring — Hide Delegate 패턴 추가

**변경 파일**: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

**Domain Logic 이동 후보에 추가:**

```
- Hide Delegate — getter 체이닝으로 내부 객체를 노출 (디미터 법칙 위반)
  - 징후: obj.getA().getB().doSomething() 형태의 체이닝
  - 해결: 중간 객체를 숨기고 위임 메서드 제공
    obj.doSomethingViaA() 또는 로직 자체를 obj로 이동
```

**Tell Don't Ask / Feature Envy와의 관계 명시:**
- Tell Don't Ask 위반 = 데이터를 꺼내서 외부에서 판단
- Hide Delegate = 내부 구조를 노출하는 체이닝
- 둘 다 Feature Envy의 증상, 해결 방향 동일: 로직을 데이터가 있는 곳으로 이동

**후보 제시 예시:**

```
## 리팩토링 후보 N: Hide Delegate (Domain Logic 이동)

**파일**: OrderService.java
**대상**: order.getCustomer().getAddress().getCity() (3단계 체이닝)

**제안 변경**:
1. Order에 getCustomerCity() 위임 메서드 추가
   또는
2. 판단 로직 자체를 Order로 이동: order.isLocatedIn("Seoul")

**적용할까요?** (yes / no / 수정)
```

---

## 제외된 기법 및 이유

| 기법 | 제외 이유 |
|---|---|
| Slide Statements | tidy의 Reorder와 동일 기법 |
| Replace Subclass with Delegate | replace-conditional-with-poly로 충분 |
| Encapsulate Record/Variable | 무시 (사용자 결정) |
| 중간 가치 섹션 전체 | 무시 (사용자 결정) |
| 낮은 가치 섹션 전체 | IDE 자동화, 너무 단순, 또는 기존 스킬에 포함 |

---

## tdd-tidy / system-wide 기법 추천 연결

신규 스킬 완성 후, 기존 추천 흐름에 연결:

**tdd-tidy 완료 후 추가 제안 후보:**
- `/consolidate-conditional` — 동일 결과 조건문이 분산된 경우
- `/introduce-assertion` — 암묵적 가정이 발견된 경우
- `/replace-loop-with-pipeline` — 명령형 루프 패턴이 발견된 경우

**system-wide 완료 후 추가 제안 후보:**
- `/introduce-special-case` — null 검사가 3곳 이상 반복되는 경우
