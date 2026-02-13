---
name: tdd-plan
description: TDD Planning - SRS, 예제, 테스트 목록 작성. /tdd-plan으로 호출.
argument-hint: "[plan-doc-path]"
allowed-tools: Write, Edit, Read, Bash(git add:*), Bash(git commit:*), Bash(git status:*)
---

# TDD Planning Skill

Kent Beck의 TDD 원칙에 따라 구현 전 계획 문서를 작성하는 전문가입니다.
SRS → 예제 → 테스트 케이스 목록 순서로 진행하며, Web Usecase 유형에서는 High Level Test와 Walking Skeleton 단계가 추가됩니다.

## Document-Based Workflow

**반드시 프로젝트 템플릿 문서(*.md)와 함께 작업합니다.**

### Step 1: 템플릿 문서 찾기
1. TDD 템플릿 문서(절차 섹션이 있는 *.md) 찾기
2. 현재 단계 파악 (체크박스 상태로 확인)
3. 해당 섹션 내용 작성

### Step 2: 단계별 진행
- 각 단계 완료 후 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 기존 내용은 변경하지 않고 append only로 갱신
- 각 단계 완료 후 사용자 피드백 대기

---

## 단계 1: SRS 작성

### SRS 작성 지침

#### 목적
- TDD의 첫 번째 단계로서, 구현할 기능에 대한 명확한 요구사항 정의
- 테스트 작성의 기반이 되는 비즈니스 규칙과 제약조건 명시
- 경계 조건과 예외 상황을 포함한 완전한 동작 명세

#### 작성 형식

현재 markdown 파일의 SRS 섹션이 비어 있으면 아래 형식으로 작성:

```markdown
## 1. SRS(소프트웨어 요구사항 명세서) 작성

### [기능명] 규칙 및 요구사항

- 규칙
    - 기본 규칙
        - [기본적인 동작 방식과 제약조건]
    - 특별 규칙
        - [예외상황이나 특수한 경우의 처리방식]

- [기능별] 요구사항
    - [세부 기능 1]
        - [구체적인 요구사항 나열]
    - [세부 기능 2]
        - [구체적인 요구사항 나열]
    - 예외 처리
        - [예외 상황과 처리 방법]
```

#### SRS 작성 원칙

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

#### SRS 템플릿 구조

**기본 규칙**
- 핵심 비즈니스 로직과 제약조건
- 시스템의 기본 동작 방식
- 데이터 처리 규칙

**특별 규칙**
- 예외 상황 처리
- 경계 조건 처리
- 특수한 케이스의 동작

**기능별 요구사항**
- 입력 요구사항
- 처리 요구사항
- 출력 요구사항

#### SRS 샘플

```markdown
## BowlingGame 규칙 및 요구사항 예

- 규칙
    - 기본 규칙
        - 단일 플레이어가 10개의 프레임으로 구성된 1개의 게임을 진행
        - 각 프레임에서 플레이어는 최대 2번의 투구 기회를 가짐
        - 첫 투구에서 10개 핀을 모두 쓰러뜨리면 스트라이크(X)로 기록하고, 해당 프레임에서는 더 이상 투구하지 않음
        - 두 번의 투구로 10개 핀을 모두 쓰러뜨리면 스페어(/)로 기록
    - 마지막 프레임 특별 규칙
        - 10번째 프레임에서 스트라이크를 기록하면 추가로 2번의 투구 기회를 얻음
        - 10번째 프레임에서 스페어를 기록하면 추가로 1번의 투구 기회를 얻음
        - 10번째 프레임에서 오픈 프레임(스트라이크나 스페어가 아닌 경우)이면 추가 투구 없음
- 점수 계산 요구사항
    - 기본 점수 계산
        - 시스템은 각 투구마다 쓰러뜨린 핀 수를 입력받아 기록해야 함
        - 각 프레임의 기본 점수는 해당 프레임에서 쓰러뜨린 핀의 총 개수
    - 보너스 점수 계산
        - 스트라이크의 경우, 기본 10점에 다음 2번의 투구에서 쓰러뜨린 핀 수를 보너스로 추가
        - 스페어의 경우, 기본 10점에 다음 1번의 투구에서 쓰러뜨린 핀 수를 보너스로 추가
        - 오픈 프레임의 경우, 해당 프레임에서 쓰러뜨린 핀 수만 점수로 계산 (보너스 없음)
    - 총점 계산
        - 게임의 총점은 각 프레임 점수의 합계로 계산
        - 최대 가능 점수는 300점 (모든 프레임에서 스트라이크를 기록한 경우)
        - 시스템은 현재까지의 누적 점수를 각 프레임마다 계산하고 표시해야 함

## CreateShoppingBasket 요구사항 예

- 장바구니가 비어 있으면 청구서를 사용할 수 없습니다.
- 총 가격은 `단가 * 수량`의 합계입니다.
- 청구서에 장바구니의 모든 품목이 나열됩니다.
- 총 금액이 10,000 초과 시 5% 할인 제공
- 총 금액이 20,000 이상이면 10% 할인을 제공합니다.
```

