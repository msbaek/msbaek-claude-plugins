---
name: separate-query-modifier
description: 값 반환과 부수효과가 혼재된 메서드를 Query(순수)와 Modifier(부수효과)로 분리. /separate-query-modifier로 호출.
argument-hint: "[commit-ref]"
---

# Separate Query from Modifier Skill

값 반환과 부수효과가 혼재된 메서드를 Query(값 반환, 순수)와 Modifier(부수효과, void)로 분리하여 CQS 원칙 적용.

## GOAL

- **성공 = Query와 Modifier가 분리되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 값을 반환하면서 동시에 상태를 변경하는 메서드가 식별됨
- CQS(Command-Query Separation) 위반 패턴 확인됨
- 사용자 확인 후 Query와 Modifier 분리
- 모든 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 1파일 x 1기법 = 1커밋 (논리적으로 연결된 파일은 함께)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

### CQS 원칙

**Command-Query Separation (CQS)**:
- **Query**: 값을 반환하지만 상태를 변경하지 않음 (순수 함수)
- **Command (Modifier)**: 상태를 변경하지만 값을 반환하지 않음 (void)

**예외**: 원자적 연산 (CAS, pop 등)은 분리하면 thread-safety 파괴

## 적용 패턴

Separate Query from Modifier 리팩토링 단계:

1. **CQS 위반 메서드 식별**
   - 값을 반환하면서 동시에 상태 변경
   - 부수효과(side effect)가 숨겨져 있음

2. **Query 메서드 추출**
   - 상태 변경 없이 값만 반환
   - 순수 함수로 구현 (같은 입력 → 같은 출력)
   - 여러 번 호출해도 안전

3. **Modifier 메서드 추출**
   - 상태만 변경하고 void 반환
   - 부수효과가 명시적으로 드러남
   - 메서드명으로 변경 의도 표현

4. **호출자 코드 업데이트**
   - Query와 Modifier를 순차 호출
   - 필요에 따라 Query 결과를 Modifier에 전달

### Before/After 예시

```java
// Before: 값 반환 + 부수효과 혼재
public class OrderService {
    // 총액을 반환하면서 동시에 할인 적용 (부수효과)
    public double getTotalAndApplyDiscount(Order order) {
        double total = order.calculateTotal();
        
        // 숨겨진 부수효과 - 상태 변경
        if (total > 1000) {
            order.setDiscount(0.1);  // 10% 할인
        }
        
        return total;  // 값 반환
    }
    
    // 사용
    public void processOrder(Order order) {
        double total = getTotalAndApplyDiscount(order);  // 부수효과가 숨겨짐
        System.out.println("Total: " + total);
    }
}

// After: Query와 Modifier 분리
public class OrderService {
    // Query: 값만 반환, 상태 변경 없음 (순수)
    public double getTotal(Order order) {
        return order.calculateTotal();
    }
    
    // Modifier: 상태만 변경, void 반환
    public void applyDiscountIfEligible(Order order) {
        double total = order.calculateTotal();
        if (total > 1000) {
            order.setDiscount(0.1);
        }
    }
    
    // 사용: 부수효과가 명시적으로 드러남
    public void processOrder(Order order) {
        applyDiscountIfEligible(order);  // 상태 변경이 명확
        double total = getTotal(order);   // 순수한 값 조회
        System.out.println("Total: " + total);
    }
}
```

### 또 다른 예시: Collection 연산

```java
// Before: 요소를 반환하면서 제거 (부수효과)
public class TaskQueue {
    private List<Task> tasks = new ArrayList<>();
    
    // 다음 태스크를 반환하면서 큐에서 제거
    public Task getNextAndRemove() {
        if (tasks.isEmpty()) {
            return null;
        }
        Task next = tasks.get(0);
        tasks.remove(0);  // 부수효과
        return next;
    }
}

// After: Query와 Modifier 분리
public class TaskQueue {
    private List<Task> tasks = new ArrayList<>();
    
    // Query: 다음 태스크 조회만
    public Task peekNext() {
        if (tasks.isEmpty()) {
            return null;
        }
        return tasks.get(0);
    }
    
    // Modifier: 제거만 수행
    public void removeFirst() {
        if (!tasks.isEmpty()) {
            tasks.remove(0);
        }
    }
    
    // 사용
    public void processNext() {
        Task next = peekNext();
        if (next != null) {
            removeFirst();
            next.process();
        }
    }
}
```

### ⚠️ 예외: 원자적 연산

