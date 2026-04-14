---
name: segregate-functional-core
description: I/O + 계산 혼재 또는 Mock stub + 계산 혼재 메서드를 Functional Core / Imperative Shell(빵속빵, Impure-Pure-Impure Sandwich)로 분리. /segregate-functional-core로 호출.
argument-hint: "[commit-ref]"
---

# Segregate Functional Core Skill

I/O 호출이나 Mock collaborator 호출과 순수 계산이 뒤섞인 메서드를 **Impure-Pure-Impure Sandwich**(빵속빵) 구조로 분리. Functional Core(순수 로직)와 Imperative Shell(I/O)이 나뉘어 테스트 용이성과 가독성 향상.

## GOAL

- **성공 = I/O/Mock과 계산이 혼재된 메서드가 Functional Core와 Imperative Shell로 분리되어 별도 브랜치에서 커밋 완료, PR 생성됨**
- T1(I/O + 계산 혼재) 또는 T2(Mock stub + 계산 혼재) smell 식별
- Functional Core는 순수 함수로 추출 (입력만 받고 결정/instruction 반환)
- Imperative Shell은 I/O만 담당 (read → pure → write 순서)
- Functional Core 테스트는 mock 없이 값 기반으로 작성
- 모든 기존 테스트 통과
- 원래 브랜치로 PR 생성

## CONSTRAINTS

### Hard Rules
- **동작 변경 금지** — 구조 개선만 수행
- **테스트 수정 금지** — 기존 테스트는 그대로 통과해야 함 (Functional Core 테스트는 **추가**)
- **사용자 확인 없이 리팩토링 금지** — 모든 후보는 사용자 승인 후 실행
- **커밋 단위** — 1파일 x 1기법 = 1커밋 (Shell/Core/새 테스트는 논리적으로 함께 커밋)
- **git add -A 금지** — 변경된 파일만 명시적으로 추가

### Functional Core / Imperative Shell 원칙

- **Functional Core**: 순수 함수. I/O 호출 없음. mutation 없음. 같은 입력 → 같은 출력
- **Imperative Shell**: I/O만 담당 (DB, 파일, 네트워크, 시스템 시간). Functional Core에 데이터를 제공하고, 리턴된 instruction/결정을 실행
- **구조**: `Impure(read) → Pure(decide) → Impure(write)` — 샌드위치의 빵-속-빵
- **DDD Trilemma**: 도메인 모델을 완전한 불변으로 만드는 비용이 지나치게 크면 Mutable Shell 수용. 순수성·완전성·성능 중 둘만 동시 만족 가능

## 적용 패턴

Segregate Functional Core 리팩토링 단계:

1. **필요 데이터 식별** — Functional Core가 판단에 필요한 모든 입력을 목록화
2. **데이터 사전 로드** — Imperative Shell이 함수 시작 전 필요한 데이터를 모두 읽어옴
3. **Functional Core 추출** — 파라미터로 데이터를 받고, 판단 결과 또는 Instruction 객체를 반환하는 순수 static 함수로 추출
4. **Imperative Shell 수렴** — 호출자를 `read → pure → write` 순서로 재배치
5. **Functional Core 테스트 추가** — Mock 없이 값 기반 테스트로 작성

### Before/After 예시 (감사 로그 서비스)

출처: Vladimir Khorikov 『단위 테스트』 + Mark Seemann "Impureim Sandwich"

```java
// Before: I/O + 계산 혼재 (T1) + Mock-heavy test (T2)
public class AuditService {
    private final FilePersister filePersister;  // mock 대상
    private final int maxEntries;

    public AuditService(FilePersister filePersister, int maxEntries) {
        this.filePersister = filePersister;
        this.maxEntries = maxEntries;
    }

    // T1: 읽기(I/O) + 판단(계산) + 쓰기(I/O) 혼재
    public void addRecord(String name, LocalDateTime timestamp) {
        List<Path> files = filePersister.listAuditFiles();            // I/O
        Path current = files.isEmpty() ? null : files.get(files.size() - 1);

        int count = current == null
                ? 0
                : filePersister.readLines(current).size();            // I/O

        String entry = name + ";" + timestamp.toString();

        if (current == null || count >= maxEntries) {                 // 계산
            Path newFile = Paths.get("audit_" + (files.size() + 1) + ".txt");
            filePersister.writeLines(newFile, List.of(entry));        // I/O
        } else {
            filePersister.appendLine(current, entry);                 // I/O
        }
    }
}

// T2: 테스트에서 mock stub이 다수 필요
class AuditServiceTest {
    @Mock FilePersister persister;

    @Test void addRecord_new_file_when_max_entries_reached() {
        when(persister.listAuditFiles())
            .thenReturn(List.of(Paths.get("audit_1.txt")));            // stub 1
        when(persister.readLines(any()))
            .thenReturn(List.of("a;...", "b;...", "c;..."));           // stub 2
        doNothing().when(persister).writeLines(any(), any());          // stub 3
        // ...

        new AuditService(persister, 3).addRecord("d", NOW);

        verify(persister).writeLines(any(), any());                    // verify 1
    }
}
```

