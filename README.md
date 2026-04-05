# msbaek-claude-plugins

Java/Spring Boot 프로젝트를 위한 TDD 워크플로우 Claude Code 플러그인 마켓플레이스입니다.

Kent Beck의 TDD 원칙을 기반으로, SRS 작성부터 Red-Green-Blue 사이클까지 체계적인 테스트 주도 개발을 지원합니다.

## 플러그인 목록

| 플러그인 | 설명 | 버전 |
|----------|------|------|
| **msbaek-tdd** | Java + Spring Boot TDD workflow plugin with RGB cycle, local tidying, system-wide refactoring, and 12 optional refactoring skills | 1.5.0 |

## 설치

### 1. Marketplace 추가

```
/plugin marketplace add msbaek/msbaek-claude-plugins
```

### 2. 플러그인 설치

```
/plugin install msbaek-tdd@msbaek-claude-plugins
```

### 3. 설치 확인

```
/plugin list
```

## 사용법

### `/tdd` - TDD 프로젝트 생성 및 관리

TDD 프로젝트의 진입점입니다. 템플릿 문서와 테스트 클래스를 생성하고, 진행 상태를 관리합니다.

```
/tdd general com.example.bowling.BowlingGame
/tdd web-usecase com.example.order.CreateOrder
```

**TDD 유형:**

| 유형 | 설명 | 단계 |
|------|------|------|
| `general` | 일반 TDD | SRS → 예제 → 테스트 목록 → RGB 사이클 (4단계) |
| `web-usecase` | Web Usecase TDD | SRS → 예제 → High Level Test → 테스트 목록 → Walking Skeleton → RGB 사이클 → HLT 활성화 → JPA → DSL (9단계) |

### `/tdd-plan` - TDD 계획 문서 작성

SRS, 예제, 테스트 케이스 목록을 순서대로 작성합니다.

```
/tdd-plan
```

**진행 단계:**
1. **SRS 작성** - 비즈니스 규칙, 요구사항 정의
2. **예제 작성** - Happy path, 경계 조건, 예외 상황 시나리오
3. **테스트 케이스 목록** - Degenerate → Simple → General 순서로 정렬
4. (web-usecase) **High Level Test** - End-to-end 테스트 작성
5. (web-usecase) **Walking Skeleton** - 전체 레이어 연결 골격 구현

### `/tdd-rgb` - Red-Green-Blue 사이클 실행

테스트 목록의 각 항목에 대해 RGB 사이클을 실행합니다.

```
/tdd-rgb
```

**사이클:**

```
Red (실패하는 테스트 작성)
  ↓
Green (최소 구현으로 테스트 통과)
  ↓
Blue (경량 리팩토링)
  ↓
[다음 테스트로 반복]
```

### `/tdd-tidy` - 독립 Tidying

TDD 사이클 없이 git diff 기준 변경 파일을 자동 탐지하여 Composed Method 지향 Tidying Process를 실행합니다. 완료 후 적용 가능한 선택 리팩토링 기법을 제안합니다.

```
/tdd-tidy          # 최근 변경 파일 대상
/tdd-tidy HEAD~3   # 특정 커밋 기준
```

### `/system-wide-refactoring` - System-wide 리팩토링

코드를 분석하여 리팩토링 후보를 제시하고, 사용자 확인 후 별도 브랜치에서 기법별 커밋을 수행한 뒤 PR을 생성합니다.

```
/system-wide-refactoring          # 최근 변경 기준
/system-wide-refactoring HEAD~5   # 특정 커밋 기준
```

### 선택 리팩토링 스킬 (12개)

`/tdd-tidy`나 `/system-wide-refactoring` 완료 후 추가로 적용할 수 있는 개별 리팩토링 기법입니다.

#### Tidy 계열 (Local Tidying 확장)

| 스킬 | 설명 |
|------|------|
| `/replace-temp-with-query` | 임시 변수를 메서드 호출로 치환하여 중복 제거 및 가독성 향상 |
| `/decompose-conditional` | 복잡한 if/then/else의 조건식과 분기를 의미 있는 메서드로 추출 |
| `/extract-method-object` | 지역 변수가 얽힌 거대 메서드를 별도 클래스(Method Object)로 추출 |
| `/naming-process` | Arlo Belshee의 6단계 네이밍 프로세스로 코드 가독성 향상 |
| `/lift-up-conditional` | 여러 곳에 중복된 조건문을 상위로 끌어올려 중복 제거 |

#### System-wide 계열 (구조적 리팩토링)

| 스킬 | 설명 |
|------|------|
| `/replace-conditional-with-poly` | 반복되는 switch/if-else 조건문을 다형성으로 치환 |
| `/discover-value-object` | Primitive Obsession 제거 — primitive 타입을 Value Object로 치환 |
| `/introduce-parameter-object` | 반복되는 파라미터 그룹을 객체로 치환하여 Value Object 발견 |
| `/first-class-collection` | 컬렉션과 관련 로직을 전용 클래스로 추출 |
| `/encapsulate-collection` | 컬렉션 getter의 내부 상태 노출 방지 (unmodifiable + add/remove) |
| `/separate-query-modifier` | 값 반환과 부수효과가 혼재된 메서드를 Query와 Modifier로 분리 (CQS) |
| `/explicit-parameters` | 암묵적 의존성(전역변수, 클래스 필드)을 명시적 파라미터로 전환 |

## 아키텍처

### 디렉토리 구조

