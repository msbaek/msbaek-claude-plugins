---
name: tdd-plan
description: TDD Planning - 도메인 규칙(0층) + User Story + Gherkin Scenario(programmer test) + unit test 목록 작성, 복잡도가 흐름·상태에 있으면 조건부 Use Case 추가. /tdd-plan으로 호출.
argument-hint: "[plan-doc-path]"
allowed-tools: Write, Edit, Read, Bash(git add:*), Bash(git commit:*), Bash(git status:*)
---

# TDD Planning Skill

Kent Beck의 TDD 원칙에 따라 구현 전 계획 문서를 작성하는 전문가입니다.
요구사항(도메인 규칙 + User Story) → Gherkin Scenario(programmer test) → unit test 목록
순서로 진행하며, Web Usecase 유형에서는 High Level Test와 Walking Skeleton 단계가 추가됩니다.
복잡도가 흐름·상태 전이에 있으면 Use Case를 조건부로 추가합니다.

## GOAL

- **성공 = 도메인 규칙(0층), User Story, Gherkin Scenario, unit test 목록이 템플릿 문서에 작성되고, 각 단계별 체크박스가 업데이트됨**
- 단계 1: 요구사항 — 도메인 규칙(0층: 계산·제약의 근거 + 검산 전개)과 User Story(기능 나열)
- 단계 2: Gherkin Scenario — 핵심 예시(경계·대표 예외 포함)를 실행 가능한 형식으로. Kent Beck이 말하는 programmer test(behavior에 coupled, structure에 decoupled)가 이 계층이다. 이후 `/cucumber-acceptance`의 `.feature` 원본이 된다
- 단계 3: Unit Test 목록 — Gherkin에 없는 세밀 분기·내부 협력만. 구현 세부사항과 결합되는 classical unit test로, programmer test와는 별개 범주다(아래 "단계 3" 도입부 참조). RGB 구현 순서는 Gherkin 시나리오와 합쳐 Degenerate → General
- (조건부) Use Case — 복잡도가 흐름·상태 전이에 있을 때만 추가 (판단 체크리스트 참조)
- (Web Usecase) 단계 E-1: High Level Test 작성, 단계 E-2: Walking Skeleton 구현
- 각 단계 완료 후 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 다음 단계 안내 제공

## CONSTRAINTS

### Hard Rules

#### Test Addition Rule

```
- 절차
  - most simple and degenerate(special)에서 시작
    - null, empty, 0, boundary, simple stuff 등과 같은 special case
  - 다음 단계로 interesting 하지만 조금 덜 degenerate한 failing 테스트 케이스(단일 아이템, 최소 유효 값 등)를 점진적으로 추가
  - test를 추가할 때는 특별한 이유가 있는 경우가 아니면 failing test만 추가. 모델 코드를 수정하지 않아도 성공하는 테스트는 추가하지 말아줘
     - TEST SHOULD FAIL WHEN YOU ADD IT
  - 마지막에 most interesting(general), 복잡한 테스트 케이스(복잡한 비즈니스 로직. 다중 할인 계산, 경계 값 케이스 등)를 추가해줘
```

#### Programmer Test 규칙 (FIRST 원칙)

1. **Fast** - 테스트는 빠르게 실행되어야 함
2. **Deterministic** - 동일한 조건에서 항상 동일한 결과
3. **Predictive** - 모든 test가 성공하면 배포했을 때 문제 없어야 함
4. **Behavior change에 민감, structure change에 둔감**
   - 사용자에게 가치를 제공하는 external behavior에 coupled
   - 리팩터링시 변경되는 internal structure에 decoupled
5. **Cheap to write** - 테스트 작성 비용이 적어야 함
6. **Cheap to read** - 테스트 코드가 명확하고 이해하기 쉬워야 함
7. **Cheap to change** - 하나의 동작 변경으로 인해 실패하는 테스트가 다수이면 안됨

> ※ 전체 Test Desiderata 12가지 속성은 tdd-rgb skill 참조

#### 피드백 규칙

