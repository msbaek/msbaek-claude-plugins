# 단계 E-1: 인수 테스트 셋업 (.feature + Runner)

> `tdd-plan` 스킬의 참조 문서 — TDD 유형이 `web-app`일 때만 진행한다.

## 규칙

Web App은 `/cucumber-acceptance`가 **필수**다. 리뷰에서 승인된 Gherkin 초안이 그대로
`.feature`로 실행되어 인수 계층을 담당하므로, **별도 High Level Test(JUnit)를 만들지
않는다** — 같은 검증이 두 계층에 중복되면 안 된다(`cucumber-acceptance`의 Hard Rule).

- `/cucumber-acceptance`를 호출해 `.feature` + Runner + Steps + Protocol Driver를 셋업
- 미구현 시나리오는 `@pending` 태그로 제외 — 4단계 RGB 사이클에서 각 Green이 자기
  시나리오의 태그를 같은 커밋에서 해제한다. `@Disabled` 일괄 토글이 아니라
  **시나리오 단위 해제**다. `Scenario Outline`의 Examples 행이 여러 규칙에 걸쳐 있으면
  블록을 쪼개 더 작은 단위로 해제한다 — `cucumber-acceptance`의 "Scenario Outline —
  Examples 블록 단위로 쪼개 한 걸음씩 해제" 참조 (전부 green이 되면 한 블록으로 합친다)
- Target Design(구현될 API 형상)은 Protocol Driver가 확정한다 — Steps는 파싱·위임만
- 대표 예제(most general한 시나리오)는 별도 테스트가 아니라 `.feature`의 한 시나리오다

> **탈출구**: 프로젝트 제약(의존성 정책 등)으로 Cucumber를 도입할 수 없는 경우에만,
> 대표 시나리오 1개를 JUnit 인수 테스트(`@Disabled`로 시작 → 구현 완료 후 활성화)로
> 작성해 대체한다. 이때도 나머지 절차는 동일하다.

## 전체 출력 잠금이 필요하면 — Approvals를 Step에 둔다

> 이 절은 **배치 문제**(Approvals를 어디에 두는가, 승인 파일명을 어떻게 가르는가)를
> 다룬다. Approvals를 **언제 쓰는가**의 판단 기준과 두 종류 승인(와이어 포맷 /
> 도메인 출력)의 구분은 `tdd-red` 에이전트의 "Approved Text Rule"이 정본이다.

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

## Gherkin 시나리오 샘플

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

## DSL 개선 목표

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

## Protocol Driver

- Protocol Drivers (PDs)는 DSL에서 시스템 언어로의 번역자/어댑터
- DSL의 인터페이스를 미러링하되 더 구체적인 파라미터 사용
- SUT와의 각 통신 채널별로 최소 하나의 PD 생성
- 모든 테스트 인프라스트럭처 지식을 여기에 격리

## Mermaid 클래스 다이어그램

테스트에 나타나는 도메인 클래스들에 대해 러프한 클래스 다이어그램 작성:
- 요구사항(도메인 규칙 + User Story) 기반 정적분석으로 domain class, value object 식별
- class, attributes, relation만 표현
- 금액 계산과 같은 행위 관련 부분은 추가하지 않음 (나중에 리팩터링을 통해 추가)

## 미구현 시나리오 처리
- 초기에는 `@pending` 태그로 실행에서 제외 (Runner 설정에서 `not @pending`)
- 각 Green 단계가 자기 시나리오의 태그를 같은 커밋에서 해제 — 일괄 활성화 단계는 없다
- (탈출구로 JUnit 인수 테스트를 쓰는 경우에만) `@Disabled("아직 기능 구현이 완료되지
  않았습니다.")`로 시작해 구현 완료 후 제거

