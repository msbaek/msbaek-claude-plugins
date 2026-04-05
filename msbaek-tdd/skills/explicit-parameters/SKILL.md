---
name: explicit-parameters
description: 암묵적 의존성(전역변수, 클래스 필드)을 명시적 파라미터로 전환하여 투명성 향상. /explicit-parameters로 호출.
argument-hint: "[commit-ref]"
---

# Explicit Parameters

## GOAL

암묵적 의존성(전역변수, 클래스 필드, Singleton)을 명시적 파라미터로 전환하여:
- 함수 시그니처로 의존성을 명확히 표현
- 테스트 용이성 향상 (의존성 주입 가능)
- 숨겨진 결합도 제거

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

## 적용 패턴

### Before: 필드에 암묵적 의존
```java
class OrderService {
    private DiscountPolicy discountPolicy;
    private TaxCalculator taxCalculator;
    
    double calculateTotal(Order order) {
        double discount = discountPolicy.calculate(order.getSubtotal());
        double tax = taxCalculator.calculate(order.getSubtotal() - discount);
        return order.getSubtotal() - discount + tax;
    }
}
```

### After: 명시적 파라미터
```java
class OrderService {
    double calculateTotal(Order order, DiscountPolicy discountPolicy, TaxCalculator taxCalculator) {
        double discount = discountPolicy.calculate(order.getSubtotal());
        double tax = taxCalculator.calculate(order.getSubtotal() - discount);
        return order.getSubtotal() - discount + tax;
    }
}
```

### 추가 예시: Singleton 의존성 제거
```java
// Before: 전역 상태 참조
double applyRate() {
    return amount * CurrencyConverter.getInstance().getRate("USD");
}

// After: 명시적 파라미터
double applyRate(CurrencyConverter converter) {
    return amount * converter.getRate("USD");
}
```

### 파라미터 과다 시: Introduce Parameter Object
```java
// 파라미터 3개 이상 시
class OrderService {
    double calculateTotal(Order order, PricingContext context) {
        double discount = context.getDiscountPolicy().calculate(order.getSubtotal());
        double tax = context.getTaxCalculator().calculate(order.getSubtotal() - discount);
        return order.getSubtotal() - discount + tax;
    }
}

class PricingContext {
    private final DiscountPolicy discountPolicy;
    private final TaxCalculator taxCalculator;
    // constructor, getters...
}
```

## 적용 기준

### ✅ 적용 대상
- 클래스 필드를 메서드 내에서만 참조
- Singleton 패턴으로 전역 접근하는 의존성
- 테스트 시 Mocking이 필요한 의존성
- 순수 함수로 전환 가능한 메서드

### ❌ 적용 제외
- **생성자 주입으로 관리되는 필드**: DI 컨테이너 관리 대상
- **도메인 상태 필드**: 객체의 본질적 상태 (e.g., `Customer.name`)
- **불변 상수**: `private static final` 값
- **파라미터 수 폭발**: 3개 이상이면 Parameter Object 고려

### ⚠️ 주의사항
- 파라미터 개수 증가는 신중히 판단
- 호출부 모두 업데이트 필요 (IDE 리팩토리 활용)
- 순수 함수화가 목적이라면 필드 제거까지 진행

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
   - 메서드 내에서만 참조되는 필드 탐지
   - Singleton 패턴 호출 탐지
   - 전역 변수 참조 탐지
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - Before/After 코드 미리보기
     - 영향받는 호출부 수 (Change Impact)

3. **사용자 확인**
   ```
   발견된 후보 2개:
   
   1. OrderService.java:25 calculateTotal()
      필드 의존: discountPolicy, taxCalculator
      → 파라미터로 전환 (영향받는 호출부 5곳)
   
   2. PaymentProcessor.java:40 processPayment()
      Singleton 의존: Logger.getInstance()
      → 파라미터로 전환 (영향받는 호출부 3곳)
   
   적용하시겠습니까? (yes / no / 수정)
   파라미터 3개 이상이면 Parameter Object 생성을 제안합니다.
   ```

4. **리팩토링 적용**
   - 메서드 시그니처에 파라미터 추가
   - 필드 참조를 파라미터 참조로 치환
   - 모든 호출부에서 인자 전달
   - (선택) 필드가 다른 곳에서 사용 안 되면 제거
   - (선택) 파라미터 3개 이상 시 Parameter Object 생성

5. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

6. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: explicit parameters in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Explicit Parameters 완료

변경 내용:
- OrderService.java: calculateTotal() 파라미터 추가 (2개)
  → discountPolicy, taxCalculator
- PaymentProcessor.java: processPayment() Singleton 제거
  → logger 파라미터 추가

영향받는 호출부: 8곳 자동 업데이트

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: explicit parameters in OrderService, PaymentProcessor

💡 제안: OrderService.calculateTotal()은 파라미터 3개 이상입니다.
   Introduce Parameter Object를 고려해보세요.
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (리팩토링 후)
- [ ] 도메인 상태 필드를 파라미터로 전환함
- [ ] 생성자 주입 필드를 파라미터로 전환함 (DI 컨테이너 방해)
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
- [ ] 파라미터 5개 이상으로 증가 (Parameter Object 미적용)
