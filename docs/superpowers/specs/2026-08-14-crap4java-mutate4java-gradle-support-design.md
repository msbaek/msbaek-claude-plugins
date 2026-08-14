# crap4java·mutate4java Gradle 지원 — Design Spec

> **저장 위치 안내**: 이 spec이 다루는 구현 대상은 이 저장소(msbaek-claude-plugins)가 아니라
> 별도 두 도구 저장소(`~/git/uncle-bob/crap4java`, `~/git/uncle-bob/mutate4java`)다. 두 저장소
> 모두 `docs/` 관례가 없어 spec을 여기(msbaek-claude-plugins)에 두고, 구현은 cross-session
> messaging으로 해당 저장소 세션에 전달한다. 구현 세션은 이 문서를 참조로 읽되, 실제 커밋은
> 각자의 저장소에 한다.

## 배경 — 왜 이 작업을 하나

msbaek-tdd 플러그인의 하드닝 게이트(`skills/tdd-rgb/references/hardening-gate.md`, 1.37.0~1.37.1)는
CRAP·DRY·mutation 3종을 완료 보고에 제안한다. 소스 코드 직접 확인 결과:

- **dry4java**: 빌드 도구 무관 — 코드 어디에도 `mvn`/`gradle`/`pom.xml` 참조 없음. 이미 완료 상태, 이 spec의 범위 밖.
- **crap4java**: `CoverageRunner.java`가 `mvn org.jacoco:jacoco-maven-plugin:...`를 직접 실행. `CliApplication.moduleRootFor`가 `pom.xml`만 찾음. **오버라이드 수단이 전혀 없음.**
- **mutate4java**: `mutate4java.coverage.CoverageRunner`가 동일하게 `mvn`+jacoco를 하드코딩. `ModuleRootFinder`도 `pom.xml`만 찾음. 단, baseline/mutant 테스트 실행은 **이미 `--test-command CMD`로 오버라이드 가능**(`ExecutionContext.java:37`, `ProcessTestCommandExecutor`) — 커버리지 계산 절반만 남음.

결과: Gradle 프로젝트에서는 CRAP·mutation 둘 다 사용 불가. `hardening-gate.md` §1-2가 Gradle이면
이 둘을 통째로 스킵하도록 이미 대응해뒀지만(1.37.1), 근본 원인(도구 자체의 Maven 결합)은
남아 있다.

## GOAL (testable)

- **성공 = crap4java·mutate4java가 Gradle 프로젝트에서 Maven과 동등한 신뢰도로 CRAP 점수·mutation KILLED/SURVIVED를 산출**
- Maven 경로는 **완전히 무회귀** — 기존 동작·출력이 코드 수정 전후로 바이트/의미 동일
- Gradle 프로젝트는 대상 프로젝트의 `build.gradle(.kts)`를 수정하지 않고도 동작(Maven이 `pom.xml`에 jacoco 플러그인 선언 없이도 동작하는 것과 동일한 "설정 불필요" 약속 유지)
- 이 spec의 범위는 **crap4java·mutate4java 코드 변경만** — msbaek-tdd 플러그인 문서(`hardening-gate.md`의 Gradle skip 로직 제거 등)는 별도 후속 작업, 이 spec에 포함하지 않는다

## CONSTRAINTS (non-negotiable)

1. **Maven 경로 무회귀 — before/after diff로 증명**: `ModuleRootFinder`/`CoverageRunner`(양쪽 도구)처럼 기존 파일을 수정하는 모든 Task는, 같은 Maven 프로젝트·같은 파일·같은 명령을 **수정 전/후로 각각 실행**해 출력을 diff한다. 완전 일치해야 커밋 가능 — 불일치는 회귀로 간주하고 원인 해소 전엔 진행 금지. (신규 파일 생성은 이 규칙 대상 아님 — 사용자 확정 사항)
2. **대상 프로젝트 빌드 파일 무수정**: Gradle 프로젝트에서 jacoco를 쓰려면 `build.gradle`에 `jacoco` 플러그인이 선언돼 있어야 하는데, 이를 요구하면 Maven 쪽과의 "설정 불필요" 약속이 깨진다. init script로 애드혹 적용한다.
3. **JaCoCo XML 파서는 수정하지 않는다**: Maven·Gradle 플러그인 모두 동일한 JaCoCo XML 스키마를 생성 — 파서(`JacocoLineCoverageParser` 등)는 그대로 재사용, 리포트 **경로 계산**만 build-tool별로 분기한다.
4. **`-DexcludeTags` 리스크는 숨기지 않고 명시**: mutate4java의 기본 baseline 명령(`mvn test -DexcludeTags=no-mutate`)에서 태그 제외는 Maven Surefire 관례다. Gradle의 `test` 태스크는 이 시스템 프로퍼티를 자동으로 태그 제외로 번역하지 않는다 — 대상 프로젝트가 `build.gradle`에 `useJUnitPlatform { excludeTags System.getProperty(...) }`를 직접 배선해야만 동작한다. 이 spec은 이 제약을 **문서화하고 사용자에게 노출**하는 것으로 처리한다(무시하거나 조용히 전체 뮤턴트를 실행하지 않는다 — Task 3 참조).
5. **crap4java에는 오버라이드 수단이 없었다는 사실을 전제로 설계**: mutate4java와 달리 `--test-command` 같은 기존 확장점이 없으므로, build-tool 분기 자체를 새로 도입한다(기존 확장점 재사용이 아니라 신규 추상화).

