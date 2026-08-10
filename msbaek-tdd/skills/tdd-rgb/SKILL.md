---
name: tdd-rgb
description: TDD RGB 사이클 진행 - Red/Green/Blue agent 순차 위임. /tdd-rgb로 호출.
argument-hint: "[plan-doc-path] [--gear=low|mid|high]"
---

# TDD RGB 사이클 Skill

Red → Green → Blue 사이클을 조율하여 테스트 목록의 각 항목을 순차적으로 구현합니다.

## GOAL

- **성공 = 테스트 목록의 모든 항목이 `- [x]`로 완료되고, 모든 테스트가 통과하며, 작업 내역이 마크다운에 반영됨**
- 모든 테스트 케이스가 `- [x]`로 완료됨
- 모든 테스트가 통과함
- 작업 내역이 마크다운 파일에 반영됨
- (Web Usecase의 경우) High Level Test 활성화, JPA Repository 전환, DSL 개선까지 완료
- 검토 지점의 밀도는 기어(low/mid/high)가 정한다 — 아래 "기어(Gears)" 섹션 참조

## CONSTRAINTS

### Hard Rules

#### Three Laws of TDD

1. "Write NO production code except to pass a failing test."
2. "Write only ENOUGH of a test to demonstrate a failure."
3. "Write only ENOUGH production code to pass the test."

#### TDD 핵심 규칙

- don't write code without a failing test.
- only write the code necessary to get the test to pass (little golf game).
- never delete tests without express permission.
- 테스트를 추가할 때는 반드시 한번에 하나씩 추가. 실패하는 테스트가 있을 때는 절대 새로운 테스트를 추가할 수 없음.

#### 마이크로 사이클

각 단계는 **2-3분 이내** 작업으로 빠른 피드백을 받습니다.

- 복잡한 목표를 작은, 집중된, 검증 가능한 단계로 분해하여 순차적으로 실행
- 각 R/G/B 에이전트가 작업 완료 후 자체적으로 커밋을 수행 (커밋 → 피드백 → 다음 단계)
- 좁은 범위의 태스크는 AI의 강점을 발휘하게 하고, 조기 검증은 복잡성 누적을 방지

#### 피드백 규칙

- **기어가 정의하는 검토 지점에서 반드시 사용자 피드백을 요청하고 대기** ("기어(Gears)" 섹션의 검토 지점 표 참조)
- 검토 지점에서는 사용자가 명시적으로 다음 단계로 진행을 결정해야만 진행
- 검토 지점이 아닌 phase 경계(mid/high 기어)에서는 대기 없이 다음 phase로 진행하되, 커밋은 phase마다 정상 수행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."

### 기어(Gears) — 검토 밀도 조절

Kent Beck의 "driving in gears": 이론에 대한 확신(confidence)이 검토 지점의 밀도를 정한다.
**기어는 검토 지점의 밀도만 바꾼다** — TDD 3법칙, 한 번에 테스트 하나, phase별 커밋,
테스트 삭제 금지는 모든 기어에서 동일하다. phase별 커밋이 남으므로 어떤 기어에서도
테스트 단위 revert가 가능하다.

#### 기어별 검토 지점

| 기어 | 검토 지점(사용자 피드백 대기) | 대응 상황 |
|---|---|---|
| **low** (기본) | Red 후 · Green 후 · Blue 후 | 이론에 확신 없음, 낯선 도메인·기술, 학습 목적 |
| **mid** | 테스트 1개의 R→G→B 사이클 완료 후 1회 | 유사 문제 경험 있음, 작동하는 이론을 빠르게 확보할 것으로 기대 |
| **high** | 전체 테스트 목록 완료 + 적대적 리뷰 통과 후 최종 1회 | 이론이 상용구(boilerplate) 수준으로 명확 |

`--gear` 미지정 시: 템플릿 문서 진행 기록에 기어 기록이 있으면 그 기어로 복원, 없으면 low.

#### 기어 전환 — 신호와 제안

사이클 사이에 아래 신호를 점검하고, 감지 시 전환을 **제안**한다. 결정은 항상 사용자.

**업시프트 신호** (low→mid, mid→high):

- 최근 2~3 사이클 연속 사용자 피드백이 "그대로 진행"뿐이었음
- Blue phase에서 새로운 통찰이 더 이상 나오지 않음 (설계 안정)
- 남은 테스트가 기존 패턴의 반복

