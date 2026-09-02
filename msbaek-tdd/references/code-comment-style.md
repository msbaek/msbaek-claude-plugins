# 코드 주석 스타일 (정본)

msbaek-tdd가 생성·수정하는 Java 코드에 적용한다. 코드를 쓰는 모든 에이전트
(`tdd-red`·`tdd-green`·`tdd-blue`·`tdd-skeleton-builder`·`tdd-acceptance-builder`)가
이 문서를 참조하며, 각자 재기술하지 않는다.

## 왜 한글인가

이 워크플로우의 주석은 "무엇을 하는 코드인가"가 아니라 **어느 앵커 규칙에서 나왔고 왜
이렇게 결정했는가**를 담는다. 성격이 코드보다 앵커 문서(`{ClassName}.md`)에 가깝다.
앵커가 한글인데 주석만 영어면 같은 근거를 두 언어로 읽게 되고, 앵커와 대조할 때마다
번역을 한 번 거친다.

## 규칙

1. **소스 주석은 한글로 쓴다** — 클래스·메서드 Javadoc, 인라인 주석, 단정(assertion)
   메시지, 예외 메시지.
2. **모호할 수 있는 용어는 `한글(english)` 병기** — 괄호 앞 공백 없음.
   예: 이음매(seam), 관리 상태(managed), 표현 선택(presentation choice),
   왕복 보존(round-trip), 공허한 단정(vacuous assertion), 실패 주입(failure injection).

## 번역하지 않는 것 (grep이 끊긴다)

- 식별자·타입·메서드명, API 경로, 애노테이션
- 프레임워크·JPA 용어가 **코드 이름으로 등장할 때**: `@Transactional`, dirty checking,
  auto-flush, detached, LAZY, OSIV 등. 본문에서 **설명할 때**는 규칙 2대로 병기한다
  (예: "지연 로딩(LAZY) 경계를 트랜잭션 안에서 닫는다").
- `@DisplayName` — 이미 한글이므로 그대로 둔다.

## 전환 예

```java
// before
// Anchor rule 7: validation order is an invariant - 404 -> 403 -> 409

// after
// 앵커 규칙 7: 검증 순서가 불변식이다 — 404 → 403 → 409 순으로 검사하고
// 먼저 걸리는 사유로 거부한다
```

## 빌드 인코딩 (한글은 주석뿐 아니라 문자열 리터럴에도 들어간다)

프로젝트 골격을 새로 만들거나 빌드 파일을 손볼 때 컴파일 인코딩을 **명시**한다.
플랫폼 기본 인코딩에 기대면 다른 환경에서 깨진다.

```gradle
// build.gradle
tasks.withType(JavaCompile).configureEach { options.encoding = 'UTF-8' }
```

```xml
<!-- pom.xml -->
<properties>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

이미 설정돼 있으면 건드리지 않는다.