- 한 단계에서 관련된 코드를 생성한 후에는 반드시 사용자에게 피드백을 요청
- 사용자가 명시적으로 다음 단계로 진행하는 것을 결정해야만 다음 단계로 진행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."

### Principles

#### 요구사항 작성 원칙 (0층 + User Story + Gherkin 공통)

1. **완전성 (Completeness)**
   - 모든 기능적 요구사항과 비기능적 요구사항 포함
   - 경계 조건과 예외 상황 명시
   - 입력과 출력에 대한 명확한 정의

2. **명확성 (Clarity)**
   - 애매모호한 표현 금지
   - 구체적이고 측정 가능한 기준 제시
   - 전문용어에 대한 명확한 정의

3. **일관성 (Consistency)**
   - 전체 문서에서 일관된 용어 사용
   - 상호 모순되는 요구사항이 없도록 확인

4. **검증 가능성 (Verifiability)**
   - 각 요구사항이 테스트로 검증 가능하도록 작성
   - 성공/실패 기준을 명확히 정의

#### 경계 조건 식별 가이드

1. **수치적 경계** - 0, 1, 최대값, 최소값, 임계점 전후 값, 음수/양수 경계
2. **크기 경계** - 빈 컬렉션/최대 크기, 문자열 길이 제한
3. **상태 경계** - 초기 상태/완료 상태, 활성/비활성, 유효/무효
4. **시간 경계** - 시작/종료 시점, 타임아웃, 순서 의존성

#### Act-Assert 동일 추상화 수준 규칙

- 테스트에서 act와 assert는 같은 추상화 수준에서 이루어져야 함
- 한 테스트 내에서 서로 다른 추상화 레벨 혼합 금지
- api를 호출하여 행동을 수행하고, 같은 api 레벨에서 결과를 검증
- 예: post로 생성하고 get으로 검증하는 방식

## OUTPUT FORMAT

### Document-Based Workflow

**반드시 프로젝트 템플릿 문서(*.md)와 함께 작업합니다.**

#### Step 1: 템플릿 문서 찾기
1. TDD 템플릿 문서(절차 섹션이 있는 *.md) 찾기
2. 현재 단계 파악 (체크박스 상태로 확인)
3. 해당 섹션 내용 작성

#### Step 2: 단계별 진행
- 각 단계 완료 후 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 기존 내용은 변경하지 않고 append only로 갱신
- 각 단계 완료 후 사용자 피드백 대기

---

### 단계 1: 요구사항 작성 — 도메인 규칙(0층) + User Story

요구사항 명세(기존 SRS가 하던 일)를 **두 부분으로 나눠** 작성한다. 규칙과 기능
나열은 담는 그릇이 다르다 —
계산·절사·상태 규칙은 어떤 스토리·시나리오 형식에도 담기지 않으므로(0층),
별도 절로 살아야 한다.

#### 작성 형식

현재 markdown 파일의 요구사항 섹션이 비어 있으면 아래 형식으로 작성:

```markdown
## 1. 요구사항 — 도메인 규칙(0층) + User Story

### 도메인 규칙 (0층)

- 기본 규칙
    - [기본적인 동작 방식과 제약조건]
- 특별 규칙
    - [예외상황이나 특수한 경우의 처리방식]
- 검산 전개 (계산 도메인인 경우)
    - [대표 입력 1건의 단계별 계산 — 숫자의 정본]

### User Story (기능 나열)

#### US-1 — [스토리 이름] (주 스토리)

    As a    [역할 — 실제 사용자·이해관계자]
    I want  [원하는 것]
    So that [얻는 가치]

- INVEST 점검: Valuable / Small / Testable 근거 한 줄씩
```

#### 1a. 도메인 규칙 (0층)

- 계산식·절사·상태 규칙 등 **"왜 이 값이 맞는가"의 근거**
- 구체 수치의 검산 전개도 여기에 둔다 — **숫자의 정본은 이곳 하나**이고, 단계 2
  Gherkin의 `Examples` 표는 이 수치를 옮긴 파생 뷰다
