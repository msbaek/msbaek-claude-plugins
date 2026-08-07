---
name: cucumber-acceptance
description: 기능의 external behavior를 Cucumber 인수 테스트(주 검증층)로 구축 — .feature 실행으로 문서↔코드 드리프트를 구조적으로 차단, Four Layer(Steps→Protocol Driver→SUT), 태그 기반 가역 제외, 기존 JUnit 인수 테스트 이관. "인수 테스트 도입", "Gherkin을 실행 가능하게", "cucumber 셋업" 요청 시 사용. /cucumber-acceptance로 호출.
argument-hint: "[feature 설명 또는 요구사항 문서/.feature 경로]"
---

# Cucumber Acceptance — 실행 가능한 명세를 주 검증층으로

## GOAL

- **성공 = 요구사항의 Gherkin 시나리오가 `.feature` 파일로 실행되어, 기대 수치가 코드와 어긋나면 빌드가 깨지는 상태**
- 기능의 external behavior(고객이 사용하는 것과 기능)를 Cucumber가 **주 검증층**으로 담당 — programmer test 역할까지 겸한다
- 더 세밀한 검증(분기 커버리지·내부 협력)은 JUnit·Mockito가 **보조**
- 문서와 코드의 기대값 드리프트가 구조적으로 불가능해짐 — 파생 뷰가 어긋나면 조용히 남지 못하고 빌드가 깨진다

## CONSTRAINTS

### Hard Rules — 테스트 전략 위계

| 검증 대상 | 도구 | 근거 |
|---|---|---|
| **external behavior** (고객이 쓰는 것과 기능) | **Cucumber `.feature`** (주 검증층) | 비개발자(+AI) 독자가 리뷰하는 실행 계약 |
| **세밀한 분기** (null/blank/미매핑 등 커버리지) | JUnit·Mockito (보조) | Gherkin에 넣으면 산문이 소음 |
| **property-based** ("모든 입력에 대해 성립") | jqwik 등 | Gherkin은 형식 자체가 example-based |
| **문제 도메인의 언어가 코드인 경우** (직렬화·동시성·성능) | 각자의 도구 | "외부 사용자 관점의 도메인 언어"가 성립 안 함 |

- **Gherkin에는 핵심 예시(key examples)만** — 망라적 edge를 시나리오로 나열하면 시나리오 폭발(Specification by Example의 규율). 커버리지용 분기는 programmer test로.
- **Protocol Driver 분리** (Dave Farley Four Layer SoC): Steps(글루)는 파싱·위임만, SUT와의 실제 상호작용은 Driver에 격리. step definition에 SUT 호출·HTTP·UI 코드를 직접 넣지 않는다.
- **주 검증층은 빨라야 한다**: in-process driver 우선. Cucumber가 programmer test 역할을 겸하려면 이 전제가 필수다. 채널이 바뀌어도(HTTP·UI) Steps는 불변, Driver만 교체.
- **실행 불가능한 시나리오는 삭제하지 말고 태그로 제외** — 문서 가치는 남기고 실행만 빼는 가역적 처리.
- **숫자의 정본 관계를 문서에 선언**: 검산 근거(왜 이 값인가)는 스펙 문서, `.feature`는 그 수치를 실행으로 강제하는 인수 게이트.

## 적용 패턴

### 도입 시점 — 두 가지

| 시점 | 방식 | 적합 |
|---|---|---|
| **구현 후 이관** (기본) | 기존 JUnit 인수 테스트를 `.feature`로 이관 — 아래 "기존 JUnit 인수 테스트 이관" 절차 | 이미 구현·테스트가 있는 프로젝트 |
| **acceptance-first** (선택) | `tdd-plan` 단계 2의 Gherkin을 plan 합의 직후 `.feature` + Runner로 셋업. 미구현 시나리오는 `@pending`으로 두고, RGB가 진행되며 하나씩 태그 해제·green — 태그 해제는 그 시나리오를 통과시킨 Green 단계가 같은 커밋에서 수행한다 | plan부터 시작하는 신규 기능 — 외부 인수 루프 + 내부 TDD 루프의 이중 루프(Dave Farley) |

