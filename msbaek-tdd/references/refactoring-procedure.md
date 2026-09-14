# 리팩토링 스킬 공통 절차 (정본)

> 이 플러그인의 리팩토링 기법 스킬 전부에 적용된다.
> 각 스킬은 **"무엇을 찾는가"(2단계)** 와 **"어떻게 바꾸는가"(4단계)** 만 자기 SKILL.md에
> 규정하고, 나머지 단계는 이 문서를 따른다. 스킬 문서가 이 문서와 어긋나면 이 문서가 정본이다.

## 0. 계열 — 승인 방식이 다르다

| 계열 | 스킬 | 승인 |
|---|---|---|
| Tidy (Local Tidying 확장) | decompose-conditional, consolidate-conditional, replace-temp-with-query, extract-method-object, naming-process, intent-revealing-names, lift-up-conditional, introduce-assertion, replace-loop-with-pipeline | **승인 없이 적용** — 후보를 보고하고 즉시 적용, 기법별 커밋으로 남긴다. 사용자는 커밋 diff로 검토하고 필요하면 되돌린다 |
| System-wide (구조적 리팩토링) | replace-conditional-with-poly, discover-value-object, introduce-parameter-object, first-class-collection, encapsulate-collection, separate-query-modifier, explicit-parameters, introduce-special-case, segregate-functional-core | **승인 후 적용** — 후보를 하나씩 제시하고 yes/no/수정 확인을 받는다 |

Tidy 계열은 동작·구조 경계를 바꾸지 않는 메서드 내부 정돈이라 되돌리기 비용이 낮다.
System-wide 계열은 클래스 경계·타입·시그니처를 바꿔 호출부에 파급되므로 사전 승인이 필요하다.

## 1. 대상 파일 수집

인자로 commit ref가 오면 그것과 비교하고, 없으면 현재 변경(unstaged + staged)을 대상으로 한다.

```bash
# 인자 없음: unstaged + staged 변경 파일
git diff --name-only -- '*.java'
git diff --cached --name-only -- '*.java'

# 인자 있음: 특정 commit과 비교
git diff --name-only <commit-ref> -- '*.java'
```

- 테스트 파일(`*Test.java`, `*Tests.java`, `*Spec.java`)은 **제외**한다
- 대상이 없으면 "리팩토링 대상 Java 파일이 없습니다."를 안내하고 종료한다 — 대상을
  넓히려고 변경되지 않은 검토하지 않는다

## 2. 후보 식별 — 각 스킬이 규정한다

기법마다 찾는 패턴이 다르다. 해당 스킬 SKILL.md의 "후보 식별" 절을 따른다.

## 3. 후보 제시와 승인

계열(§0)에 따라 두 모드 중 하나를 따른다.

### 3-A. Tidy 계열 — 보고 후 즉시 적용

후보 목록을 아래 형식으로 보고한 뒤 **확인을 기다리지 않고** 4단계로 진행한다.

```
발견된 후보 N개 (승인 없이 적용 — Tidy 계열):

1. OrderService.java:45-58  [기법명] → 제안 변경 한 줄
2. ...
```

- 후보가 0개면 "후보 없음"을 보고하고 종료한다.
- 사용자가 특정 후보를 제외하고 싶으면 커밋 후 되돌린다(6단계). 사전 필터를 원하면
  `[commit-ref]` 인자로 대상 범위를 좁힌다.

### 3-B. System-wide 계열 — 승인 후 적용

후보를 하나씩 제시하고 사용자 확인을 받는다.

```
## 리팩토링 후보 N: [기법명]

**파일**: OrderService.java
**대상**: processOrder() 메서드 (45줄)

**현재 코드**:
[해당 코드 블록]

**제안 변경**:
- [무엇을 어떻게 바꾸는가 — 항목별로]

**적용할까요?** (yes / no / 수정 요청)
```

- **yes** → 실행 목록에 추가
- **no** → 스킵
- **수정 요청** → 요청을 반영해 재제시