업시프트 제안 문구에 반드시 포함: "지루함은 업시프트를 얻어냈다는 정직한 신호지만, 조급함은 그렇지 않습니다."

**다운시프트 신호** (high→mid, mid→low):

- revert 발생
- 예상과 다른 이유의 테스트 실패 반복
- 구현이 불투명 — 사용자 이견·질문 반복
- Green phase에서 최소 구현 범위를 넘는 코드 생성 감지

#### 폭발 반경(blast radius) 경고

시작 시와 업시프트 제안 전에 대상 코드 영역에서 high-stakes 신호를 점검한다:
인증/인가, 결제/금액 계산, 데이터 삭제·변경(마이그레이션), 외부 API 호출, 동시성.

감지 시 경고: "이 작업은 폭발 반경이 큽니다({영역}). 확신이 높아도 한 단 낮은 기어를
권장합니다. 틀릴 확률이 낮아도 틀렸을 때 비용이 큽니다." 경고 후 결정은 사용자.
high-stakes 영역에서는 업시프트 제안을 억제한다 (다운시프트 제안은 정상 동작).

#### 기어 기록

템플릿 문서 진행 기록 섹션에 현재 기어와 전환 이력을 남긴다:

```
기어: mid (사이클 7에서 low→mid, 사유: 설계 안정)
```

기어 변경(시작 지정 포함) 시마다 갱신한다. high 기어 자율 진행 시작 시에는 현재 HEAD
해시도 함께 기록한다 (적대적 리뷰 diff 기준점):

```
기어: high (사이클 12에서 mid→high, 사유: 남은 테스트가 패턴 반복) / 시작 커밋: abc1234
```

### Principles

#### Interface/Implementation Split — TDD 설계의 두 축

> TDD를 논의할 때 사람들이 하는 **첫번째 오해**는 "모든 설계를 하나로 묶어야 한다"고
> 생각하는 것이다. TDD에는 **2가지 종류의 설계**가 있다. — Kent Beck

| 설계 유형 | 언제 | 누가 | 핵심 질문 |
|---|---|---|---|
| **인터페이스 설계** | 테스트 목록 작성, 테스트 코드 작성 시 | Red Phase | "이 행위가 외부에서 어떻게 호출되어야 하는가?" |
| **구현 설계** | 리팩토링 시 | Blue Phase | "이 행위를 내부적으로 어떻게 구현할 것인가?" |

##### Red Phase = 인터페이스 설계 단계
- 테스트를 작성할 때 내리는 설계 결정은 주로 **인터페이스 설계(interface design)**
- 오퍼레이션의 **완벽한 인터페이스(Model Client)**를 상상
- 가능한 **최선(best possible)의 API에서 시작**해서 거꾸로 작업
- 지금 오퍼레이션이 **외부에서 어떤 식으로 보일 지**에 대한 이야기를 테스트 코드에 적는 것
- 처음부터 일을 복잡하고 보기 흉하며 "현실적"이게 하는 것보다 낫다

##### Green Phase = 설계 없음, 오직 동작
- **문제를 이해**하고 **이슈를 파악**하는 단계
- **빠르게 성공시키는 것이 모든 것을 지배**
- Duct Tape Programming을 해서라도 빠르게 동작하도록
- 이렇게 구현을 해 봐야 문제를 제대로 이해할 수 있음

##### Blue Phase = 구현 설계 단계
- 리팩토링 시 내리는 설계 결정은 **구현 설계(implementation design)**
- 테스트 목록 작성 시 구현 설계 결정을 혼합하면 안 됨
- **내부 구현을 어떻게 설계할 지 결정할 시간은 나중에 충분히 있음**
- 테스트 목록 작성에만 집중하면 테스트 목록을 더 잘 작성할 수 있음

---

#### Test Desiderata

Kent Beck의 Test Desiderata — 좋은 테스트가 갖춰야 할 12가지 속성.
테스트 작성 시(Red phase) 이 속성들을 기준으로 품질을 검토합니다.

> "Tests should be **coupled to the behavior of code** and **decoupled from the structure of code**."

