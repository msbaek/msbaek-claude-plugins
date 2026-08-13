# Before/After 예시 2 — DDD Aggregate (주문 할인 적용)

SKILL.md 본문의 감사 로그 예제는 stateless 한 계산이었다. DDD 맥락에서는 aggregate
mutation이 개입해 **DDD Trilemma**(순수성·완전성·성능 중 둘만 동시 만족)를 체감할 수 있다.
도메인 모델 mutation이 얽힌 대상을 분리할 때 읽는다.

```java
// Before: 판단 + aggregate mutation + I/O 혼재
public class OrderDiscountService {
    private final OrderRepository orderRepo;
    private final CustomerRepository customerRepo;
    private final DiscountPolicyRepository policyRepo;

    public void applyDiscount(OrderId orderId, CouponCode coupon) {
        Order order = orderRepo.load(orderId);                         // I/O
        Customer customer = customerRepo.load(order.customerId());     // I/O
        DiscountPolicy policy = policyRepo.findByCode(coupon);         // I/O

        if (!policy.isApplicable(customer, order)) {                   // 계산
            throw new DiscountNotApplicableException(coupon);
        }
        BigDecimal amount = policy.calculate(order);                   // 계산
        if (order.total().subtract(amount).signum() < 0) {             // 계산
            throw new IllegalStateException("음수 금액");
        }

        order.applyDiscount(amount);                                   // aggregate mutation
        orderRepo.save(order);                                         // I/O
    }
}
```

```java
// After: Functional Core는 "무엇을 할지"만 결정, aggregate mutation은 Shell에서

// Functional Core: 순수 판단. Order를 읽기 전용으로만 사용.
public final class OrderDiscountDecider {
    private OrderDiscountDecider() {}

    public static DiscountDecision decide(
            Order order, Customer customer, DiscountPolicy policy) {

        if (!policy.isApplicable(customer, order)) {
            return new DiscountDecision.Reject("정책 미적용");
        }
        BigDecimal amount = policy.calculate(order);
        if (order.total().subtract(amount).signum() < 0) {
            return new DiscountDecision.Reject("음수 금액 방지");
        }
        return new DiscountDecision.Apply(amount);
    }
}

// Decision 값 타입 (sealed + record)
public sealed interface DiscountDecision {
    record Apply(BigDecimal amount) implements DiscountDecision {}
    record Reject(String reason) implements DiscountDecision {}
}

// Imperative Shell: I/O + aggregate mutation
public class OrderDiscountService {
    public void applyDiscount(OrderId orderId, CouponCode coupon) {
        // 빵 (read)
        Order order = orderRepo.load(orderId);
        Customer customer = customerRepo.load(order.customerId());
        DiscountPolicy policy = policyRepo.findByCode(coupon);

        // 속 (decide — 순수)
        DiscountDecision decision = OrderDiscountDecider.decide(order, customer, policy);

        // 빵 (apply + write)
        switch (decision) {
            case DiscountDecision.Apply a -> {
                order.applyDiscount(a.amount());
                orderRepo.save(order);
            }
            case DiscountDecision.Reject r ->
                throw new DiscountNotApplicableException(coupon, r.reason());
        }
    }
}

// 순수 테스트 — Order/Customer/DiscountPolicy는 값 기반으로 구성
class OrderDiscountDeciderTest {
    @Test void reject_when_policy_not_applicable() {
        DiscountDecision actual = OrderDiscountDecider.decide(
                orderWith(total("10000")),
                newCustomer(),
                policyThatRejects());

        assertThat(actual).isInstanceOf(DiscountDecision.Reject.class);
    }

    @Test void apply_when_amount_within_total() {
        DiscountDecision actual = OrderDiscountDecider.decide(
                orderWith(total("10000")),
                newCustomer(),
                policyWithFlatAmount("3000"));

        assertThat(actual).isEqualTo(new DiscountDecision.Apply(new BigDecimal("3000")));
    }
}
```

## DDD Trilemma 포인트

- `Order`를 완전 불변(immutable aggregate)으로 만들고 Functional Core에서 "새 Order"를
  반환하는 방식도 가능. 하지만 JPA/Hibernate 환경에서는 dirty checking과 충돌하고 성능
  비용이 크다 → **순수성 일부를 포기하고 mutation을 Shell에 허용**.
- 선택: Functional Core는 **읽기 전용으로 Order 참조**하여 판단만 수행, mutation은
  Shell에서 aggregate 메서드(`order.applyDiscount`)로 위임. 완전한 pure는 아니지만
  판단 로직은 mock 없이 테스트 가능.
- 성능 크리티컬한 경로(대용량 배치 등)에서는 사전 로드 비용이 문제되면 이 리팩토링을
  적용하지 않는 것이 맞다.
