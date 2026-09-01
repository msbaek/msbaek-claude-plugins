# 단계 E-2 (계속): 영속성 경계와 Controller

> `tdd-plan` 스킬의 참조 문서 — `web-app-skeleton.md`에서 이어진다.

skeleton을 세울 때 **영속성 경계를 함께 확정**한다. 나중에 정하면 그때는 이미 우회가
쌓여 있다 — LAZY 접근이 터지는 지점마다 EAGER로 바꾸는 식으로 번지기 때문이다.

```yaml
spring:
  jpa:
    open-in-view: false    # 항상 명시한다 — 적지 않으면 기본값 true로 켜져 있다
```

**OSIV는 항상 끈다. 도입 시점을 판단할 항목이 아니다** — JPA를 쓰는 순간부터 off다.

**부재는 off가 아니라 on이다**(Principles의 "조용한 실패"). 설정 파일에 `open-in-view`
항목이 아예 없으면 Spring Boot 기본값 `true`가 적용된다. "우리는 OSIV를 안 쓰니까 꺼져 있겠지"는 틀렸다 —
**적어야 꺼진다.** 이 항목이 없는 채로 개발하면 켜진 상태를 모르고 그 위에서 설계하게
되고, 나중에 되돌리는 비용이 3단계로 쌓인다: LAZY 접근이 우연히 성공 → 터지는 지점을
EAGER로 우회 → 경계를 잡으면서 EAGER를 도로 LAZY로 되돌리기.

OSIV가 켜져 있으면 영속성 컨텍스트가 뷰 렌더링까지 열려 있어, 트랜잭션 밖에서도 LAZY
접근이 우연히 성공한다. 경계가 어디인지 코드로 드러나지 않고, DB 커넥션이 요청 처리
내내 붙잡힌다. 끄면 경계를 명시해야 한다:

- **트랜잭션 경계는 Controller에 둔다(이 단계 한정)** — skeleton에는 서비스 계층이 없고
  Controller가 Repository를 직접 호출한다("절차적 pass-through" 원칙). 경계만을 위해
  서비스 계층을 새로 만들지 않는다. 조회는 `@Transactional(readOnly = true)`.
  DTO 매핑을 이 경계 **안에서** 끝내면 LAZY 접근이 트랜잭션 안에서 해소된다
- **연관관계는 LAZY를 유지한다** — "OSIV 밖에서 터지니까 EAGER로" 는 우회다. EAGER는
  전역 결정이라 목록 조회가 생기는 순간 N+1이 되고, 그때는 되돌리기 어렵다. 필요한
  지점에서 fetch join·`@EntityGraph`로 **명시적으로** 당겨 온다. 조회 메서드가 애그리게이트를
  돌려준다면 그 구성물을 함께 당기는 것이 기본이다(아래 계약 테스트 항목 참조)
- **저장은 명시적 `save()` 호출을 관례로 한다** — JPA는 managed entity의 변경을 커밋
  시점에 auto-flush하므로 프레임워크가 강제해 주지 않는다. **규율로 지킨다.**
  회귀 가드를 테스트로 두려면 반드시 **트랜잭션 경계 안**(Controller 경계 테스트)에
  둔다 — 아래 계약 테스트는 트랜잭션 밖에서 돌아 조회 결과가 즉시 detached이므로,
  "`save()` 없는 변경이 새어 나가지 않는다"가 **항상 통과한다**(위험 경로를 한 번도
  실행하지 않는 공허한 검증)

**적용 순서 — 쓰기 경로에서는 가드가 경계보다 먼저 들어와야 한다.**

Controller에 트랜잭션 경계가 없는 동안에는 리포지토리 메서드 단위로 커밋되어 조회
결과가 곧바로 detached이므로, `save()` 없는 변경은 애초에 새어 나갈 수 없다 —
**위험이 없으니 가드도 없는 상태가 정상으로 보인다.** 그러다 경계를 Controller로 올리는
순간 엔티티가 요청 내내 managed로 남고 커밋 시 dirty checking이 flush하므로, **그 변경
하나가 leak 경로를 연다.** 그 시점에 가드가 없으면 새 위험을 잡을 장치 없이 위험만 켜진다.

**단, 조회 경로에는 이 순서 문제가 없다.** `@Transactional(readOnly = true)`는 Hibernate
FlushMode를 MANUAL로 두어 커밋 시 auto-flush가 일어나지 않으므로, 조회 중 managed
엔티티를 실수로 바꿔도 저장되지 않는다 — **경계를 만드는 애노테이션이 가드를 겸한다.**
순서가 문제되는 것은 `readOnly`가 아닌 **쓰기 경로**이고, 거기서 명시적 `save()` 규율과
그 회귀 테스트가 경계와 **같은 변경에** 들어가야 한다.