#### 품질 체크리스트

SRS 작성 후 다음 사항을 확인:

- [ ] 모든 기능적 요구사항이 명시되었는가?
- [ ] 경계 조건과 예외 상황이 포함되었는가?
- [ ] 각 요구사항이 테스트 가능한가?
- [ ] 애매모호한 표현이 없는가?
- [ ] 상호 모순되는 요구사항이 없는가?

#### 작업 절차

1. 요구사항 수집 및 분석 - 사용자 요구사항 파악, 비즈니스 규칙 정의
2. 구조화된 SRS 작성 - 템플릿에 따른 체계적 작성
3. 검토 및 검증 - 완전성, 명확성, 일관성 검토
4. **사용자 승인 대기** - 피드백 요청 후 승인 시 다음 단계 진행
5. **커밋** - 승인 후 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: SRS 작성 - [기능명]"`

---

## 단계 2: 예제 작성

### 예제 작성 지침

#### 목적
- SRS에 정의된 요구사항을 구체적인 사용 사례로 설명
- 경계 조건과 예외 상황을 포함한 다양한 시나리오 제시
- 테스트 케이스 작성의 기반이 되는 명확한 예제 제공

#### 예제 구성 요소

**1. 기본 예제 (Happy Path)**
- 정상적인 입력과 예상되는 출력
- 가장 일반적인 사용 시나리오
- 핵심 비즈니스 로직 검증

**2. 경계 조건 예제**
- 최소/최대 값 경계
- 임계점에서의 동작
- 경계값 전후의 다른 결과

**3. 예외 상황 예제**
- 유효하지 않은 입력
- 시스템 제약 위반
- 에러 처리 시나리오

**4. 특수 케이스 예제**
- 도메인 특화 규칙 적용
- 복잡한 비즈니스 로직
- 여러 조건의 조합

#### 예제 작성 템플릿

```markdown
## 2. SRS를 잘 설명할 수 있는 예제 목록 작성

### [기능명] 예제 시나리오

- **예제1: [시나리오 이름]**
    - 입력: [구체적인 입력 값]
    - 기대 결과: [예상되는 출력]
    - 설명: [시나리오 설명]

- **예제2: [경계 조건 시나리오]**
    - 입력: [경계값 입력]
    - 기대 결과: [경계에서의 동작]
    - 설명: [경계 조건 설명]
```

#### 예제 샘플

```markdown
## BowlingGame 예

- 거터 게임 (모든 투구에서 0점)
    - 예시: 20번의 투구에서 모두 0개의 핀을 쓰러뜨린 경우
    - 기대 결과: 모든 프레임의 점수는 0점, 최종 점수도 0점

- 스페어 예제:
    - 예시: 첫 프레임에서 5, 5로 스페어, 다음 투구에서 8점, 이후 모두 0점
    - 기대 결과: 첫 프레임 점수는 18점(10+8), 두 번째 프레임은 8점, 최종 점수 26점

- 스트라이크 예제:
    - 예시: 첫 프레임에서 스트라이크, 다음 투구들이 3점, 4점, 이후 모두 0점
    - 기대 결과: 첫 프레임 점수는 17점(10+3+4), 두 번째 프레임은 7점, 최종 점수 24점

- 퍼펙트 게임:
    - 예시: 모든 프레임에서 스트라이크(12번의 투구)
    - 기대 결과: 모든 프레임 점수는 30점, 최종 점수 300점

- 복합 예제:
    - 예시: X, 9/0, X, 2/8, 7/0, X, X, 9/0, X, 8/2/9
    - 기대 결과: 각 프레임 점수 19,9,20,17,7,29,19,9,20,19, 총점 168점

## CreateShoppingBasket 예

- 예제1: 정확히 20,000원 - 10% 할인 적용
    - 스마트폰 케이스 1개 (단가: 15,000원, 총액: 15,000원)
    - 보호필름 1개 (단가: 5,000원, 총액: 5,000원)
    - 소계: 20,000원
    - 할인: 2,000원 (10% 할인)
    - 최종 결제 금액: 18,000원

- 예제2: 10,000원 초과 20,000원 미만 - 5% 할인 적용
    - 스마트폰 케이스 1개 (단가: 12,000원, 총액: 12,000원)
    - 보호필름 1개 (단가: 5,000원, 총액: 5,000원)
    - 소계: 17,000원
    - 할인: 850원 (5% 할인)
    - 최종 결제 금액: 16,150원

- 예제3: 10,000원 이하 - 할인 없음
    - 보호필름 2개 (단가: 5,000원, 총액: 10,000원)
    - 소계: 10,000원
    - 할인: 0원 (할인 없음)
    - 최종 결제 금액: 10,000원

- 예제4: 빈 장바구니 - 청구서 발행 불가
    - 시스템은 적절한 오류 메시지와 함께 예외를 발생시켜야 합니다.
```

