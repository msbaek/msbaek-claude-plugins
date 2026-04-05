---
name: extract-method-object
description: 지역 변수가 얽힌 거대 메서드를 별도 클래스(Method Object)로 추출. /extract-method-object로 호출.
argument-hint: "[commit-ref]"
---

# Extract Method Object Skill

지역 변수가 얽혀 Extract Method가 어려운 거대 메서드를 별도 클래스로 추출.

## GOAL

- **성공 = 지역 변수가 얽힌 긴 메서드가 Method Object로 추출되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 50줄 이상의 복잡한 메서드가 식별됨
- 지역 변수가 메서드 전역에 걸쳐 얽혀있어 Extract Method 불가
- 사용자 확인 후 Method Object 패턴 적용
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

Extract Method Object 리팩토링 단계:

1. **메서드를 클래스로 변환**
   - 새 클래스 생성 (메서드명 + "er" 또는 명사형)
   - 원본 메서드를 invoke() 또는 execute() 메서드로 이동

2. **지역 변수를 필드로 변환**
   - 메서드 내 지역 변수들을 클래스 필드로 변환
   - 읽기 전용 변수는 final 필드로

3. **외부 의존성을 생성자 파라미터로 전달**
   - 원본 클래스의 필드 참조를 생성자 파라미터로
   - 필요한 최소한의 의존성만 전달

4. **작은 메서드로 분해**
   - 큰 invoke() 메서드를 의미 있는 작은 private 메서드들로 분해
   - 각 메서드는 단일 책임 수행

### Before/After 예시

```java
// Before: 지역 변수가 얽힌 거대 메서드 (50+ lines)
public class RefundService {
    public List<RefundDiff> refundDiff() {
        // 지역 변수 선언
        Map<String, Cost> costMap = new HashMap<>();
        Map<String, AcmeCost> acmeCostMap = new HashMap<>();
        List<RefundDiff> differences = new ArrayList<>();
        
        // 복잡한 로직이 50줄 이상...
        for (Cost cost : costs) {
            costMap.put(cost.getItemId(), cost);
        }
        
        for (AcmeCost acmeCost : acmeCosts) {
            acmeCostMap.put(acmeCost.getItemId(), acmeCost);
        }
        
        for (OrderItem item : orderItems) {
            Cost cost = costMap.get(item.getItemId());
            AcmeCost acmeCost = acmeCostMap.get(item.getItemId());
            
            if (cost != null && acmeCost != null) {
                double diff = cost.getAmount() - acmeCost.getAmount();
                if (Math.abs(diff) > 0.01) {
                    differences.add(new RefundDiff(item, diff));
                }
            }
        }
        
        return differences;
    }
}

// After: Method Object로 추출
public class RefundService {
    public List<RefundDiff> refundDiff() {
        return new RefundDifferenceCalculator(costs, acmeCosts).invoke(orderItems);
    }
}

class RefundDifferenceCalculator {
    private final List<Cost> costs;
    private final List<AcmeCost> acmeCosts;
    private Map<String, Cost> costMap;
    private Map<String, AcmeCost> acmeCostMap;
    private List<RefundDiff> differences;
    
    RefundDifferenceCalculator(List<Cost> costs, List<AcmeCost> acmeCosts) {
        this.costs = costs;
        this.acmeCosts = acmeCosts;
    }
    
    List<RefundDiff> invoke(List<OrderItem> orderItems) {
        buildCostMaps();
        calculateDifferences(orderItems);
        return differences;
    }
    
    private void buildCostMaps() {
        costMap = costs.stream()
            .collect(Collectors.toMap(Cost::getItemId, c -> c));
        acmeCostMap = acmeCosts.stream()
            .collect(Collectors.toMap(AcmeCost::getItemId, c -> c));
    }
    
    private void calculateDifferences(List<OrderItem> orderItems) {
        differences = new ArrayList<>();
        for (OrderItem item : orderItems) {
            findAndAddDifference(item);
        }
    }
    
    private void findAndAddDifference(OrderItem item) {
        Cost cost = costMap.get(item.getItemId());
        AcmeCost acmeCost = acmeCostMap.get(item.getItemId());
        
        if (cost != null && acmeCost != null) {
            addDifferenceIfSignificant(item, cost, acmeCost);
        }
    }
    
    private void addDifferenceIfSignificant(OrderItem item, Cost cost, AcmeCost acmeCost) {
        double diff = cost.getAmount() - acmeCost.getAmount();
        if (Math.abs(diff) > 0.01) {
            differences.add(new RefundDiff(item, diff));
        }
    }
}
```

## 적용 기준

Extract Method Object를 적용해야 하는 경우:

1. **메서드 길이**: 50줄 이상의 긴 메서드
2. **지역 변수 얽힘**: 여러 지역 변수가 메서드 전체에 걸쳐 상호작용
3. **Extract Method 불가**: 파라미터가 너무 많아져 Extract Method로 분해 불가
4. **임시 변수 과다**: 중간 결과를 저장하는 임시 변수가 많음
5. **단계적 계산**: 여러 단계의 계산이 순차적으로 진행됨

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

#### 2. Method Object 후보 식별

대상 파일에서 다음 패턴을 찾는다:

- 50줄 이상의 긴 메서드
- 5개 이상의 지역 변수 선언
- 지역 변수가 메서드 전체에 걸쳐 읽기/쓰기됨
- Extract Method 시 파라미터가 4개 이상 필요
- 여러 단계의 계산이 순차적으로 진행

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Extract Method Object

**파일**: RefundService.java
**대상**: refundDiff() 메서드 (68줄)

**현재 코드**:
[해당 메서드 전체]

**지역 변수 분석**:
- costMap, acmeCostMap, differences (메서드 전체에서 사용)
- 5개 이상의 지역 변수가 얽혀있음
- Extract Method 불가 (파라미터 6개 필요)

**제안 변경**:
1. RefundDifferenceCalculator 클래스 생성
2. 지역 변수를 필드로 변환
3. costs, acmeCosts를 생성자 파라미터로
4. invoke(orderItems) 메서드로 계산 수행
5. buildCostMaps(), calculateDifferences() 등으로 분해

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

#### 5. Method Object 추출 실행

확정된 리팩토링을 하나씩 수행:

1. Method Object 클래스 생성 및 메서드 이동
2. 지역 변수를 필드로 변환
3. 외부 의존성을 생성자 파라미터로
4. 작은 메서드로 분해
5. 테스트 실행 (gradle test 또는 mvn test)
6. 테스트 통과 확인
7. 해당 파일만 git add
8. 커밋

**커밋 메시지 형식**:
```
refactor: extract method object [클래스명] from [원본클래스명].[메서드명]
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
  --title "refactor: extract method object for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- Extract Method Object 적용: [클래스명] from [원본클래스명]

## Changes
- 긴 메서드를 별도 Method Object 클래스로 추출
- 지역 변수를 필드로 변환하여 Extract Method 가능하게 분해
- 외부 의존성을 생성자 파라미터로 명시

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
- 적용된 Method Object 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 지역 변수가 적은 (3개 이하) 단순 메서드에 적용 (Extract Method로 충분)
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ Method Object 생성 후 작은 메서드로 분해하지 않음 (단순히 코드만 옮김)
- ❌ 필요 이상의 의존성을 생성자로 전달 (원본 클래스 전체 전달 등)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