**가드로 detach를 쓰지 않는다 — LAZY 유지와 배타적이다.** 조회 시점에 detach하면 이후
LAZY 연관 접근이 전부 `LazyInitializationException`이다(detached 엔티티는 지연 로딩을
할 수 없다). "LAZY를 유지한다"와 "detach로 누출을 막는다"는 동시에 성립하지 않으므로,
쓰기 경로의 가드는 detach가 아니라 **Controller 경계 테스트**(트랜잭션 안에서 `save()`
없는 변경이 저장되지 않는지)로 세운다.

**새로 추가하는 회귀 테스트는 실패 주입으로 비공허성을 확인한다.** 이 영역의 결함은
거의 전부 "초록색인데 검증이 일어나지 않는" 유형이다 — 보호 장치를 **일부러 제거하고
그 테스트가 실제로 빨간불이 되는지** 본 뒤에야 그 테스트를 믿는다. 통과했다는 사실
자체는 정보가 아니다. 실패 주입 결과(무엇을 제거했더니 실패했는가)를 테스트 주석에
남기면, 나중에 장치가 하나 더 늘었을 때 그 테스트가 무엇을 잠그는지 다시 판정할 수 있다.

## Controller 구현 원칙

1. **로직 없는 pass-through** - 저장하고 그대로 돌려준다. 계산이 필요한 시나리오는
   skeleton 대상이 아니다 — 하드코딩할 로직 자체가 없을 만큼 얇은 시나리오를 고른다
   - **단, 반환 타입은 엔티티가 아니라 DTO다** (위 skeleton 테스트의
     `BasketDetailsResponse`). "그대로 돌려준다"는 *로직을 넣지 않는다*는 뜻이지
     *엔티티를 그대로 노출한다*는 뜻이 아니다. OSIV를 끈 상태에서 엔티티를 반환하면
     JSON 직렬화가 컨트롤러 메서드가 끝난 **뒤**(`HttpMessageConverter`) 일어나므로
     트랜잭션 밖이고, LAZY 연관에 닿는 순간 `LazyInitializationException`(HTTP 500)이다.
     **이 실패는 테스트에서 안 보인다** — skeleton 테스트는 클래스 레벨
     `@Transactional`이라 직렬화까지 테스트 트랜잭션 안에서 끝난다. 테스트는 초록색,
     실서버는 500. DTO 매핑을 트랜잭션 경계 안에서 끝내는 것이 이 경로를 막는다
   - 이것은 2번 "메서드 추출 금지"의 예외가 아니라 **반환 타입 규정**이다
2. **절차적/명령형 스타일** - 하나의 메서드에 모든 로직 작성, 메서드 추출이나 클래스 분리 금지
3. **Feature Envy 허용** - Controller가 모든 로직 담당, 데이터 중심 설계로 시작
4. **예외 처리는 처음부터 분리** - `@RestControllerAdvice` 전역 핸들러에 둔다. 컨트롤러
   안에 `@ExceptionHandler`를 두지 않는다 — 컨트롤러가 늘어나면 같은 처리가 흩어진다.
   (이것은 2번 "메서드 추출 금지"의 예외가 아니라 배치 위치의 문제다)

## 이후 단계와의 연결

아래 단계 번호는 Web App TDD 템플릿의 "전체적인 절차" 8단계(tdd skill의 템플릿
참조) 기준이다.

- **4단계 RGB 사이클**: 도메인 규칙은 repository 없는 단위 테스트로 성장시키고,
  저장이 필요한 테스트만 `inMemory` profile의 In-Memory 구현(Map 기반)을 사용
- **5단계 JPA Repository**: "처음 구현"이 아니라 **완성** — skeleton의 최소 JPA를
  성장한 도메인 전체를 커버하도록 확장하고, 같은 계약 테스트 스위트를 InMemory·JPA
  양쪽에 실행해 두 구현의 동등성을 검증한다 (in-memory가 JPA 의미론과 조용히
  어긋나는 드리프트 방지):

