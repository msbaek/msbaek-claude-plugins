---
name: lift-up-conditional
description: 여러 곳에 중복된 조건문을 상위로 끌어올려 중복 제거. /lift-up-conditional로 호출.
argument-hint: "[commit-ref]"
---

# Lift Up Conditional Skill

여러 곳에 중복된 조건문을 상위로 끌어올려 중복을 제거하고 코드 의도를 명확히.

## GOAL

- **성공 = 중복 조건문이 상위로 끌어올려져 별도 브랜치에서 커밋 완료, PR 생성됨**
- 동일한 조건문이 여러 메서드/블록에서 반복됨
- 조건에 따라 다른 처리가 필요한 패턴 식별됨
- 사용자 확인 후 조건문 끌어올리기 적용
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

Lift Up Conditional 리팩토링 단계:

1. **중복 조건문 식별**
   - 동일한 조건식이 여러 곳에서 반복
   - 조건에 따라 다른 동작 수행

2. **조건을 변수로 추출**
   - 중복된 조건식을 boolean 변수로 추출
   - 의미 있는 변수명으로 조건 의도 명확히

3. **조건을 메서드로 추출 (선택적)**
   - 복잡한 조건은 별도 메서드로
   - 메서드명으로 조건의 비즈니스 의미 표현

4. **조건을 상위로 끌어올림**
   - Surround with if-else로 조건을 한 곳으로 모음
   - 조건 내부에서 각 메서드 호출
   - 불필요한 중간 변수 제거 (inline)

### Before/After 예시

```java
// Before: 동일 조건 중복
public class ProductService {
    public double calculatePrice(Product product) {
        if (product.isOnSale()) {
            return product.getPrice() * 0.9;  // 10% 할인
        }
        return product.getPrice();
    }
    
    public String formatLabel(Product product) {
        if (product.isOnSale()) {
            return "SALE: " + product.getName();
        }
        return product.getName();
    }
    
    public String getBadgeColor(Product product) {
        if (product.isOnSale()) {
            return "red";
        }
        return "blue";
    }
}

// After: 조건을 상위로 끌어올림
public class ProductService {
    public ProductDisplay createDisplay(Product product) {
        if (product.isOnSale()) {
            return createSaleDisplay(product);
        }
        return createNormalDisplay(product);
    }
    
    private ProductDisplay createSaleDisplay(Product product) {
        double price = product.getPrice() * 0.9;
        String label = "SALE: " + product.getName();
        String badgeColor = "red";
        return new ProductDisplay(price, label, badgeColor);
    }
    
    private ProductDisplay createNormalDisplay(Product product) {
        double price = product.getPrice();
        String label = product.getName();
        String badgeColor = "blue";
        return new ProductDisplay(price, label, badgeColor);
    }
}
```

### 단계별 리팩토링 과정

```java
// Step 1: 조건을 변수로 추출
boolean isOnSale = product.isOnSale();
if (isOnSale) { ... }

// Step 2: 조건을 메서드로 추출 (복잡한 경우)
private boolean isEligibleForDiscount(Product product) {
    return product.isOnSale() && product.getPrice() > 1000;
}

// Step 3: Surround with if-else로 조건 끌어올림
if (isEligibleForDiscount(product)) {
    double price = calculateSalePrice(product);
    String label = formatSaleLabel(product);
    String badge = getSaleBadgeColor();
} else {
    double price = calculateNormalPrice(product);
    String label = formatNormalLabel(product);
    String badge = getNormalBadgeColor();
}

// Step 4: 각 분기를 메서드로 추출 + inline
if (isEligibleForDiscount(product)) {
    return createSaleDisplay(product);
}
return createNormalDisplay(product);
```

## 적용 기준

Lift Up Conditional을 적용해야 하는 경우:

1. **조건 중복**: 동일한 조건문이 2곳 이상에서 반복
2. **논리적 연관**: 중복된 조건들이 같은 비즈니스 규칙을 나타냄
3. **일관성**: 조건이 참/거짓일 때의 처리가 여러 곳에서 일관됨
4. **복잡도**: 조건이 복잡하여 의도가 불명확함
5. **변경 빈도**: 조건이 자주 변경되어 여러 곳 수정 필요

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

#### 2. 중복 조건문 후보 식별

대상 파일에서 다음 패턴을 찾는다:

- 동일한 조건식이 2곳 이상에서 반복
- 조건식이 같은 변수/메서드를 참조
- 조건 분기에서 서로 다른 메서드 호출
- 논리적으로 같은 비즈니스 규칙

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Lift Up Conditional

**파일**: ProductService.java
**중복 조건**: product.isOnSale()

**반복 위치** (3곳):
1. calculatePrice() 메서드
2. formatLabel() 메서드
3. getBadgeColor() 메서드

**현재 코드**:
[조건이 반복되는 메서드들]

**제안 변경**:
1. 조건을 변수로 추출: boolean isOnSale = product.isOnSale()
2. createDisplay() 메서드 생성
3. 조건을 상위로 끌어올림 (surround with if-else)
4. 각 분기를 메서드로 추출
   - createSaleDisplay(product)
   - createNormalDisplay(product)
5. ProductDisplay 객체로 결과 통합

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

#### 5. 조건문 끌어올리기 실행

확정된 리팩토링을 하나씩 수행:

1. 조건을 변수로 추출
2. 조건을 메서드로 추출 (복잡한 경우)
3. Surround with if-else로 조건 끌어올림
4. 각 분기를 메서드로 추출
5. 불필요한 중간 변수 제거 (inline)
6. 테스트 실행 (gradle test 또는 mvn test)
7. 테스트 통과 확인
8. 해당 파일만 git add
9. 커밋

**커밋 메시지 형식**:
```
refactor: lift up conditional [조건 설명] in [클래스명]
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
  --title "refactor: lift up conditional for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- Lift Up Conditional 적용: [조건 설명]

## Changes
- 중복된 조건문을 상위로 끌어올림
- 조건별 처리를 명시적 메서드로 분리
- 조건의 비즈니스 의미를 메서드명으로 표현

## Benefits
- 중복 조건 제거로 유지보수성 향상
- 조건 변경 시 한 곳만 수정
- 코드 의도가 명확해짐

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
- 적용된 조건문 끌어올리기 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 논리적으로 다른 조건을 동일하다고 판단 (조건식은 같아도 의미가 다를 수 있음)
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ 조건 평가 순서 변경으로 부수효과 발생 (short-circuit 주의)
- ❌ 단순히 조건만 이동하고 메서드 추출 없음 (가독성 개선 부족)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