구현할 로직과 무관한, 중복되는 예제가 있다면 제거합니다. 최대한 간결하게 유지합니다.

#### 경계 조건 식별 가이드

1. **수치적 경계** - 0, 1, 최대값, 최소값, 임계점 전후 값, 음수/양수 경계
2. **크기 경계** - 빈 컬렉션/최대 크기, 문자열 길이 제한
3. **상태 경계** - 초기 상태/완료 상태, 활성/비활성, 유효/무효
4. **시간 경계** - 시작/종료 시점, 타임아웃, 순서 의존성

#### 경계 조건 샘플

- BowlingGame 예: gutter game, spare, strike, perfect game 등을 고려
- CreateShoppingBasket: 2만원 이상, 2만원 미만 1만원 초과, 1만원 이하, 하나의 상품이 1개만 담겨서 단가가 총계이면서 할인이 적용 안된 경우, 빈장바구니인 경우 등을 고려

#### 작업 절차

1. SRS 요구사항 분석 - 핵심 비즈니스 규칙 식별
2. 시나리오 설계 - Happy path, 경계 조건, 예외 상황
3. 예제 구체화 - 실제 도메인 데이터 사용
4. **사용자 승인 대기** - 피드백 요청 후 승인 시 다음 단계 진행
5. **커밋** - 승인 후 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: 예제 작성 - [기능명]"`

---

## 단계 3: 테스트 케이스 목록

### 테스트 추가 규칙 (Test Addition Rule)

```
- 절차
  - most simple and degenerate(special)에서 시작
    - null, empty, 0, boundary, simple stuff 등과 같은 special case
  - 다음 단계로 interesting 하지만 조금 덜 degenerate한 failing 테스트 케이스(단일 아이템, 최소 유효 값 등)를 점진적으로 추가
  - test를 추가할 때는 특별한 이유가 있는 경우가 아니면 failing test만 추가. 모델 코드를 수정하지 않아도 성공하는 테스트는 추가하지 말아줘
     - TEST SHOULD FAIL WHEN YOU ADD IT
  - 마지막에 most interesting(general), 복잡한 테스트 케이스(복잡한 비즈니스 로직. 다중 할인 계산, 경계 값 케이스 등)를 추가해줘
```

### Programmer Test 규칙 (FIRST 원칙)

1. **Fast** - 테스트는 빠르게 실행되어야 함
2. **Deterministic** - 동일한 조건에서 항상 동일한 결과
3. **Predictive** - 모든 test가 성공하면 배포했을 때 문제 없어야 함
4. **Behavior change에 민감, structure change에 둔감**
   - 사용자에게 가치를 제공하는 external behavior에 coupled
   - 리팩터링시 변경되는 internal structure에 decoupled
5. **Cheap to write** - 테스트 작성 비용이 적어야 함
6. **Cheap to read** - 테스트 코드가 명확하고 이해하기 쉬워야 함
7. **Cheap to change** - 하나의 동작 변경으로 인해 실패하는 테스트가 다수이면 안됨

### 테스트 케이스 작성 템플릿

```markdown
## 3. 테스트 케이스 목록 작성

### [기능명]을 위한 테스트 리스트

가장 단순한 특수 케이스(degenerate)에서 일반적인 케이스(general)로 진행하는 테스트 리스트:

- [ ] [가장 단순한 degenerate case]
- [ ] [기본적인 단일 요소 case]
- [ ] [경계 조건 case]
- [ ] [일반적인 비즈니스 규칙 case]
- [ ] [복잡한 종합 case]
```

### 테스트 케이스 목록 샘플

```markdown
## Bowling Game을 위한 테스트 리스트

- [ ] gutter game
- [ ] all ones(모든 프레임에서 핀을 한개만 쓰러뜨린 경우)
- [ ] one spare(하나의 프레임만 스페어 처리하고, 다른 프레임은 open인 경우)
- [ ] one strike(하나의 프레임만 스트라이크 처리하고, 다른 프레임은 open인 경우)
- [ ] perfect game

## 쇼핑 카트 테스트 케이스 리스트

- [ ] 빈 장바구니에서 청구서 요청 시 예외 발생
- [ ] 단일 상품을 1개만 장바구니에 추가 (할인 없음, 10,000원 이하)
- [ ] 10,000원 초과 20,000원 미만 구매 시 5% 할인 적용 (여러 상품)
- [ ] 정확히 20,000원 구매 시 10% 할인 적용
- [ ] 20,000원 초과 구매 시 10% 할인 적용 (여러 상품)
```

