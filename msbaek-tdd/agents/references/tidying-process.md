# Tidying Process — Composed Method 지향 리팩토링 절차

> `tdd-blue` 에이전트가 참조하는 정본. 판단 기준(80% 규칙, 언제 멈추는가)은 `tdd-blue.md`
> 본문에 있고, 여기는 **각 단계를 어떻게 적용하는가**(절차 + before/after 예시)만 담는다.

Tidying의 목표는 **Composed Method Pattern** — 메서드 내 모든 작업이 동일한 추상화 수준에
있고, 각 메서드가 하나의 식별 가능한 작업만 수행하는 상태.

## 프로세스 흐름

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
      2.5 Normalize Symmetries (Canonical Order 포함)
           ▼                              │
      3. Chunk Statements                 │
           ▼                              │
      4. Explaining Comment ← 필수1       │
           ▼                              │
      5. Extract Variable ← 필수2         │
           ▼                              │
      5.5 Split Loop                      │
           │                              │
           ├→ 6. Trimming                 │
           ▼                              │
      7. 이해하기 어려워졌나?              │
           ├─ Yes ────────────────────────┘
           └─ No → 완료
```

## 0. Guard Clauses (중첩 제거 — 가장 먼저)

**목적**: 깊은 중첩을 early return으로 평탄화하여 이후 Tidying이 효과적으로 동작하도록 준비

```java
// Before: 깊은 중첩
public void processOrder(Order order) {
    if (order != null) {
        if (order.isValid()) {
            if (order.hasPayment()) {
                processPayment(order);
                shipOrder(order);
            }
        }
    }
}

// After: Guard clauses로 평탄화
public void processOrder(Order order) {
    if (order == null) return;
    if (!order.isValid()) return;
    if (!order.hasPayment()) return;

    processPayment(order);
    shipOrder(order);
}
```

## 1. One Pile (inline method) — 조건부

**목적**: 커플링된 관심사가 여러 메서드에 분산되어 있을 때, 한 곳에 모아 전체 흐름을 파악한 뒤 직교적으로 재분리

> "커플링을 유발하는 관심사를 직교화할 방법을 찾을 때까지의 임시 방안" — Kent Beck

**진입 조건** (하나 이상 해당 시):
- 조숙한 리팩터링으로 Composed Method가 위배되어 코드 의도가 전달되지 않을 때
- **여러 메서드에 걸친 관심사**: 자원 열기/닫기, 트랜잭션 시작/종료 등이 분산
- **인스턴스 변수를 통한 암묵적 결합**: 한 메서드에서 열고, 다른 메서드에서 닫는 패턴
- **적절한 추상화가 보이지 않을 때**: 분리의 축이 불분명한 상태

**3단계 프로세스**:
```
관심사가 서로 섞여 있는 상태 (intermixed concerns)
    ↓
모든 것을 한 곳에 모음 (One Pile — interim design)
    ↓
직교성이 보이면 관심사를 깔끔하게 분리
```

```java
// 1단계: 자원 관리가 여러 메서드에 분산 (커플링 발생)
class Processor {
    File file; // 인스턴스 변수로 결합 유발
    void step1() {
        file = new File(...); // 여기서 열고
        // ... step1 로직
    }
    void step2() { ... }    // 예외 시 파일 미정리 (암묵적 결합)
    void step3() {
        // ... step3 로직
        file.close();        // 여기서 닫음
    }
}

// 2단계: One Pile — 한 곳에 모아 전체 흐름 파악
void process() {
    File file = new File(...);
    // step 1 로직
    // step 2 로직
    // step 3 로직
    file.close();
    // → 파일 열기/닫기가 한눈에 보임. 하지만 비즈니스 로직과 자원 관리가 뒤섞임
}

// 3단계: 직교성 발견 후 분리 (자원 관리 ↔ 비즈니스 로직)
void process() {
    File.openWhile(file -> {   // 자원 관리는 여기서 보장
        step1(file);           // 비즈니스 로직만 담당
        step2(file);
        step3(file);
    }); // 예외 발생해도 파일 반드시 닫힘
}
```

**직교성 판단 기준** (분리 시점):
- 독립적으로 변경 가능한가?
- 서로 다른 이유로 변경되는가?
- 재사용 가능한 단위인가?
→ 기준이 충족되지 않으면 One Pile 상태를 유지 (성급한 추상화보다 나음)

**핵심 원칙**:
- One Pile은 **중간 설계(interim design)** — 최종 목표가 아님
- **성급한 추상화보다 One Pile 상태가 낫다**: 가장 강력한 추상화는 실행 중인 코드에서 발견됨 (need driven)
- 직교하는 서로 다른 관심사를 발견할 때까지 합치고, 직교성이 보이면 분리

**커밋 전략**: One Pile은 **항상** 별도 커밋으로 분리한다 (`refactor: one-pile [대상]`).
중간 설계 상태를 반드시 기록하여, 이후 재분리에서 문제 발생 시 이 지점으로 복원 가능하게 한다.

## 2. Reorder (Slide Statements)

**목적**: 코드 읽기 순서를 개선하여 의도가 드러나도록 구성

2가지 관점에서 재배치:
- **Reading Order**: 변수 선언을 사용 위치 가까이로 이동 (`Move declaration closer to usages`)
- **Cohesion Order**: 관련된 로직끼리 함께 배치 (Step Down Rule 적용)

문장 수준을 넘어 **클래스 멤버 수준**에도 같은 원칙을 적용한다:
- **클래스 멤버 순서**: private field → constructor → public method → 그 public method들이
  호출하는 private method (호출 순서를 따르는 step-down 배열). 논문의 요약·소개만 읽고도
  전체를 파악할 수 있듯, 파일 위쪽만 읽으면 이 클래스가 무엇을 하는지 알 수 있게 한다.
  여러 메서드가 호출하는 leaf 헬퍼(예: 절사·포맷 유틸)는 클래스 하단에 둔다.

```java
// Before: 모든 변수를 맨 위에 선언 (사용과 거리가 멀음)
public OrderProcessResult processOrder(Order order, Customer customer) {
    double totalAmount = 0;
    boolean isVipCustomer = false;
    String customerEmail = customer.getEmail();
    double discountRate = 0;
    double shippingCost = 0;
    // ... 100줄 후에 변수 사용
}