## FAILURE CONDITIONS (spec 전체)

| 증상 | 대처 |
|---|---|
| Maven 프로젝트 재실행 결과가 수정 전과 한 글자라도 다름 | 회귀 — 커밋 중단, 원인 파악 후 재작업 |
| Gradle 프로젝트에서 대상 `build.gradle`을 수정해야만 동작 | Constraint 2 위반 — init script 방식으로 재설계 |
| `-DexcludeTags` 제약을 사용자에게 알리지 않고 조용히 전체 뮤턴트 실행 | Constraint 4 위반 — 경고 메시지 필수 |
| JaCoCo XML 파서 코드에 diff 발생 | Constraint 3 위반 — 파서는 건드리지 않고 경로 계산만 분기했는지 재검토 |

---

## 아키텍처

두 도구 각각에 `BuildTool` 개념(enum 또는 interface)을 도입한다. 책임 3가지:

1. **모듈 루트 탐색**: `pom.xml` 또는 `build.gradle`/`build.gradle.kts` 존재로 판정
2. **커버리지 실행**: Maven이면 기존 `mvn jacoco-maven-plugin` 그대로, Gradle이면 신규 init script 경로
3. **리포트 경로 계산**: Maven `target/site/jacoco/jacoco.xml` vs Gradle `build/reports/jacoco/test/jacocoTestReport.xml`

```
BuildTool.detect(moduleRoot)
 ├─ MAVEN  (pom.xml 존재)
 │   └─ 기존 CoverageRunner 그대로 — 무변경, 회귀 검증만
 └─ GRADLE (build.gradle[.kts] 존재)
     └─ 신규: (./gradlew 있으면 우선, 없으면 gradle)
              --init-script <bundled-jacoco-init.gradle>
              test jacocoTestReport --console=plain -q
         → build/reports/jacoco/test/jacocoTestReport.xml 파싱 (파서 재사용)
```

### Gradle init script (신규 리소스 파일, 두 도구 공통 내용)

각 도구의 jar 리소스로 번들. 대상 프로젝트의 `build.gradle`을 전혀 건드리지 않고 커맨드라인에서만
jacoco를 애드혹 적용한다 (Maven의 `mvn org.jacoco:jacoco-maven-plugin:0.8.12:...` 애드혹 호출과
동등한 역할):

```groovy
// jacoco-init.gradle (개념 스케치 — 정확한 문법은 구현 Task에서 실제 Gradle 버전으로 검증)
allprojects {
    apply plugin: 'jacoco'
    jacoco { toolVersion = "0.8.12" }
    tasks.withType(Test).configureEach {
        finalizedBy jacocoTestReport
    }
    tasks.withType(JacocoReport).configureEach {
        reports {
            xml.required.set(true)
        }
    }
}
```

구현 Task에서 실제 대상 프로젝트(Gradle Groovy DSL·Kotlin DSL 둘 다, 단일/멀티모듈)로
검증해 문법을 확정한다 — 이 spec은 개념만 고정.

---

## 도구별 변경 지점 (코드 확인 완료, 정확한 파일·줄)

### crap4java (`~/git/uncle-bob/crap4java`)

| 파일 | 현재 | 변경 |
|---|---|---|
| `src/crap4java/CliApplication.java:110-120` (`moduleRootFor`) | `pom.xml`만 탐색 | `pom.xml` OR `build.gradle`/`build.gradle.kts` 탐색으로 확장 |
| `src/crap4java/CliApplication.java:57` | `moduleRoot.resolve("target/site/jacoco/jacoco.xml")` 고정 | 감지된 BuildTool 기준 경로 계산 |
| `src/crap4java/CoverageRunner.java` (전체) | `mvn` 하드코딩, 오버라이드 없음 | BuildTool 분기 추가. Maven 분기는 **기존 코드 그대로 이동**(diff 없어야 함), Gradle 분기 신설 |

### mutate4java (`~/git/uncle-bob/mutate4java`)

| 파일 | 현재 | 변경 |
|---|---|---|
| `src/mutate4java/project/ModuleRootFinder.java:29` | `pom.xml`만 탐색 | crap4java와 동일하게 확장 |
| `src/mutate4java/coverage/CoverageRunner.java` (전체) | `mvn`+jacoco 하드코딩 | BuildTool 분기. Maven 분기 그대로 유지, Gradle 분기 신설 |
| `src/mutate4java/exec/ProcessTestCommandExecutor.java:16` (`DEFAULT_COMMAND`) | `mvn test -DexcludeTags=no-mutate` 고정 | 감지된 BuildTool 기준 기본값 전환(`--test-command`로 이미 오버라이드 가능하니 이건 **기본값만** 개선). Gradle 기본값은 `-DexcludeTags` 리스크(Constraint 4)를 CLI 경고로 노출 |

