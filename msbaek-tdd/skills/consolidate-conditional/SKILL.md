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