// After: 사용 직전에 선언, 관련 로직끼리 배치
public OrderProcessResult processOrder(Order order, Customer customer) {
    // 고객 분석 (사용 직전에 선언)
    boolean isVipCustomer = customer.getOrderHistory().size() > 10;
    double discountRate = calculateDiscountRate(customer, order, isVipCustomer);

    // 재고 확인 (사용 직전에 선언)
    List<OrderItem> validItems = validateInventory(order.getItems());
    double totalAmount = calculateTotalAmount(validItems, isVipCustomer);
}
```

## 2.5 Normalize Symmetries (Canonical Order 포함)

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

## 3. Chunk Statements (빈 라인으로 그룹핑)

**목적**: 빈 줄을 삽입하여 관련된 코드 블록을 논리적으로 그룹화

```java
// Before: 모든 코드가 밀집
if (order == null) throw new IllegalArgumentException("Order is null");
if (customer == null) throw new IllegalArgumentException("Customer is null");
boolean isVipCustomer = customer.getOrderHistory().size() > 10;
double discountRate = calculateDiscountRate(customer, order, isVipCustomer);
List<OrderItem> validItems = validateInventory(order.getItems());
double totalAmount = calculateTotalAmount(validItems, isVipCustomer);

// After: 논리적 블록으로 그룹핑
// 입력 검증
if (order == null) throw new IllegalArgumentException("Order is null");
if (customer == null) throw new IllegalArgumentException("Customer is null");

// 고객 분석 및 할인 계산
boolean isVipCustomer = customer.getOrderHistory().size() > 10;
double discountRate = calculateDiscountRate(customer, order, isVipCustomer);

// 재고 확인 및 가격 계산
List<OrderItem> validItems = validateInventory(order.getItems());
double totalAmount = calculateTotalAmount(validItems, isVipCustomer);
```

## 4. Explaining Comment ← 필수1

**목적**: 복잡한 비즈니스 로직에 의도(WHY)를 설명하는 주석 추가

> **Extract Method의 전 단계** — 좋은 이름을 떠올릴 수 없을 때 먼저 주석으로 의도를 표현

```java
// Before: 의도가 불명확한 조건
if (item.getProduct().getCategory().equals("ELECTRONICS") && item.getQuantity() > 2) {
    itemPrice = itemPrice * 0.9;
}
if (item.getProduct().isOnSale() && !isVipCustomer) {
    itemPrice = itemPrice * 0.95;
}

// After: 비즈니스 의도를 설명하는 주석
// 전자제품 대량 구매 할인: 3개 이상 구매 시 10% 할인
if (item.getProduct().getCategory().equals("ELECTRONICS") && item.getQuantity() > 2) {
    itemPrice = itemPrice * 0.9;
}

// 세일 상품 추가 할인: VIP는 이미 15% 기본 할인을 받으므로 중복 적용 안함
if (item.getProduct().isOnSale() && !isVipCustomer) {
    itemPrice = itemPrice * 0.95;
}
```

**중복 설명 금지**: 같은 사실을 두 곳(예: 상수 선언부와 사용처)에 설명하지 않는다 —
의미가 필요한 한 곳에만 둔다. 두 곳에 두면 규칙이 바뀔 때 한 곳을 놓쳐 comment rot이 생긴다.
이름(상수명·메서드명)이 이미 의미를 전달하면 그 자체로 충분하고, 주석은 이름이 담지 못하는
근거(예: 스펙 조항 참조)에만 쓴다.

## 5. Extract Variable ← 필수2

**목적**: 복잡한 표현식을 의미있는 변수로 추출하여 가독성 향상

> 복잡한 조건식이나 계산식에 의도를 드러내는 이름을 붙인다.
> 같은 클래스 내부로의 Extract Method(사설 메서드 추출)는 이 단계 이후 허용된다.
> 다른 클래스로 옮기는 이동(Domain Logic 이동)은 system-wide-refactoring 스킬에서 수행한다.

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

## 5.5 Split Loop (루프가 2가지 이상 일을 하면 분리)

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

## 6. Trimming

**목적**: 사용하지 않는 변수, 메서드, 조건문 등 불필요한 코드 제거

```java
// Before: 불필요한 코드
String unusedVariable = "This is never used";
Date orderDate = new Date(); // order.confirm()에서 처리하므로 불필요

private void oldCalculationMethod(Order order) { /* deprecated */ }

// After: 필요한 코드만 유지
// (위 코드 모두 제거)
```

## 7. 품질 게이트: 이해하기 어려워졌나?

5번까지 진행한 결과 코드가 오히려 이해하기 어려워졌다면:
- **Yes** → **1. One Pile**로 돌아가서 잘못 추출된 메서드를 inline한 후 처음부터 다시 진행
- **No** → **완료** — 다음 Red Phase 준비

> 잘못 추출된 메서드는 이름과 실제 동작이 불일치하거나, 너무 많은 책임을 가진 경우.
> 이때는 억지로 고치지 말고 One Pile로 합친 후 올바르게 재추출한다.
