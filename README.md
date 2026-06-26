# msbaek-tdd — Claude Code TDD Plugin

Java/Spring Boot 프로젝트를 위한 TDD 워크플로우 Claude Code 플러그인입니다.

Kent Beck의 TDD 원칙을 기반으로, SRS 작성부터 Red-Green-Blue 사이클, Composed Method 지향 리팩토링까지 체계적인 테스트 주도 개발을 지원합니다.

| 플러그인 | 설명 | 버전 |
|----------|------|------|
| **msbaek-tdd** | Java + Spring Boot TDD workflow with RGB cycle, feature-level autonomous implementation, local tidying, system-wide refactoring, and 16 optional refactoring skills | 1.8.0 |

## 설치

### 방법 1: Claude Code CLI에서 직접 설치

```bash
# 1. Marketplace 등록
/plugin marketplace add msbaek/msbaek-claude-plugins

# 2. 플러그인 설치
/plugin install msbaek-tdd@msbaek-claude-plugins

# 3. 설치 확인
/plugin list
```

### 방법 2: 팀 프로젝트에 설정 (자동 설치)

프로젝트 루트의 `.claude/settings.json`에 아래 내용을 추가하면, 팀원이 해당 프로젝트에서 Claude Code를 실행할 때 자동으로 플러그인 설치 안내를 받습니다.

```json
{
  "extraKnownMarketplaces": {
    "msbaek-claude-plugins": {
      "source": {
        "source": "github",
        "repo": "msbaek/msbaek-claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "msbaek-tdd@msbaek-claude-plugins": true
  }
}
```

### 요구사항