- User Story·Gherkin·Use Case 어디에도 담기지 않는 내용이므로, 생략하면 근거가
  코드 주석·머릿속으로 흩어진다

#### 1b. User Story (기능 나열)

- 기능별 요구사항을 User Story로 나열한다. `So that`이 "왜 필요한가"를 강제한다 —
  이 줄을 채울 수 없으면 스토리가 아니라 작업 지시다
- **INVEST 점검** (스토리마다):
    - *Valuable* — So that이 사용자 언어인가 (시스템 내부 사정이 아니라)
    - *Small* — 한 단위인가 (계산만·조회만 등. 저장·이벤트는 별도 스토리)
    - *Testable* — 단계 2 Gherkin으로 검증 가능한가

#### 샘플

```markdown
## BowlingGame — 도메인 규칙 (0층)

- 기본 규칙
    - 단일 플레이어가 10개의 프레임으로 구성된 1개의 게임을 진행
    - 각 프레임에서 플레이어는 최대 2번의 투구 기회를 가짐
    - 첫 투구에서 10개 핀을 모두 쓰러뜨리면 스트라이크(X)로 기록하고, 해당 프레임 종료
    - 두 번의 투구로 10개 핀을 모두 쓰러뜨리면 스페어(/)로 기록
- 마지막 프레임 특별 규칙
    - 10번째 프레임에서 스트라이크를 기록하면 추가로 2번의 투구 기회를 얻음
    - 10번째 프레임에서 스페어를 기록하면 추가로 1번의 투구 기회를 얻음
    - 오픈 프레임이면 추가 투구 없음
- 점수 계산 규칙
    - 스트라이크: 기본 10점 + 다음 2번의 투구에서 쓰러뜨린 핀 수
    - 스페어: 기본 10점 + 다음 1번의 투구에서 쓰러뜨린 핀 수
    - 오픈 프레임: 해당 프레임에서 쓰러뜨린 핀 수만 (보너스 없음)
    - 총점은 각 프레임 점수의 합계, 최대 300점 (전 프레임 스트라이크)

## ShoppingBasket — User Story

### US-1 — 구간 할인 자동 적용 (주 스토리)

    As a    장바구니에 상품을 담은 고객
    I want  총 금액 구간에 따른 할인이 자동 적용되기를
    So that 직접 계산하지 않아도 정확한 결제 금액을 알 수 있다

- Valuable: 결제 전에 최종 부담액을 알고 구매를 결정할 수 있다
- Small: 할인 계산만 다룬다. 결제·재고는 별도 스토리
- Testable: 단계 2 Gherkin 구간별 시나리오로 검증

### US-2 — 청구서 발행

    As a    고객
    I want  품목·할인·최종 금액이 나열된 청구서를 받기를
    So that 무엇에 얼마를 내는지 확인할 수 있다
```

#### 단계 1 작업 절차

1. 도메인 규칙(0층) 정리 - 비즈니스 규칙·제약, 계산 도메인이면 검산 전개 포함
2. User Story 나열 - INVEST 점검 포함, 모호하면 사용자에게 질문
3. 검토 및 검증 - 완전성, 명확성, 일관성 검토
4. **사용자 승인 대기** - 피드백 요청 후 승인 시 다음 단계 진행
5. **커밋** - 승인 후 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: 요구사항(도메인 규칙 + User Story) 작성 - [기능명]"`

---

### 단계 2: Gherkin Scenario 작성 (예제)

예제를 **Gherkin**으로 작성한다. 입력/기대결과/설명 3중 기술과 정보량은 같지만
두 가지를 더 얻는다:

1. **실행 가능성** — 이 Gherkin이 그대로 `/cucumber-acceptance`의 `.feature` 원본이
   된다. 재작성 없이 문서→실행 이관되고, 기대값이 코드와 어긋나면 빌드가 깨져
   드리프트가 구조적으로 차단된다.
2. **핵심 예시 규율** — "key examples만"이라는 Specification by Example의 규율이
   plan 단계부터 적용된다.

#### 작성 규칙