모든 후보를 확인한 뒤 최종 실행 목록을 보여주고 진행 여부를 확인한다.
**승인 없이 적용하지 않는다** — 후보가 하나뿐이거나 자명해 보여도 마찬가지다(System-wide 계열 한정).

예외: `intent-revealing-names`는 Tidy 계열이지만 관통형(grouping→extract→rename)이라 5·6단계 진입 시 사용자 합의를 유지한다.

## 4. 리팩토링 적용 — 각 스킬이 규정한다

기법마다 변환 절차가 다르다. 해당 스킬 SKILL.md의 "리팩토링 적용" 절을 따른다.
공통 제약: **동작을 바꾸지 않는다. 테스트를 고치지 않는다.** 구조 변경이 테스트를
깨뜨리면 그 변경이 틀린 것이므로 되돌린다.

## 5. 테스트 실행

```bash
./gradlew test    # 또는 mvn test
```

## 6. 커밋 또는 되돌리기

- **1파일 × 1기법 = 1커밋** (논리적으로 분리할 수 없는 파일은 함께)
- 변경된 파일만 명시적으로 추가한다 — **`git add -A` 금지**
- 커밋 메시지는 `refactor:` 접두사. body는 `commit-style.md`(간결성)와
  `reviewable-commits.md`(Why·버린 대안) 정본을 따른다 — 여기서 재기술하지 않는다
- 한글 커밋 메시지는 **임시 파일 + `git commit -F <파일>`** 로 만든다. heredoc은 한글이
  실패할 수 있어 쓰지 않는다

```bash
# 테스트 통과 시
git add <변경된파일.java>
git commit -F <임시파일>   # subject: refactor: ...

# 테스트 실패 시 — 그 리팩토링만 되돌리고 사유를 알린 뒤 다음 후보로 진행
git checkout -- <변경된파일.java>
```

## 브랜치와 PR — 기본은 만들지 않는다

리팩토링은 현재 브랜치에 작은 커밋으로 누적한다.

**아래 중 하나라도 해당하면** 별도 브랜치에서 작업하고 PR을 만든다:

- 영향 범위(blast radius)(인증·인가, 결제·금액 계산, 데이터 삭제·변경, 외부 API, 동시성)
- 한 기법이 여러 파일의 공개 API를 동시에 바꾼다
- 리뷰어의 확인을 받고 합치기로 팀이 정한 변경이다

```bash
CURRENT_BRANCH=$(git branch --show-current)
git checkout -b "refactor/${CURRENT_BRANCH}"
# ... 기법별 커밋 ...
gh pr create --base "${CURRENT_BRANCH}" --title "refactor: ..." --body-file <파일>
git checkout "${CURRENT_BRANCH}"
```

PR 본문은 `docs/reviewable-commits.md`(없으면 `${CLAUDE_PLUGIN_ROOT}/references/reviewable-commits.md`)
표준을 따른다. 본문에 한글이 들어가면 heredoc 대신 `--body-file`을 쓴다.
PR의 base는 **원래 작업 브랜치**다 — main으로 직접 열지 않는다.

## 결과 보고

적용한 기법·파일·테스트 결과를 요약한다. 리팩토링 중에 발견했지만 이번 범위에 넣지
않은 개선 기회가 있으면 해당 스킬을 함께 제안한다(예: `/extract-method-object` —
상호 의존해 … 불가능함).

## 공통 FAILURE CONDITIONS

각 스킬의 FAILURE CONDITIONS에 아래가 이미 포함된 것으로 본다. 스킬 문서에는 그
기법에 고유한 실패만 적는다.

- 계열별 승인 규칙 위반 — System-wide 계열을 승인 없이 적용하거나, Tidy 계열에서 승인을 요구해 흐름을 멈춤
- 동작이 바뀌어 테스트가 실패함 (되돌리지 않음)
- 테스트를 고쳐서 통과시킴
- 기법별로 나누지 않고 한꺼번에 커밋함
- `git add -A`로 전체 파일을 추가함
- heredoc으로 한글 커밋 메시지를 만듦
- (PR을 만든 경우) main 브랜치로 직접 PR을 염