### 구조 — Four Layer 축소형

```
.feature (Test Case — 문제 도메인 언어)
   ↓
Steps (DSL/글루 — 텍스트 파싱 + Driver 위임만)
   ↓
Protocol Driver (SUT 상호작용 격리 — in-process/HTTP/UI 중 택일)
   ↓
SUT
```

```java
// Steps: 파싱만 하고 위임한다
public class CheckoutSteps {
    private final CheckoutDriver driver = new CheckoutDriver();

    @Given("^할인가 ([\\d,]+)엔인 상품 1건이 담겨 있다$")
    public void 단일_상품(final String price) {
        driver.addLine(yen(price), null);
    }

    @Then("^DDP 세액은 ([\\d,]+)엔이다$")
    public void 세액_확인(final String expected) {
        assertThat(driver.ddpAmount()).isEqualByComparingTo(yen(expected));
    }
}

// Protocol Driver: SUT와의 상호작용을 여기에만 둔다
class CheckoutDriver {
    private final List<Line> lines = new ArrayList<>();
    private BigDecimal ddpAmount;

    void addLine(final BigDecimal price, final String hsCode) { lines.add(new Line(price, hsCode)); }
    void checkOut() { ddpAmount = JapanDdp.calculateDdp(lines.toArray(new Line[0])); }
    BigDecimal ddpAmount() { return ddpAmount; }
}
```

### 태그 기반 가역적 제외

```gherkin
@api-enforced   # API 형태로 만족 — 해당 파라미터가 시그니처에 없어 구조적으로 충족, 실행 불가
Scenario: A-3. 배송비는 임계값 판정에 포함하지 않는다
  ...

@pending        # SUT가 아직 그 값을 노출하지 않음 — 노출되면 태그만 해제
Scenario: B-4-1. 무관세 품목이어도 소비세는 부과된다
  ...
```

```java
@ConfigurationParameter(key = FILTER_TAGS_PROPERTY_NAME,
    value = "not @api-enforced and not @pending")
```

실행 트리에서 SKIPPED/ignored로 표시된다 — "did not match this scenario" 메시지는 오류가 아니라 skip 사유 텍스트다.

### 기존 JUnit 인수 테스트 이관 (기존 프로젝트)

1. 요구사항 문서의 Gherkin을 `.feature`로 이관 (문서 쪽에는 "실행되는 원본은 `.feature`" 정본 선언)
2. Runner + Driver + Steps 작성 → 전체 green 확인
3. JUnit에서 **같은 검증을 하던 인수 테스트 제거** (같은 검증이 두 계층에 중복되면 안 됨)
4. 분기 커버리지용 programmer test만 JUnit에 잔류
5. `@Order`·`@TestClassOrder` 같은 순서 장치가 있었다면 함께 해체 — `.feature`는 파일에 적힌 순서가 곧 실행·표시 순서라 순서 어노테이션이 불필요하다

## 적용 기준

### ✅ 적용 대상
- 고객·이해관계자가 보는 기능의 external behavior
- 요구사항 문서에 Gherkin/기대값 표가 이미 있고, 코드와의 드리프트가 걱정되는 경우
- `tdd-plan` 단계 2에서 Gherkin으로 작성한 예제 — 재작성 없이 그대로 `.feature`가 된다 (위 "도입 시점"의 acceptance-first)
- 비개발자(PO·QA·도메인 전문가) 또는 AI가 명세를 리뷰·승인하는 워크플로우

### ❌ 적용 제외
- 분기 커버리지·내부 협력 검증 → JUnit·Mockito (위계 표 참조)
- property-based 검증 → jqwik 등
- 직렬화·동시성·성능 등 문제 도메인의 언어가 코드인 영역
- **문서↔실행 트리 정렬이 목적의 전부인 경우** — JUnit `@Nested`+`@Order`로 Gherkin 구조를 흉내 내는 것은 격리된 테스트에 "순서 의존"이라는 거짓 신호를 주는 냄새다(Test Desiderata의 Isolated). 정렬이 필요하면 순서 어노테이션이 아니라 이 스킬(실행 가능한 명세)로 푼다.