```java
// After: Functional Core / Imperative Shell 분리

// Functional Core: 순수 static 함수. 파일 I/O 없음, mutation 없음.
public final class AuditDecider {
    private AuditDecider() {}

    public static AuditInstruction decide(
            List<Path> existingFiles,
            int currentFileLineCount,
            int maxEntries,
            String name,
            LocalDateTime timestamp) {

        String entry = name + ";" + timestamp.toString();
        boolean needNewFile = existingFiles.isEmpty()
                || currentFileLineCount >= maxEntries;

        if (needNewFile) {
            Path newFile = Paths.get(
                "audit_" + (existingFiles.size() + 1) + ".txt");
            return AuditInstruction.createFile(newFile, entry);
        }
        Path current = existingFiles.get(existingFiles.size() - 1);
        return AuditInstruction.appendTo(current, entry);
    }
}

// Imperative Shell: I/O만. 순수 함수를 호출하고 instruction 실행.
public class AuditService {
    private final FilePersister filePersister;
    private final int maxEntries;

    public void addRecord(String name, LocalDateTime timestamp) {
        // 빵 (Impure: read)
        List<Path> files = filePersister.listAuditFiles();
        int count = files.isEmpty()
                ? 0
                : filePersister.readLines(files.get(files.size() - 1)).size();

        // 속 (Pure: decide)
        AuditInstruction instruction =
                AuditDecider.decide(files, count, maxEntries, name, timestamp);

        // 빵 (Impure: write)
        instruction.execute(filePersister);
    }
}

// Functional Core 테스트는 mock 불필요 — 값 기반
class AuditDeciderTest {
    @Test void create_new_file_when_max_reached() {
        AuditInstruction actual = AuditDecider.decide(
                List.of(Paths.get("audit_1.txt")), 3, 3, "d", NOW);

        assertThat(actual).isEqualTo(
                AuditInstruction.createFile(
                    Paths.get("audit_2.txt"), "d;" + NOW));
    }

    @Test void append_when_below_limit() {
        AuditInstruction actual = AuditDecider.decide(
                List.of(Paths.get("audit_1.txt")), 1, 3, "b", NOW);

        assertThat(actual).isEqualTo(
                AuditInstruction.appendTo(Paths.get("audit_1.txt"), "b;" + NOW));
    }
}
```

#### AuditInstruction 값 타입 정의 (Java 17+: sealed interface + record)

```java
public sealed interface AuditInstruction
        permits AuditInstruction.CreateFile, AuditInstruction.AppendTo {

    void execute(FilePersister persister);

    record CreateFile(Path file, String entry) implements AuditInstruction {
        @Override public void execute(FilePersister persister) {
            persister.writeLines(file, List.of(entry));
        }
    }

    record AppendTo(Path file, String entry) implements AuditInstruction {
        @Override public void execute(FilePersister persister) {
            persister.appendLine(file, entry);
        }
    }

    static AuditInstruction createFile(Path file, String entry) {
        return new CreateFile(file, entry);
    }

    static AuditInstruction appendTo(Path file, String entry) {
        return new AppendTo(file, entry);
    }
}
```

**왜 sealed + record?**
- `permits`로 variant 집합이 닫혀 있어 Shell에서 `switch` pattern matching이 exhaustiveness 검증됨 → 새 Instruction 추가 시 컴파일러가 누락을 잡음
- record는 `equals`/`hashCode`/`toString` 자동 생성 → Functional Core 테스트에서 `assertThat(...).isEqualTo(...)` 바로 사용

> Java 8+ 호환이 필요한 경우: `AuditInstruction`을 abstract class 또는 interface로 두고 `CreateFile`/`AppendTo`를 일반 class + factory method로 구현. 기능은 동일하지만 pattern matching 이점은 포기.

**핵심 변화**:
- `addRecord`의 제어 흐름이 **read → decide → write** 3단계로 직선화됨
- 판단 로직은 `AuditDecider.decide`로 이동, I/O 의존성 0
- Mock 없이 값 기반 테스트로 복수의 엣지 케이스를 저비용으로 커버
- Imperative Shell 테스트는 통합 테스트 1~2개로 축소 가능

