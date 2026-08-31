# 단계 E-2: Walking Skeleton 구현

> `tdd-plan` 스킬의 참조 문서 — TDD 유형이 `web-app`일 때만 진행한다.
> 영속성 경계(OSIV·트랜잭션 위치)와 Controller 규칙은 `web-app-persistence.md`에 이어진다.

## Walking Skeleton 목적 — 두 축: real과 thinnest

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

## Repository와 Profile 규칙

Walking Skeleton은 **진짜 JPA Repository 최소 구현 + docker MySQL(Spring Boot Docker Compose)**로
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

## 인수 조건에 없는 API를 발명하지 않는다

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
// 정본: https://github.com/msbaek/tmpl/blob/main/src/test/java/pe/msbaek/tmpl/member/MemberApiTest.java
/// Walking skeleton: real HTTP -> real app -> real docker MySQL.
/// The approval locks the raw wire body (serialization, number format, field presence)
/// instead of picking fields with jsonPath, so an unasserted field cannot drift silently.
/// Ids here are seeded by @Sql, so no Scrubber is needed; add a RegExScrubber once ids
/// become generated.
@SpringBootTest
@AutoConfigureMockMvc
@Sql("/sql/members.sql")           // 쓰기 API가 인수 조건에 없으므로 SQL로 직접 시드
class MemberApiTest {

    @Autowired
    MockMvc mockMvc;

    private MemberApi memberApi() {
        return new MemberApi(mockMvc);   // Protocol Driver — HTTP 상호작용은 이 클래스에만
    }

    @Test
    @DisplayName("@Sql seed로 넣은 회원을 조회하면 응답 본문 전체가 승인된 와이어 포맷과 같다")
    void returnsMemberSeededBySqlScript() throws Exception {
        Approvals.verify(memberApi().getMember(1L));
    }

    @Test
    @DisplayName("없는 id를 조회하면 404와 에러 본문을 돌려준다")
    void returnsNotFoundForUnknownId() throws Exception {
        Approvals.verify(memberApi().getMemberExpectingNotFound(999L));
    }
}
```

```java
// 정본: https://github.com/msbaek/tmpl/blob/main/src/test/java/pe/msbaek/tmpl/member/MemberApi.java
/// Protocol Driver (Dave Farley's Four Layer): the only place tests touch HTTP.
/// Tests say what they do in domain terms ("get member 1"); how it is done over the wire
/// (paths, MockMvc, status codes) lives here. Cucumber Steps, when added, delegate here too.
class MemberApi {

    private final MockMvc mockMvc;

    MemberApi(MockMvc mockMvc) {
        this.mockMvc = mockMvc;
    }

    String getMember(Long id) throws Exception {
        return getMember(id, HttpStatus.OK);
    }

    String getMemberExpectingNotFound(Long id) throws Exception {
        return getMember(id, HttpStatus.NOT_FOUND);
    }

    private String getMember(Long id, HttpStatus expected) throws Exception {
        return mockMvc.perform(get("/members/{id}", id))
                .andExpect(status().is(expected.value()))
                .andReturn().getResponse().getContentAsString();
    }
}
```

> **skeleton의 승인 대상은 raw body다.** 응답을 DTO로 역직렬화해 다시 찍지 않는다 —
> 재직렬화하면 수치 표기·필드 유무 같은 와이어 포맷 결함이 보이지 않는다
> (`{"amount":4.6E+3}`). 비결정 값(id)은 Scrubber로 치환한다(위 예시는 `@Sql` 고정
> id라 불필요). 읽기 좋은 출력이 함께 필요하면 raw를 **교체하지 말고** 한 승인 파일에
> raw 구획 + printer 구획 두 개로 담는다. 404 본문도 같은 방식으로 승인한다 —
> 예외는 처음부터 `@RestControllerAdvice` 한 곳(`web-app-persistence.md` 4번).
> 판단 기준과 두 종류 승인의 구분은 `tdd-red` 에이전트의 "Approved Text Rule"이
> 정본이다.
> 정본이다.

> 생성이 실제 인수 조건인 경우(예: "고객이 장바구니를 만든다" 시나리오가 있음)에만
> POST → GET 왕복으로 관통시킨다. 이때 act와 assert는 같은 API 레벨에서 이루어져야 한다.

## 테스트 클래스 설정 — 진짜 DB로

skeleton 테스트에 Fake Repository를 주입하지 않는다(real 위반). docker MySQL을
**Spring Boot Docker Compose**로 띄우고 진짜 JPA 경로로 관통한다 — `compose.yaml`
하나를 `bootRun`과 테스트가 공유하고, 연결 정보(url·user·password)는 Spring Boot가
compose 파일에서 읽어 자동 주입하므로 `application.yml`에 datasource 설정을 쓰지 않는다:

```kotlin
// build.gradle.kts — testAndDevelopmentOnly (developmentOnly는 test classpath에서
// 빠져 테스트 DataSource가 구성되지 않고, implementation은 운영 아티팩트에 섞인다)
testAndDevelopmentOnly("org.springframework.boot:spring-boot-docker-compose")
```

```yaml
# compose.yaml (프로젝트 루트)
services:
  mysql:
    image: 'mysql:8'
    environment:
      - 'MYSQL_DATABASE=mydatabase'
      - 'MYSQL_USER=myuser'
      - 'MYSQL_PASSWORD=secret'
      - 'MYSQL_ROOT_PASSWORD=verysecret'
    ports:
      - '3306:3306'