- `Rule:`로 User Story·비즈니스 규칙별로 그룹화한다 (US ↔ Rule 대응이 추적성)
- 같은 규칙의 수치 변형은 `Scenario Outline` + `Examples` 표로 묶는다
- **핵심 예시만** — happy path, 경계(임계값 전후), 대표 예외. 망라적 edge 나열
  금지(시나리오 폭발). 커버리지용 분기는 단계 3 unit test로
- 시나리오 선정 시 Principles의 "경계 조건 식별 가이드"를 사용한다
- 숫자의 정본은 단계 1a의 검산 전개 — `Examples` 표는 파생 뷰임을 문서에 선언한다
- 구현할 로직과 무관하거나 같은 규칙을 반복하는 시나리오는 제거하고 최대한 간결하게

#### 예제 작성 템플릿

````markdown
## 2. Gherkin Scenario 작성

(숫자의 정본은 §1 도메인 규칙의 검산 전개다. 아래 Examples 표는 파생 뷰이며,
`/cucumber-acceptance` 적용 시 실행되는 원본은 `.feature` 파일이 된다.)

```gherkin
Feature: [기능명]

  Rule: [비즈니스 규칙]   # ← US-N

    Scenario Outline: <케이스>. [규칙이 드러나는 이름]
      Given [전제]
      When [행동]
      Then [검증]

      Examples:
        | 케이스 | 입력 | 기대값 | 걸리는 규칙 |
```
````

#### Gherkin 샘플

```gherkin
Feature: 장바구니 청구서 생성

  Rule: 총 금액 구간에 따라 할인율이 결정된다   # ← US-1

    Scenario Outline: <케이스>. 구간별 할인 적용
      Given 총 금액이 <총금액>원이 되도록 상품이 담겨 있다
      When 청구서를 요청하면
      Then 할인은 <할인>원이고 최종 결제 금액은 <최종금액>원이다

      Examples:
        | 케이스 | 총금액 | 할인  | 최종금액 | 걸리는 규칙            |
        | E-1   | 10000 | 0    | 10000  | 1만원 이하 할인 없음    |
        | E-2   | 17000 | 850  | 16150  | 1만원 초과 5% 할인     |
        | E-3   | 20000 | 2000 | 18000  | 경계: 정확히 2만원 10%  |

  Rule: 청구서에는 담긴 모든 품목이 나열된다     # ← US-2

    Scenario: E-4. 빈 장바구니는 청구서를 만들 수 없다
      Given 장바구니가 비어 있다
      When 청구서를 요청하면
      Then 청구서 발행이 거부된다
```

BowlingGame이라면 gutter game · one spare · one strike · perfect game이 핵심
예시다 — 이 넷이면 규칙 전체가 덮이고, 나머지 조합은 나열하지 않는다.

#### 단계 2 작업 절차

1. 도메인 규칙(0층)·User Story 분석 - Rule 그룹 구성
2. 핵심 예시 선정 - happy path, 경계, 대표 예외 (경계 조건 식별 가이드 활용)
3. Gherkin 작성 - Examples 표 수치는 0층 검산 전개에서 가져옴
4. **사용자 승인 대기** - 피드백 요청 후 승인 시 다음 단계 진행
5. **커밋** - 승인 후 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: Gherkin Scenario 작성 - [기능명]"`

---

### 단계 3: Unit Test 목록

Gherkin 시나리오가 external behavior의 인수 목록을 담당하므로, 여기는 **Gherkin에
없는 것만** 담는다:

- **세밀한 분기** — null·empty·미매핑 입력 등 커버리지용 (Gherkin에 넣으면 산문이 소음)
- **내부 협력·기술 도메인** — 직렬화·동시성·성능 등 문제 도메인의 언어가 코드인 영역
- **property-based 후보** — "모든 입력에 대해 성립"해야 하는 성질

