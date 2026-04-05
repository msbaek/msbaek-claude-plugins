---
name: system-wide-refactoring
description: 대화형 System-wide Refactoring — Extract Method, Domain Logic 이동을 별도 브랜치에서 기법별 커밋 후 PR 생성. /system-wide-refactoring으로 호출.
argument-hint: "[commit-ref]"
---

# System-wide Refactoring Skill

코드 분석 → 리팩토링 후보 제시 → 사용자 확인 → 별도 브랜치에서 기법별 커밋 → PR 생성.

## GOAL

- **성공 = 사용자가 확인한 리팩토링이 별도 브랜치에서 기법별 커밋으로 완료되고, 원래 브랜치로 PR이 생성됨**
- Extract Method / Extract Delegate / Domain Logic 이동 / SoC(Split Phase, Split by Abstraction Layer, Split by Unrelated Complexity) 후보가 식별됨
- 사용자와 질의응답으로 방향이 확정됨
- 별도 브랜치에서 기법별 커밋 완료
- 모든 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 1파일 x 1기법 = 1커밋 (논리적으로 연결된 파일은 함께)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

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

#### 2. 코드 분석 — 리팩토링 후보 식별

대상 파일을 읽고 다음 패턴을 찾는다:

**Extract Method 후보**:
- 긴 메서드 (20줄 이상)에서 독립적인 로직 블록
- 여러 곳에서 반복되는 코드 패턴
- 서로 다른 추상화 수준이 섞인 메서드

**Extract Delegate 후보**:
- 한 클래스가 너무 많은 책임을 가진 경우
- 관련 필드와 메서드가 그룹을 이루는 경우

**Domain Logic 이동 후보**:
- Feature Envy — Service에서 도메인 객체의 데이터를 직접 조작
- Tell, Don't Ask 위반 — getter 체이닝으로 로직 수행
- Domain Service, Value Object, First Class Collection 추출 가능

**Split by Abstraction Layer 후보**:
- High-level 비즈니스 로직과 Low-level 인프라 코드(DB, I/O)가 한 메서드에 혼재
- App 계층과 Domain 계층이 분리되지 않은 경우

**Split by Unrelated Complexity 후보**:
- 서로 관계없는 복잡성(예: 사용자 처리 로직과 상품 처리 로직)이 한 메서드/클래스에 혼재
- 서로 다른 변경 이유를 가진 코드가 결합된 경우

**Split Phase 후보** (Functional Core & Imperative Shell 포함):
- 서로 다른 계산 단계가 한 메서드에 혼재 (예: 파싱 → 처리 → 포매팅)
- 순수 로직과 부수효과(I/O)가 분리되지 않은 경우 (빵속빵 패턴)
  - 패턴: I/O(impure) → 비즈니스 로직(pure) → I/O(impure)
- 중간 데이터 구조(Intermediate Data Structure)로 단계를 연결

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Extract Method

**파일**: OrderService.java
**대상**: processOrder() 메서드 (45줄)

**현재 코드**:
[해당 코드 블록]

**제안 변경**:
- calculateDiscount() 메서드 추출 (라인 23-35)
- validateInventory() 메서드 추출 (라인 37-42)

**적용할까요?** (yes / no / 수정 요청)
```

```
## 리팩토링 후보 N: Split Phase (Functional Core & Imperative Shell)

**파일**: OrderService.java
**대상**: processOrder() 메서드 (35줄)

**현재 코드**:
[해당 코드 블록 — DB 조회, 비즈니스 로직, DB 저장이 혼재]

**제안 변경**:
1. DB 조회를 메서드 상단으로 모음 (Imperative Shell — 빵)
2. 순수 비즈니스 로직을 별도 메서드로 추출 (Functional Core — 속)
3. DB 저장을 메서드 하단으로 모음 (Imperative Shell — 빵)

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

#### 5. 기법별 커밋 실행

확정된 리팩토링을 하나씩 수행:

1. 리팩토링 적용
2. 테스트 실행 (gradle test 또는 mvn test)
3. 테스트 통과 확인
4. 해당 파일만 git add
5. 커밋

**커밋 메시지 형식**:
- `refactor: extract method [메서드명] from [클래스명]`
- `refactor: extract delegate [클래스명] from [원본클래스명]`
- `refactor: move [설명] to [대상 클래스]`
- `refactor: split phase [설명] in [클래스명]`
- `refactor: split by abstraction layer [설명] in [클래스명]`
- `refactor: split unrelated complexity [설명] from [클래스명]`

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
  --title "refactor: system-wide refactoring for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- [적용된 기법 1]: [설명]
- [적용된 기법 2]: [설명]

## Commits
각 커밋은 하나의 리팩토링 기법을 적용합니다.
Commits 탭에서 개별 리뷰할 수 있습니다.

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
- 적용된 리팩토링 목록
- 리뷰 후 squash merge 안내

리팩토링 과정에서 발견된 추가 개선 기회를 제안:

```
추가로 발견된 개선 기회:
[발견 시에만 해당 항목 표시]
- /extract-method-object — [파일명]에서 지역 변수 얽힘으로 Extract Method 불가
- /replace-conditional-with-poly — [파일명]에 반복 switch/if-else [N]곳
- /introduce-parameter-object — [파일명]에 3개 이상 파라미터 그룹 반복
- /discover-value-object — [파일명]에 primitive 타입에 로직 집중
- /first-class-collection — [파일명]에 컬렉션+관련 로직 산재
- /lift-up-conditional — [파일명]에 동일 조건문 중복
- /separate-query-modifier — [파일명]에 값 반환과 부수효과 혼재
적용할 기법을 선택하세요 (slash command 또는 skip)
```

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ 동작이 변경되어 테스트가 실패 (되돌리기 필수)
- ❌ 기법별 커밋 없이 한꺼번에 커밋
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
- ❌ Local Tidying 기법 수행 (Guard Clauses, Reorder 등은 tdd-tidy 전담)
- ❌ Split Phase 적용 시 중간 데이터 구조 없이 단계만 분리 (단계 간 결합 유발)
