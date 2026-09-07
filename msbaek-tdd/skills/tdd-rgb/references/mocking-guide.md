# Mocking 가이드라인 (정본)

`tdd-rgb` SKILL.md의 Mocking 판단 규칙에 대한 근거·인용·안티패턴 상세. SKILL.md에는
바로 쓰는 규칙만 있고, 여기는 그 근거와 세부 목록을 담는다.

## 1. 대체 대상 판단 기준

**Mock Roles, not Objects** — 대체 대상은 역할(role)이지 객체가 아니다. 내부 구현을
대체하면 구현 세부사항과 테스트가 결합된다. 대체할 것은 모듈의 경계면(port, 다른
application service)이다.

**Only Mock Types You Own** — 소유하지 않은 타입(3rd party 라이브러리)을 직접
대체하면 테스트가 복잡해지고 구현 세부사항과 결합된다. 얇은 추상화 계층으로 감싸고
그 계층을 대체한다(JPA Repository를 직접 대체하지 않고 앞에 추상화 계층을 두는 이유).

**Specify as little as possible in a test** — 실제 요구사항을 반영하는 동작만
검증한다. 구현의 부산물인 동작은 검증하지 않는다.

## 2. 경계 객체는 통합 테스트한다

경계 객체(Repository·DAO, 외부 API 클라이언트, 파일 시스템 인터페이스, 메시징 연동
클래스, 네트워크 통신 컴포넌트)는 대체하지 않고 통합 테스트한다.

이유:
- 외부 시스템 동작이 바뀌면 Mock 기반 테스트는 그 변화를 검출하지 못한다
- Mock은 프로덕션 동작을 정확히 반영하지 못할 수 있다
- 통합 테스트만이 네트워크 장애·DB 오류 같은 실제 경계 조건을 검증한다

예: UserService 테스트는 UserRepository를 대체하지만, UserRepositoryImpl 테스트는
실제 DB로 통합 테스트한다("Don't mock adapters — mock ports, not things we don't own").

## 3. 안티패턴

| 패턴 | 문제 |
|---|---|
| mock이 mock을 반환 | 대체 체인이 복잡성을 증가시키고 테스트가 실패하기 쉬워짐 |
| 데이터 객체(Entity·Value Object) 대체 | 실제 객체를 쓰면 될 것을 불필요하게 대체 |
| 과다한 mock 수 | 테스트가 실패하기 쉬워짐 |
| Partial Mock | 객체 일부만 대체해 혼란을 유발 |
| static 메서드 대체 | static이 문제이지 대체가 해법이 아니다 |
| stub한 메서드를 verify | CQS(Command Query Separation) 위반 — 같은 메서드를 stub·verify 둘 다 하면 위반 |
| 호출 횟수 검증 | 구현 세부사항에 결합됨 |
| "junior가 mock을 올바르게 썼는지 감시" 목적의 대체 | 테스트와 구현이 결합되어 변경이 어려워짐 |

query는 stub(when)한다 — 실제로 호출됐는지 verify할 필요는 없다. verify할 대상은
테스트 대상 코드가 수행한 결과(반환값·예외)다. verify가 필요하다면 그 query가 side
effect를 유발한다는 뜻이며 CQS 위반이다.

## 4. 테스트 더블 분류

| 종류 | 정의 |
|---|---|
| Dummy | 모든 메서드가 `return null;`인 최소 구현. 행위 없음 |
| Stub | 지정한 값을 반환하는 Dummy의 일종 |
| Spy | 호출 사실(횟수·인자·시점)을 기록하는 Stub의 일종 |
| Mock | 상호작용을 검증하는 Spy의 일종 |
| Fake | 대안 구현(in-memory repository 등). stubbing 대신 실제와 유사한 로직으로 동작하고, verify 대신 실제 결과를 검증한다. 영속성 계층에 특히 유용 |

Fake는 인터페이스의 일부로 함께 제공된다. Fake를 쓴 단위 테스트는 짧아지고
유지보수성이 높아진다.

## 5. 단위 테스트의 '단위'

단위는 메서드도, 완전한 use case도 아니라 **동작(behavior)의 단위**다("It's a unit
of behavior" — Kent Beck). 격리 대상은 SUT가 아니라 테스트 자체다("the unit of
isolation is the test not the thing under test"). 테스트끼리 격리되어 있다면 단위
테스트가 DB나 파일시스템과 통신해도 된다.

## 6. 모킹 프레임워크 사용 원칙

대체 도구는 protected·final·private 접근까지 우회할 수 있는 강력한 도구다. 잘
설계된 시스템에서는 이 강력함이 거의 필요 없다(레거시 시스템에서는 필요할 수 있음).
가독성이 더 중요하면 프레임워크 없이 직접 작성한 Fake·Stub를 쓴다. 필요할 때만
최소한으로 쓴다.

헥사고날 아키텍처에서 outbound adapter 자체는 테스트하지 않는다. adapter가 아니라
그 앞의 port를 대체한다("Don't Mock What You Don't Own").

## 7. 함수형 코어 / 명령형 쉘로 모킹 자체를 줄인다

복잡한 로직을 순수 함수로 분리하면 stubbing(given)·verify가 필요 없어진다
(`segregate-functional-core` 스킬 참조). 의존성(I/O)은 외부 쉘로 밀어내고, 코어는
입력→출력만 검증한다.

```java
// 순수 함수로 분리하면 시간·정책을 값으로 주입해 mock 없이 검증 가능
Supplier<LocalDateTime> fixedTimeProvider = () -> LocalDateTime.of(2023, 1, 15, 10, 0);
Function<LocalDateTime, Boolean> notPromotionDay = time -> false;

BigDecimal discount = discountService.applyDiscount(basket, fixedTimeProvider, notPromotionDay);
```

**대체 단위는 클래스가 아니라 컴포넌트**(하나 이상의 클래스)다 — 명확한 계약이 있는
역할만 대체한다("Mock (Well-defined) Roles, Not Objects without a clear contract").

## 8. Classicist vs London School

| | Classicist(Inside-Out) | London School(Outside-In) |
|---|---|---|
| 검증 대상 | 상태와 알고리즘 | 상호작용 |
| 기법 | Triangulation(Kent Beck) | 역할·책임·메시지 패싱 |
| 진행 방향 | 테스트가 구체화되며 코드가 일반화 | 협력 객체 식별과 대체를 통한 설계 |
| 모킹 태도 | 최소화 | 객체 간 상호작용 설계에 사용 |

DHH·Martin Fowler·Kent Beck은 "Is TDD Dead?" 대담에서 모두 "거의 모킹을 하지
않는다"고 밝혔다. Kent Beck: "don't go very far down the mock path."