**"Unit Test"이지 "Programmer Test"가 아니다** — Kent Beck의 programmer test는
FIRST 4번째 원칙(behavior change에 민감, structure change에 둔감)을 만족해야
하는데, 위 세 범주는 정의상 구현 세부사항(분기·내부 협력)에 결합된다. 이 결합은
리팩터링 시 깨지기 쉬운 대가를 감수하고 커버리지·엣지케이스를 얻는 의도적
선택이다. 단계 2 Gherkin 시나리오가 이 프로젝트에서 programmer test 계층이다.

Cucumber를 쓰지 않는 프로젝트에서는 Gherkin 시나리오도 이 목록에 합쳐 JUnit으로
구현한다(시나리오당 테스트 1개) — 이 경우 목록은 programmer test(Gherkin 유래)와
unit test(세밀 분기)가 물리적으로 한 목록에 섞이지만, 개념적 구분은 유지된다.
**RGB 구현 순서는 Gherkin 시나리오 + unit test를 합쳐 Degenerate → General로
정렬한다.**

#### 테스트 목록 작성 템플릿

```markdown
## 3. Unit Test 목록 작성

### [기능명]을 위한 테스트 리스트

가장 단순한 특수 케이스(degenerate)에서 일반적인 케이스(general)로 진행하는 테스트 리스트:

- [ ] [가장 단순한 degenerate case]
- [ ] [기본적인 단일 요소 case]
- [ ] [경계 조건 case]
- [ ] [일반적인 비즈니스 규칙 case]
- [ ] [복잡한 종합 case]
```

#### 테스트 목록 샘플

```markdown
## Bowling Game 테스트 리스트 — Cucumber 미사용 시 (시나리오 포함 전체 목록)

- [ ] gutter game
- [ ] all ones(모든 프레임에서 핀을 한개만 쓰러뜨린 경우)
- [ ] one spare(하나의 프레임만 스페어 처리하고, 다른 프레임은 open인 경우)
- [ ] one strike(하나의 프레임만 스트라이크 처리하고, 다른 프레임은 open인 경우)
- [ ] perfect game

## 쇼핑 카트 테스트 리스트 — Gherkin 병행 시 (세밀 분기만)

구간별 할인·빈 장바구니 거부는 단계 2 Gherkin이 담당한다. 여기는 그 아래 분기만:

- [ ] 빈 장바구니 거부의 예외 타입·메시지 검증 (Gherkin은 "거부된다"까지만 고정)
- [ ] 품목 수량 0 / 단가 음수 입력 검증 분기
```

#### JavaDoc 형식 테스트 목록 샘플

테스트 클래스 최상단에 Java 23 마크다운 형식 커멘트로 테스트 목록 추가:

```java
/// - [ ] gutter game
/// - [ ] all ones
/// - [ ] one spare
/// - [ ] one strike
/// - [ ] perfect game
```

#### External Behavior 테스트 케이스 샘플

Kent Beck의 TDD 접근법에 따라:
- 가장 간단한 케이스부터 시작
- 점진적으로 복잡성 증가
- 사용자 관점에서의 행동 검증

```markdown
ex. 테니스 게임 External Behavior 테스트 케이스

1단계: 기본 점수 시스템
- 게임 시작: "0-0" (Love-Love)
- 첫 번째 득점: "15-0" 또는 "0-15"
- 두 번째 득점: "30-0", "15-15", "0-30"

2단계: 게임 승리 조건
- 40-0에서 한 점 더: "Player1 wins"

3단계: Deuce 상황
- 40-40: "Deuce"
- Deuce에서 한 점: "Advantage Player1"

4단계: 엣지 케이스
- 여러 번의 Deuce 반복
- Advantage 상태에서의 연속 득점
```

#### 중복 제거 기준
- 비즈니스 규칙과 무관한 중복되는 테스트 케이스 제거
- 동일한 비즈니스 규칙이 적용되는 테스트 케이스는 합치거나 제거
- **Cucumber 병행 시, Gherkin 시나리오와 같은 검증을 unit test로 중복 작성하지 않는다** (두 계층 중복 금지. Cucumber 미사용이면 단계 3 도입부대로 시나리오를 이 목록에 합친다 — 그건 중복이 아니라 유일한 구현처)
- 구현하려는 코드가 어떻게 동작해야 하는지 알고 있는 시나리오들을 나열

