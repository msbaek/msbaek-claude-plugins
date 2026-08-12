---
name: tdd-plan
description: TDD Planning - 도메인 규칙(0층) + User Story + Gherkin Scenario(programmer test) + unit test 목록 작성, 복잡도가 흐름·상태에 있으면 조건부 Use Case 추가. /tdd-plan으로 호출.
argument-hint: "[plan-doc-path]"
allowed-tools: Write, Edit, Read, Bash(git add:*), Bash(git commit:*), Bash(git status:*)
---

# TDD Planning Skill

Kent Beck의 TDD 원칙에 따라 구현 전 계획 문서를 작성하는 전문가입니다.
요구사항(도메인 규칙 + User Story) → Gherkin Scenario(programmer test) → unit test 목록
순서로 진행하며, Web App 유형에서는 인수 테스트 셋업(.feature)과 Walking Skeleton 단계가 추가됩니다.
복잡도가 흐름·상태 전이에 있으면 Use Case를 조건부로 추가합니다.

## GOAL

- **성공 = 도메인 규칙(0층), User Story, Gherkin Scenario, unit test 목록이 템플릿 문서에 작성되고, 각 단계별 체크박스가 업데이트됨**
- 단계 1: 요구사항 — 도메인 규칙(0층: 계산·제약의 근거 + 검산 전개)과 User Story(기능 나열)
- 단계 2: Gherkin Scenario — 핵심 예시(경계·대표 예외 포함)를 실행 가능한 형식으로. Kent Beck이 말하는 programmer test(behavior에 coupled, structure에 decoupled)가 이 계층이다. 이후 `/cucumber-acceptance`의 `.feature` 원본이 된다
- 단계 3: Unit Test 목록 — Gherkin에 없는 세밀 분기·내부 협력만. 구현 세부사항과 결합되는 classical unit test로, programmer test와는 별개 범주다(아래 "단계 3" 도입부 참조). RGB 구현 순서는 Gherkin 시나리오와 합쳐 Degenerate → General
- (조건부) Use Case — 복잡도가 흐름·상태 전이에 있을 때만 추가 (판단 체크리스트 참조)
- (Web App) 단계 E-1: 인수 테스트 셋업(.feature + Runner, `/cucumber-acceptance` 필수), 단계 E-2: Walking Skeleton 구현
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
5. **집계 경계** - 같은 키(상품·회원·쿠폰)가 여러 항목(라인·요청·이벤트)으로 나뉠 수
   있는가? 나뉠 수 있다면, **항목별로는 각각 통과하지만 합산하면 규칙을 위반하는**
   입력이 존재하는가?

> 5번이 놓치기 쉬운 이유: "여러 항목 중 하나가 규칙 위반"(서로 다른 상품 A·B) 시나리오는
> 자연히 떠오르지만, **같은 키가 여러 항목으로 쪼개진 경우**는 떠오르지 않는다. 검증은
> 항목별로 하고 반영은 누적으로 하면 그 사이가 벌어진다:
>
> ```
> 장바구니: [("A", 2개), ("A", 2개)]   ← 같은 상품이 두 라인
> 재고: A = 3개
> 검증(라인별): 2≤3 ✓ , 2≤3 ✓  → 통과
> 차감(누적):   3-2=1 , 1-2=-1  → 재고 음수, 오버셀
> ```
>
> 검증 단위와 반영 단위가 다르면 그 차이가 곧 결함이다. 재고·한도·쿠폰 사용횟수·
> 포인트처럼 **합산되는 자원**을 다루는 규칙이 있으면 이 경계를 반드시 시나리오로 만든다.

#### Act-Assert 동일 추상화 수준 규칙