---

## Testing Strategy — Before/After Diff 프로토콜

**적용 대상**: 위 표의 기존 파일 수정 4곳(`CliApplication.java`, `CoverageRunner.java`×2,
`ProcessTestCommandExecutor.java`). 신규 파일(`BuildTool`, `jacoco-init.gradle` 등)은 이 프로토콜 대상 아님.

### Maven 회귀 검증 (필수, 모든 관련 Task의 완료 조건)

Baseline은 이미 이 저장소의 `docs/superpowers/plans/2026-08-14-hardening-gate-proposal.md`
"3차 검증" 절에 원문으로 존재한다 — `/Users/msbaek/git/coding-dojo/unit-testing` 대상,
`PriceService.java`·`ExcelExporter.java`·`BigService.java` 3파일 CRAP, `PriceService.java`
mutation(`--mutate-all`).

절차:
1. 코드 수정 **전** — 위 baseline이 이미 존재하면 재사용(같은 JAR 버전·같은 커밋이면 재실행 불필요). 버전이 바뀌었으면 재실행해 새 baseline 기록.
2. 코드 수정 **후** — **동일 명령**을 **동일 파일**에 재실행.
3. 두 출력(CRAP 표 전체, mutation summary 전체)을 diff. **완전 일치**해야 함:
   - CRAP: 모든 Method 행의 CC·Cov%·CRAP 수치 동일
   - mutation: KILLED/SURVIVED/UNCOVERED 각 사이트의 줄 번호·설명·판정 동일
4. 불일치 발견 시 커밋하지 않고 원인 규명 — Maven 분기 코드가 실수로 함께 바뀌었을 가능성이 가장 크다.

### Gradle 신규 동작 검증 (baseline 없음 — diff 아닌 신규 확인)

대상: `tdd-agent-verifiyer` 저장소(CouponUsageLimit, Gradle) — 이전 세션에서 크로스세션 검증에 이미 쓰인 프로젝트, 재사용.

- 실행 성공 여부(exit code, 에러 없음)
- CRAP 점수가 코드 복잡도와 방향이 맞는지(복잡한 메서드가 높게 나오는지) 육안 대조
- mutation KILLED/SURVIVED가 실제 테스트 강도와 일치하는지(테스트 있는 파일은 KILLED 다수, 없는 파일은 UNCOVERED) — Maven 검증 때와 같은 해석 방식

---

## 구현 순서 (writing-plans에서 Task로 세분화할 골격)

1. crap4java: `BuildTool` 도입 + `moduleRootFor` 확장 (신규 로직, Maven 분기는 순수 이동)
2. crap4java: `CoverageRunner` Gradle 분기 + init script 리소스 신설 → Maven 회귀 diff → Gradle `unit-testing`은 Maven이므로, Gradle 신규 검증은 `tdd-agent-verifiyer`로
3. mutate4java: `ModuleRootFinder` 확장 (crap4java 패턴 재사용)
4. mutate4java: `CoverageRunner` Gradle 분기 + init script(1과 리소스 공유 검토) → Maven 회귀 diff
5. mutate4java: `ProcessTestCommandExecutor.DEFAULT_COMMAND` 전환 + `-DexcludeTags` 경고 메시지 → Gradle `tdd-agent-verifiyer`로 신규 검증

각 Task는 "Maven 회귀 diff 통과"를 완료 조건에 명시(writing-plans 단계에서 Task별 Output Format에 반영).

## 크로스세션 전달 계획

이 spec 승인 후 writing-plans로 구현 계획을 이 저장소에 작성한 뒤, crap4java·mutate4java
각각을 다루는 별도 세션(또는 새로 시작하는 세션)에 SendMessage로 spec 경로 + 담당 Task
범위를 전달한다. 구현·커밋은 각 도구 저장소에서, 검증 결과 보고는 이 저장소의 plan
문서에 크로스세션 검증 절로 기록(기존 하드닝 게이트 검증과 동일한 패턴).

## Self-Review 결과

- **Placeholder scan**: 없음 — 모든 변경 지점이 실제 파일:줄 번호로 명시됨.
- **Internal consistency**: Constraint 1(무회귀 diff)이 Testing Strategy·구현 순서 양쪽에 일관 반영. Constraint 4(-DexcludeTags)가 CONSTRAINTS·변경 지점 표·구현 순서 3곳에서 일치.
- **Scope check**: 단일 spec으로 충분 — 두 도구가 같은 패턴(BuildTool 분기)을 공유해 하나의 writing-plans로 이어가도 무리 없음.
- **Ambiguity check**: init script 정확한 Gradle 문법은 "구현 Task에서 검증"으로 명시적으로 열어둠(지어내지 않음) — Gradle 버전·단일/멀티모듈 조합에 따라 문법이 달라질 수 있어 spec 단계에서 확정하면 오히려 틀릴 위험.