#### 테스트 목록 작업 절차

1. Gherkin 시나리오 분석 - 이미 덮인 검증 확인, 남은 세밀 분기 식별
2. 테스트 순서 결정 - Degenerate → Simple → Interesting → General
3. 테스트 목록 정제 - 중복 제거, 누락 확인
4. 체크박스 업데이트
5. **커밋** - 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: unit test 목록 작성 - [기능명]"`
6. **다음 단계 안내**
   - **기본(acceptance-first)**: plan 합의 직후 `/cucumber-acceptance`로 `.feature` +
     Runner를 먼저 셋업(미구현 시나리오는 `@pending`) — RGB가 진행되며 시나리오가
     하나씩 green이 되는 이중 루프(외부 인수 루프 + 내부 TDD 루프). `tdd-plan`을
     거쳐 온 신규 기능은 기본적으로 이 경로를 따른다
   - 대안: `/tdd-rgb`(단계별 확인) 또는 `/tdd-feature`(feature 단위 자율)로 Cucumber
     없이 바로 구현 — 이미 구현·테스트가 있는 기존 프로젝트에 기능을 추가할 때,
     또는 `tdd-plan`을 거쳤어도 이 기능만 Cucumber를 의도적으로 쓰지 않기로
     사용자가 명시적으로 선택했을 때. **후자를 선택하면 구현 시작 전에 단계 3의
     Unit Test 목록으로 돌아가 Gherkin 시나리오를 합쳐 넣는다**(단계 3 도입부의
     "Cucumber를 쓰지 않는 프로젝트" 경로대로) — 단계 3은 acceptance-first를
     가정하고 Gherkin이 담당할 검증을 목록에서 제외한 채 작성됐으므로, 병합 없이
     그대로 구현하면 external behavior 검증이 어디에도 남지 않는다

---

### (조건부) Use Case 추가 — 복잡도가 흐름에 있을 때

복잡도가 **규칙**에 있으면 0층(1a)이 두꺼워지고 Use Case는 얇아진다 — 계산 중심
도메인은 생략이 기본이다. 복잡도가 **흐름·상태 전이**에 있으면 Use Case의 확장절이
주역이 된다 — 주로 `web-usecase` 유형에서 해당한다.

**판단 체크리스트 — 2개 이상이면 추가한다:**

1. 액터가 2명 이상이고 이해관계자 관심사가 충돌한다 (예: 고객 vs 정산 담당자)
2. 상태 전이가 있다 (예: 배정 전/후, 승인 대기/완료, 반품 접수/검수/환불)
3. 대안·예외 흐름이 3개 이상이다 — "정상 흐름의 어느 지점에서 갈라지는가"가 중요
4. 기능 간 불변식이 있다 (예: 조회가 보여준 금액 = 주문이 확정한 금액)

**작성 시:**

- 확장절(대안·예외 흐름)과 기능 간 불변식 중심으로 쓴다 — Gherkin은 시나리오를
  나열할 수 있지만 "정상 흐름의 어느 지점에서 갈라지는가"라는 구조는 확장절만
  표현한다
- 계산 규칙은 0층(1a) 참조로 둔다 — Use Case 본문에 계산을 풀어쓰지 않는다
- `web-usecase` 유형이면 E-1 High Level Test가 UC 주 성공 시나리오의 실행 가능한
  형태다 — UC를 썼다면 HLT가 검증할 흐름·확장 지점이 문서로 먼저 확정된 것이다

**UC Scenario(구체 인스턴스 전개)는 만들지 않는다** — 하던 일의 실행 가능한
대체물이 이미 파이프라인에 있다: 구체 수치는 Gherkin `Examples` 표(실행됨), 주
흐름의 단계별 추적은 High Level Test(Approvals 출력). 검산 전개만 0층에 남긴다.

---

### Web Usecase 추가 단계

> 다음 단계들은 TDD 유형이 `web-usecase`일 때만 진행합니다.