- 테스트에서 act와 assert는 같은 추상화 수준에서 이루어져야 함
- 한 테스트 내에서 서로 다른 추상화 레벨 혼합 금지
- api를 호출하여 행동을 수행하고, 같은 api 레벨에서 결과를 검증
- 예: post로 생성하고 get으로 검증하는 방식 — 단, **그 post가 실제 인수 조건일 때만**이다.
  시나리오가 요구하지 않는 쓰기 API를 검증 편의를 위해 만들지 않는다(단계 E-2의
  "인수 조건에 없는 API를 발명하지 않는다" 참조). 이때는 given을 Repository 시드로 두고
  읽기 경로만 같은 레벨에서 검증한다

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

**Degenerate → General 순서의 도출 절차** (결과가 아니라 만드는 방법):

1. 가장 중요한 테스트(핵심 시나리오)를 먼저 적는다
2. 거기 도달하기 위한 징검다리(stair-step) 테스트를 거슬러 내려간다
3. most degenerate 테스트를 발견할 때까지 반복한다
4. 목록을 **reverse order로 정렬**해 degenerate-first 순서를 만든다

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
     사용자가 명시적으로 선택했을 때. **단 `web-app` 유형은 Cucumber가 필수이므로,
     프로젝트 제약(의존성 정책 등)으로 도입 불가한 경우에만 이 대안을 택하고
     대표 시나리오 1개를 JUnit 인수 테스트로 작성한다**(단계 E-1의 탈출구). **이 대안을 고르면(사유 무관) 구현 시작
     전에 단계 3의 Unit Test 목록으로 돌아가 Gherkin 시나리오를 합쳐 넣고
     체크박스·커밋을 갱신한다**(단계 3 도입부의 "Cucumber를 쓰지 않는 프로젝트"
     경로대로) — 단계 3은 acceptance-first를 가정하고 Gherkin이 담당할 검증을
     목록에서 제외한 채 작성됐으므로, 병합 없이 그대로 구현하면 external
     behavior 검증이 어디에도 남지 않는다

---

### (조건부) Use Case 추가 — 복잡도가 흐름에 있을 때

복잡도가 **규칙**에 있으면 0층(1a)이 두꺼워지고 Use Case는 얇아진다 — 계산 중심
도메인은 생략이 기본이다. 복잡도가 **흐름·상태 전이**에 있으면 Use Case의 확장절이
주역이 된다 — 주로 `web-app` 유형에서 해당한다.

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
- `web-app` 유형이면 E-1의 `.feature` 시나리오가 UC 주 성공 시나리오의 실행 가능한
  형태다 — UC를 썼다면 인수 테스트가 검증할 흐름·확장 지점이 문서로 먼저 확정된 것이다

**UC Scenario(구체 인스턴스 전개)는 만들지 않는다** — 하던 일의 실행 가능한
대체물이 이미 파이프라인에 있다: 구체 수치는 Gherkin `Examples` 표(실행됨), 주
흐름의 단계별 추적은 `.feature` 시나리오(필요 시 Step의 Approvals 출력). 검산 전개만 0층에 남긴다.

---

### Web App 추가 단계

> 다음 단계들은 TDD 유형이 `web-app`일 때만 진행합니다.

#### 단계 E-1: 인수 테스트 셋업 (.feature + Runner)

##### 규칙

Web App은 `/cucumber-acceptance`가 **필수**다. 단계 2에서 쓴 Gherkin이 그대로
`.feature`로 실행되어 인수 계층을 담당하므로, **별도 High Level Test(JUnit)를 만들지
않는다** — 같은 검증이 두 계층에 중복되면 안 된다(`cucumber-acceptance`의 Hard Rule).

- `/cucumber-acceptance`를 호출해 `.feature` + Runner + Steps + Protocol Driver를 셋업
- 미구현 시나리오는 `@pending` 태그로 제외 — 6단계 RGB 사이클에서 각 Green이 자기
  시나리오의 태그를 같은 커밋에서 해제한다. `@Disabled` 일괄 토글이 아니라
  **시나리오 단위 해제**다
