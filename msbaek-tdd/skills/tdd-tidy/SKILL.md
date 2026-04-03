---
name: tdd-tidy
description: git diff 기준 변경 파일을 자동 탐지하여 Composed Method 지향 Tidying Process를 독립 실행. /tdd-tidy로 호출.
argument-hint: "[commit-ref]"
---

# Tidying Skill — Composed Method 지향 독립 리팩토링

git diff로 최근 변경된 Java 파일을 자동 탐지하여, tdd-blue agent의 Local Tidying Process를 TDD 사이클 없이 독립 실행합니다.

## GOAL

- **성공 = 변경된 파일의 코드 냄새가 안전하게 제거되고, 모든 테스트가 통과하며, `refactor:` 커밋 완료됨**
- git diff 기준으로 대상 파일이 정확히 식별됨
- Local Tidying Process가 적용됨 (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming)
- 모든 기존 테스트가 통과함
- 하나의 `refactor:` 커밋으로 완료됨 (변경이 있는 경우)

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 구조 변경이 테스트를 깨면 되돌리기
- **80% 규칙** — 지금 할 수 있는 수준에서 80% 이하로 리팩토링
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
- 변경 파일이 없으면: "tidying 대상 Java 파일이 없습니다." 안내 후 종료

#### 2. 대상 파일 확인

수집된 파일 목록을 사용자에게 보여주고 확인:

```
다음 파일에 Tidying Process를 적용합니다:
- src/main/java/com/example/OrderService.java
- src/main/java/com/example/PaymentProcessor.java

진행할까요?
```

#### 3. tdd-blue agent 호출

사용자 확인 후 tdd-blue agent를 **standalone 모드**로 호출:

```
[standalone] 다음 파일에 Local Tidying Process를 적용해주세요:
- src/main/java/com/example/OrderService.java
- src/main/java/com/example/PaymentProcessor.java

Local Tidying Process (Guard Clauses → One Pile → Reorder → Chunk → Comment → Extract Variable → Trimming)를 순서대로 적용하고,
변경이 있으면 하나의 refactor: 커밋으로 완료해주세요.
Extract Method와 Domain Logic 이동은 수행하지 마세요 (system-wide-refactoring 스킬 전담).
```

#### 4. 결과 보고

tdd-blue agent 완료 후 사용자에게 결과 보고:
- 적용된 tidying 단계
- 변경된 파일과 주요 개선 사항
- 커밋 해시 (변경이 있는 경우)

## FAILURE CONDITIONS

- ❌ 테스트 파일을 tidying 대상에 포함
- ❌ 동작이 변경되어 테스트가 실패
- ❌ 사용자 확인 없이 tidying 진행
- ❌ git add -A로 전체 파일 추가
