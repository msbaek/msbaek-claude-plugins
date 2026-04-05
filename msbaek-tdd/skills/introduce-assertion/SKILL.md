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