- Target Design(구현될 API 형상)은 Protocol Driver가 확정한다 — Steps는 파싱·위임만
- 대표 예제(most general한 시나리오)는 별도 테스트가 아니라 `.feature`의 한 시나리오다

> **탈출구**: 프로젝트 제약(의존성 정책 등)으로 Cucumber를 도입할 수 없는 경우에만,
> 대표 시나리오 1개를 JUnit 인수 테스트(`@Disabled`로 시작 → 구현 완료 후 활성화)로
> 작성해 대체한다. 이때도 나머지 절차는 동일하다.

##### 전체 출력 잠금이 필요하면 — Approvals를 Step에 둔다

영수증처럼 **출력 전체 형상**(품목 나열·소계·할인 줄 순서)을 잠그고 싶으면, 별도 JUnit
테스트를 만들지 말고 Steps에서 Approvals를 호출한다. 이때 승인 파일명이 시나리오마다
갈라지게 해야 한다 — Scenario Outline은 Examples 행이 모두 같은 step을 타므로, 구분자
없이 쓰면 행끼리 같은 승인 파일을 덮어써서 검증이 조용히 통과한다.

Cucumber `@Before` 훅에 주입되는 `Scenario` 객체의 `getId()`는 Examples 행마다 다르므로
(uri + line 기반) 이를 승인 파일명 접미사로 쓴다:

```java
private String approvalKey;

@Before
public void 시나리오_기록(Scenario scenario) {
    this.approvalKey = scenario.getId().replaceAll("\\W+", "_");
}

@Then("영수증이 출력된다")
public void 영수증_출력() {
    Approvals.verify(driver.printReceipt(),
            new Options().forFile().withAdditionalInformation(approvalKey));
}
```

##### Gherkin 시나리오 샘플