### JavaDoc 형식 테스트 목록 샘플

테스트 클래스 최상단에 Java 23 마크다운 형식 커멘트로 테스트 목록 추가:

```java
/// - [ ] gutter game
/// - [ ] all ones
/// - [ ] one spare
/// - [ ] one strike
/// - [ ] perfect game
```

### External Behavior 테스트 케이스 샘플

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

### 중복 제거 기준
- 비즈니스 규칙과 무관한 중복되는 테스트 케이스 제거
- 동일한 비즈니스 규칙이 적용되는 테스트 케이스는 합치거나 제거
- 구현하려는 코드가 어떻게 동작해야 하는지 알고 있는 시나리오들을 나열

### 작업 절차

1. 예제 분석 - 핵심 시나리오 식별, 경계 조건 파악
2. 테스트 순서 결정 - Degenerate → Simple → Interesting → General
3. 테스트 목록 정제 - 중복 제거, 누락 확인
4. 체크박스 업데이트
5. **커밋** - 변경된 파일 커밋
   - `git add [변경된 파일들]` (git add -A 금지)
   - `git commit -m "docs: 테스트 케이스 목록 작성 - [기능명]"`
6. **"/tdd-rgb 실행하세요" 안내** (General TDD의 경우)

---

## Web Usecase 추가 단계

> 다음 단계들은 TDD 유형이 `web-usecase`일 때만 진행합니다.

### 단계 E-1: High Level Test 작성

#### High Level Test 규칙

- 대표 예제 선택: 예제 중에서 요구사항의 제약 조건을 가장 많이 충족하는 경우(most general한 경우)를 선택
- 이 예제를 통해 구현할 기능이 어떻게 사용되는지 감을 잡고, 어떤 결과를 갖게 될지 계획과 목표(Target Design)를 가지고 진행

#### Act-Assert 동일 추상화 수준 규칙

- 테스트에서 act와 assert는 같은 추상화 수준에서 이루어져야 함
- 한 테스트 내에서 서로 다른 추상화 레벨 혼합 금지
- api를 호출하여 행동을 수행하고, 같은 api 레벨에서 결과를 검증
- 예: post로 생성하고 get으로 검증하는 방식

#### High Level Test 코드 샘플

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

#### DSL 개선 목표

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

#### Protocol Driver

- Protocol Drivers (PDs)는 DSL에서 시스템 언어로의 번역자/어댑터
- DSL의 인터페이스를 미러링하되 더 구체적인 파라미터 사용
- SUT와의 각 통신 채널별로 최소 하나의 PD 생성
- 모든 테스트 인프라스트럭처 지식을 여기에 격리

#### Mermaid 클래스 다이어그램

테스트에 나타나는 도메인 클래스들에 대해 러프한 클래스 다이어그램 작성:
- SRS 기반 정적분석으로 domain class, value object 식별
- class, attributes, relation만 표현
- 금액 계산과 같은 행위 관련 부분은 추가하지 않음 (나중에 리팩터링을 통해 추가)

#### @Disabled 처리
- 초기에는 `@Disabled("아직 기능 구현이 완료되지 않았습니다.")` 추가
- 모든 단계별 테스트 완료 후 활성화

---

### 단계 E-2: Walking Skeleton 구현

#### Walking Skeleton 목적
- End-to-end 아키텍처의 기본 골격 구현
- Controller부터 Repository까지 전체 레이어 연결
- 실제 기능보다는 구조적 연결성 검증

#### Walking Skeleton 테스트 샘플

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

#### Fake Repository 규칙

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

#### Controller 구현 원칙

1. **Fake it 적용** - 복잡한 계산은 하드코딩으로 처리, 최소한의 구현
2. **절차적/명령형 스타일** - 하나의 메서드에 모든 로직 작성, 메서드 추출이나 클래스 분리 금지
3. **Feature Envy 허용** - Controller가 모든 로직 담당, 데이터 중심 설계로 시작

---

## 완료 조건

- 해당 단계의 체크박스가 업데이트됨 (`- [ ]` → `- [x]`)
- 다음 단계 안내가 제공됨

## 피드백 규칙

- 한 단계에서 관련된 코드를 생성한 후에는 반드시 사용자에게 피드백을 요청
- 사용자가 명시적으로 다음 단계로 진행하는 것을 결정해야만 다음 단계로 진행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."
