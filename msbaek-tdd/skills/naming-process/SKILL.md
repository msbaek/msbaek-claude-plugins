---
name: naming-process
description: Arlo Belshee의 6단계 네이밍 프로세스와 Clean Code 네이밍 규칙을 적용해, 여러 파일에 흩어진 개별 이름 스멜(타입 반복·-er/-Utils·불용어·축약어 등)을 탐지하고 배치 교체하여 코드 가독성 향상. 단, 하나의 긴 메서드를 통째로 관통(grouping→extract→rename)하는 것은 /intent-revealing-names가 적합. /naming-process로 호출.
argument-hint: "[commit-ref]"
---

# Naming as a Process

## GOAL

Arlo Belshee의 **6단계 네이밍 진화**와 **Clean Code 네이밍 규칙**을 적용하여:
- 코드의 의도를 이름으로 명확히 전달
- Naming Smells 제거
- 도메인 언어를 코드로 표현

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

## 6단계 네이밍 프로세스

1. **Obvious Nonsense** → 2. **Honest** → 3. **Completely Honest** → 4. **Does the Right Thing** → 5. **Intent Revealing** → 6. **Domain Abstraction**

### 예시: 네이밍 진화
```java
// 1. Obvious Nonsense
int x;

// 2. Honest (타입 반복)
int intValue;

// 3. Completely Honest (맥락 포함)
int orderItemCount;

// 4. Does the Right Thing (역할 명확)
int itemsInCart;

// 5. Intent Revealing (의도 표현)
int pendingOrderItems;

// 6. Domain Abstraction (도메인 언어)
int itemsAwaitingFulfillment;
```

## Clean Code 네이밍 규칙

### The Scope Rule
- **변수**: scope ↑ → 이름 ↑ (짧은 scope는 짧은 이름, 긴 scope는 긴 이름)
- **함수/클래스**: scope ↑ → 이름 ↓ (public은 짧고 명확, private은 구체적)

```java
// ✅ Good: 변수 scope 규칙
for (int i = 0; i < 10; i++) { ... }  // 짧은 scope → 짧은 이름
private Customer currentlyAuthenticatedCustomer;  // 긴 scope → 긴 이름

// ✅ Good: 함수 scope 규칙
public void save() { ... }  // public → 짧고 명확
private void validateAndPersistToDatabase() { ... }  // private → 구체적
```

### Parts of Speech
- **클래스**: 명사 (Customer, Order, Invoice)
- **메서드**: 동사 (calculate, save, send)
- **Boolean**: 서술어 (isValid, hasPermission, canExecute)

```java
// ✅ Good
if (employee.isLate()) {
    employee.reprimand();
}

// ❌ Bad
if (employee.late()) {  // 서술어 아님
    employee.punishment();  // 명사
}
```

### System of Names
이름의 체계가 도메인을 전달해야 함.

```java
// ✅ Good: 일관된 네이밍 체계
class OrderProcessor {
    void processOrder(Order order) { ... }
    void validateOrder(Order order) { ... }
    void fulfillOrder(Order order) { ... }
}

// ❌ Bad: 체계 없음
class OrderHandler {
    void doOrder(Order order) { ... }
    void checkOrder(Order order) { ... }
    void executeOrder(Order order) { ... }
}
```

## Naming Smells

### 1. 라이프사이클 이벤트명 (Lifecycle Event Names)
```java
// ❌ Bad
void onCreate() { ... }
void onDestroy() { ... }

// ✅ Good
void initialize() { ... }
void cleanup() { ... }
```

### 2. 타입 반복 (Type Repetition)
```java
// ❌ Bad
String nameString;
List<Order> orderList;

// ✅ Good
String name;
List<Order> orders;
```

### 3. -er / -Utils 클래스
```java
// ❌ Bad
class OrderProcessor { ... }
class StringUtils { ... }

// ✅ Good
class OrderService { ... }  // 또는 구체적 역할명
class TextFormatter { ... }
```

