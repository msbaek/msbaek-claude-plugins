# Web App 추가 단계

> 모든 테스트(`- [ ]` → `- [x]`)가 완료된 후 진행한다.
> 적대적 리뷰가 예정되어 있다면 **이 단계를 마친 뒤** 리뷰를 실행한다 — 리뷰 diff가
> 전체 구현을 포함해야 하기 때문이다.

## 인수 테스트 완료 확인

`.feature`의 모든 시나리오가 `@pending` 해제 상태이고 green인지 확인한다. 태그 해제는
그 시나리오를 통과시킨 Green 단계가 같은 커밋에서 수행하므로, 여기서 일괄 활성화할
대상은 없다 — 남아 있는 `@pending`이 있으면 구현되지 않은 시나리오가 있다는 뜻이다.

## JPA Repository 완성

Walking Skeleton에서 최소 JPA로 시작해 RGB 사이클 동안 `inMemory` profile로 도메인을
성장시켰으므로, 여기서는 JPA를 **완성**한다 (처음 작성이 아니다):

1. **JPA Mapping**: 성장한 Entity, Value Object에 대해 매핑 완성. 필요 시 inner class를 outer class로 분리
2. **JPA Repository Interface**: JpaRepository를 상속받는 인터페이스 확장
3. **Repository Impl**: `@Profile("!inMemory")` 구현이 도메인 전체를 커버하도록 확장
4. **계약 테스트**: 같은 계약 테스트 스위트를 InMemory·JPA 양쪽에 실행해 두 구현의
   동등성 검증 (tdd-plan의 `references/web-app-persistence.md` "이후 단계와의 연결" 참조)
5. **클래스 다이어그램**: Repository 관련 클래스들에 대해 mermaid 다이어그램 작성

주의사항:

- 구현 전환은 **profile로** 한다 — `@TestConfiguration` 주석 토글 금지
  (`inMemory` = Map 기반, 그 외 모든 profile = JPA)
- 인수 테스트·계약 테스트(JPA)는 H2가 아니라 실제 MySQL로 실행 — Spring Boot Docker Compose(`compose.yaml`, `skip.in-tests=false`) 사용.
  `@DataJpaTest`에는 `@AutoConfigureTestDatabase(replace = NONE)`가 없으면 임베디드 DB로
  조용히 대체된다

## DSL 개선

- Protocol Driver 개선 (Cucumber Steps는 파싱·위임만 유지)
- Test Data Builder 패턴 적용
- 가독성과 재사용성 향상
