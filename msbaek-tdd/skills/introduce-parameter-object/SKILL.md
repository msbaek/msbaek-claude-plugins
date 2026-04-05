---
name: introduce-parameter-object
description: 반복되는 파라미터 그룹을 객체로 치환하여 Value Object 발견. /introduce-parameter-object로 호출.
argument-hint: "[commit-ref]"
---

# Introduce Parameter Object Skill

반복되는 파라미터 그룹을 객체로 치환하여 응집도 높은 Value Object 발견.

## GOAL

- **성공 = 반복 파라미터 그룹이 Parameter Object로 치환되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- 3개 이상의 파라미터가 함께 전달되는 패턴이 2회 이상 반복됨
- 논리적으로 관련 있는 파라미터 그룹이 식별됨
- 사용자 확인 후 Parameter Object 적용
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

Introduce Parameter Object 리팩토링 단계:

1. **반복 파라미터 그룹 식별**
   - 3개 이상의 파라미터가 함께 전달되는 패턴
   - 2곳 이상에서 동일한 파라미터 조합 반복

2. **Parameter Object 클래스 생성**
   - 논리적으로 관련된 파라미터를 하나의 클래스로
   - record 또는 immutable class 사용 (Java 14+)
   - 의미 있는 이름 부여

3. **메서드 시그니처 변경**
   - 개별 파라미터를 Parameter Object로 치환
   - 호출자 코드 업데이트

4. **관련 동작 이동 (선택적)**
   - Parameter Object와 관련된 로직을 객체 내부로 이동
   - Value Object로 발전 가능

### Before/After 예시

```java
// Before: 반복되는 파라미터 그룹
public class PriceService {
    public void processPrice(int originalPrice, int discountedPrice, String currency) {
        // 처리 로직
        validatePrice(originalPrice, discountedPrice, currency);
        formatPrice(originalPrice, discountedPrice, currency);
    }
    
    private void validatePrice(int originalPrice, int discountedPrice, String currency) {
        if (originalPrice < 0 || discountedPrice < 0) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        if (discountedPrice > originalPrice) {
            throw new IllegalArgumentException("Discounted price cannot exceed original");
        }
    }
    
    private String formatPrice(int originalPrice, int discountedPrice, String currency) {
        double discount = (originalPrice - discountedPrice) * 100.0 / originalPrice;
        return String.format("%s %.0f%% off: %d -> %d", 
            currency, discount, originalPrice, discountedPrice);
    }
}

// After: Parameter Object 적용
record Price(int original, int discounted, String currency) {
    // 생성자에서 검증
    public Price {
        if (original < 0 || discounted < 0) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        if (discounted > original) {
            throw new IllegalArgumentException("Discounted price cannot exceed original");
        }
    }
    
    // 관련 동작을 객체 내부로 이동
    public double discountPercentage() {
        return (original - discounted) * 100.0 / original;
    }
    
    public String formatted() {
        return String.format("%s %.0f%% off: %d -> %d", 
            currency, discountPercentage(), original, discounted);
    }
}

public class PriceService {
    public void processPrice(Price price) {
        // Parameter Object 하나만 전달
        // 검증은 Price 생성자에서 자동 수행
        String formatted = price.formatted();
    }
}
```

## 적용 기준

Introduce Parameter Object를 적용해야 하는 경우:

1. **파라미터 수**: 3개 이상의 파라미터가 함께 전달
2. **반복 패턴**: 동일한 파라미터 조합이 2회 이상 반복
3. **논리적 관계**: 파라미터들이 논리적으로 관련 있음
4. **함께 검증**: 파라미터들이 함께 검증되어야 함
5. **동시 변경**: 파라미터들이 함께 변경되는 경향

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

#### 2. 반복 파라미터 그룹 후보 식별

대상 파일에서 다음 패턴을 찾는다:

- 3개 이상의 파라미터를 받는 메서드
- 동일한 파라미터 조합이 2곳 이상에서 반복
- 파라미터들이 논리적으로 관련 있음 (같은 도메인 개념)
- 파라미터 순서가 일관됨

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Introduce Parameter Object

**파일**: PriceService.java
**반복 파라미터**: (int originalPrice, int discountedPrice, String currency)

**반복 위치** (3곳):
1. processPrice() 메서드
2. validatePrice() 메서드
3. formatPrice() 메서드

**현재 시그니처**:
void processPrice(int originalPrice, int discountedPrice, String currency)
void validatePrice(int originalPrice, int discountedPrice, String currency)
String formatPrice(int originalPrice, int discountedPrice, String currency)

**제안 변경**:
1. Price record 생성 (original, discounted, currency)
2. 검증 로직을 Price 생성자로 이동
3. 포맷팅 로직을 Price.formatted()로 이동
4. 모든 메서드 시그니처를 Price로 변경

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

#### 5. Parameter Object 도입 실행

확정된 리팩토링을 하나씩 수행:

1. Parameter Object 클래스(record) 생성
2. 검증 로직을 생성자로 이동
3. 관련 동작을 객체 메서드로 이동
4. 메서드 시그니처 변경
5. 호출자 코드 업데이트
6. 테스트 실행 (gradle test 또는 mvn test)
7. 테스트 통과 확인
8. 해당 파일만 git add
9. 커밋

**커밋 메시지 형식**:
```
refactor: introduce parameter object [객체명] in [클래스명]
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
  --title "refactor: introduce parameter object for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- Introduce Parameter Object 적용: [객체명]

## Changes
- 반복되는 파라미터 그룹을 Parameter Object로 통합
- 관련 검증/동작을 객체 내부로 이동
- 메서드 시그니처 간소화

## Benefits
- 파라미터 수 감소로 가독성 향상
- 관련 로직이 한곳에 모여 응집도 향상
- Value Object로 발전 가능한 기반 마련

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
- 적용된 Parameter Object 목록
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 논리적 관계 없는 파라미터를 억지로 묶음 (불필요한 결합)
- ❌ 1곳에만 사용되는 파라미터 그룹에 적용 (과도한 추상화)
- ❌ 동작이 변경되어 테스트 실패 (되돌리기 필수)
- ❌ mutable Parameter Object 생성 (불변성 보장 필요)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
