# msbaek-tdd — Claude Code TDD Plugin

Java/Spring Boot 프로젝트를 위한 TDD 워크플로우 Claude Code 플러그인입니다.

Kent Beck의 TDD 원칙을 기반으로, 요구사항(도메인 규칙 + User Story) 작성부터 Gherkin Scenario, Red-Green-Blue 사이클, Cucumber 인수 테스트, Composed Method 지향 리팩토링까지 체계적인 테스트 주도 개발을 지원합니다.

| 플러그인 | 설명 | 버전 |
|----------|------|------|
| **msbaek-tdd** | Java + Spring Boot TDD workflow with RGB cycle, gear-based review density, feature-level autonomous implementation, Cucumber acceptance testing, legacy-code safety net, local tidying, system-wide refactoring, and 18 optional refactoring skills | 1.20.0 |

> **[전체 워크플로우 지도 (시각화) →](https://msbaek.github.io/talk-visuals/msbaek-tdd-workflow/)**
> `/tdd` 진입부터 계획·구현 파이프라인, 기어별 스킬 라우팅, 독립 진입점까지 한 장으로.

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
- **Java 17+** / Spring Boot 3.x 프로젝트 (web-app 유형)
- **Gradle** 또는 **Maven** 빌드 시스템
- **커밋 표준 파일** — RGB 커밋이 참조하는 `reviewable-commits.md` 표준. 프로젝트 `docs/reviewable-commits.md` 또는 `~/.claude/docs/reviewable-commits.md` 중 하나에 두면 된다. 없으면 아래 ["커밋 표준"](#커밋-표준-reviewable-commits) 섹션의 전문을 복사해 생성하라.

## 두 가지 사용 방식

이 플러그인은 **명시적 호출**과 **암묵적 적용** 두 가지로 쓸 수 있습니다. 숙련도에 따라 골라 쓰거나 섞어 쓰면 됩니다.

| 방식 | 어떻게 | 누구에게 |
|------|--------|----------|
| **명시적 호출** | `/tdd-plan`, `/tdd-rgb --gear=low`처럼 슬래시 커맨드로 직접 지정 | TDD·Java가 아직 낯선 개발자 |
| **암묵적 적용** | 설치만 해두면, 작업이 스킬에 맞을 때 Claude가 알아서 해당 스킬을 적용 | TDD·Java에 익숙한 개발자 |

### 초보자 — 조금 느리더라도 명시적으로

TDD가 익숙하지 않다면 슬래시 커맨드로 **명시적으로 호출**하는 편이 낫습니다. 단계를 건너뛰지 않게 강제되고, 각 단계에서 무엇을 왜 하는지 스킬 문서가 안내하기 때문입니다.

```bash
/tdd general com.example.bowling.BowlingGame   # 1. 프로젝트 생성
/tdd-plan                                       # 2. 요구사항 → Gherkin → test 목록
/tdd-rgb --gear=low                             # 3. 매 단계(R/G/B)마다 검토
```

- `low` 기어를 쓰면 Red·Green·Blue 각 단계 후 멈춰서 확인할 수 있습니다 — 느리지만 TDD 리듬이 몸에 익습니다
- 한 단계씩 눈으로 확인하면서 "실패하는 테스트 → 최소 구현 → 정리"의 순서가 왜 중요한지 체감하게 됩니다

> 각 커맨드의 상세 옵션은 [사용법](#사용법), 유형별 전체 흐름은 [워크플로우 예시](#워크플로우-예시)를 참고하세요.

### 숙련자 — 설치만 해도 이득

Java·TDD에 익숙하다면 매번 커맨드를 칠 필요가 없습니다. **설치만 해두면** Claude가 작업 맥락을 보고 적합한 스킬을 스스로 적용합니다.

- "테스트 없는 이 레거시 클래스 손보려는데" → `/tdd-legacy`의 안전망 절차(Characterization → Approval → Mutation)
- "이 긴 메서드 이름이 하는 일을 안 드러낸다" → `/intent-revealing-names`의 이름 주도 관통 리팩토링
- "인수 테스트 도입하고 싶다" → `/cucumber-acceptance`의 Four Layer 구축
- "이 기능 TDD로 끝까지 구현해줘" → `/tdd-feature`의 plan 합의 → 자율 RGB

즉, 평소처럼 자연어로 요청해도 검증된 절차와 커밋 규율이 따라옵니다.

> **단, 자동 적용의 범위**: 핵심 워크플로우 스킬은 위처럼 자연어 요청에서 발동하지만, [선택 리팩토링 스킬 18개](#선택-리팩토링-스킬-18개)는 대부분 커맨드로 **명시 호출**해야 확실합니다(`/decompose-conditional`, `/discover-value-object` 등). 특정 기법을 태우고 싶다면 이름을 직접 부르세요.

## 사용법

### 핵심 워크플로우

#### `/tdd` — TDD 프로젝트 생성

TDD 프로젝트의 진입점입니다. 템플릿 문서와 테스트 클래스를 생성하고 진행 상태를 관리합니다.

```
/tdd general com.example.bowling.BowlingGame
/tdd web-app com.example.order.CreateOrder
```

| 유형 | 설명 | 단계 |
|------|------|------|
| `general` | 일반 TDD | 요구사항 → Gherkin Scenario → Unit Test 목록 → RGB 사이클 (4단계) |
| `web-app` | Web App TDD | 요구사항 → Gherkin Scenario → 인수 테스트 셋업(.feature) → Unit Test 목록 → Walking Skeleton → RGB 사이클 → JPA 완성 → DSL (8단계) |

#### `/tdd-plan` — TDD 계획 수립

요구사항, Gherkin Scenario, unit test 목록을 순서대로 작성합니다.

```
/tdd-plan
```

**진행 단계:**
1. **요구사항 작성** — 도메인 규칙(0층) + User Story
2. **Gherkin Scenario 작성** — Happy path, 경계 조건, 예외 상황을 예제로 (Cucumber 병행 시 실행 가능한 명세가 됨)
3. **Unit Test 목록** — Degenerate → Simple → General 순서로 정렬 (Gherkin 병행 시 세밀 분기만)
4. (조건부) **Use Case 추가** — 복잡도가 흐름·상태에 있을 때만
5. (web-app) **인수 테스트 셋업** — Gherkin을 `.feature` + Runner로 (미구현은 `@pending`)
6. (web-app) **Walking Skeleton** — 진짜 DB(docker MySQL)까지 관통하는 최소 골격 구현

#### `/cucumber-acceptance` — Cucumber 인수 테스트 (주 검증층)

기능의 external behavior를 Cucumber 인수 테스트로 구축합니다. `.feature` 실행으로 문서↔코드 드리프트를 구조적으로 차단합니다.

```
/cucumber-acceptance
```

- **Four Layer 축소형**: Steps → Protocol Driver → SUT
- **타입 경계**: 도메인 타입 ≠ DTO 타입
- **태그 기반 가역 제외** — 미구현 시나리오를 태그로 제외했다가 구현 후 복원
- 기존 JUnit 인수 테스트의 이관도 지원
- 도입 시점: 프로젝트 시작 시 또는 나중에 (tdd-plan의 Gherkin Scenario를 실행 가능한 명세로 승격)

#### `/tdd-rgb` — Red-Green-Blue 사이클

테스트 목록의 각 항목에 대해 RGB 사이클을 실행합니다.

```
/tdd-rgb [--gear=low|mid|high]
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

**기어(Gears) — 검토 밀도 조절** (Kent Beck의 "driving in gears")

이론에 대한 확신에 따라 사용자 검토 지점의 밀도를 조절합니다. 기어는 검토 지점의 밀도만 바꾸며, TDD 3법칙·phase별 커밋 등 나머지 규칙은 모든 기어에서 동일합니다.

| 기어 | 검토 지점 | 대응 상황 |
|------|-----------|-----------|
| `low` (기본) | Red 후 · Green 후 · Blue 후 | 확신 없음, 낯선 도메인, 학습 목적 |
| `mid` | 테스트 1개의 R→G→B 완료 후 1회 | 유사 문제 경험, 이론을 빠르게 확보할 것으로 기대 |
| `high` | 전체 목록 완료 + 적대적 리뷰 통과 후 1회 | 이론이 상용구(boilerplate) 수준 |

- 사이클 사이에 신호(설계 안정·지루함 ↔ revert·불투명)를 점검해 기어 전환을 **제안**합니다 — 결정은 항상 사용자
- 인증·결제 등 폭발 반경(blast radius)이 큰 영역에서는 한 단 낮은 기어를 권장합니다
- `high` 기어는 완료 후 적대적 리뷰(adversarial review)가 의무 — green 스위트 + 리뷰 통과가 Definition of Done
- 기어 상태는 템플릿 문서 진행 기록에 남아 세션 재개 시 복원됩니다 (`--gear` 생략 시 복원, 명시하면 우선)

**기어별 호출 — 어떤 스킬을 쓰나**

| 상황 | 기어 | 호출 |
|------|------|------|
| 낯선 도메인·학습 목적 | `low` | `/tdd-rgb --gear=low` |
| 유사 경험 있음, 설계 안정화 중 | `mid` | `/tdd-rgb --gear=mid` |
| 이론 명확, **테스트 목록 전체** 자율 | `high` | `/tdd-rgb --gear=high` |
| 이론 명확, **feature 하나** plan 합의 후 자율 | `high` | `/tdd-feature` |

#### `/tdd-feature` — 간결 Plan → Feature 단위 자율 구현

`/tdd-plan`과 `/tdd-rgb`를 feature(use case) 단위로 묶은 상위 워크플로우입니다. 간결한 plan을 사용자와 합의한 뒤, **하나의 feature**를 RGB 사이클로 **끝까지 자율** 구현합니다.

```
/tdd-feature [feature 설명 또는 plan 경로]
```

- **Phase A (인터랙티브)**: 문제 정의 → 기능 분해 → 완료 조건(programmer test) 합의
- **Phase B (자율)**: 합의 후 그 feature의 모든 test에 대해 R→G→B를 피드백 없이 끝까지, 각 단계를 reviewable-commits 표준(Why-body)으로 분리 커밋
- **WIP = 1**: 한 번에 하나의 feature만. 남은 feature는 이어서 호출하거나 다른 세션에서.

> `/tdd-rgb`는 기어가 정한 검토 지점에서 피드백을 받지만, `/tdd-feature`는 plan 합의 후 feature를 끝까지 자율 진행합니다.

**기어 위치**: `/tdd-feature`는 `--gear`를 받지 않습니다 — Phase B 자율 진행이 곧 **feature 범위의 high 기어**이기 때문입니다. 따라서 high의 안전장치를 동일하게 적용합니다: 시작 전 폭발 반경 점검, 시작 커밋 해시 기록, 완료 보고 전 적대적 리뷰. low·mid 검토 밀도가 필요하면 `/tdd-feature` 대신 `/tdd-rgb --gear=low|mid`를 사용하세요.

#### `/tdd-legacy` — 레거시 코드 안전망 구축

테스트 없는 기존 코드의 현재 행위를 고정하는 안전망을 만들고, 개선은 기존 스킬로 넘깁니다.

```
/tdd-legacy <대상 클래스 FQCN 또는 파일 경로>
```

- **1단계 Characterization** — golden master로 현재 행위 고정, SUT sabotage로 어설션 검증, scrubber로 비결정 출력 정규화
- **2단계 Approval** — 조합 폭발 구간은 CombinationApprovals로 확장 (unit vs approval은 설계 품질 트레이드오프)
- **3단계 Mutation 검증** — mutate4java(있으면) 또는 PIT로 안전망 실효성 확인
- 완료 후 `/tdd-tidy`·`/system-wide-refactoring`으로 핸드오프 (개선은 범위 밖)

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

### 선택 리팩토링 스킬 (18개)

`/tdd-tidy`나 `/system-wide-refactoring` 완료 후 추가로 적용할 수 있는 개별 리팩토링 기법입니다.

#### Tidy 계열 — Local Tidying 확장 (9개)

| 스킬 | 설명 |
|------|------|
| `/decompose-conditional` | 복잡한 if/then/else의 조건식과 분기를 의미 있는 메서드로 추출 |
| `/consolidate-conditional` | 동일한 결과를 내는 여러 조건문을 하나로 통합하고 의미 있는 메서드로 추출 |
| `/replace-temp-with-query` | 임시 변수를 메서드 호출로 치환하여 중복 제거 및 가독성 향상 |
| `/extract-method-object` | 지역 변수가 얽힌 거대 메서드를 별도 클래스(Method Object)로 추출 |
| `/naming-process` | Arlo Belshee의 6단계 네이밍 프로세스로 코드 가독성 향상 |
| `/intent-revealing-names` | 긴 메서드 하나를 grouping·comment로 정돈해 책임을 드러낸 뒤, 6단계 네이밍으로 extract를 유도하며 관통 리팩토링 |
| `/lift-up-conditional` | 여러 곳에 중복된 조건문을 상위로 끌어올려 중복 제거 |
| `/introduce-assertion` | 암묵적 가정을 Assert/Validate로 명시하여 가정 위반 시 즉시 발견 |
| `/replace-loop-with-pipeline` | 명령형 루프를 Stream API/Collection Pipeline으로 변환 |

#### System-wide 계열 — 구조적 리팩토링 (9개)

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
| `/segregate-functional-core` | 순수 비즈니스 로직(Functional Core)과 부수효과(Imperative Shell)를 분리 |

## 워크플로우 예시

### General TDD — BowlingGame

```bash
# 1. 프로젝트 생성
/tdd general com.example.bowling.BowlingGame

# 2. 요구사항, Gherkin Scenario, unit test 목록 작성
/tdd-plan

# 3. RGB 사이클로 구현
/tdd-rgb

# 4. (선택) 추가 리팩토링
/tdd-tidy
```

### Web App TDD — CreateShoppingBasket

```bash
# 1. 프로젝트 생성
/tdd web-app com.example.basket.CreateShoppingBasket

# 2. 요구사항, Gherkin Scenario, 인수 테스트 셋업, unit test 목록, Walking Skeleton 작성
/tdd-plan

# 3. RGB 사이클로 구현 (각 Green이 @pending 해제) + JPA 완성 + DSL 개선
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
│   │   └── plugin.json               # 플러그인 매니페스트
│   ├── skills/
│   │   ├── tdd/                      # /tdd 오케스트레이터
│   │   ├── tdd-plan/                 # /tdd-plan 계획 수립
│   │   ├── tdd-rgb/                  # /tdd-rgb 사이클 조율 (step-wise)
│   │   ├── tdd-feature/              # /tdd-feature feature 단위 자율 구현
│   │   ├── cucumber-acceptance/      # /cucumber-acceptance 인수 테스트 구축
│   │   ├── tdd-legacy/               # /tdd-legacy 레거시 안전망 구축
│   │   ├── tdd-tidy/                 # /tdd-tidy 독립 tidying
│   │   ├── system-wide-refactoring/  # /system-wide-refactoring
│   │   ├── decompose-conditional/    # Tidy 계열 (9개)
│   │   ├── consolidate-conditional/
│   │   ├── replace-temp-with-query/
│   │   ├── extract-method-object/
│   │   ├── naming-process/
│   │   ├── intent-revealing-names/
│   │   ├── lift-up-conditional/
│   │   ├── introduce-assertion/
│   │   ├── replace-loop-with-pipeline/
│   │   ├── replace-conditional-with-poly/  # System-wide 계열 (9개)
│   │   ├── discover-value-object/
│   │   ├── introduce-parameter-object/
│   │   ├── first-class-collection/
│   │   ├── encapsulate-collection/
│   │   ├── separate-query-modifier/
│   │   ├── explicit-parameters/
│   │   ├── introduce-special-case/
│   │   └── segregate-functional-core/
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
 ├── 요구사항 작성 — 도메인 규칙(0층) + User Story
 ├── Gherkin Scenario 작성 (예제)
 ├── Unit Test 목록 작성
 └── (조건부) Use Case 추가

/cucumber-acceptance (인수 테스트 구축)
 ├── .feature를 실행 가능한 명세로 (주 검증층)
 ├── Steps → Protocol Driver → SUT (Four Layer 축소형)
 └── 태그 기반 가역 제외, 기존 JUnit 인수 테스트 이관

/tdd-legacy (레거시 안전망)
 ├── Characterization (sabotage 검증 + scrubber)
 ├── Approval (CombinationApprovals)
 └── Mutation 검증 (mutate4java/PIT) → tdd-tidy·system-wide-refactoring 핸드오프

/tdd-rgb (사이클 조율 — 기어가 검토 밀도 결정, 기본 low = 매 단계 피드백)
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

선택 리팩토링 스킬 (18개)
 ├── Tidy 계열 (9개): decompose-conditional, consolidate-conditional,
 │   replace-temp-with-query, extract-method-object, naming-process,
 │   intent-revealing-names, lift-up-conditional, introduce-assertion,
 │   replace-loop-with-pipeline
 └── System-wide 계열 (9개): replace-conditional-with-poly,
     discover-value-object, introduce-parameter-object, first-class-collection,
     encapsulate-collection, separate-query-modifier, explicit-parameters,
     introduce-special-case, segregate-functional-core
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
- **사용자 피드백 대기** — 기어가 정의하는 검토 지점에서 반드시 사용자 승인을 받고 진행 (기본 low 기어 = 각 단계 완료 후)

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