```

```yaml
# application.yml
spring:
  docker:
    compose:
      lifecycle-management: start_only   # 종료 시 컨테이너를 내리지 않음 — 재실행이 빠르다
      skip:
        in-tests: false                  # 기본 true — 이게 없으면 테스트에서 compose를 건너뛴다
```

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("local")     // 진짜 JPA + docker MySQL — Fake/TestConfiguration 주입 금지
@Transactional               // 테스트 격리: 각 테스트 후 롤백
                             // ※ Repository 계약 테스트는 반대다 — 트랜잭션 밖에서 실행 (7단계 참조)
public class CreateShoppingBasketTest {
    // @Testcontainers/@Container/@ServiceConnection 없음 — compose.yaml이 DB를 제공한다

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
| **Spring Boot Docker Compose** (기본) | `compose.yaml` 하나를 `bootRun`과 테스트가 공유, datasource 설정·`@Container`/`@ServiceConnection` 보일러플레이트 없음 | `skip.in-tests=false`를 빠뜨리면 테스트에서 조용히 건너뛰어 임베디드 DB로 대체됨(아래 "관통 확인"으로 잡는다). CI에는 Docker Compose가 있어야 한다 |
| **Testcontainers** (대안) | 테스트가 컨테이너 수명을 소유, CI에서 표준 (`@Testcontainers` + `@Container @ServiceConnection static MySQLContainer<?>`) | 일부 Docker 환경(OrbStack 등)에서 docker-java의 API 버전 협상이 실패하면 `1.32`로 폴백해 "minimum supported API version is 1.40" 오류. 라이브러리 문제이며 `systemProperty("api.version", "1.41")`로 우회 가능 |

## 관통 확인 — 실행 SQL 로깅

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
implementation("com.github.gavlyukovskiy:p6spy-spring-boot-starter:1.12.1")
```