| 속성 | 설명 |
|------|------|
| **격리성(Isolated)** | 실행 순서에 관계없이 동일한 결과 반환 |
| **조합 가능성(Composable)** | 1개든 1,000,000개든 동일한 결과 |
| **신속성(Fast)** | 빠르게 실행 |
| **신뢰성(Inspiring)** | 통과하면 배포 자신감 제공 |
| **작성 용이성(Writable)** | 테스트 작성 비용이 저렴 |
| **가독성(Readable)** | 테스트 작성 동기를 전달 |
| **동작 중심성(Behavioral)** | 동작 변화에 민감 |
| **구조 비민감성(Structure-insensitive)** | 구조 변경에 둔감 |
| **자동화(Automated)** | 인간 개입 없이 실행 |
| **구체성(Specific)** | 실패 시 원인이 명확 |
| **결정론적(Deterministic)** | 변경 없으면 결과도 불변 (shared fixture 주의) |
| **예측성(Predictive)** | 모든 테스트 통과 = 프로덕션 적합 |

---

#### Mocking 가이드라인

모킹(Mocking)은 테스트에서 자주 사용되는 기법이지만, 잘못 사용하면 오히려 테스트를 취약하게 만들 수 있습니다. 이 문서에서는 모킹이 허용되는 대상과 상황, 그리고 주의해야 할 사항을 정리합니다.

##### 1. 모킹이 허용되는 대상

###### 1.1 비용이 높은 자원과 공유 자원

- **상황**: "mocks are useful when a resource is expensive to create and represents a shared fixed a problem"
- **예시**: 데이터베이스나 외부 서비스 등 생성하기 비용이 큰 자원
- **이유**: 테스트 속도 개선과 테스트 간 격리를 위해

###### 1.2 새로운 API 경계 발견 시(service, port out)

- **상황**: 리팩토링 중 새로운 공개 API를 식별했을 때
- **인용**: "that's probably an appropriate time to think about a mock for use in your test and later go and implement that other part your API that you're currently missing"
- **의도**: 아직 구현되지 않은 API의 사용 방식을 설계하기 위해

###### 1.3 모킹해야 할 대상

- API의 일부인 다른 public 클래스들
- perimeter(경계)에 있는 컴포넌트들
- 특정 API 부분을 다룰 때, 테스트 대상이 아닌 다른 API 부분들

Ian Cooper는 모킹해야 할 대상을 다음과 같이 명확히 제시합니다:

- **other application service, driven port 정도만 mocking해야**

##### 2. 모킹 사용 시 주의사항

###### 2.1 모킹을 피해야 할 대상 - Mock Roles, not Objects

- **내부 구현을 Mock으로 만들지 말고, 모듈의 경계면을 Mock으로 대체해야(Mock Roles not Objects)** 합니다.
- **Mock은 구현 디테일과 테스트가 엮이는 것을 방지하기 위해 사용해야** 합니다.

구체적으로:

- **내부**는 Mock으로 만드는 게 아닙니다.
  - **Mock을 통해서 구현 디테일과 테스트가 엮이게 되거든**요
- **Don't mock internals** - they come from _refactoring_. No peering behind the curtain don't mock implementation details
- **다른 모듈의 Port**나 **공개된 인터페이스**를 Mock으로 대체하세요. 저 경계면에 있는 것들이 효과적으로 Mock으로 만들 수 있는 것입니다.

###### 2.2 타사 코드 모킹 주의 - Only Mock Types You Own

1. 3rd party 코드를 mocking하면 테스트 코드가 *복잡*해지고 **구현 세부사항과 밀접하게 결합**됩니다.
2. 이는 _관심사의 분리, 추상화, 캡슐화 등 좋은 소프트웨어 설계 원칙을 위반_ 합니다.
3. TDD 관점에서 _테스트 작성을 어렵게_ 만들고 _리팩토링을 방해_ 합니다.
4. 대신 3rd party 라이브러리에 대한 얇은 **추상화 계층**을 만들어 사용하는 것이 좋습니다(**JPA Repository**를 mocking하지 않고 그 앞에 추상화 계층을 두어야 하는 이유)

다음 원칙을 따르는 것이 좋습니다:

1. "**Only Mock Types You Own**" (자신이 소유한 타입만 모킹하기)
   - *변경 가능한 코드만 모킹*해야 함
   - 외부 라이브러리는 얇은 래퍼로 감싸서 모킹
   - 도메인 개념으로 추상화하여 의존성 관리
1. "**Specify as little as possible in a test**" (테스트에서 최소한의 명세만 하기)
   - _실제 요구사항을 반영하는 동작만 검증_
   - 구현의 부산물인 동작은 검증하지 않기

##### 3. 경계 객체 테스트와 모킹

###### 3.1 경계 객체란?

경계 객체(Boundary Objects)는 시스템이 외부 세계와 상호작용하는 지점에 위치한 객체를 의미합니다:

- 데이터베이스 접근 레이어 (Repository, DAO 등)
- 외부 API 클라이언트
- 파일 시스템 인터페이스
- 메시징 시스템 연동 클래스
- 네트워크 통신 컴포넌트

###### 3.2 "Don't use mocks to test boundary objects" 원칙

경계 객체는 모킹보다 통합 테스트가 적합합니다:

- 실제 환경과 최대한 유사하게 테스트
- 외부 의존성은 모킹하되, 경계 객체 자체는 모킹하지 않음
- HTTP 요청/응답, DB 쿼리, 직렬화 등의 실제 동작을 검증

경계 객체를 모킹하지 말아야 하는 이유:

- **취약한 Mock들**: 실제 외부 시스템의 동작이 변경되면 Mock들이 테스트를 깨뜨릴 수 있음
- **제한적인 테스트 신뢰성**: Mock은 프로덕션에서의 실제 동작을 정확하게 반영하지 못할 수 있음
- **실제 시나리오**: 실제 외부 시스템과 통합해야 네트워크 장애, 데이터베이스 오류 등의 엣지 케이스를 테스트할 수 있음
- **유지보수 오버헤드 감소**: 실제 시스템에 의존하면 외부 시스템 변경 시 Mock을 지속적으로 업데이트할 필요가 없음
- **상호작용 테스트**: 경계 객체 테스트의 주된 목표는 외부 시스템과의 올바른 상호작용 확인임

중요 원칙:

- **Don't mock adapters - mock ports, not things we don't own**

예시:

- UserService를 테스트할 때는 UserRepository를 mocking
- UserRepositoryImpl을 테스트할 때는 DB를 Mocking하지 말고 통합 테스트 수행

##### 4. 모킹의 위험성과 제약 사항

###### 4.1 구현 디테일과의 결합

- 모킹이 과도하면 테스트가 코드의 내부 구현과 강하게 결합됨
- 이는 리팩토링 시 테스트 코드도 함께 변경해야 하는 문제 발생

###### 4.2 취약한 테스트

- 코드 구현이 조금만 변경되어도 테스트가 깨질 수 있음
- Kent Beck: "과도한 모킹은 코드의 구조적 민감성을 증가시킨다"

###### 4.3 단위 테스트 개념의 오해

- 단위 테스트는 "테스트 대상을 격리"하는 게 아닌 "테스트 자체를 격리"하는 것
- "the unit of isolation is the test not the thing under test"

##### 5. 모킹 관련 안티패턴

###### 5.1 절대 금지되는 모킹 패턴

**클래스 격리를 위한 모킹**

- **강한 경고**: "don't mock internals processor adapters"
- **원인**: "the unit of isolation is the test not the thing under test"
- **잘못된 인식**: "these all have to be mocks you can't interact with anything else you got a mock all the classes dependencies right because otherwise it's not a proper unit test
  you are wrong"

**주니어 개발자 감시용 모킹**

- **명확한 거부**: "especially don't do this thing where effectively you say I'm going to make sure junior developers have done the right thing by by mocking I forced them to use
  mocks so I can see how they implemented the method"
- **결과**: "couples your test to your software means you can't change it"

###### 5.2 최악의 모킹 관행들

다음은 피해야 할 안티패턴들입니다:

- Mocks returning Mocks: 모킹 체인은 복잡성을 증가시키고 취약함
- Mock data objects (Entities, Value Objects, ...): 데이터 객체는 모킹 대신 실제 객체 사용
- Too many mocks: 테스트에서 과도한 모킹은 취약성을 증가시킴
- Partial Mocks: 객체의 일부만 모킹하는 것은 혼란 야기
- Static 메서드 모킹: 정적 메서드 모킹은 테스트 구조를 복잡하게 만듦
- stubbing한 메서드 verify: CQS(Command Query Separation) 원칙 위반
- 호출 횟수 검증: 구현 디테일에 지나치게 의존하게 됨
- Verify no extra call happen or never
- Capture and assert every argument

static을 mocking해야 한다면 그건 static이 아니어야 합니다. too many mocks는 code smell입니다.

###### 5.3 Stubbing 검증의 문제

- **query를 stub(when). stubbing한 코드가 실제로 호출되었는지 verify할 필요 없음**
- 테스트에서 verify할 코드는 user의 상태에 기반하여 테스트한 코드(testedCode())가 무엇을 했는가 입니다.
  - 어떤 값을 반환하거나 예외를 발생시켰을 수 있다.