### Before/After 예시 2 (DDD Aggregate — 주문 할인 적용)

감사 로그 예제는 stateless 한 계산이었다. DDD 맥락에서는 aggregate mutation이 개입해 **DDD Trilemma**(순수성·완전성·성능 중 둘)를 체감할 수 있다.

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

**DDD Trilemma 포인트**:
- `Order`를 완전 불변(immutable aggregate)으로 만들고 Functional Core에서 "새 Order"를 반환하는 방식도 가능. 하지만 JPA/Hibernate 환경에서는 dirty checking과 충돌하고 성능 비용이 크다 → **순수성 일부를 포기하고 mutation을 Shell에 허용**.
- 선택: Functional Core는 **읽기 전용으로 Order 참조**하여 판단만 수행, mutation은 Shell에서 aggregate 메서드(`order.applyDiscount`)로 위임. 완전한 pure는 아니지만 판단 로직은 mock 없이 테스트 가능.
- 성능 크리티컬한 경로(대용량 배치 등)에서는 사전 로드 비용이 문제되면 이 리팩토링을 적용하지 않는 것이 맞다.

## 적용 기준 (Trigger Smells)

다음 **둘 중 하나 이상** 감지 시 이 리팩토링을 제안한다.

### T1: I/O + 계산 혼재
프로덕션 메서드 내부에 **모두 존재**:
- I/O 호출 **2회 이상** — `Repository.*`, `*Client.*`, `Jdbc*`, `FileReader/Writer`, `HttpClient`, `Files.*`, 외부 시스템 SDK 호출
- 분기/루프를 포함한 판단 로직 — `if`/`for`/`while`/`switch`/복수 조건식

### T2: Mock stub + 계산 혼재 (테스트 관점)
대응되는 테스트에서:
- Mock stub **3개 이상** — `when(...).thenReturn(...)`, `given(...).willReturn(...)`, `doReturn/doNothing/doThrow`
- 같은 프로덕션 메서드 안에 순수 계산 로직(분기/루프) 존재

### 적용하지 말아야 하는 경우
- **단순 passthrough** — I/O 1회 + 결과 반환만 (분리할 가치 없음)
- **성능상 사전 로드 불가** — 대량 데이터를 Functional Core 앞에서 모두 읽는 비용이 감당 불가
- **도메인 모델 불변 비용 과다** — DDD Trilemma에서 성능·완전성 대신 순수성을 포기해야 하는 경우
- **원자적 연산** — read-modify-write가 원자성을 요구 (CAS, 분산 락 등)

## OUTPUT FORMAT

### 실행 절차

#### 1. 대상 파일 수집

인자가 전달된 경우 해당 commit ref와 비교, 없으면 unstaged + staged 변경 파일 수집:

```bash
# 인자 없음: unstaged + staged 변경 파일
git diff --name-only -- '*.java'
git diff --cached --name-only -- '*.java'

# 인자 있음: 특정 commit과 비교
git diff --name-only <commit-ref> -- '*.java'
```

- 프로덕션 Java 파일만 대상, 테스트 파일(`*Test.java`, `*Tests.java`, `*Spec.java`)은 smell 탐지 보조 용도로만 사용
- 변경 파일이 없으면: "리팩토링 대상 Java 파일이 없습니다." 안내 후 종료

#### 2. Smell 후보 식별

대상 파일에서 T1/T2 smell을 탐지:

**T1 탐지**:
- 한 메서드 내 I/O 호출 카운트 (Repository/Client/Jdbc/FileReader/HttpClient/Files 등) ≥ 2
- 동일 메서드에 `if`/`for`/`while`/`switch` 존재

**T2 탐지**:
- 대응되는 테스트 파일 경로 추정 (`src/test/.../ClassNameTest.java`)
- 해당 테스트 클래스에서 `when/given/do(Return|Nothing|Throw)` 호출 수 ≥ 3
- 대상 프로덕션 메서드에 분기/루프 존재

이미 순수 함수이거나 I/O만 있는 단순 passthrough는 제외.

#### 3. 리팩토링 후보 제시 — 사용자와 질의응답

후보를 하나씩 제시하고 사용자 확인:

```
## 리팩토링 후보 1: Segregate Functional Core

**파일**: AuditService.java
**대상**: addRecord() 메서드

**감지된 smell**:
- T1: I/O 호출 3회 (listAuditFiles, readLines, writeLines/appendLine) + if 분기 1회
- T2: AuditServiceTest에서 mock stub 4개 필요

**현재 코드**:
[대상 메서드 전체]

**제안 변경**:
1. Functional Core 신규 클래스 `AuditDecider` (static) 생성
2. `decide(existingFiles, currentFileLineCount, maxEntries, name, timestamp)` 순수 함수
3. `AuditInstruction` 값 타입 도입 — "무엇을 쓸지" 표현 (createFile / appendTo)
4. `AuditService.addRecord`를 [read → decide → write] 3단계로 재배치
5. `AuditDeciderTest` 추가 — mock 없는 값 기반 테스트 (엣지 케이스 다수)

**적용할까요?** (yes / no / 수정 요청)

⚠️ 성능상 모든 데이터 사전 로드가 부담되면 적용하지 말 것.
⚠️ 도메인 모델 불변 비용이 크면 Mutable Shell로 타협 가능.
```

- 사용자가 **yes** → 실행 목록에 추가
- 사용자가 **no** → 스킵
- 사용자가 **수정 요청** → 요청 반영 후 재제시

모든 후보 확인 후 최종 실행 목록을 보여주고 진행 여부 확인.

#### 4. 브랜치 생성

```bash
CURRENT_BRANCH=$(git branch --show-current)
git checkout -b "refactor/${CURRENT_BRANCH}"
```

#### 5. Functional Core / Imperative Shell 분리 실행

확정된 리팩토링을 하나씩 수행:

1. Functional Core 클래스/함수 추출 (static, 파라미터만으로 동작)
2. 필요 시 Instruction/Decision Value Object 생성 (record 또는 sealed 타입)
3. Imperative Shell을 `read → pure → write` 순서로 재배치
4. Functional Core 테스트 추가 (mock 없이 값 기반)
5. 기존 테스트 실행 (gradle test 또는 mvn test)
6. 통과 확인
7. 변경된 파일만 명시적으로 git add (Core, Shell, 새 테스트)
8. 커밋

**커밋 메시지 형식**:
```
refactor: segregate functional core from [원본클래스명].[메서드명]
```

한글 커밋 메시지가 필요한 경우 Write tool로 임시 파일 생성 후 `git commit -F <파일>` 사용.

테스트 실패 시:
- 해당 리팩토링 변경사항 되돌리기 (`git checkout -- [파일]`)
- 사용자에게 실패 사유 안내
- 다음 리팩토링으로 진행

#### 6. PR 생성

모든 리팩토링 커밋 완료 후:

```bash
gh pr create \
  --base "${CURRENT_BRANCH}" \
  --title "refactor: segregate functional core for [대상 요약]" \
  --body "$(cat <<'EOF'
## Summary
- Segregate Functional Core 적용: [메서드명]
- Impure-Pure-Impure Sandwich 구조로 분리

## Changes
- Functional Core: 순수 static 함수/클래스로 판단 로직 추출
- Instruction 값 타입 도입 (필요 시)
- Imperative Shell: read → pure → write 3단계로 재배치
- Functional Core 테스트 추가 (mock 없는 값 기반)

## Benefits
- 순수 함수로 엣지 케이스 테스트 용이
- Mock stub 수 감소 → 테스트 fragility 감소
- I/O와 비즈니스 로직 분리로 가독성 향상
- Functional Core 재사용 가능

## Test
- [x] 기존 테스트 모두 통과
- [x] Functional Core 값 기반 테스트 추가

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

#### 7. 원래 브랜치로 복귀 및 결과 보고

```bash
git checkout "${CURRENT_BRANCH}"
```

사용자에게 보고:
- PR URL
- 적용된 Functional Core 분리 목록 (대상 메서드, 생성된 Core 클래스, Instruction 타입)
- 리뷰 후 squash merge 안내

## FAILURE CONDITIONS

- ❌ 사용자 확인 없이 리팩토링 실행
- ❌ Functional Core 내부에 I/O 호출 잔존 (진짜 pure 아님)
- ❌ Functional Core 내부에서 mutation 발생 (입력 컬렉션 수정 등)
- ❌ Imperative Shell이 여전히 판단 로직 포함 (read → write 사이에 분기 존재)
- ❌ `read → pure → write` 순서가 어긋남 (중간에 I/O 끼어듦)
- ❌ Functional Core 테스트에 mock 사용 (값 기반이어야 함)
- ❌ DDD Trilemma 무시하고 성능 감당 불가능한 사전 로드 강행
- ❌ 원자성이 필요한 read-modify-write를 분리하여 race condition 유발
- ❌ 동작이 변경되어 기존 테스트 실패 (되돌리기 필수)
- ❌ git add -A로 전체 파일 추가
- ❌ main 브랜치로 직접 PR 생성 (반드시 원래 작업 브랜치로)