## Cucumber-JVM 셋업

```kotlin
// build.gradle.kts
testImplementation("io.cucumber:cucumber-java:7.20.1")
testImplementation("io.cucumber:cucumber-junit-platform-engine:7.20.1")
testImplementation("org.junit.platform:junit-platform-suite")
```

```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("example/japanddp")   // .feature 위치 (src/test/resources 하위)
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "example.japanddp")
@ConfigurationParameter(key = FILTER_TAGS_PROPERTY_NAME, value = "not @pending")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME, value = "pretty")
class RunCucumberTest {
}
```

`./gradlew test`로 다른 JUnit 테스트와 함께 실행된다. IntelliJ에서는 Runner 클래스 실행으로 Feature→Rule→Scenario 트리를 보고, "Cucumber for Java" 플러그인을 설치하면 `.feature` 파일·개별 Scenario에서 직접 실행할 수도 있다.

### Environment Notes — cucumber-java 실전 제약 (직접 확인)

- **정규식 스텝은 `^...$` 앵커 필수** — 앵커가 없으면 Cucumber Expression으로 오인식되어(`([\d,]+)` 등이 CE 문법과 충돌) 모든 스텝이 undefined로 처리된다.
- **glue 클래스는 `public` 필수** — package-private이면 glue 스캔이 클래스를 찾지 못해 리터럴 스텝까지 undefined가 된다.
- **`{int}`는 쉼표 표기를 못 받는다** — "16,666엔" 같은 한국어 표기에서 자동 생성 스켈레톤이 "16"만 `{int}`로 잘라낸다. 정규식 `([\d,]+)` + 쉼표 제거 파싱 헬퍼로 우회한다. **자동 생성 스켈레톤은 "어떤 스텝이 빠졌는지" 찾는 용도로만 쓰고 텍스트를 그대로 신뢰하지 않는다.**

## OUTPUT FORMAT

### 실행 절차

1. **대상 파악** — 요구사항 문서의 Gherkin(또는 인수 조건)과 기존 테스트 현황 확인
2. **`.feature` 작성/이관** — `src/test/resources/{package_path}/` 하위. 실행 불가 시나리오는 태그 부여. 문서에 정본 선언 갱신
3. **Runner + Protocol Driver + Steps 작성** — Four Layer 축소형 구조
4. **전체 green 확인** — 태그 제외가 의도한 시나리오만 SKIPPED인지 함께 확인
5. **기존 JUnit 정리** — 중복 인수 테스트 제거, programmer test만 잔류, 순서 장치 해체
6. **문서 갱신** — 정본 선언·테스트 위치 표·프로젝트 CLAUDE.md의 두 계층 설명
7. **커밋** — 단계별 분리(인프라 도입 / JUnit 이관 정리 / 문서 갱신). 메시지는 `docs/reviewable-commits.md`(없으면 `~/.claude/docs/reviewable-commits.md`) 표준을 따르고, 한글 메시지는 임시 파일 + `git commit -F`

## FAILURE CONDITIONS

- ❌ 망라적 edge case를 시나리오로 나열 (시나리오 폭발 — 핵심 예시만)
- ❌ step definition에 SUT 상호작용을 직접 삽입 (Protocol Driver 미분리)
- ❌ 실행 불가능한 시나리오를 삭제 (태그 제외로 가역 처리해야 함)
- ❌ 이관 후 JUnit에 같은 검증의 인수 테스트 방치 (두 계층 중복)
- ❌ 문서↔실행 정렬을 `@Order`류 순서 어노테이션으로 흉내 냄
- ❌ property-based·기술 도메인 검증을 Gherkin으로 작성
- ❌ 느린 채널(브라우저 등)을 기본 driver로 선택해 주 검증층이 느려짐
