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

### 패턴 2-1: 집계 — 객체 타입 (BigDecimal 등)

primitive가 아닌 타입은 `sum()`이 없으므로 `reduce(항등원, 누적 연산)`을 쓴다.
금액(BigDecimal) 합산이 대표 사례:

```java
// Before
BigDecimal total = BigDecimal.ZERO;
for (Line line : lines) {
    total = total.add(line.amount());
}

// After
BigDecimal total = lines.stream()
    .map(Line::amount)
    .reduce(BigDecimal.ZERO, BigDecimal::add);
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
     - `T acc = 항등원` + for + 재대입 누적 (BigDecimal 등 객체 타입) → map + reduce(항등원, 누적 연산)
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