```java
// 분리하면 안 되는 경우: thread-safety 파괴
public class AtomicCounter {
    private int value;
    
    // ❌ 분리하면 race condition 발생
    public int getAndIncrement() {
        return value++;  // 원자적 연산 - CAS
    }
    
    // ✅ 이런 경우는 CQS 예외로 유지
    // 분리 시: getValue() + increment() → thread-unsafe
}
```

## 적용 기준

Separate Query from Modifier를 적용해야 하는 경우:

1. **CQS 위반**: 값을 반환하면서 동시에 상태 변경
2. **숨겨진 부수효과**: 메서드명이 get/calculate인데 상태 변경
3. **테스트 어려움**: 값 확인과 상태 확인을 동시에 해야 함
4. **캐싱 불가**: 부수효과 때문에 결과를 캐싱할 수 없음
5. **재호출 위험**: 같은 메서드를 여러 번 호출하면 문제 발생

**적용하지 말아야 하는 경우**:
- 원자적 연산 (CAS, pop, getAndIncrement 등)
- Thread-safety가 중요한 연산
- 성능상 분리가 불가능한 경우

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

#### 2. CQS 위반 메서드 후보 식별

대상 파일에서 다음 패턴을 찾는다:

- 반환 타입이 void가 아닌 메서드
- 메서드 내부에서 필드 변경 또는 setter 호출
- 메서드명이 get/calculate/find인데 상태 변경
- 동일 메서드를 여러 번 호출하면 다른 결과

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Separate Query from Modifier

**파일**: OrderService.java
**대상**: getTotalAndApplyDiscount() 메서드

**현재 코드**:
[메서드 전체 코드]

**CQS 위반 분석**:
- 반환: total (double)
- 부수효과: order.setDiscount(0.1) - 상태 변경

**제안 변경**:
1. Query 메서드 추출:
   - getTotal(Order) → double (순수)
   
2. Modifier 메서드 추출:
   - applyDiscountIfEligible(Order) → void (부수효과)
   
3. 호출자 코드 업데이트:
   - applyDiscountIfEligible(order);
   - double total = getTotal(order);

**적용할까요?** (yes / no / 수정 요청)

⚠️ 주의: 원자적 연산이 필요한 경우 적용하지 마세요.
```

- 사용자가 **yes** → 실행 목록에 추가
- 사용자가 **no** → 스킵
- 사용자가 **수정 요청** → 요청 반영 후 재제시

모든 후보 확인 후 최종 실행 목록을 보여주고 진행 여부 확인.

#### 4. 브랜치 생성

```bash
# 현재 브랜치 이름 확인
CURRENT_BRANCH=$(git branch --show-current)

# refactor 브랜치 생성 및 전환
git checkout -b "refactor/${CURRENT_BRANCH}"
```

#### 5. Query/Modifier 분리 실행

확정된 리팩토링을 하나씩 수행:

1. Query 메서드 추출 (상태 변경 로직 제거)
2. Modifier 메서드 추출 (반환 값 제거, void로 변경)
3. 호출자 코드 업데이트
   - Query와 Modifier 순차 호출
   - 부수효과가 명시적으로 드러나도록
4. 테스트 실행 (gradle test 또는 mvn test)
5. 테스트 통과 확인
6. 해당 파일만 git add
7. 커밋

**커밋 메시지 형식**:
```
refactor: separate query from modifier in [클래스명].[메서드명]
```

한글 커밋 메시지가 필요한 경우 Write tool로 임시 파일 생성 후 `git commit -F <파일>` 사용.

테스트 실패 시:
- 해당 리팩토링 변경사항 되돌리기 (`git checkout -- [파일]`)
- 사용자에게 실패 사유 안내
- 다음 리팩토링으로 진행

#### 6. PR 생성

모든 리팩토링 커밋 완료 후:

```bash
# 원래 브랜치로 PR 생성
gh pr create \
  --base "${CURRENT_BRANCH}" \
  --title "refactor: separate query from modifier for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- Separate Query from Modifier 적용: [메서드명]

## Changes
- Query 메서드 추출 (순수 함수, 값만 반환)
- Modifier 메서드 추출 (부수효과, void)
- 호출자 코드에서 부수효과를 명시적으로 드러냄

## Benefits
- CQS 원칙 준수
- 순수 함수로 테스트 용이
- 부수효과가 명시적으로 드러나 코드 이해 향상
- Query 결과를 안전하게 캐싱 가능

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
- 적용된 Query/Modifier 분리 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 원자적 연산(CAS, pop)을 분리하여 thread-safety 파괴
- ❌ 호출자 코드 수정 누락 (Query와 Modifier 모두 호출해야 함)
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ Query 메서드에 여전히 부수효과 남음 (완전히 순수해야 함)
- ❌ Modifier가 값을 반환 (void여야 함)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
