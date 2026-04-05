---
name: replace-temp-with-query
description: 임시 변수를 메서드 호출로 치환하여 중복 제거 및 가독성 향상. /replace-temp-with-query로 호출.
argument-hint: "[commit-ref]"
---

# Replace Temp with Query

## GOAL

한 번만 대입되고 여러 곳에서 사용되는 임시 변수를 의미 있는 이름의 메서드로 추출하여:
- 중복된 계산 로직 제거
- 표현식의 의미를 명확한 메서드명으로 전달
- Extract Method의 전제 조건 충족 (임시 변수 제거)

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

## 적용 패턴

### Before
```java
double basePrice = quantity * itemPrice;
if (basePrice > 1000) {
    return basePrice * 0.95;
} else {
    return basePrice * 0.98;
}
```

### After
```java
if (basePrice() > 1000) {
    return basePrice() * 0.95;
} else {
    return basePrice() * 0.98;
}

private double basePrice() {
    return quantity * itemPrice;
}
```

### 추가 예시: 복잡한 조건식
```java
// Before
double tax = order.getTotal() * 0.1;
double shipping = order.getTotal() > 100 ? 0 : 10;
return order.getTotal() + tax + shipping;

// After
return order.getTotal() + tax() + shipping();

private double tax() { return order.getTotal() * 0.1; }
private double shipping() { return order.getTotal() > 100 ? 0 : 10; }
```

## 적용 기준

### ✅ 적용 대상
- 한 번만 대입되는 임시 변수
- 여러 곳에서 참조되는 변수
- 복잡한 표현식을 담은 변수 (의미 부여 가치 높음)
- Extract Method 전 단계로 사용

### ❌ 적용 제외
- **루프 내 누적 변수** (accumulator): `sum += value;`
- **부수효과 있는 표현식**: 메서드 호출이 상태 변경하는 경우
- **여러 번 대입되는 변수**: 값이 변경되는 경우
- **성능 크리티컬 구간**: 측정된 성능 문제가 있는 경우만

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
   - 임시 변수 패턴 탐지 (한 번 대입, 여러 번 참조)
   - 적용 제외 조건 필터링
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - Before/After 코드 미리보기
     - 적용 근거 (참조 횟수, 표현식 복잡도)

3. **사용자 확인**
   ```
   발견된 후보 3개:
   
   1. OrderService.java:45
      basePrice = quantity * itemPrice
      → private double basePrice() { return quantity * itemPrice; }
      (참조 3회, 복잡도 낮음)
   
   적용하시겠습니까? (yes / no / 수정)
   ```

4. **리팩토링 적용**
   - 메서드 추출 (private, 원본 표현식)
   - 임시 변수 참조를 메서드 호출로 치환
   - 임시 변수 선언 제거

5. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

6. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: replace temp with query in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Replace Temp with Query 완료

변경 내용:
- OrderService.java: basePrice 변수 → basePrice() 메서드
- InvoiceCalculator.java: discount 변수 → discount() 메서드

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: replace temp with query in OrderService, InvoiceCalculator
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (리팩토링 후)
- [ ] 부수효과 있는 표현식을 메서드로 추출함
- [ ] 누적 변수를 메서드로 치환함
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