- **꼭 verify가 필요하다면 query(stubbing 대상)가 side effect을 유발하고 있어서임. CQS 위반. 동일 메소드를 stub, verify 한다면 CQS 위반**

##### 6. 효과적인 모킹 대안

###### 6.1 테스트 더블(Test Double)의 다양한 종류 활용

- **Dummy**: 행위 변경 없음, interface의 모든 메소드들이 `return null;`로 구현된 테스트 더블
- **Stub**: 특정 메소드 호출에 지정한 응답을 반환, dummy의 일종. 0이나 null 대신 테스트가 필요로 하는 특정 값을 반환
- **Spy**:
  - stub의 일종. 자신이 호출된 fact를 기억하고 후에 테스트에 이러한 fact를 보고
  - 어떤 함수가, 언제, 몇번, 어떤 인자로 호출되었는지 등
- **Mock**: interaction을 검증, spy의 일종으로 어떤 일이 일어나야 하는지를 아는 spy
- **Fake**: 대안 구현(memory repository impl. 등), simulator, 실세계 객체처럼 입력에 따라 다른 응답을 함. stubbing(when) 대신 실제와 유사한 로직 구현. verify 대신 실제 동작 결과를 검증. 특히 영속성 관련 코드에서 유용

###### 6.2 Fake 활용하기

- DB 대신 HashMap에 저장하는 것과 같은 테스트를 위한 구현
- **stubbing(when) 대신 save();**
- **verify 대신 실제 findAll 등을 호출해서 검증 가능**

Fake를 사용하면 모킹의 단점을 피할 수 있습니다:

- **중첩된 '페이크(fake)' 클래스는 인터페이스의 일부이며 인터페이스와 함께 제공됨**
- Fake를 사용한 _단위 테스트는 훨씬 짧아지고 유지보수성이 높아짐_

###### 6.3 클래스 간 협력에 초점 맞추기

- **통합테스트를 최대한 많이 작성하라. 아마 한 UC에 최대 7개 정도**
- 그러다 **복잡성이 높아서 통합테스트로 테스트하기 어려운 경우가 생김. 이럴 때만 구현의 상세를 단위 테스트로 검증**하라

##### 7. 실용적인 모킹 전략

###### 7.1 Mock Roles, Not Objects

- Mock Roles not Objects > _Role-based Design_
  - roles = dependencies
  - mocking할 대상의 역할을 점검해라
  - 그래고 테스트를 최대한 일찍 작성하라
  - 이걸 지켜야 리팩터링을 해도 mock test가 깨지지 않음

###### 7.2 테스트 단위의 올바른 이해

단위 테스트의 '단위'는:

