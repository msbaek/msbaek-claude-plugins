---
name: first-class-collection
description: 컬렉션과 관련 로직을 전용 클래스로 추출하여 First Class Collection 생성. /first-class-collection으로 호출.
argument-hint: "[commit-ref]"
---

# First Class Collection Skill

컬렉션과 관련 로직이 산재할 때 전용 클래스로 추출하여 응집도 향상.

## GOAL

- **성공 = 컬렉션과 관련 로직이 First Class Collection으로 추출되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 컬렉션에 대한 연산/필터링/집계 로직이 여러 곳에 산재함
- 3개 이상의 컬렉션 관련 메서드가 식별됨
- 사용자 확인 후 First Class Collection 추출
- 모든 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 1파일 x 1기법 = 1커밋 (논리적으로 연결된 파일은 함께)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

## 적용 패턴

First Class Collection 리팩토링 단계:

1. **컬렉션 관련 로직 식별**
   - 컬렉션에 대한 필터링/매핑/집계 로직
   - 컬렉션 검증 로직
   - 컬렉션 기반 비즈니스 규칙

2. **First Class Collection 클래스 생성**
   - 컬렉션을 wrapping하는 전용 클래스
   - 컬렉션 필드는 private final로 캡슐화
   - Immutable 설계 (방어적 복사)

3. **관련 로직 이동**
   - 산재된 컬렉션 연산을 메서드로 이동
   - 필터링 로직을 의미 있는 메서드명으로 추출
   - 집계/계산 로직을 메서드로 캡슐화

4. **Value Object 연계**
   - 컬렉션 요소가 primitive인 경우 Value Object 적용 고려
   - /discover-value-object와 연계

### Before/After 예시

```java
// Before: 컬렉션 관련 로직이 Service에 산재
public class OrderService {
    private List<Order> orders;
    
    public double totalAmount() {
        return orders.stream()
            .mapToDouble(Order::getAmount)
            .sum();
    }
    
    public List<Order> expensiveOrders() {
        return orders.stream()
            .filter(order -> order.getAmount() > 1000)
            .collect(Collectors.toList());
    }
    
    public List<Order> ordersByStatus(OrderStatus status) {
        return orders.stream()
            .filter(order -> order.getStatus() == status)
            .collect(Collectors.toList());
    }
    
    public boolean hasExpensiveOrder() {
        return orders.stream()
            .anyMatch(order -> order.getAmount() > 1000);
    }
    
    public int orderCount() {
        return orders.size();
    }
}

// After: First Class Collection으로 추출
public class Orders {
    private final List<Order> items;
    
    public Orders(List<Order> items) {
        this.items = new ArrayList<>(items);  // 방어적 복사
    }
    
    // 집계 연산
    public double totalAmount() {
        return items.stream()
            .mapToDouble(Order::getAmount)
            .sum();
    }
    
    public int size() {
        return items.size();
    }
    
    // 필터링 연산 (새로운 Orders 반환)
    public Orders expensive() {
        return new Orders(
            items.stream()
                .filter(order -> order.getAmount() > 1000)
                .toList()
        );
    }
    
    public Orders byStatus(OrderStatus status) {
        return new Orders(
            items.stream()
                .filter(order -> order.getStatus() == status)
                .toList()
        );
    }
    
    // 조건 검사
    public boolean hasExpensive() {
        return items.stream()
            .anyMatch(order -> order.getAmount() > 1000);
    }
    
    public boolean isEmpty() {
        return items.isEmpty();
    }
    
    // 불변성을 유지하는 접근
    public List<Order> asList() {
        return Collections.unmodifiableList(items);
    }
}

public class OrderService {
    private Orders orders;
    
    // 간결해진 Service 로직
    public double totalAmount() {
        return orders.totalAmount();
    }
    
    public Orders expensiveOrders() {
        return orders.expensive();
    }
    
    public boolean hasExpensiveOrder() {
        return orders.hasExpensive();
    }
}
```

## 적용 기준

First Class Collection을 적용해야 하는 경우:

1. **로직 산재**: 컬렉션 관련 로직이 3곳 이상에 분산
2. **반복 연산**: 동일한 필터링/집계 로직이 반복됨
3. **비즈니스 규칙**: 컬렉션 자체에 대한 비즈니스 규칙 존재
4. **검증 필요**: 컬렉션 상태에 대한 검증이 필요
5. **불변성**: 컬레션 변경을 제어하고 싶음

**관련 기법**:
- **/encapsulate-collection**: Collection을 getter로 노출하지 않고 캡슐화 (전 단계)
- **/discover-value-object**: 컬렉션 요소를 Value Object로 치환 (내부 요소 개선)

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

#### 2. First Class Collection 후보 식별

대상 파일에서 다음 패턴을 찾는다:

- List/Set/Map 필드를 가진 클래스
- 해당 컬렉션에 대한 연산 메서드가 3개 이상
- 동일한 필터링/집계 패턴이 반복됨
- 컬렉션 상태에 대한 비즈니스 규칙 존재

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: First Class Collection

**파일**: OrderService.java
**대상**: List<Order> orders

**컬렉션 관련 로직** (5개 메서드):
1. totalAmount() - 집계
2. expensiveOrders() - 필터링
3. ordersByStatus() - 필터링
4. hasExpensiveOrder() - 조건 검사
5. orderCount() - 집계

**현재 코드**:
[관련 메서드들]

**제안 변경**:
1. Orders 클래스 생성 (First Class Collection)
2. 컬렉션 관련 로직을 Orders로 이동
   - totalAmount()
   - expensive() (expensiveOrders 대체)
   - byStatus(status) (ordersByStatus 대체)
   - hasExpensive() (hasExpensiveOrder 대체)
   - size() (orderCount 대체)
3. 불변성 보장 (방어적 복사, unmodifiable)
4. OrderService는 Orders에 위임

**적용할까요?** (yes / no / 수정 요청)
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

#### 5. First Class Collection 추출 실행

확정된 리팩토링을 하나씩 수행:

1. First Class Collection 클래스 생성
2. 컬렉션을 private final 필드로 캡슐화
3. 방어적 복사 구현
4. 관련 로직을 메서드로 이동
5. 원본 클래스를 First Class Collection에 위임
6. 테스트 실행 (gradle test 또는 mvn test)
7. 테스트 통과 확인
8. 해당 파일만 git add
9. 커밋

**커밋 메시지 형식**:
```
refactor: extract first class collection [클래스명] from [원본클래스명]
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
  --title "refactor: extract first class collection for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- First Class Collection 적용: [클래스명]

## Changes
- 컬렉션과 관련 로직을 전용 클래스로 추출
- 필터링/집계 로직을 의미 있는 메서드로 캡슐화
- 불변성 보장 (방어적 복사)

## Benefits
- 컬렉션 관련 로직이 한곳에 모여 응집도 향상
- 반복되는 Stream 연산 제거
- 비즈니스 규칙이 명시적으로 표현됨
- 컬렉션 상태 보호 (캡슐화)

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
- 적용된 First Class Collection 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 컬렉션 관련 로직이 1~2개뿐인데 적용 (불필요한 복잡도)
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ 방어적 복사 없이 원본 컬렉션 노출 (불변성 파괴)
- ❌ 단순 getter/setter만 제공 (캡슐화 의미 없음)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