#### 단계 E-1: High Level Test 작성

##### High Level Test 규칙

- 대표 예제 선택: 단계 2 Gherkin 시나리오 중에서 요구사항의 제약 조건을 가장 많이 충족하는 경우(most general한 경우)를 선택
- 이 예제를 통해 구현할 기능이 어떻게 사용되는지 감을 잡고, 어떤 결과를 갖게 될지 계획과 목표(Target Design)를 가지고 진행

##### High Level Test 코드 샘플

```java
@SpringBootTest
@AutoConfigureMockMvc
public class CreateShoppingBasketTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Disabled("아직 기능 구현이 완료되지 않았습니다.")
    @DisplayName("여러 상품이 있고 20,000원 초과 시 10% 할인 적용되는 청구서 생성")
    @Test
    void create_and_verify_basket() throws Exception {
        // given
        BasketItemRequests items = new BasketItemRequests(List.of(
                new BasketItemRequest("스마트폰 케이스", BigDecimal.valueOf(15000), 1),
                new BasketItemRequest("보호필름", BigDecimal.valueOf(5000), 2),
                new BasketItemRequest("충전 케이블", BigDecimal.valueOf(8000), 1)
        ));

        // when
        MvcResult postResult = mockMvc.perform(post("/api/baskets")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(items)))
                .andExpect(status().isOk())
                .andReturn();

        BasketResponse response = objectMapper.readValue(
                postResult.getResponse().getContentAsString(),
                BasketResponse.class);

        String basketId = response.basketId();

        // assert: get을 통해 같은 api 레벨에서 결과 확인
        MvcResult getResult = mockMvc.perform(get("/api/baskets/" + basketId))
                .andExpect(status().isOk())
                .andReturn();

        BasketDetailsResponse basketDetails = objectMapper.readValue(
                getResult.getResponse().getContentAsString(),
                BasketDetailsResponse.class);

        Approvals.verify(printBasketDetails(basketDetails));
    }

    private String printBasketDetails(BasketDetailsResponse basketDetails) {
        return """
                ===== 영수증 =====
                품목:
                - 스마트폰 케이스 1개 (단가: 15,000원, 총액: 15,000원)
                - 보호필름 2개 (단가: 5,000원, 총액: 10,000원)
                - 충전 케이블 1개 (단가: 8,000원, 총액: 8,000원)
                소계: 33,000원
                할인: 3,300원 (10% 할인)
                최종 결제 금액: 29,700원
                ==================
                """;
    }
}
```

##### DSL 개선 목표

초기 구현 후 Protocol Driver, Test Data Builder 등을 적용하여 DSL 스타일로 개선:

```java
@Test
void create_and_verify_basket() throws Exception {
    Long basketId = basketApi.createBasket(
            aBasket()
                    .withItem(anItem("스마트폰 케이스").withPrice(15000).withQuantity(1))
                    .withItem(anItem("보호필름").withPrice(5000).withQuantity(2))
                    .withItem(anItem("충전 케이블").withPrice(8000).withQuantity(1))
    );

    verifyReceipt(basketApi.basketDetails(basketId));
}
```

##### Protocol Driver

- Protocol Drivers (PDs)는 DSL에서 시스템 언어로의 번역자/어댑터
- DSL의 인터페이스를 미러링하되 더 구체적인 파라미터 사용
- SUT와의 각 통신 채널별로 최소 하나의 PD 생성
- 모든 테스트 인프라스트럭처 지식을 여기에 격리

##### Mermaid 클래스 다이어그램

테스트에 나타나는 도메인 클래스들에 대해 러프한 클래스 다이어그램 작성:
- 요구사항(도메인 규칙 + User Story) 기반 정적분석으로 domain class, value object 식별
- class, attributes, relation만 표현
- 금액 계산과 같은 행위 관련 부분은 추가하지 않음 (나중에 리팩터링을 통해 추가)

##### @Disabled 처리
- 초기에는 `@Disabled("아직 기능 구현이 완료되지 않았습니다.")` 추가
- 모든 단계별 테스트 완료 후 활성화