```
msbaek-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace 카탈로그
├── msbaek-tdd/                       # TDD 플러그인
│   ├── .claude-plugin/
│   │   └── plugin.json               # 플러그인 매니페스트 (v1.5.0)
│   ├── skills/
│   │   ├── tdd/SKILL.md              # /tdd 오케스트레이터
│   │   ├── tdd-plan/SKILL.md         # /tdd-plan 계획 수립
│   │   ├── tdd-rgb/SKILL.md          # /tdd-rgb 사이클 조율
│   │   ├── tdd-tidy/SKILL.md         # /tdd-tidy 독립 tidying
│   │   ├── system-wide-refactoring/  # /system-wide-refactoring
│   │   ├── replace-temp-with-query/  # Tidy 계열 선택 스킬
│   │   ├── decompose-conditional/
│   │   ├── extract-method-object/
│   │   ├── naming-process/
│   │   ├── lift-up-conditional/
│   │   ├── replace-conditional-with-poly/  # System-wide 계열 선택 스킬
│   │   ├── discover-value-object/
│   │   ├── introduce-parameter-object/
│   │   ├── first-class-collection/
│   │   ├── encapsulate-collection/
│   │   ├── separate-query-modifier/
│   │   └── explicit-parameters/
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

/tdd-rgb (사이클 조율)
 ├── tdd-red agent   → 실패하는 테스트 작성
 ├── tdd-green agent → 최소 구현으로 통과
 └── tdd-blue agent  → Composed Method 지향 Local Tidying Process

/tdd-tidy (독립 tidying)
 ├── git diff로 변경 파일 자동 탐지
 ├── tdd-blue agent  → Local Tidying Process 독립 실행
 └── 완료 후 선택 리팩토링 기법 제안

/system-wide-refactoring (구조적 리팩토링)
 ├── 코드 분석 → 리팩토링 후보 제시
 ├── 별도 브랜치에서 기법별 커밋
 ├── PR 생성
 └── 완료 후 선택 리팩토링 기법 제안

선택 리팩토링 스킬 (12개)
 ├── Tidy 계열 (5개): replace-temp-with-query, decompose-conditional,
 │   extract-method-object, naming-process, lift-up-conditional
 └── System-wide 계열 (7개): replace-conditional-with-poly,
     discover-value-object, introduce-parameter-object, first-class-collection,
     encapsulate-collection, separate-query-modifier, explicit-parameters
```

### 전문 에이전트

| 에이전트 | 역할 | 핵심 원칙 |
|----------|------|-----------|
| **tdd-red** | 실패하는 테스트 작성 | TDD 1법칙: "Write NO production code except to pass a failing test" |
| **tdd-green** | 최소 구현으로 테스트 통과 | TPP (Transformation Priority Premise), Make-it-Work 전략 (Obvious / Fake it / Triangulation) |
| **tdd-blue** | Composed Method 지향 리팩토링 | Tidying Process: Guard Clauses → One Pile → Reorder → Normalize Symmetries → Chunk → Comment → Extract Variable → Split Loop → Trimming |

## 워크플로우 예시

### General TDD (BowlingGame)

```
# 1. 프로젝트 생성
/tdd general com.example.bowling.BowlingGame

# 2. SRS, 예제, 테스트 목록 작성
/tdd-plan

# 3. RGB 사이클로 구현
/tdd-rgb
```

### Web Usecase TDD (CreateShoppingBasket)

```
# 1. 프로젝트 생성
/tdd web-usecase com.example.basket.CreateShoppingBasket

# 2. SRS, 예제, High Level Test, 테스트 목록, Walking Skeleton 작성
/tdd-plan

# 3. RGB 사이클로 구현 + HLT 활성화 + JPA 전환 + DSL 개선
/tdd-rgb
```

## 핵심 원칙

- **Three Laws of TDD** - 실패하는 테스트 없이 프로덕션 코드를 작성하지 않음
- **Test Addition Rule** - Degenerate(특수)에서 General(일반)으로 점진적 진행
- **Programmer Test (FIRST)** - Fast, Isolated, Deterministic, Predictive, Specific
- **Micro Cycle** - 각 단계는 2-3분 이내, 빠른 피드백
- **사용자 피드백 대기** - 각 단계 완료 후 반드시 사용자 승인을 받고 다음 단계 진행

### Prompt Contracts

모든 Skill과 Agent 문서에 [Prompt Contracts](https://medium.com/@rentierdigital/i-stopped-vibe-coding-and-started-prompt-contracts-claude-code-went-from-gambling-to-shipping-4080ef23efac) 프레임워크의 4섹션 구조를 적용합니다:

| 섹션 | 역할 |
|------|------|
| **GOAL** | 성공 기준을 1분 내 검증 가능하게 정의 |
| **CONSTRAINTS** | Hard Rules(비협상 경계)와 Principles(설계 원칙) |
| **OUTPUT FORMAT** | 작업 절차, 워크플로우, 템플릿 |
| **FAILURE CONDITIONS** | "이것이 있으면 수용 불가" 목록 (가드레일) |

## 팀 프로젝트에 적용

프로젝트의 `.claude/settings.json`에 추가하면 팀원이 자동으로 설치 안내를 받습니다:

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

## 요구사항

- Claude Code CLI
- Java 17+ / Spring Boot 3.x 프로젝트 (web-usecase 유형)
- Gradle 또는 Maven 빌드 시스템

## 라이선스

MIT
