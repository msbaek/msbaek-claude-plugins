# Tidy/Refactoring 스킬 분리 설계

## 배경

현재 `/tdd-tidy` 스킬은 8단계 Tidying Process 전체를 하나의 `refactor:` 커밋으로 수행한다.
문제점:
- local tidying과 system-wide refactoring이 혼재되어 리뷰가 어려움
- Extract Method, Domain Logic 이동 같은 설계 판단이 필요한 기법이 자동 실행됨
- Kent Beck의 "Tidy First?" 관점에서 tidying은 최소한의 local 정리여야 함

## 결정 사항

### 원칙

- **Tidying** = local, 몇 분 내 완료, 기계적으로 적용 가능한 구조 개선 → 하나의 커밋
- **System-wide refactoring** = 설계 판단 필요, 여러 파일에 영향 → 별도 브랜치/PR, 기법별 커밋
- Beck의 tidying 정의에 따라 두 성격을 명확히 분리

### 커밋 전략

| 스킬 | 커밋 단위 | 브랜치 |
|------|-----------|--------|
| tdd-tidy | 하나의 `refactor:` 커밋 | 현재 브랜치 |
| system-wide-refactoring | 1파일 x 1기법 = 1커밋 | `refactor/<현재브랜치>` |

커밋 예외: Extract Delegate처럼 하나의 기법이 논리적으로 여러 파일에 영향을 미치는 경우 하나의 커밋으로 처리.

## 변경 1: tdd-tidy / tdd-blue 범위 축소

**적용 대상**: tdd-tidy (standalone), tdd-blue (RGB Blue Phase) 모두

**변경 후 Tidying Process (6단계 + 품질 게이트)**:

```
0. Guard Clauses (중첩 제거)
1. One Pile (inline — 조건부)
2. Reorder (Slide Statements)
3. Chunk Statements
4. Explaining Comment
5. Extract Variable (Extract Method 제외)
6. Trimming
7. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
```

**제거 항목**:
- Extract Method → system-wide-refactoring으로 이동
- Domain Logic 이동 → system-wide-refactoring으로 이동

**수정 대상 파일**:
- `msbaek-tdd/agents/tdd-blue.md` — Tidying Process에서 5번을 Extract Variable로 한정, 6번(Domain Logic) 제거
- `msbaek-tdd/skills/tdd-tidy/SKILL.md` — tdd-blue 호출 시 전달하는 단계 목록 업데이트

**커밋 전략**: 기존대로 하나의 `refactor:` 커밋 (변경 없음)

## 변경 2: system-wide-refactoring 스킬 신규 생성

**파일**: `msbaek-tdd/skills/system-wide-refactoring/SKILL.md`

### 실행 방식

tdd-blue agent를 사용하지 않고, 스킬 자체에서 직접 실행한다.
이유: 질의응답 기반 대화형 워크플로우 + 브랜치/PR 관리는 tdd-blue agent의 역할과 다름.

### 포함 기법

- Extract Method (메서드 추출)
- Extract Delegate (클래스 추출/위임)
- Domain Logic 이동 (Feature Envy 제거, Tell Don't Ask)

### 워크플로우

```
1. 호출 (/system-wide-refactoring [commit-ref])
2. git diff로 대상 파일 수집 (또는 사용자 지정)
3. 코드 분석 → 리팩토링 후보 제시
4. 사용자와 질의응답 (방향 확정까지)
5. refactor/<현재브랜치> 브랜치 생성
6. 기법별 커밋 (1파일 x 1기법 = 1커밋, 논리적 연결 시 함께)
7. 각 커밋 후 테스트 통과 확인
8. 원래 브랜치로 PR 생성 (gh pr create)
9. 결과 보고
```

### 질의응답 단계 (Step 4) 상세

- 후보마다 "현재 코드 → 제안 변경"을 보여주고 하나씩 확인
- 사용자가 거부하면 스킵, 수정 요청하면 반영
- 모든 후보 확인 후 실행 여부 최종 확인

### 커밋 메시지 형식

- `refactor: extract method [메서드명] from [클래스명]`
- `refactor: move domain logic [설명] to [대상 클래스]`

### PR 생성

- 대상: `refactor/<현재브랜치>` → `<현재브랜치>` (main이 아님)
- 제목: `refactor: system-wide refactoring for [대상 요약]`
- 본문: 적용된 기법별 커밋 목록 + 변경 전/후 요약
- 리뷰어가 Commits 탭에서 기법별 커밋을 개별 리뷰 가능
- 승인 후 squash merge → 원래 브랜치에 하나의 `refactor:` 커밋

## 영향 범위

| 파일 | 변경 유형 |
|------|-----------|
| `msbaek-tdd/agents/tdd-blue.md` | Modify — Tidying Process 범위 축소 |
| `msbaek-tdd/skills/tdd-tidy/SKILL.md` | Modify — 단계 목록 업데이트 |
| `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` | Create |
| `msbaek-tdd/.claude-plugin/plugin.json` | Modify — 버전 범프 |