- 메소드가 아님
- 완전한 유스케이스(a full use case)도 아님
- **동작(behavior)의 단위**(It's a unit of **behavior**) - **Kent Beck**, inventor of TDD, XP, Unit Testing
  - =격리된 상태로 테스트할 수 있는 기능의 최소 단위(the smallest part of a feature that you can test in isolation)
- 단위 테스트가 데이터베이스나 파일시스템과 통신하는 것도 괜찮음!(It's perfectly fine for _unit tests to talk to databases_ and filesystems!)
- 중요한 것은 각 테스트가 서로 격리되는 것임 (예: in-memory DB, Docker)(talk _as long as your tests are isolated_(from other tests) --> in-memory DB: Docker)

###### 7.3 모킹 프레임워크 사용 지침

- mock framework이 나쁜 것이 아니라 **mock을 작성하는 것은 정말 쉬워서 가독성을 높이기 위해 직접 작성하는 것이 더 좋을 수 있습니다**
- **필요할 때만 사용**하세요:
  - 모킹 도구는 매우 강력합니다 (protected된 final interface 오버라이드, private 변수/함수 접근 등)
  - 잘 설계된 시스템에서는 이런 강력한 기능이 거의 필요 없음
  - 레거시 시스템에서는 이러한 기능이 필요할 수 있음
- **mock이 계속해서 mock을 반환**하는 경우는 피해야 함
- 모킹 프레임워크는 **가능한 적게 사용**하는 것이 좋음
  - 앰블런스와 같이 - 필요할 때만!

###### 7.4 헥사고날 아키텍처에서의 모킹 전략

- 외부로 나가는 Adapter에 대한 테스트는 할 필요가 없음
- "Don't Mock What You Don't Own"
- **Adapter도 Mock으로 만들면 안됩**니다. **Adapter와 연계하는 Port를 Mock으로 만드세요**

##### 8. 함수형 접근으로 모킹 최소화

###### 8.1 함수형 코어/명령형 쉘 패턴

- stubbing 제거(given)
- mocking 제거(verify)
- 이 설계 원칙이 "Functional Core / Imperative Shell Segregation" 원칙임
- **복잡성에서 순수함수를 식별**하고 **의존성을 외부로 밀어냄**
  - 데이터 조회/저장 기능과 순수함수를 갖는 함수형 코어에 위임하는 기능을 분리
  - 테스트를 많이 만들려면 mock 사용을 줄여야 함. 그렇지 않으면 survive하지 못함
  - **Design the Most Complex Parts of Logic as Pure Functions**
    - 이해하고 테스트하기 더 쉬움

###### 8.2 소셜 테스트와 솔리터리 테스트 균형

- solitary test(mocking)는 잘 깨짐
- sociable test 테스트는 더 안정적임

###### 8.3 의존성 주입 활용 예

```java
// 항상 현재 날짜가 2023-01-15 반환
Supplier<LocalDateTime> fixedTimeProvider = () ->
    LocalDateTime.of(2023, 1, 15, 10, 0);

// 항상 프로모션 아님을 반환
Function<LocalDateTime, Boolean> notPromotionDay = time -> false;

// when
BigDecimal discount = discountService.applyDiscount(
    basket,
    fixedTimeProvider,
    notPromotionDay
);
```

###### 8.4 테스트 계층 구성

- 클래스 단위로 mocking하지 말고 component(하나 이상의 클래스) 단위로 mocking
- "Mock (Well-defined) Roles, Not Objects without a clear contract"
- Try to extract an interface from the class you want to mock!
- Redesign until that interface makes sense

##### 9. 클래시시스트 vs 모키스트 접근법

- Classic TDD (Inside-Out)
  - 상태 검증과 알고리즘에 초점
  - Kent Beck, Triangulation 기법 강조
  - 테스트가 구체화됨에 따라 코드가 일반화
  - 모킹 최소화 선호
- London School TDD (Outside-In)
  - 상호작용 검증 강조
  - 역할, 책임, 상호작용 중심
  - 메시지 패싱과 협력 객체 식별에 중점
  - 모킹을 통한 객체 간 상호작용 설계 강조
- DHH, Martin Fowler, Kent Beck은 "Is TDD Dead?" 행아웃에서 "거의 모킹을 하지 않는다"고 밝혔습니다
  - 자동화된 테스트 작성 시 과도한 모킹(mocking)과 스터빙(stubbing)의 사용에 대한 심각한 우려 제기
  - 특히 주목할 만한 점은 이 세 전문가 모두가 "거의 모킹을 하지 않는다"고 밝혔다는 것
- Kent Beck: Mock을 사용하지 않고도 테스트 가능한 설계 방법을 우선적으로 고려
  - "don't go very far down the mock path"
  - "Tests should not use mocks to isolate the SUT, so they are not unit tests!!!!"

##### 결론

- 모킹은 적절한 상황(공유 자원, 비용이 높은 자원, API 경계)에서만 사용하라
- 내부 구현 세부사항을 모킹하지 말고 모듈의 경계면에서 모킹하라
- 소유하지 않은 타입을 모킹하지 말고 추상화 계층을 통해 격리하라
- 상태 테스트를 선호하고 너무 많은 상호작용 테스트를 피하라
- 테스트의 깨지기 쉬움을 최소화하기 위해 모킹보다 실제 객체나 Fake 객체 사용을 고려하라
- 모킹 프레임워크는 필요할 때만 신중하게 사용하라
- 함수형 코어/명령형 쉘 패턴을 적용하여 순수 함수를 분리하고 모킹의 필요성을 줄이라

## OUTPUT FORMAT

### 실행 흐름

#### Step 1: 현재 상태 확인

1. 템플릿 문서(*.md)에서 unit test 목록 확인 (Cucumber 미사용 시 Gherkin 시나리오도 포함되어 programmer test와 섞임)
2. 첫 미완성 테스트(`- [ ]`) 식별
3. 현재 테스트 실행 상태 확인
4. **기어 결정**: `--gear` 파라미터 > 템플릿 문서의 기어 기록 > 기본 low 순으로 결정.
   폭발 반경 점검("기어(Gears)" 섹션)을 수행하고, high-stakes 영역이면 한 단 낮은 기어를
   권장하는 경고를 출력 — 경고를 출력한 경우 사용자의 기어 확정 응답을 기다린 뒤 진행.
   `--gear`로 명시 지정되었거나 문서의 기존 기록과 다를 때만 진행 기록을 갱신 —
   `--gear` 미지정 + 기록 없음이면 low로 동작하되 문서는 변경하지 않는다(하위 호환).

#### Step 2: RGB 사이클 실행

각 미완성 테스트(`- [ ]`)에 대해 다음 사이클을 반복:

##### Red 단계
- **tdd-red agent**에 위임
- 실패하는 테스트 작성
- approved.txt 파일 생성 (필요 시)
- 에이전트 내에서 `test:` 접두사로 커밋 수행
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### Green 단계
- **tdd-green agent**에 위임
- 최소 구현으로 테스트 통과
- TPP (Transformation Priority Premise) 적용
- Make-it-Work 전략 (Obvious / Fake it / Triangulation)
- 에이전트 내에서 `feat:` 접두사로 커밋 수행
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### Blue 단계
- **tdd-blue agent**에 위임
- Tidying Process — Composed Method 지향 리팩토링
  - 0. Guard Clauses (중첩 제거)
  - 1. One Pile (조건부 — Composed Method 위배 시)
  - 2. Reorder (Slide Statements)
  - 3. Chunk Statements
  - 4. Explaining Comment ← 필수1
  - 5. Extract Variable/Method ← 필수2
  - 6. Domain Logic 이동 (Advanced)
  - 7. Trimming (Advanced)
  - 8. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
- 변경이 있는 경우 에이전트 내에서 `refactor:` 접두사로 커밋 수행
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### 사이클 완료 시 (테스트 1개의 R→G→B 종료)

- **mid 기어**: 여기가 검토 지점 — 사이클 요약(테스트·구현·리팩토링)을 보고하고 사용자 피드백 대기
- **high 기어**: 대기 없이 다음 테스트로 진행
- **기어 전환 점검** (모든 기어): "기어(Gears)" 섹션의 업/다운시프트 신호를 점검하고,
  감지 시 전환을 제안 — 전환을 제안한 경우 사용자 응답을 기다린 뒤 진행한다(제안만
  출력하고 지나가지 않는다). 사용자가 수락하면 템플릿 문서의 기어 기록을 갱신하고
  다음 사이클부터 새 기어 적용

#### Step 3: 완료 처리
- 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 작업 내역을 마크다운 파일에 반영
- 다음 테스트 안내 또는 전체 완료
- **전체 완료 시 high 기어였다면**: Web Usecase의 경우 추가 단계(High Level Test 활성화·
  JPA Repository·DSL 개선)까지 완료한 뒤 적대적 리뷰를 실행한다 — 리뷰 diff가 전체
  구현을 포함해야 하기 때문. 최종 사용자 검토 전에 적대적 리뷰를 실행
  (아래 "high 기어: 적대적 리뷰" 섹션). green 스위트 + 적대적 리뷰 통과가
  high 기어의 Definition of Done

---

### 각 테스트 구현 절차 (Implement Each Test Rule)

새로운 테스트를 추가하고 코드를 구현할 때는 다음 절차를 따릅니다:

1. **실패하는 테스트 추가**
   - Test Desiderata 준수 (위 Test Desiderata 섹션 참조)

2. **최소한의 코드로 테스트 성공** (Little Golf Game)
   - Make-it-Work 전략 준수
   - TPP 규칙 준수
   - 하나의 테스트가 성공하면 javadoc comment의 테스트 항목에 완료 표시('X')

3. **작업 내역을 마크다운 파일에 반영**
   - 각 테스트에 대한 작업 내역을 `### n.x` 레벨로 추가
   - multiline git commit message 수준으로 작성
   - "gutter test 추가"처럼 제목을 달고, 빈칸 넣고, 주목할 내용 2~3줄
   - code는 markdown 파일에 추가하지 않음

4. **중복 제거** (필요한 경우 리팩터링)

5. **피드백 요청 (검토 지점일 때만)**
   - 검토 지점이면("기어(Gears)" 섹션의 검토 지점 표 참조) 피드백을 요청하고 대기:
     "이 테스트 구현에 대한 피드백을 주시겠어요? 특히 [구현 방식/테스트 명확성/코드 품질] 부분에 대해서요."
   - 검토 지점이 아니면 생략하고 다음으로 진행

---

### high 기어: 적대적 리뷰

high 기어에서 전체 테스트 목록이 green이 되면, 최종 사용자 검토 **전에** 반드시 실행한다.

#### 리뷰어 선택

1. 환경에 `adversarial-reviewer` agent가 있으면 그것으로 dispatch (1순위)
2. 없으면 general-purpose sub-agent에 아래 내장 프롬프트로 dispatch

내장 프롬프트 (fallback):

> 당신은 이 diff를 깨뜨리려는 적대적 리뷰어입니다. 평가하지 말고 공격하세요.
> 다음을 찾아 심각도(critical/major/minor)와 함께 보고하세요:
> 1. 테스트가 검증하지 않는 동작 (green이지만 커버되지 않은 경로)
> 2. 테스트 목록 문서와 구현의 표류(drift)
> 3. 최소 구현을 가장한 과잉 구현 (테스트가 요구하지 않는 코드)
> 4. 코드 스멜 (중복, 불명확한 이름, 긴 메소드)
> 각 지적에 구체적 실패 시나리오("이게 일어나면 → 저게 깨진다")를 붙이세요.

#### 입력

- 진행 기록의 시작 커밋..HEAD diff (`git diff {시작커밋}..HEAD`)
- 테스트 목록 문서 (intent 요약 — 리뷰어의 depth 보정에 사용)

#### 결과 처리

1. 지적 사항을 심각도별로 분류해 사용자에게 보고
2. 수정이 필요한 항목은 사용자 승인 후 반영 — 반영도 RGB 규칙 준수 (실패 테스트 먼저)
3. 리뷰 통과 후에야 최종 사용자 검토를 요청
   - **통과 기준**: critical/major 지적이 모두 해소(수정 반영 또는 사용자가 명시적으로 수용)된 상태

---

### Web Usecase 추가 단계

> 모든 테스트(`- [ ]` → `- [x]`)가 완료된 후 진행합니다.

#### High Level Test 활성화
- `@Disabled` 어노테이션 제거
- High Level Test가 성공하는지 확인
- 실패하는 경우 원인 분석 및 수정

#### JPA Repository 전환

Fake Repository로 모든 기능이 동작하면 JPA Repository를 작성:

1. **JPA Mapping**: Entity, Value Object에 대해 JPA Mapping 작성. 필요 시 inner class를 outer class로 분리
2. **JPA Repository Interface**: JpaRepository를 상속받는 인터페이스 생성
3. **Repository Impl**: BasketRepository를 구현하고 JPA Repository에 위임하는 구현 클래스 작성
4. **테스트 전환**: @TestConfiguration 부분을 커멘트 처리하여 실제 Repository 사용
5. **클래스 다이어그램**: Repository 관련 클래스들에 대해 mermaid 다이어그램 작성

주의사항:
- @TestConfiguration이 있으면 FakeRepository 사용, 커멘트 처리하면 JPA Repository 사용
- H2 데이터베이스 미사용 (spring-boot-docker-compose로 연결)

#### DSL 개선
- Protocol Driver 적용
- Test Data Builder 패턴 적용
- 가독성과 재사용성 향상

## FAILURE CONDITIONS

### 단계별 검증 체크리스트

#### 1. 테스트 작성 후 확인

- [ ] 테스트가 명확한 하나의 동작만 검증하는가?
- [ ] 테스트 이름이 검증하려는 내용을 명확하게 설명하는가?
- [ ] approved.txt 파일이 필요한 경우 작성되었는가?
- [ ] 테스트가 실행되고 예상대로 실패하는가?

#### 2. 구현 후 확인

- [ ] 테스트를 통과하는 가장 단순한 구현인가?
- [ ] make-it-work-strategy, TPP 규칙의 단계를 적절히 적용했는가?
- [ ] 불필요한 코드가 없는가?
- [ ] 모든 테스트가 통과하는가?

#### 3. 리팩토링 후 확인

- [ ] 중복이 제거되었는가?
- [ ] 코드가 더 명확해졌는가?
- [ ] 모든 테스트가 여전히 통과하는가?

#### 4. 전체 과정 후 확인

- [ ] 작업 내역이 마크다운 파일에 반영되었는가?
- [ ] 다음 단계 진행을 위한 피드백을 요청했는가?
- [ ] (high 기어) 적대적 리뷰를 실행하고 결과를 보고했는가?
- [ ] (high 기어) 시작 커밋 해시가 진행 기록에 있는가?