```gherkin
Feature: 장바구니 청구서

  @pending
  Scenario: 여러 상품이 있고 20,000원 초과 시 10% 할인 적용
    Given 장바구니에 다음 상품이 담겨 있다
      | 상품명       | 단가   | 수량 |
      | 스마트폰 케이스 | 15000 | 1  |
      | 보호필름      | 5000  | 2  |
      | 충전 케이블    | 8000  | 1  |
    When 청구서를 생성한다
    Then 소계는 33,000원이다
    And 할인은 3,300원이다
    And 최종 결제 금액은 29,700원이다
    And 영수증이 출력된다
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

##### 미구현 시나리오 처리
- 초기에는 `@pending` 태그로 실행에서 제외 (Runner 설정에서 `not @pending`)
- 각 Green 단계가 자기 시나리오의 태그를 같은 커밋에서 해제 — 일괄 활성화 단계는 없다
- (탈출구로 JUnit 인수 테스트를 쓰는 경우에만) `@Disabled("아직 기능 구현이 완료되지
  않았습니다.")`로 시작해 구현 완료 후 제거

---

#### 단계 E-2: Walking Skeleton 구현

##### Walking Skeleton 목적 — 두 축: real과 thinnest

GOOS(Growing Object-Oriented Software)의 정의: "자동으로 빌드·배포·테스트할 수 있는
실제 기능(real functionality)의 가장 얇은 슬라이스(thinnest possible slice)".
인프라 미지수(빌드 설정·DB 연결·wire 포맷)와 도메인 미지수를 한 방정식에 넣지 않기 위해,
도메인 사이클(RGB) 시작 전에 인프라 경로를 먼저 증명한다. 이 단계의 테스트는
기능 검증이 아니라 **뼈대 자체가 동작하는지 확인하는 테스트**다.

**real과 "비즈니스 로직 제외"는 충돌하지 않는다 — 축이 다르다**:

| 축 | 질문 | 기준 |
|---|---|---|
| **real** | 실행 경로가 진짜인가? | fake/하드코딩 금지 — 실제 HTTP → 실제 앱 → **실제 DB(docker MySQL)** 관통 |
| **thinnest** | 기능이 얇은가? | 비즈니스 규칙(합산·할인·검증) 제외 — "너무 단순해서 흥미롭지 않을 정도"의 저장·조회 pass-through |

하드코딩된 응답은 파이프라인을 거쳐도 real이 아니고, 비즈니스 규칙이 들어가면 thinnest가
아니다. DB를 in-memory로 대체하는 것은 real 위반이자, DB 셋업류 unknown unknowns의
발견을 정확히 뒤로 미루는 일이다.

##### Repository와 Profile 규칙

Walking Skeleton은 **진짜 JPA Repository 최소 구현 + docker MySQL(Testcontainers)**로
관통한다. In-Memory 구현은 skeleton용이 아니라 **이후 RGB 사이클의 빠른 루프용**이다.
이 단계에서 profile 구조를 함께 셋업한다:

```java
// 주석 토글("JPA 사용을 위해 주석 처리")이 아니라 profile로 전환한다 —
// 코드 수정 없이 @ActiveProfiles / spring.profiles.active로 구현을 선택
@Repository
@Profile("inMemory")     // RGB 사이클의 빠른 루프 전용
class InMemoryBasketRepository implements BasketRepository {
    private final Map<Long, Basket> baskets = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public Basket save(Basket basket) {
        if (basket.getId() == null) {
            Long id = idGenerator.getAndIncrement();
            Basket savedBasket = new Basket(id, basket.getItems());
            baskets.put(id, savedBasket);
            return savedBasket;
        }
        baskets.put(basket.getId(), basket);
        return basket;
    }

    public Optional<Basket> findById(Long id) {
        return Optional.ofNullable(baskets.get(id));
    }

    public void clear() {    // 테스트 격리용 — @BeforeEach에서 호출
        baskets.clear();
        idGenerator.set(1);
    }
}

@Repository
@Profile("!inMemory")    // local, dev, stage, prod 전부 — 새 환경 추가 시 수정 불필요
class JpaBasketRepository implements BasketRepository { ... }
```

**네이밍 주의 — Spring Data 자동 프래그먼트와의 충돌 (실제 빌드 실패 사례)**

Spring Data JPA는 리포지토리 인터페이스 `X`가 있으면 같은 패키지의 `XImpl`을 "커스텀
구현 프래그먼트"로 **자동 병합**한다(직접 작성한 메서드를 추가하라고 만든 정식 기능).
따라서 Spring Data 인터페이스명 뒤에 그대로 `Impl`을 붙인 이름을 **포트 구현체에 쓰면
안 된다** — 프록시가 우리 어댑터를 프래그먼트로 삼고, 어댑터는 생성자로 그 인터페이스를
다시 요구해 `BeanCurrentlyInCreationException`(순환 의존)이 난다.

| | 안전 | 위험 |
|---|---|---|
| Spring Data 인터페이스 | `BasketRepositoryJpa` | `BasketRepositoryJpa` |
| 포트 구현체(어댑터) | `BasketRepositoryImpl` (포트 `BasketRepository` + Impl) | `BasketRepositoryJpaImpl` ← 자동 병합 대상과 이름이 일치 |

어댑터 이름은 **Spring Data 인터페이스가 아니라 포트 인터페이스 이름**에서 파생시킨다.

`@Profile("!inMemory")`는 활성 profile이 없는 기본 상태에도 매칭된다 — 의도된 동작이다.
"진짜 DB가 기본, in-memory는 명시적으로 요청할 때만"이 real 원칙의 기본값이다.

RGB 사이클에서의 사용법. 도메인 테스트는 Spring 컨텍스트 없이 **직접 생성**해 쓰는 것이
가장 빠르다 (profile 빈은 앱을 `inMemory`로 띄울 때 쓰인다):

```java
class AddItemToBasketTest {                        // Spring 부팅 없음 — 밀리초 단위
    private final InMemoryBasketRepository repository = new InMemoryBasketRepository();

    @BeforeEach
    void setup() {
        repository.clear();
    }
}
```

Spring 컨텍스트가 필요한 테스트(Controller 경유 등)만 profile로 전환한다 — JPA로 바꿀 때
주석을 해제하는 게 아니라 `@ActiveProfiles` 값만 `local`로 바꾼다:

```java
@SpringBootTest
@ActiveProfiles("inMemory")   // local로 바꾸면 같은 테스트가 docker MySQL로 실행
class BasketControllerTest {
    @Autowired
    InMemoryBasketRepository repository;   // profile로 구현이 확정되므로 instanceof 검사 불필요
}
```

- profile은 환경 이름 한 축으로 정렬: `inMemory` / `local`(docker MySQL) / `dev` / `stage` / `prod`
- Walking Skeleton 테스트와 인수 테스트(`.feature`)는 **항상 `local`**(docker MySQL)에서
  실행한다 — skeleton이 증명한 real 경로를 이후에도 지키는 것은 인수 테스트의 몫
- RGB 사이클의 도메인 단위 테스트는 repository가 필요 없고, 저장이 필요한 테스트만
  `inMemory` profile로 빠르게 실행한다

##### 인수 조건에 없는 API를 발명하지 않는다

skeleton이 관통을 증명하려면 HTTP 요청이 필요하지만, **그 요청은 Gherkin 시나리오가
실제로 요구하는 것이어야 한다.** 시나리오가 전부 "이미 상태가 정해진 장바구니"를 전제로
시작한다면 생성(POST) API는 어떤 인수 조건도 요구하지 않는 발명품이다. 두 가지 이유로
금지한다:

- **Target Design 선점** — 구현될 API 형상은 Protocol Driver가 확정한다
  (`cucumber-acceptance`). skeleton이 먼저 POST 계약을 못박으면 이 원칙과 충돌한다
- **No overengineering** — 요구되지 않은 엔드포인트는 이후 계속 유지·검증해야 하는 부채다

**판단 절차**: 단계 2 Gherkin에서 그 쓰기 경로를 요구하는 시나리오를 찾는다. 없으면
API로 노출하지 말고 테스트의 `@BeforeEach`에서 Repository로 직접 시드한 뒤 **읽기 경로
하나만 HTTP로 검증**한다 — 인프라 관통 증명에는 그것으로 충분하다.

```java
@DisplayName("엔드-투-엔드 관통: HTTP → 앱 → 진짜 DB에서 읽어 응답한다")
@Test
void walking_skeleton_shopping_basket() throws Exception {
    // given — 쓰기 API가 인수 조건에 없으므로 Repository로 직접 시드
    Long basketId = basketRepository.save(aBasketWith("충전 케이블", 8000, 1)).getId();

    // when — 시나리오가 실제로 요구하는 읽기 경로만 HTTP로
    MvcResult result = mockMvc.perform(get("/api/baskets/" + basketId))
            .andExpect(status().isOk())
            .andReturn();

    BasketDetailsResponse basketDetails = objectMapper.readValue(
            result.getResponse().getContentAsString(),
            BasketDetailsResponse.class);

    // then — 로직 없는 pass-through 확인 (금액 계산은 RGB 사이클에서)
    Approvals.verify(printBasketDetails(basketDetails));
}
```

> 생성이 실제 인수 조건인 경우(예: "고객이 장바구니를 만든다" 시나리오가 있음)에만
> POST → GET 왕복으로 관통시킨다. 이때 act와 assert는 같은 API 레벨에서 이루어져야 한다.

##### 테스트 클래스 설정 — 진짜 DB로

skeleton 테스트에 Fake Repository를 주입하지 않는다(real 위반). docker MySQL을
Testcontainers로 띄우고 진짜 JPA 경로로 관통한다:

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("local")     // 진짜 JPA + docker MySQL — Fake/TestConfiguration 주입 금지
@Transactional               // 테스트 격리: 각 테스트 후 롤백 (컨테이너는 클래스 단위 공유)
@Testcontainers
public class CreateShoppingBasketTest {
    @Container @ServiceConnection
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private BasketRepository basketRepository;   // 시드용 — 위 skeleton 테스트가 사용
}
```

**docker MySQL을 띄우는 방법은 두 가지** — 어느 쪽이든 real 원칙(진짜 DB)은 동일하게
지켜지므로 환경에 맞춰 고른다:

| 방법 | 장점 | 주의 |
|---|---|---|
| **Testcontainers** (기본) | 테스트가 컨테이너 수명을 소유, CI에서 표준 | 일부 Docker 환경(OrbStack 등)에서 docker-java의 API 버전 협상이 실패하면 `1.32`로 폴백해 "minimum supported API version is 1.40" 오류. 라이브러리 문제이며 `systemProperty("api.version", "1.41")`로 우회 가능 |
| **Spring Boot Docker Compose** | `compose.yaml` 하나를 `bootRun`과 테스트가 공유, `@Container`/`@ServiceConnection` 보일러플레이트 없음 | `spring.docker.compose.lifecycle-management=start-only` + `spring.docker.compose.skip.in-tests=false`(기본 true라 테스트에서 건너뜀), 의존성은 `testAndDevelopmentOnly` |

##### 관통 확인 — 실행 SQL 로깅

real 원칙은 "진짜 DB를 거쳤다"고 **선언**하는 것으로 지켜지지 않는다. 이 단계의 실패는
대부분 조용하다 — 임베디드 DB로 대체되거나(아래 7단계의 `replace = NONE` 항목),
설정이 무시되어 의도한 경로가 아닌 곳으로 흐른다. 테스트는 그대로 초록색이다.
그래서 skeleton을 세울 때 **실행된 SQL을 눈으로 확인할 수단**을 함께 넣는다.

```yaml
# 기본 — 의존성 추가 없음. 실행된 SQL 문장을 로그로 본다
spring:
  jpa:
    show-sql: true
```

이것으로 "MySQL에 정말 쿼리가 나갔는가"는 확인된다. 다만 파라미터가 `?`로 남아
**바인딩된 실제 값은 보이지 않는다**. 값까지 봐야 하거나 JPA를 거치지 않는 경로
(`JdbcTemplate` 등)까지 덮으려면 p6spy를 얹는다:

```kotlin
// build.gradle.kts — 버전은 반드시 Spring Boot 버전에 맞춰 고른다 (아래 주의 참조)
implementation("com.github.gavlyukovskiy:p6spy-spring-boot-starter:2.0.1")
```

```yaml
# application.yml — 최상위 prefix 는 decorator. `spring.` 을 앞에 붙이지 않는다
decorator:
  datasource:
    p6spy:
      enable-logging: true
      logging: slf4j
```

**버전 주의**: 이 스타터는 Spring Boot 메이저 버전에 묶여 있다. 맞지 않는 조합을 쓰면
자동 설정이 적용되지 않고, 그 실패 역시 조용하다.

| Spring Boot | p6spy-spring-boot-starter |
|---|---|
| 4.x | `2.0.x` (2.0.0이 "Prepare for Spring Boot 4") |
| 3.x | `1.12.1` |

위 표는 이 문서를 쓴 시점의 값이다. 좌표를 복사하기 전에
[README](https://github.com/gavlyukovskiy/spring-boot-data-source-decorator)의
호환 표에서 현재 프로젝트에 맞는 최신 값을 확인한다.

**Spring Boot 버전 선택**: 새 프로젝트를 만든다면 [start.spring.io](https://start.spring.io/)에서
제공하는 **GA 최신 버전**을 쓴다 — 목록에 `(SNAPSHOT)`이 붙은 항목은 제외한다.
이 문서 작성 시점의 GA 최신은 4.1.0이었다(4.1.1·4.0.8은 SNAPSHOT). 특정 버전을
관성으로 복사하지 말고 매번 확인한다.

**프로퍼티 이름 주의**: prefix는 `decorator.datasource.p6spy`이고 활성화 키는
`enable-logging`이다. `logging`은 활성화 플래그가 아니라 appender 선택
(`slf4j`/`sysout`/`file`/`custom`)이다. Spring Boot는 인식하지 못하는 프로퍼티를
조용히 무시하고, 스타터는 설정이 없어도 기본값으로 로그를 내보내므로 — **키를 틀려도
SQL은 보인다.** "로그가 나온다"는 사실은 설정이 맞다는 증거가 되지 못한다.

##### Controller 구현 원칙

1. **로직 없는 pass-through** - 저장하고 그대로 돌려준다. 계산이 필요한 시나리오는
   skeleton 대상이 아니다 — 하드코딩할 로직 자체가 없을 만큼 얇은 시나리오를 고른다
2. **절차적/명령형 스타일** - 하나의 메서드에 모든 로직 작성, 메서드 추출이나 클래스 분리 금지
3. **Feature Envy 허용** - Controller가 모든 로직 담당, 데이터 중심 설계로 시작
4. **예외 처리는 처음부터 분리** - `@RestControllerAdvice` 전역 핸들러에 둔다. 컨트롤러
   안에 `@ExceptionHandler`를 두지 않는다 — 컨트롤러가 늘어나면 같은 처리가 흩어진다.
   (이것은 2번 "메서드 추출 금지"의 예외가 아니라 배치 위치의 문제다)

##### 이후 단계와의 연결

아래 단계 번호는 Web App TDD 템플릿의 "전체적인 절차" 8단계(tdd skill의 템플릿
참조) 기준이다.

- **6단계 RGB 사이클**: 도메인 규칙은 repository 없는 단위 테스트로 성장시키고,
  저장이 필요한 테스트만 `inMemory` profile의 In-Memory 구현(Map 기반)을 사용
- **7단계 JPA Repository**: "처음 구현"이 아니라 **완성** — skeleton의 최소 JPA를
  성장한 도메인 전체를 커버하도록 확장하고, 같은 계약 테스트 스위트를 InMemory·JPA
  양쪽에 실행해 두 구현의 동등성을 검증한다 (in-memory가 JPA 의미론과 조용히
  어긋나는 드리프트 방지):

```java
abstract class BasketRepositoryContractTest {
    abstract BasketRepository repository(); // 구현별로 제공

    @Test
    void 저장_후_조회하면_동일_상태의_바구니를_돌려준다() { ... }
}

class InMemoryBasketRepositoryTest extends BasketRepositoryContractTest { ... }  // 매 빌드

@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)   // 없으면 임베디드 DB로 조용히 대체됨 — MySQL 검증 무력화
@Testcontainers
class JpaBasketRepositoryTest extends BasketRepositoryContractTest { ... }       // docker MySQL
```

- **인수 테스트 실행**: 별도 활성화 단계 없음 — 각 Green이 자기 시나리오의 `@pending`을
  같은 커밋에서 해제한다. 실행은 항상 `local` profile — in-memory로 인수 테스트를
  통과시키지 않는다

## FAILURE CONDITIONS

### 품질 체크리스트

단계 1~2 작성 후 다음 사항을 확인:

- [ ] 모든 기능이 User Story로 나열되었고, So that이 사용자 언어인가? (비었거나 시스템 내부 사정이면 작업 지시)
- [ ] 계산·절사 규칙의 근거(검산 전개)가 0층에 있는가? (Gherkin Examples에만 있으면 정본 부재)
- [ ] Gherkin이 핵심 예시만 담았는가? (경계·대표 예외 포함, 망라적 edge 나열 금지)
- [ ] 각 요구사항이 테스트로 검증 가능한가?
- [ ] 애매모호한 표현·상호 모순되는 요구사항이 없는가?
- [ ] UC Scenario 문서를 만들지 않았는가? (Gherkin Examples 표·`.feature` 실행이 대체)