기본 한 줄 로그는 긴 쿼리를 읽기 어렵다. `spy.properties`로 포매터를 갈아 끼워 정렬된
박스 형태로 본다(정본: https://github.com/msbaek/tmpl/blob/main/src/main/java/pe/msbaek/tmpl/config/PrettySqlFormatter.java):

```properties
# src/main/resources/spy.properties
appender=com.p6spy.engine.spy.appender.Slf4JLogger
logMessageFormat=pe.msbaek.tmpl.config.PrettySqlFormatter
excludecategories=info,debug,result,resultset,batch
```

```java
/**
 * Renders every statement p6spy intercepts as an indented, boxed SQL block
 * so that a single query is readable at a glance in the console.
 */
public class PrettySqlFormatter implements MessageFormattingStrategy {

    private static final String LINE = "─".repeat(100);

    @Override
    public String formatMessage(int connectionId, String now, long elapsed, String category,
                                String prepared, String sql, String url) {
        if (sql == null || sql.isBlank()) {
            return "";
        }
        String trimmed = sql.trim();
        String formatted = isDdl(trimmed)
                ? FormatStyle.DDL.getFormatter().format(trimmed)     // org.hibernate.engine.jdbc.internal
                : FormatStyle.BASIC.getFormatter().format(trimmed);
        return "\n┌%s\n│ %s | %d ms | conn %d\n│%s\n└%s".formatted(
                LINE, category, elapsed, connectionId, formatted.replace("\n", "\n│"), LINE);
    }

    private boolean isDdl(String sql) {
        String head = sql.substring(0, Math.min(6, sql.length())).toLowerCase();
        return head.startsWith("create") || head.startsWith("alter")
                || head.startsWith("drop") || head.startsWith("commen");
    }
}
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
| 4.x | 쓰지 않음 — `2.0.x`도 실측 무동작(문서 끝 "Boot 4로 올릴 때 함정" 참조) |
| 3.x | `1.12.1` |

위 표는 이 문서를 쓴 시점의 값이다. 좌표를 복사하기 전에
[README](https://github.com/gavlyukovskiy/spring-boot-data-source-decorator)의
호환 표에서 현재 프로젝트에 맞는 최신 값을 확인한다.

**Spring Boot 버전 선택**: 새 프로젝트를 만든다면 [start.spring.io](https://start.spring.io/)에서
제공하는 **3.x 계열의 최신 GA 버전**을 쓴다 — 목록에 `(SNAPSHOT)`이 붙은 항목은
제외하고, 4.x는 테스트 어노테이션 패키지 이동·p6spy 스타터 무동작 등 함정이 있어
아직 기본으로 쓰지 않는다(문서 끝 "Boot 4로 올릴 때 함정"). 특정 버전을
관성으로 복사하지 말고 매번 확인한다.

**프로퍼티 이름 주의**: prefix는 `decorator.datasource.p6spy`이고 활성화 키는
`enable-logging`이다. `logging`은 활성화 플래그가 아니라 appender 선택
(`slf4j`/`sysout`/`file`/`custom`)이다. Spring Boot는 인식하지 못하는 프로퍼티를
조용히 무시하고, 스타터는 설정이 없어도 기본값으로 로그를 내보내므로 — **키를 틀려도
SQL은 보인다.** "로그가 나온다"는 사실은 설정이 맞다는 증거가 되지 못한다
(Principles의 "조용한 실패" 참조).

**도입 시점**: p6spy는 skeleton 초기 셋업에 미리 넣지 않는다 — 필요해진 시점에 넣는다
(Principles의 "도구는 최초로 필요해진 시점에 추가한다"). `show-sql`만으로 관통 확인이
되는 동안에는 그것으로 충분하다.

## Boot 4로 올릴 때 함정 (기본은 3.x 최신 GA — 아래는 4.x 전환 시에만)

**Boot 4 어노테이션 패키지 이동** — import를 Boot 3 기억으로 쓰면 컴파일 에러다:

| 어노테이션 | Boot 4 패키지 |
|---|---|
| `@AutoConfigureMockMvc` | `org.springframework.boot.webmvc.test.autoconfigure` |
| `@DataJpaTest` | `org.springframework.boot.data.jpa.test.autoconfigure` |
| `@AutoConfigureTestDatabase` | `org.springframework.boot.jdbc.test.autoconfigure` |

**Boot 4에서는 스타터를 쓰지 않는다** — `p6spy-spring-boot-starter`(gavlyukovskiy)는
Boot 4에서 `DataSourceAutoConfiguration` 패키지 이동 때문에 **조용히 무동작**한다
(에러 없음, 로그도 그대로 `?`). 순정 p6spy를 넣고 `BeanPostProcessor`로 DataSource를
직접 감싼다(실측: [tmpl](https://github.com/msbaek/tmpl) Boot 4 시도 당시):

```kotlin
// build.gradle.kts — Boot 4: 순정 p6spy
implementation("p6spy:p6spy:3.9.1")
```

```java
// P6SpyConfig.java — DataSource 빈을 P6DataSource로 감싼다
@Configuration
class P6SpyConfig {
    @Bean
    static BeanPostProcessor p6spyWrapper() {
        return new BeanPostProcessor() {
            @Override
            public Object postProcessAfterInitialization(Object bean, String name) {
                if (bean instanceof DataSource ds && !(bean instanceof P6DataSource)) {
                    return new P6DataSource(ds);
                }
                return bean;
            }
        };
    }
}
```

로그 형식은 `src/main/resources/spy.properties`(`appender=com.p6spy.engine.spy.appender.Slf4JLogger`,
`logMessageFormat=...`)로 정한다. 아래 스타터 방식은 **Boot 3.x까지**만 유효하다.