- **Claude Code** CLI (최신 버전 권장)
- **Java 17+** / Spring Boot 3.x 프로젝트 (web-usecase 유형)
- **Gradle** 또는 **Maven** 빌드 시스템
- **커밋 표준 파일** — RGB 커밋이 참조하는 `reviewable-commits.md` 표준. 프로젝트 `docs/reviewable-commits.md` 또는 `~/.claude/docs/reviewable-commits.md` 중 하나에 두면 된다. 없으면 아래 ["커밋 표준"](#커밋-표준-reviewable-commits) 섹션의 전문을 복사해 생성하라.

## 사용법

### 핵심 워크플로우

#### `/tdd` — TDD 프로젝트 생성

TDD 프로젝트의 진입점입니다. 템플릿 문서와 테스트 클래스를 생성하고 진행 상태를 관리합니다.

```
/tdd general com.example.bowling.BowlingGame
/tdd web-usecase com.example.order.CreateOrder
```

| 유형 | 설명 | 단계 |
|------|------|------|
| `general` | 일반 TDD | SRS → 예제 → 테스트 목록 → RGB 사이클 (4단계) |
| `web-usecase` | Web Usecase TDD | SRS → 예제 → High Level Test → 테스트 목록 → Walking Skeleton → RGB 사이클 → HLT 활성화 → JPA → DSL (9단계) |

#### `/tdd-plan` — TDD 계획 수립

SRS, 예제, 테스트 케이스 목록을 순서대로 작성합니다.

```
/tdd-plan
```

**진행 단계:**
1. **SRS 작성** — 비즈니스 규칙, 요구사항 정의
2. **예제 작성** — Happy path, 경계 조건, 예외 상황 시나리오
3. **테스트 케이스 목록** — Degenerate → Simple → General 순서로 정렬
4. (web-usecase) **High Level Test** — End-to-end 테스트 작성
5. (web-usecase) **Walking Skeleton** — 전체 레이어 연결 골격 구현

#### `/tdd-rgb` — Red-Green-Blue 사이클

테스트 목록의 각 항목에 대해 RGB 사이클을 실행합니다.

```
/tdd-rgb
```

```
Red (실패하는 테스트 작성)
  ↓
Green (최소 구현으로 테스트 통과)
  ↓
Blue (Composed Method 지향 Local Tidying)
  ↓
[다음 테스트로 반복]
```

#### `/tdd-feature` — 간결 Plan → Feature 단위 자율 구현

`/tdd-plan`과 `/tdd-rgb`를 feature(use case) 단위로 묶은 상위 워크플로우입니다. 간결한 plan을 사용자와 합의한 뒤, **하나의 feature**를 RGB 사이클로 **끝까지 자율** 구현합니다.

```
/tdd-feature [feature 설명 또는 plan 경로]
```

- **Phase A (인터랙티브)**: 문제 정의 → 기능 분해 → 완료 조건(programmer test) 합의
- **Phase B (자율)**: 합의 후 그 feature의 모든 test에 대해 R→G→B를 피드백 없이 끝까지, 각 단계를 reviewable-commits 표준(Why-body)으로 분리 커밋
- **WIP = 1**: 한 번에 하나의 feature만. 남은 feature는 이어서 호출하거나 다른 세션에서.

> `/tdd-rgb`는 매 R/G/B 단계마다 피드백을 받지만, `/tdd-feature`는 plan 합의 후 feature를 끝까지 자율 진행합니다.

#### `/tdd-tidy` — 독립 Tidying

TDD 사이클 없이 git diff 기준 변경 파일을 자동 탐지하여 Composed Method 지향 Tidying Process를 실행합니다. 완료 후 적용 가능한 선택 리팩토링 기법을 제안합니다.

```
/tdd-tidy          # 최근 변경 파일 대상
/tdd-tidy HEAD~3   # 특정 커밋 기준
```

**Tidying Process:**

```
Guard Clauses → One Pile → Reorder → Normalize Symmetries
  → Chunk → Comment → Extract Variable → Split Loop → Trimming
```

> One Pile 적용 시 항상 별도 커밋(`refactor: one-pile [대상]`)으로 분리합니다.

#### `/system-wide-refactoring` — System-wide 리팩토링

코드를 분석하여 리팩토링 후보를 제시하고, 사용자 확인 후 별도 브랜치에서 기법별 커밋을 수행한 뒤 PR을 생성합니다.

```
/system-wide-refactoring          # 최근 변경 기준
/system-wide-refactoring HEAD~5   # 특정 커밋 기준
```

### 선택 리팩토링 스킬 (16개)

`/tdd-tidy`나 `/system-wide-refactoring` 완료 후 추가로 적용할 수 있는 개별 리팩토링 기법입니다.

#### Tidy 계열 — Local Tidying 확장 (8개)

| 스킬 | 설명 |
|------|------|
| `/decompose-conditional` | 복잡한 if/then/else의 조건식과 분기를 의미 있는 메서드로 추출 |
| `/consolidate-conditional` | 동일한 결과를 내는 여러 조건문을 하나로 통합하고 의미 있는 메서드로 추출 |
| `/replace-temp-with-query` | 임시 변수를 메서드 호출로 치환하여 중복 제거 및 가독성 향상 |
| `/extract-method-object` | 지역 변수가 얽힌 거대 메서드를 별도 클래스(Method Object)로 추출 |
| `/naming-process` | Arlo Belshee의 6단계 네이밍 프로세스로 코드 가독성 향상 |
| `/lift-up-conditional` | 여러 곳에 중복된 조건문을 상위로 끌어올려 중복 제거 |
| `/introduce-assertion` | 암묵적 가정을 Assert/Validate로 명시하여 가정 위반 시 즉시 발견 |
| `/replace-loop-with-pipeline` | 명령형 루프를 Stream API/Collection Pipeline으로 변환 |

#### System-wide 계열 — 구조적 리팩토링 (8개)

| 스킬 | 설명 |
|------|------|
| `/replace-conditional-with-poly` | 반복되는 switch/if-else 조건문을 다형성으로 치환 |
| `/discover-value-object` | Primitive Obsession 제거 — primitive 타입을 Value Object로 치환 |
| `/introduce-parameter-object` | 반복되는 파라미터 그룹을 객체로 치환 (Preserve Whole Object 포함) |
| `/first-class-collection` | 컬렉션과 관련 로직을 전용 클래스로 추출 |
| `/encapsulate-collection` | 컬렉션 getter의 내부 상태 노출 방지 (unmodifiable + add/remove) |
| `/separate-query-modifier` | 값 반환과 부수효과가 혼재된 메서드를 Query와 Modifier로 분리 (CQS) |
| `/explicit-parameters` | 암묵적 의존성(전역변수, 클래스 필드)을 명시적 파라미터로 전환 |
| `/introduce-special-case` | 반복되는 null 검사를 Special Case(Null Object) 클래스로 대체 |

## 워크플로우 예시

### General TDD — BowlingGame

```bash
# 1. 프로젝트 생성
/tdd general com.example.bowling.BowlingGame

# 2. SRS, 예제, 테스트 목록 작성
/tdd-plan

# 3. RGB 사이클로 구현
/tdd-rgb

# 4. (선택) 추가 리팩토링
/tdd-tidy
```

### Web Usecase TDD — CreateShoppingBasket

```bash
# 1. 프로젝트 생성
/tdd web-usecase com.example.basket.CreateShoppingBasket

# 2. SRS, 예제, High Level Test, 테스트 목록, Walking Skeleton 작성
/tdd-plan

# 3. RGB 사이클로 구현 + HLT 활성화 + JPA 전환 + DSL 개선
/tdd-rgb
```

### 기존 코드 리팩토링 (TDD 없이)

```bash
# 최근 변경된 Java 파일에 Tidying Process 적용
/tdd-tidy

# 제안된 기법 중 선택하여 추가 적용
/decompose-conditional
/discover-value-object

# 구조적 리팩토링이 필요하면
/system-wide-refactoring
```

## 아키텍처

### 디렉토리 구조

```
msbaek-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace 카탈로그
├── msbaek-tdd/                       # TDD 플러그인
│   ├── .claude-plugin/
│   │   └── plugin.json               # 플러그인 매니페스트 (v1.8.0)
│   ├── skills/
│   │   ├── tdd/                      # /tdd 오케스트레이터
│   │   ├── tdd-plan/                 # /tdd-plan 계획 수립
│   │   ├── tdd-rgb/                  # /tdd-rgb 사이클 조율 (step-wise)
│   │   ├── tdd-feature/              # /tdd-feature feature 단위 자율 구현
│   │   ├── tdd-tidy/                 # /tdd-tidy 독립 tidying
│   │   ├── system-wide-refactoring/  # /system-wide-refactoring
│   │   ├── decompose-conditional/    # Tidy 계열 (8개)
│   │   ├── consolidate-conditional/
│   │   ├── replace-temp-with-query/
│   │   ├── extract-method-object/
│   │   ├── naming-process/
│   │   ├── lift-up-conditional/
│   │   ├── introduce-assertion/
│   │   ├── replace-loop-with-pipeline/
│   │   ├── replace-conditional-with-poly/  # System-wide 계열 (8개)
│   │   ├── discover-value-object/
│   │   ├── introduce-parameter-object/
│   │   ├── first-class-collection/
│   │   ├── encapsulate-collection/
│   │   ├── separate-query-modifier/
│   │   ├── explicit-parameters/
│   │   └── introduce-special-case/
│   └── agents/
│       ├── tdd-red.md                # Red phase 전문 에이전트
│       ├── tdd-green.md              # Green phase 전문 에이전트
│       └── tdd-blue.md               # Blue phase 전문 에이전트
├── README.md
└── PUBLISHING-GUIDE.md               # Marketplace 배포 가이드
```

### Skills과 Agents 관계

```
/tdd (오케스트레이터)
 ├── 프로젝트 생성 및 상태 관리
 ├── /tdd-plan 안내
 └── /tdd-rgb 안내

/tdd-plan (계획 수립)
 ├── SRS 작성
 ├── 예제 작성
 └── 테스트 케이스 목록 작성

/tdd-rgb (사이클 조율, step-wise — 매 단계 피드백)
 ├── tdd-red agent   → 실패하는 테스트 작성
 ├── tdd-green agent → 최소 구현으로 통과
 └── tdd-blue agent  → Composed Method 지향 Local Tidying Process

/tdd-feature (feature 단위 자율 구현)
 ├── Phase A: 간결 plan 합의 (인터랙티브)
 └── Phase B: feature 끝까지 자율 (tdd-red/green/blue 재사용, reviewable 커밋)

/tdd-tidy (독립 tidying)
 ├── git diff로 변경 파일 자동 탐지
 ├── tdd-blue agent  → Local Tidying Process 독립 실행
 └── 완료 후 선택 리팩토링 기법 제안

/system-wide-refactoring (구조적 리팩토링)
 ├── 코드 분석 → 리팩토링 후보 제시
 ├── 별도 브랜치에서 기법별 커밋
 ├── PR 생성
 └── 완료 후 선택 리팩토링 기법 제안

선택 리팩토링 스킬 (16개)
 ├── Tidy 계열 (8개): decompose-conditional, consolidate-conditional,
 │   replace-temp-with-query, extract-method-object, naming-process,
 │   lift-up-conditional, introduce-assertion, replace-loop-with-pipeline
 └── System-wide 계열 (8개): replace-conditional-with-poly,
     discover-value-object, introduce-parameter-object, first-class-collection,
     encapsulate-collection, separate-query-modifier, explicit-parameters,
     introduce-special-case
```

### 전문 에이전트

| 에이전트 | 역할 | 핵심 원칙 |
|----------|------|-----------|
| **tdd-red** | 실패하는 테스트 작성 | TDD 1법칙: "Write NO production code except to pass a failing test" |
| **tdd-green** | 최소 구현으로 테스트 통과 | TPP (Transformation Priority Premise), Make-it-Work 전략 (Obvious / Fake it / Triangulation) |
| **tdd-blue** | Composed Method 지향 리팩토링 | Tidying Process: Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming |

## 핵심 원칙

- **Three Laws of TDD** — 실패하는 테스트 없이 프로덕션 코드를 작성하지 않음
- **Test Addition Rule** — Degenerate(특수)에서 General(일반)으로 점진적 진행
- **Programmer Test (FIRST)** — Fast, Isolated, Deterministic, Predictive, Specific
- **Micro Cycle** — 각 단계는 2-3분 이내, 빠른 피드백
- **사용자 피드백 대기** — 각 단계 완료 후 반드시 사용자 승인을 받고 다음 단계 진행

### Prompt Contracts

모든 Skill과 Agent 문서에 [Prompt Contracts](https://medium.com/@rentierdigital/i-stopped-vibe-coding-and-started-prompt-contracts-claude-code-went-from-gambling-to-shipping-4080ef23efac) 프레임워크의 4섹션 구조를 적용합니다:

| 섹션 | 역할 |
|------|------|
| **GOAL** | 성공 기준을 1분 내 검증 가능하게 정의 |
| **CONSTRAINTS** | Hard Rules(비협상 경계)와 Principles(설계 원칙) |
| **OUTPUT FORMAT** | 작업 절차, 워크플로우, 템플릿 |
| **FAILURE CONDITIONS** | "이것이 있으면 수용 불가" 목록 (가드레일) |

## 커밋 표준 (reviewable-commits)

이 플러그인의 RGB 커밋(`test:`/`feat:`/`refactor:`)은 **하나의 커밋 표준을 단일 출처(SSoT)로 참조**합니다. 스킬·에이전트는 형식을 재기술하지 않고 경로(`docs/reviewable-commits.md` → 없으면 `~/.claude/docs/reviewable-commits.md`)로만 가리키므로, 규칙이 바뀌어도 **표준 파일 1곳만** 고치면 됩니다.

**배포받은 분(distributee) 설치 방법**: 아직 자신의 커밋 표준이 없다면, 아래 전문을 `~/.claude/docs/reviewable-commits.md`(전역) 또는 프로젝트 `docs/reviewable-commits.md`(프로젝트별)에 저장하세요. 이미 자신의 표준이 있으면 같은 경로에 두기만 하면 이 플러그인이 그것을 사용합니다.

> 아래는 작성자(@msbaek)의 개인 `~/.claude/docs/reviewable-commits.md` **사본(snapshot)**입니다. 원본이 갱신되면 이 사본도 함께 갱신됩니다.

<details>
<summary><b>reviewable-commits.md 전문 펼치기</b></summary>

````markdown
# Reviewable Commits & PRs — 의도 전달 표준 (SSoT)

> `/commit`(forward·작은 단위), `reconstruct-commits`(backward·히스토리 교정),
> `/compose-pr`(PR 텍스트 종합) **세 도구가 공유하는 단일 body 표준**이다.

## 핵심 원칙 — Why를 박제하라

**메시지·PR은 What이 아니라 Why를 전달한다.**

- **What**(무엇을 바꿨나)은 diff가 이미 보여준다 → 메시지에서 반복하지 마라.
- 남길 것 셋:
  - **Why** — 이 변경이 왜 필요한가, 무엇을 해결하나.
  - **버린 대안** — 고려했으나 배제한 접근과 그 이유 (있을 때).
  - **결정 순서(추론)** — 어떤 이론·근거로 이 경로를 택했나.

### 같은 diff, 다른 Why — 의도 구분 예시

`null` 체크 한 줄은 두 경우에 What이 똑같이 보이지만 Why가 정반대다. 메시지에
의도를 안 남기면 리뷰어가 옳은지 판단할 수 없다.

```java
// "없음 = 예외" — 없으면 안 되는 상황
if (user == null) throw new UserNotFoundException(orderId);
// → FK로 보장되는 값이라 null은 데이터 무결성 위반 신호
```
```java
// "없음 = 값" — 없는 게 정상
if (avatar == null) avatar = Avatar.DEFAULT;
// → 아바타 부재는 정상 상태, null을 기본값으로 대체
```

## Acceptance Criterion (이 표준의 합격선)

> PR 텍스트 + "Files changed"만 가진 리뷰어가, 각 변경에 대해
> ⓐ 왜 했는지 ⓑ 무엇을 배제했는지 ⓒ 어떤 추론 순서로 도달했는지를 말할 수 있다.

## 커밋 메시지 형식

```
type(scope): subject (50자 이내, 한국어, 의도 표현 — 왜 우선)

<Why — 이 변경이 왜 필요한가 / 무엇을 해결하나. 72자 줄바꿈>
<버린 대안 — 배제한 접근과 그 이유 (있을 때만)>

[Decision-Log: 한 줄 요약]   # 선택 — 결정 로그 trailer
```

- type: `feat`/`fix`/`docs`/`style`/`refactor`/`test`/`chore`.
- body는 항목 수에 집착하지 말고 **Why가 복원되는 데 필요한 만큼**. 사소한 변경은 한 줄도 OK.
- **작은 단위 원칙**: 한 커밋 = 하나의 결정 + 그 검증.
- 한글 메시지는 **임시 파일 + `git commit -F`** (heredoc·`-m "한글"` 금지 — 깨짐).

## 4-Channel 모델 — 무엇을 어디에 남기나

| 채널 | 담는 것 | 안 담는 것 |
|------|---------|-----------|
| **테스트 코드** | 인수조건·엣지 케이스, "이 동작이 왜 중요한가" | 구현 상세 |
| **커밋 메시지** | 이 커밋 **한 개 결정**의 Why + 버린 대안 | 여러 결정 뭉치, What 나열 |
| **PR 메시지** | 커밋 내러티브 **종합** + 결정 로그 + 리뷰 가이드 | 커밋별 What 재나열 |
| **코드 주석** | 코드로 표현 못 하는 근거(왜 이 값·이 순서) | What 재진술 |
````

</details>

## 라이선스

MIT