```java
// 정본: https://github.com/msbaek/tmpl/blob/main/src/test/java/pe/msbaek/tmpl/member/MemberRepositoryContractTest.java
import static org.springframework.transaction.annotation.Propagation.NOT_SUPPORTED;

/**
 * The contract both MemberRepository implementations must satisfy.
 * Runs outside a transaction on purpose: inside one, the persistence context
 * would answer findById from its first-level cache and the round trip to the
 * database would never happen, making the JPA run vacuous.
 */
// 트랜잭션 속성은 "테스트 메서드가 선언된 클래스"에서 찾는다 — 계약 테스트 메서드는
// 전부 이 부모에 선언돼 있으므로, 어노테이션도 여기 붙여야 적용된다 (아래 주의 참조)
@Transactional(propagation = NOT_SUPPORTED)
abstract class MemberRepositoryContractTest {

    abstract MemberRepository repository();   // 구현별로 제공

    abstract void cleanUp();                  // 롤백이 없으므로 구현이 스스로 치운다

    /** Guard: round-trip assertions pass inside and outside a transaction alike. */
    @Test
    @DisplayName("계약 테스트는 트랜잭션 밖에서 실행된다")
    void runsOutsideTransaction() {
        assertThat(TestTransaction.isActive()).isFalse();
    }

    @Test
    @DisplayName("없는 id를 조회하면 빈 결과를 돌려준다")
    void returnsEmptyForUnknownId() {
        assertThat(repository().findById(999L)).isEmpty();
    }

    @Test
    @DisplayName("저장한 회원을 id로 다시 찾는다")
    void findsSavedMemberById() {
        repository().save(new Member(1L, "백명석"));

        Member found = repository().findById(1L).orElseThrow();

        assertThat(found.getId()).isEqualTo(1L);
        assertThat(found.getName()).isEqualTo("백명석");
    }

    @Test
    @DisplayName("같은 id로 다시 저장하면 덮어쓴다")
    void overwritesMemberSavedWithSameId() {
        repository().save(new Member(1L, "백명석"));

        repository().save(new Member(1L, "명석백"));

        assertThat(repository().findById(1L).orElseThrow().getName()).isEqualTo("명석백");
    }

    /**
     * Without this, an in-memory Map may alias its stored value into the caller's
     * hands while JPA returns a detached copy - a divergence the fast loop would
     * never notice.
     */
    @Test
    @DisplayName("조회 결과는 저장소가 들고 있는 객체가 아니라 스냅샷이다")
    void returnsSnapshotRatherThanStoredInstance() {
        Member saved = new Member(1L, "백명석");
        repository().save(saved);

        Member found = repository().findById(1L).orElseThrow();

        assertThat(found).isNotSameAs(saved);
        assertThat(repository().findById(1L).orElseThrow()).isNotSameAs(found);
    }

    @AfterEach
    void tearDown() {
        cleanUp();
    }
}

class InMemoryMemberRepositoryTest extends MemberRepositoryContractTest { ... }  // Spring 없음, 매 빌드

@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)   // 없으면 임베디드 DB로 조용히 대체됨 — MySQL 검증 무력화
class MemberRepositoryImplTest extends MemberRepositoryContractTest { ... }      // docker MySQL — compose.yaml이 제공 (web-app-skeleton.md)
```