---

#### 단계 E-2: Walking Skeleton 구현

##### Walking Skeleton 목적
- End-to-end 아키텍처의 기본 골격 구현
- Controller부터 Repository까지 전체 레이어 연결
- 실제 기능보다는 구조적 연결성 검증

##### Walking Skeleton 테스트 샘플

```java
@DisplayName("엔드-투-엔드 기능 구현: UI부터 데이터베이스까지 전체 시스템을 관통하는 기본적인 흐름 포함")
@Test
void walking_skeleton_shopping_basket() throws Exception {
    // given
    BasketItemRequests items = new BasketItemRequests(List.of(
            new BasketItemRequest("충전 케이블", BigDecimal.valueOf(8000), 1)
    ));

    // when
    MvcResult postResult = mockMvc.perform(post("/api/baskets")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(items)))
            .andExpect(status().isOk())
            .andReturn();

    BasketResponse response = objectMapper.readValue(
            postResult.getResponse().getContentAsString(),
            BasketResponse.class);

    String basketId = response.basketId();

    // assert: get을 통해 같은 api 레벨에서 결과 확인
    MvcResult getResult = mockMvc.perform(get("/api/baskets/" + basketId))
            .andExpect(status().isOk())
            .andReturn();

    BasketDetailsResponse basketDetails = objectMapper.readValue(
            getResult.getResponse().getContentAsString(),
            BasketDetailsResponse.class);

    Approvals.verify(printBasketDetails(basketDetails));
}
```

##### Fake Repository 규칙

```java
@SpringBootTest
@AutoConfigureMockMvc
public class CreateShoppingBasketTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private BasketRepository basketRepository;

    @BeforeEach
    void setup() {
        if (basketRepository instanceof FakeBasketRepository) {
            ((FakeBasketRepository) basketRepository).clear();
        }
    }

    @TestConfiguration
    static class TestConfig {
        @Bean
        public BasketRepository basketRepository() {
            return new FakeBasketRepository();
        }
    }

    static class FakeBasketRepository implements BasketRepository {
        private final Map<Long, Basket> baskets = new ConcurrentHashMap<>();
        private final AtomicLong idGenerator = new AtomicLong(1);

        public Basket save(Basket basket) {
            if (basket.getId() == null) {
                Long id = idGenerator.getAndIncrement();
                Basket savedBasket = new Basket(id, basket.getItems());
                baskets.put(id, savedBasket);
                return savedBasket;
            } else {
                baskets.put(basket.getId(), basket);
                return basket;
            }
        }

        public Optional<Basket> findById(Long id) {
            return Optional.ofNullable(baskets.get(id));
        }

        public void clear() {
            baskets.clear();
            idGenerator.set(1);
        }
    }
}
```

##### Controller 구현 원칙

1. **Fake it 적용** - 복잡한 계산은 하드코딩으로 처리, 최소한의 구현
2. **절차적/명령형 스타일** - 하나의 메서드에 모든 로직 작성, 메서드 추출이나 클래스 분리 금지
3. **Feature Envy 허용** - Controller가 모든 로직 담당, 데이터 중심 설계로 시작

## FAILURE CONDITIONS

### 품질 체크리스트

단계 1~2 작성 후 다음 사항을 확인:

- [ ] 모든 기능이 User Story로 나열되었고, So that이 사용자 언어인가? (비었거나 시스템 내부 사정이면 작업 지시)
- [ ] 계산·절사 규칙의 근거(검산 전개)가 0층에 있는가? (Gherkin Examples에만 있으면 정본 부재)
- [ ] Gherkin이 핵심 예시만 담았는가? (경계·대표 예외 포함, 망라적 edge 나열 금지)
- [ ] 각 요구사항이 테스트로 검증 가능한가?
- [ ] 애매모호한 표현·상호 모순되는 요구사항이 없는가?
- [ ] UC Scenario 문서를 만들지 않았는가? (Gherkin Examples 표·High Level Test가 대체)