### 4. 불용어 (Noise Words)
```java
// ❌ Bad
class OrderData { ... }
class CustomerInfo { ... }
void processData() { ... }

// ✅ Good
class Order { ... }
class Customer { ... }
void calculateTotal() { ... }
```

### 5. 축약어 (Abbreviations)
```java
// ❌ Bad
int qty;
String custNm;

// ✅ Good
int quantity;
String customerName;
```

## 적용 기준

### ✅ 적용 대상
- 단일 문자 변수명 (i, j, k 제외 - 루프 인덱스는 허용)
- 타입 반복 이름
- -er/-Utils 클래스
- 불용어 포함 이름
- 축약어 사용
- 의도를 드러내지 않는 이름

### ❌ 적용 제외
- **루프 인덱스**: `i, j, k`는 관례상 허용
- **수학 공식**: `x, y, z`는 맥락상 명확한 경우 허용
- **도메인 표준 용어**: 업계 표준 축약어 (HTTP, URL, ID)

## OUTPUT FORMAT

### 실행 절차

공통 골격(대상 파일 수집 → 후보 제시·승인 → 적용 → 테스트 → 커밋/되돌리기, 브랜치·PR이
필요한 조건)은 이 스킬 디렉터리 기준 `../../references/refactoring-procedure.md`가 정본이다.
아래는 이 기법에 고유한 부분만 규정한다.

#### 후보 식별 — Collapse All + Naming Smells 탐지 (공통 절차 2단계)

- IDE Collapse All (구조만 보기)
- Naming Smells 패턴 탐지:
  - 타입 반복 (orderList, nameString)
  - -er/-Utils 클래스
  - 불용어 (Data, Info, Manager)
  - 단일 문자 변수 (루프 외)
  - 축약어 (qty, nm, addr)
- 6단계 네이밍 프로세스로 현재 단계 평가

#### 후보 제시 예시 (공통 절차 3단계)

```
발견된 Naming Smells 5개:

1. OrderProcessor.java (클래스)
   현재: OrderProcessor
   단계: 2 (Honest) - -er 클래스
   제안: OrderService (단계 5: Intent Revealing)

2. OrderProcessor.java:15 (변수)
   현재: List<Order> orderList
   단계: 2 (Honest) - 타입 반복
   제안: List<Order> pendingOrders (단계 5: Intent Revealing)

3. Customer.java:30 (메서드)
   현재: void processData()
   단계: 2 (Honest) - 불용어
   제안: void calculateLoyaltyPoints() (단계 6: Domain Abstraction)

적용하시겠습니까? (yes / no / 수정)
```

#### 리팩토링 적용 — IDE Rename (공통 절차 4단계)

- IDE의 Rename 리팩토리 사용 (모든 참조 자동 업데이트)
- 한 번에 하나씩 적용 (충돌 방지)

커밋 메시지: `refactor: improve naming in <클래스명>` (공통 절차 6단계)

### 출력 예시
```
✅ Naming Process 완료

변경 내용:
- OrderProcessor.java → OrderService.java
  (단계 2 → 5: -er 제거)
  
- orderList → pendingOrders (단계 2 → 5: 타입 반복 제거)

- processData() → calculateLoyaltyPoints()
  (단계 2 → 6: 불용어 제거, 도메인 언어 사용)

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: improve naming in OrderService

💡 제안: Customer.java에 축약어 3개가 남아 있습니다.
   다음 리팩토링 시 고려해보세요.
```

## FAILURE CONDITIONS

공통 실패 조건(승인 없이 적용, 테스트 실패 방치, 테스트 수정, 커밋 단위, `git add -A`, heredoc
한글 메시지)은 `../../references/refactoring-procedure.md`에 있다. 아래는 이 기법에 고유한 것만.

- [ ] 루프 인덱스(i, j, k)를 불필요하게 변경함
- [ ] 도메인 표준 용어(HTTP, URL)를 축약어로 판단하여 변경함
- [ ] Parts of Speech 위반 (클래스가 동사, 메서드가 명사 등)