스냅샷 조항을 만족하려면 in-memory 어댑터도 **저장·조회 양쪽에서 복사**해야 한다
(정본: https://github.com/msbaek/tmpl/blob/main/src/main/java/pe/msbaek/tmpl/member/InMemoryMemberRepository.java):

```java
@Repository
@Profile("inMemory")
public class InMemoryMemberRepository implements MemberRepository {

    private final Map<Long, Member> members = new ConcurrentHashMap<>();

    @Override
    public Member save(Member member) {
        Member stored = snapshotOf(member);
        members.put(stored.getId(), stored);
        return snapshotOf(stored);
    }

    @Override
    public Optional<Member> findById(Long id) {
        return Optional.ofNullable(members.get(id)).map(this::snapshotOf);
    }

    private Member snapshotOf(Member member) {
        return new Member(member.getId(), member.getName());
    }
}
```

**계약 테스트만 트랜잭션 밖에서 실행한다 — Walking Skeleton 테스트의 `@Transactional`과
모순이 아니라 역할 분담이다:**

| 테스트 | 트랜잭션 | 정리 | 이유 |
|---|---|---|---|
| Walking Skeleton·인수 테스트 | `@Transactional` 롤백 유지 | 자동 | 목적이 **격리**다. 왕복 자체를 검증하지 않는다 |
| Repository 계약 테스트 | **없음** (`NOT_SUPPORTED`) | `@AfterEach`·`@Sql` | 목적이 **왕복 검증**이다 |

테스트 트랜잭션 안에서는 1차 캐시(영속성 컨텍스트)가 살아 있어 `findById`가 DB가
아니라 캐시를 돌려준다. 그러면 "저장 후 조회하면 같은 상태"라는 계약이 **DB를 거치지
않고도 통과**한다 — 검증이 공허해진다(vacuous). `@DataJpaTest`는 기본이 트랜잭션 +
롤백이므로, 계약 테스트에서는 명시적으로 꺼야 한다.

**어노테이션을 붙이는 위치가 곧 동작을 가른다 — 하위 클래스에 붙이면 무시된다.**
Spring은 트랜잭션 속성을 "가장 구체적인 메서드 → **그 메서드의 선언 클래스**" 순으로
찾는다. 계약 테스트 메서드는 하위 클래스가 오버라이드하지 않은 상속 메서드이므로,
선언 클래스는 언제나 부모 계약 클래스다. `MemberRepositoryImplTest`(자식)에 붙인
`@Transactional`은 그 탐색 경로에 없어 **조용히 무시된다** — `@DataJpaTest`의 기본
트랜잭션이 그대로 남아 검증이 공허해지는데 테스트는 초록색이다(Principles의
"조용한 실패"). 같은 이유로
`@DataJpaTest`가 주는 트랜잭션도 상속 메서드에는 적용 여부가 갈리므로, **의도를
부모에 명시**해 두 경우 모두 확정한다.

**실측(Boot 3.5·4.1 양쪽 동일, 정본 예제 프로젝트 [tmpl](https://github.com/msbaek/tmpl) `member/Member.md`)** — 예측과 다른 점이 하나 있다.
`@DataJpaTest`는 하위 클래스에 붙으므로 그 트랜잭션은 부모 선언 메서드에 **애초에
닿지 않는다**. 따라서 부모의 `NOT_SUPPORTED`를 제거해도 계약 테스트는 이미 트랜잭션
밖이라 아무것도 red가 되지 않는다 — "제거하면 공허해진다"는 예측은 틀렸고, 그
선언은 오늘 시점엔 **방어적 명시**다(부모에 순수 `@Transactional`을 넣으면 적용되므로
위치 규칙 자체는 맞다). 여기서 얻는 교훈 두 가지:

- **왕복 단언은 트랜잭션 안/밖 모두 통과한다** — 행위 단언만으로는 이 불변조건을
  잠글 수 없다. `TestTransaction.isActive() == false`를 직접 단언하는 **guard test**를
  계약에 둔다(위 예시 `runsOutsideTransaction`). 부모에 `@Transactional`을 주입하면
  guard만 red가 되는 것으로 민감함을 확인했다.
- 같은 계약이 in-memory 어댑터의 숨은 버그(Map 참조를 그대로 반환 → 호출자 mutate 시
  저장소 오염)도 잡았다 — 단, identity/snapshot을 **명시적으로 단언한 뒤에야**.
  계약이 잡아야 할 차이(트랜잭션 경계·identity·null 처리)는 나열하고 항목마다 실패
  주입으로 red를 확인한다.

트랜잭션을 켠 채로 왕복을 검증하려 하면 우회가 겹겹이 쌓인다 — `flush()` + `clear()`로
1차 캐시 수동 비우기, 위 탐색 규칙 때문에 트랜잭션이 실제로 걸렸는지 확인하는 가드
코드, LAZY 회귀 테스트만 개별적으로 전파 속성을 무력화하기. **트랜잭션 밖에서
실행하면 셋이 전부 사라진다** — 각 `save()`·`findById()`가 자기 트랜잭션으로 커밋되어
애초에 캐시가 공유되지 않기 때문이다.

**트랜잭션 밖 실행의 대가 세 가지** (롤백이 없어지면서 따라온다):

- **데이터가 남는다** — 같은 docker MySQL을 쓰는 Walking Skeleton·인수 테스트와
  간섭한다. `@AfterEach`에서 FK 역순으로 지우거나 `@Sql` 정리 스크립트를 둔다
- **LAZY 연관을 그대로 두면 검증할 수 없다** — 세션이 닫혀 있어 접근 시
  `LazyInitializationException`이다. 여기서 연관을 검증 대상에서 **빼지 않는다** —
  빼면 그 부분 계약이 어디에서도 검증되지 않는다. 대신 **리포지토리 포트의 계약을
  "완전한 애그리게이트를 돌려준다"로 정하고**, 조회 메서드에 `@EntityGraph`·fetch join을
  걸어 조회 시점에 명시적으로 당긴다. 매핑은 LAZY로 두고 조회 지점에서 명시하는 것이라
  "EAGER 금지"와 충돌하지 않고, **호출부가 트랜잭션 안인지에 따라 결과의 사용 가능
  여부가 달라지지 않는다** — 애그리게이트 루트가 자기 구성물을 갖춰 돌려주는 것이
  설계상으로도 맞다
- **`@DataJpaTest`는 슬라이스다** — `local` profile의 DataSource 설정·SQL 로깅이 그대로
  적용되는지는 별도로 확인한다

- **인수 테스트 실행**: 별도 활성화 단계 없음 — 각 Green이 자기 시나리오의 `@pending`을
  같은 커밋에서 해제한다. 실행은 항상 `local` profile — in-memory로 인수 테스트를
  통과시키지 않는다

