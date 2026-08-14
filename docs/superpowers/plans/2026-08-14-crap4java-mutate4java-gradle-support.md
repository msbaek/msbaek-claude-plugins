# crap4java·mutate4java Gradle 지원 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **저장소 안내 (중요)**: 이 계획의 Task는 **두 개의 외부 저장소**를 대상으로 한다 —
> `~/git/uncle-bob/crap4java`(Task 1~2)와 `~/git/uncle-bob/mutate4java`(Task 3~5). 이
> 계획 파일 자체는 msbaek-claude-plugins에 있지만, 실행자는 각 Task 시작 전에
> **해당 저장소로 작업 디렉터리를 옮겨서** 진행해야 한다. 커밋도 각 도구 저장소에 한다.

**Goal:** crap4java·mutate4java가 Gradle 프로젝트에서 CRAP·mutation을 Maven과 동등한 신뢰도로 산출하게 한다. Maven 경로는 완전 무회귀.

**Architecture:** 두 도구 각각에 `BuildTool`(MAVEN/GRADLE) 판별 로직을 도입해 모듈 루트 탐색·커버리지 실행·리포트 경로 계산 3곳을 분기한다. Gradle 경로는 대상 프로젝트의 `build.gradle(.kts)`를 수정하지 않고 임시 init script로 jacoco를 애드혹 적용한다. JaCoCo XML 파서는 두 도구 모두 수정하지 않는다(경로만 다르고 스키마는 같음).

**Tech Stack:** Java 17+, JUnit 5, Maven(도구 자체의 빌드), JaCoCo 0.8.12

**Spec:** `docs/superpowers/specs/2026-08-14-crap4java-mutate4java-gradle-support-design.md`

## Global Constraints

- **Maven 경로 무회귀**: `CoverageRunner`(양쪽 도구)·`ModuleRootFinder`/`moduleRootFor`를 건드리는 모든 Task는, 코드 수정 전/후로 `/Users/msbaek/git/coding-dojo/unit-testing`(Maven) 대상 CRAP·mutation 명령을 재실행해 출력이 완전 일치함을 diff로 확인한다 — 이미 baseline이 `docs/superpowers/plans/2026-08-14-hardening-gate-proposal.md`의 "3차 검증" 절에 원문으로 있다.
- **대상 프로젝트 빌드 파일 무수정**: Gradle 프로젝트의 `build.gradle(.kts)`를 절대 편집하지 않는다 — init script만 사용.
- **JaCoCo XML 파서 무수정**: `crap4java.JacocoCoverageParser`·`mutate4java.coverage.JacocoLineCoverageParser` 둘 다 이 계획에서 변경하지 않는다.
- **기존 테스트 스타일 유지**: crap4java의 `CoverageRunnerTest`는 `CommandExecutor` mock(`RecordingExecutor`) 기반, mutate4java의 `CoverageRunnerTest`는 `TestProjectFactory`로 실제 프로젝트를 만들어 실제 `mvn`/`gradle`을 돌리는 통합 테스트 스타일이다 — 각 저장소의 기존 스타일을 그대로 따른다(새 스타일을 만들지 않는다).
- **`-DexcludeTags` 제약 사용자 노출**: mutate4java의 Gradle 기본 baseline 명령에서 태그 제외가 자동으로 동작하지 않음을 CLI 경고로 알린다.

---

### Task 1: crap4java — `BuildTool` 도입 + `moduleRootFor` 확장

**Files:**
- Create: `~/git/uncle-bob/crap4java/src/crap4java/BuildTool.java`
- Modify: `~/git/uncle-bob/crap4java/src/crap4java/CliApplication.java:110-120` (`moduleRootFor`)
- Test: `~/git/uncle-bob/crap4java/test/crap4java/BuildToolTest.java` (신설)
- Test: `~/git/uncle-bob/crap4java/test/crap4java/CliApplicationTest.java` (기존 파일에 케이스 추가)

**Interfaces:**
- Produces: `enum BuildTool { MAVEN, GRADLE }` + `static BuildTool detect(Path moduleRoot)` — Task 2가 소비
- Produces: `CliApplication.moduleRootFor(Path workspaceRoot, Path file)` — 기존 시그니처 그대로, 판정 로직만 확장(Maven 전용 파일도 이 메서드로 계속 루트를 찾으므로 회귀 대상)

- [ ] **Step 1: `~/git/uncle-bob/crap4java`로 이동, 현재 브랜치·clean 상태 확인**

```bash
cd ~/git/uncle-bob/crap4java
git status --short
```
Expected: clean (변경 없음). 더러우면 중단하고 사용자에게 보고.

- [ ] **Step 2: Maven 회귀 baseline 확보 (수정 전)**

`docs/superpowers/plans/2026-08-14-hardening-gate-proposal.md`(msbaek-claude-plugins 저장소)의 "3차 검증" 절에 이미 있는 CRAP 출력을 baseline으로 재사용한다. JAR 버전이 그때와 같은지 확인:

```bash
git log -1 --format=%H
```
이 해시를 `/tmp/crap4java-baseline-commit.txt`에 기록해 Step 8에서 비교.

- [ ] **Step 3: 실패하는 테스트 작성 — `BuildToolTest.java`**

```java
package crap4java;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;

class BuildToolTest {

    @TempDir
    Path tempDir;

    @Test
    void detectsMavenWhenPomXmlPresent() throws Exception {
        Files.writeString(tempDir.resolve("pom.xml"), "<project/>");

        assertEquals(BuildTool.MAVEN, BuildTool.detect(tempDir));
    }

    @Test
    void detectsGradleWhenBuildGradlePresent() throws Exception {
        Files.writeString(tempDir.resolve("build.gradle"), "");

        assertEquals(BuildTool.GRADLE, BuildTool.detect(tempDir));
    }

    @Test
    void detectsGradleWhenBuildGradleKtsPresent() throws Exception {
        Files.writeString(tempDir.resolve("build.gradle.kts"), "");

        assertEquals(BuildTool.GRADLE, BuildTool.detect(tempDir));
    }

    @Test
    void defaultsToMavenWhenNeitherMarkerPresent() {
        assertEquals(BuildTool.MAVEN, BuildTool.detect(tempDir));
    }
}
```

- [ ] **Step 4: 테스트 실패 확인**

```bash
mvn -q -DskipTests=false -Dtest=BuildToolTest test 2>&1 | tail -20
```
Expected: 컴파일 실패(`BuildTool` 클래스 없음) 또는 테스트 실패.

- [ ] **Step 5: `BuildTool.java` 구현**

```java
package crap4java;

import java.nio.file.Files;
import java.nio.file.Path;

enum BuildTool {
    MAVEN, GRADLE;

    static BuildTool detect(Path moduleRoot) {
        if (Files.exists(moduleRoot.resolve("build.gradle"))
                || Files.exists(moduleRoot.resolve("build.gradle.kts"))) {
            return GRADLE;
        }
        return MAVEN;
    }
}
```

- [ ] **Step 6: `moduleRootFor` 확장 — `pom.xml` 단일 매치를 이중 매치로**

`CliApplication.java`의 기존 코드:
```java
static Path moduleRootFor(Path workspaceRoot, Path file) {
    Path normalizedWorkspaceRoot = workspaceRoot.normalize();
    Path current = Files.isDirectory(file) ? file.normalize() : file.normalize().getParent();
    while (current != null && current.startsWith(normalizedWorkspaceRoot)) {
        if (Files.exists(current.resolve("pom.xml"))) {
            return current;
        }
        current = current.getParent();
    }
    return normalizedWorkspaceRoot;
}
```
다음으로 교체:
```java
static Path moduleRootFor(Path workspaceRoot, Path file) {
    Path normalizedWorkspaceRoot = workspaceRoot.normalize();
    Path current = Files.isDirectory(file) ? file.normalize() : file.normalize().getParent();
    while (current != null && current.startsWith(normalizedWorkspaceRoot)) {
        if (isModuleRoot(current)) {
            return current;
        }
        current = current.getParent();
    }
    return normalizedWorkspaceRoot;
}

private static boolean isModuleRoot(Path dir) {
    return Files.exists(dir.resolve("pom.xml"))
            || Files.exists(dir.resolve("build.gradle"))
            || Files.exists(dir.resolve("build.gradle.kts"));
}
```

- [ ] **Step 7: `CliApplicationTest.java`에 Gradle 판정 케이스 추가**

기존 `moduleRootForFindsNearestAncestorWithPom` 테스트 바로 다음에 추가:
```java
@Test
void moduleRootForFindsNearestAncestorWithBuildGradle() throws Exception {
    Path moduleRoot = tempDir.resolve("tools/gradle-project");
    Path source = moduleRoot.resolve("src/main/java/Sample.java");
    Files.createDirectories(source.getParent());
    Files.writeString(moduleRoot.resolve("build.gradle"), "");
    Files.writeString(source, "class Sample {}");

    Path module = CliApplication.moduleRootFor(tempDir, source);

    assertEquals(moduleRoot, module);
}
```

- [ ] **Step 8: 전체 테스트 통과 확인**

```bash
mvn -q test 2>&1 | tail -30
```
Expected: 전부 PASS (`BuildToolTest` 4건, `CliApplicationTest` 기존 + 신규 1건 포함).

- [ ] **Step 9: Maven 회귀 diff — Global Constraints 필수 항목**

```bash
cd /Users/msbaek/git/coding-dojo/unit-testing
java -jar ~/git/uncle-bob/crap4java/target/crap4java-0.1.0-SNAPSHOT.jar \
    src/main/java/victor/testing/design/purity/PriceService.java \
    src/main/java/victor/testing/design/onion/infra/ExcelExporter.java \
    src/main/java/victor/testing/design/spy/BigService.java > /tmp/crap4java-after.txt
```
plan 문서(`docs/superpowers/plans/2026-08-14-hardening-gate-proposal.md`)의 "3차 검증" CRAP 표와 `/tmp/crap4java-after.txt`를 줄 단위로 대조. **한 글자라도 다르면 다음 단계로 가지 않는다** — `moduleRootFor`/`BuildTool` 변경이 Maven 경로에 영향을 준 것이므로 원인 규명.

- [ ] **Step 10: 커밋**

```bash
cd ~/git/uncle-bob/crap4java
git add src/crap4java/BuildTool.java src/crap4java/CliApplication.java test/crap4java/BuildToolTest.java test/crap4java/CliApplicationTest.java
git commit -m "feat: detect Gradle projects alongside Maven in module root resolution

Why: crap4java only recognized pom.xml as a module boundary, so Gradle
projects fell through to the workspace root and coverage/CRAP analysis
broke. BuildTool.detect() and the extended moduleRootFor() are the
foundation for Task 2's Gradle coverage path.

Maven regression check: re-ran CRAP against unit-testing (Maven fixture)
before and after — output identical, see docs/superpowers/plans/2026-08-14-hardening-gate-proposal.md 3차 검증 절 for baseline."
```

---

### Task 2: crap4java — Gradle 커버리지 실행 경로 신설

**Files:**
- Create: `~/git/uncle-bob/crap4java/src/crap4java/GradleInitScript.java`
- Create: `~/git/uncle-bob/crap4java/src/crap4java/GradleWrapperLocator.java`
- Modify: `~/git/uncle-bob/crap4java/src/crap4java/CoverageRunner.java` (전체 리팩터링)
- Modify: `~/git/uncle-bob/crap4java/src/crap4java/CliApplication.java:57` (jacoco XML 경로 계산)
- Test: `~/git/uncle-bob/crap4java/test/crap4java/CoverageRunnerTest.java` (기존 파일 — Maven 케이스는 그대로 두고 Gradle 케이스 추가)
- Test: `~/git/uncle-bob/crap4java/test/crap4java/GradleInitScriptTest.java` (신설)

**Interfaces:**
- Consumes: Task 1의 `BuildTool.detect(Path)`
- Produces: `CoverageRunner.generateCoverage(Path projectRoot)` — 시그니처 변경 없음(기존 호출부 무수정)

- [ ] **Step 1: `~/git/uncle-bob/crap4java`에서 clean 상태 확인**

```bash
cd ~/git/uncle-bob/crap4java && git status --short
```

- [ ] **Step 2: 실패하는 테스트 작성 — `GradleInitScriptTest.java`**

```java
package crap4java;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class GradleInitScriptTest {

    @Test
    void materializesScriptContainingJacocoPluginApplication() throws Exception {
        Path script = GradleInitScript.materialize();

        String content = Files.readString(script);
        assertTrue(content.contains("apply plugin: 'jacoco'"));
        assertTrue(content.contains("xml.required.set(true)"));
        assertTrue(Files.exists(script));
    }
}
```

- [ ] **Step 3: 테스트 실패 확인**

```bash
mvn -q -Dtest=GradleInitScriptTest test 2>&1 | tail -20
```

- [ ] **Step 4: `GradleInitScript.java` 구현**

```java
package crap4java;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

final class GradleInitScript {

    private static final String CONTENT = """
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
            """;

    static Path materialize() throws IOException {
        Path script = Files.createTempFile("crap4java-jacoco-init", ".gradle");
        Files.writeString(script, CONTENT);
        script.toFile().deleteOnExit();
        return script;
    }
}
```

- [ ] **Step 5: `GradleWrapperLocator.java` 구현 (테스트 없이 — 단순 조회, Step 7 통합 테스트로 커버)**

```java
package crap4java;

import java.nio.file.Files;
import java.nio.file.Path;

final class GradleWrapperLocator {

    static String commandFor(Path projectRoot) {
        String wrapperName = isWindows() ? "gradlew.bat" : "gradlew";
        Path wrapper = projectRoot.resolve(wrapperName);
        if (Files.isExecutable(wrapper)) {
            return wrapper.toAbsolutePath().toString();
        }
        return "gradle";
    }

    private static boolean isWindows() {
        return System.getProperty("os.name", "").toLowerCase().contains("win");
    }
}
```

- [ ] **Step 6: `CoverageRunner.java` 리팩터링 — Maven 분기는 순수 이동, Gradle 분기 신설**

기존 `generateCoverage`를 다음으로 교체(주의: `deleteIfExists`·에러 메시지는 **글자 하나까지 그대로** 유지 — Maven 경로 회귀 방지):

```java
void generateCoverage(Path projectRoot) throws Exception {
    BuildTool tool = BuildTool.detect(projectRoot);
    if (tool == BuildTool.GRADLE) {
        generateGradleCoverage(projectRoot);
    } else {
        generateMavenCoverage(projectRoot);
    }
}

private void generateMavenCoverage(Path projectRoot) throws Exception {
    deleteIfExists(projectRoot.resolve("target/site/jacoco"));
    deleteIfExists(projectRoot.resolve("target/jacoco.exec"));

    int exit = executor.run(List.of(
            "mvn", "-q",
            "org.jacoco:jacoco-maven-plugin:0.8.12:prepare-agent",
            "test",
            "org.jacoco:jacoco-maven-plugin:0.8.12:report"
    ), projectRoot);
    if (exit != 0) {
        throw new IllegalStateException("Coverage command failed with exit " + exit);
    }
}

private void generateGradleCoverage(Path projectRoot) throws Exception {
    deleteIfExists(projectRoot.resolve("build/reports/jacoco"));

    Path initScript = GradleInitScript.materialize();
    String gradleCommand = GradleWrapperLocator.commandFor(projectRoot);
    int exit = executor.run(List.of(
            gradleCommand,
            "--init-script", initScript.toString(),
            "test", "jacocoTestReport",
            "--console=plain", "-q"
    ), projectRoot);
    if (exit != 0) {
        throw new IllegalStateException("Coverage command failed with exit " + exit);
    }
}
```
`deleteIfExists` 메서드는 그대로 둔다(수정 없음).

- [ ] **Step 7: `CoverageRunnerTest.java`에 Gradle 케이스 추가 (기존 Maven 케이스는 그대로 둔다)**

기존 테스트 클래스 끝, `RecordingExecutor` 선언 앞에 추가:
```java
@Test
void deletesStaleCoverageAndRunsGradleCoverageCommand() throws Exception {
    Path jacocoDir = tempDir.resolve("build/reports/jacoco");
    Files.createDirectories(jacocoDir);
    Files.writeString(jacocoDir.resolve("old.xml"), "stale");
    Files.writeString(tempDir.resolve("build.gradle"), "");

    RecordingExecutor executor = new RecordingExecutor(0);
    CoverageRunner runner = new CoverageRunner(executor);

    runner.generateCoverage(tempDir);

    assertFalse(Files.exists(jacocoDir));
    List<String> command = executor.commands.get(0);
    assertEquals("gradle", command.get(0));
    assertEquals("--init-script", command.get(1));
    assertEquals("test", command.get(3));
    assertEquals("jacocoTestReport", command.get(4));
}
```
(마지막 `assertEquals` 인덱스는 실제 리스트 크기에 맞춰 구현 중 확인 — init script 임시 경로가 매번 달라지므로 `command.get(2)`의 정확한 값 대신 존재 여부만 확인)

- [ ] **Step 8: `CliApplication.java:57`의 jacoco XML 경로 계산 수정**

기존:
```java
Path jacocoXml = moduleRoot.resolve("target/site/jacoco/jacoco.xml");
```
교체:
```java
Path jacocoXml = BuildTool.detect(moduleRoot) == BuildTool.GRADLE
        ? moduleRoot.resolve("build/reports/jacoco/test/jacocoTestReport.xml")
        : moduleRoot.resolve("target/site/jacoco/jacoco.xml");
```

- [ ] **Step 9: 전체 단위 테스트 통과 확인**

```bash
cd ~/git/uncle-bob/crap4java && mvn -q test 2>&1 | tail -40
```

- [ ] **Step 10: Maven 회귀 diff (Task 1의 Step 9와 동일 절차, 재실행)**

```bash
cd /Users/msbaek/git/coding-dojo/unit-testing
java -jar ~/git/uncle-bob/crap4java/target/crap4java-0.1.0-SNAPSHOT.jar \
    src/main/java/victor/testing/design/purity/PriceService.java \
    src/main/java/victor/testing/design/onion/infra/ExcelExporter.java \
    src/main/java/victor/testing/design/spy/BigService.java > /tmp/crap4java-after-task2.txt
diff <(grep -A 10 "CRAP Report" /tmp/crap4java-after.txt) <(grep -A 10 "CRAP Report" /tmp/crap4java-after-task2.txt)
```
Expected: diff 출력 없음(완전 일치).

- [ ] **Step 11: Gradle 신규 동작 확인 (baseline 없음 — 실행 성공 여부만)**

```bash
cd ~/git/tdd-agent-verifiyer 2>/dev/null || echo "경로 확인 필요 — CouponUsageLimit 저장소"
# 실제 경로 확인 후:
find . -name "CouponUsageLimit.java" -o -name "RejectionReason.java"
java -jar ~/git/uncle-bob/crap4java/target/crap4java-0.1.0-SNAPSHOT.jar \
    src/main/java/com/example/coupon/CouponUsageLimit.java \
    src/main/java/com/example/coupon/RejectionReason.java
```
Expected: exit 0, CRAP Report 출력(N/A 아닌 실제 커버리지 수치). 실패하면 gradle wrapper 존재 여부·Gradle 버전 호환성 확인.

- [ ] **Step 12: 커밋**

```bash
cd ~/git/uncle-bob/crap4java
git add src/crap4java/GradleInitScript.java src/crap4java/GradleWrapperLocator.java src/crap4java/CoverageRunner.java src/crap4java/CliApplication.java test/crap4java/CoverageRunnerTest.java test/crap4java/GradleInitScriptTest.java
git commit -m "feat: run CRAP coverage analysis on Gradle projects via init script

Why: Gradle has no CLI-only way to apply a plugin ad hoc the way
'mvn org.jacoco:jacoco-maven-plugin:...' does for Maven. An init script
applies jacoco without touching the target project's build.gradle,
preserving the same zero-config promise Maven users already get.

Maven regression check: CRAP output on unit-testing identical before/after
(diff clean). New Gradle capability verified against CouponUsageLimit."
```

---

### Task 3: mutate4java — `ModuleRootFinder` Gradle 확장

**Files:**
- Modify: `~/git/uncle-bob/mutate4java/src/mutate4java/project/ModuleRootFinder.java:29`
- Test: `~/git/uncle-bob/mutate4java/test/mutate4java/project/ModuleRootFinderTest.java` (신설 — 기존에 테스트 파일 없음)

**Interfaces:**
- Produces: `ModuleRootFinder.find(Path file)` — 반환 타입·시그니처 무변경, 판정 로직만 확장

- [ ] **Step 1: `~/git/uncle-bob/mutate4java`에서 clean 상태 확인**

```bash
cd ~/git/uncle-bob/mutate4java && git status --short
```

- [ ] **Step 2: 패키지 접근을 위해 테스트 디렉터리 확인**

```bash
ls test/mutate4java/project/ 2>/dev/null || mkdir -p test/mutate4java/project
```

- [ ] **Step 3: 실패하는 테스트 작성 — `ModuleRootFinderTest.java`**

`ModuleRootFinder`가 package-private(`final class`, public 생성자 없음)이므로 테스트는 같은 패키지(`mutate4java.project`)에 둔다:

```java
package mutate4java.project;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ModuleRootFinderTest {

    @TempDir
    Path tempDir;

    @Test
    void findsNearestAncestorWithPomXml() throws Exception {
        Path moduleRoot = tempDir.resolve("module");
        Path source = moduleRoot.resolve("src/mutate4java/Sample.java");
        Files.createDirectories(source.getParent());
        Files.writeString(moduleRoot.resolve("pom.xml"), "<project/>");
        Files.writeString(source, "class Sample {}");

        Path found = new ModuleRootFinder(tempDir).find(source);

        assertEquals(moduleRoot, found);
    }

    @Test
    void findsNearestAncestorWithBuildGradle() throws Exception {
        Path moduleRoot = tempDir.resolve("gradle-module");
        Path source = moduleRoot.resolve("src/main/java/Sample.java");
        Files.createDirectories(source.getParent());
        Files.writeString(moduleRoot.resolve("build.gradle"), "");
        Files.writeString(source, "class Sample {}");

        Path found = new ModuleRootFinder(tempDir).find(source);

        assertEquals(moduleRoot, found);
    }

    @Test
    void findsNearestAncestorWithBuildGradleKts() throws Exception {
        Path moduleRoot = tempDir.resolve("kotlin-gradle-module");
        Path source = moduleRoot.resolve("src/main/java/Sample.java");
        Files.createDirectories(source.getParent());
        Files.writeString(moduleRoot.resolve("build.gradle.kts"), "");
        Files.writeString(source, "class Sample {}");

        Path found = new ModuleRootFinder(tempDir).find(source);

        assertEquals(moduleRoot, found);
    }
}
```

- [ ] **Step 4: 테스트 실패 확인 (2·3번째 케이스만 실패해야 정상)**

```bash
mvn -q -Dtest=mutate4java.project.ModuleRootFinderTest test 2>&1 | tail -30
```
Expected: `findsNearestAncestorWithPomXml`는 PASS(기존 로직으로 이미 통과), 나머지 2건 FAIL.

- [ ] **Step 5: `ModuleRootFinder.java` 수정**

기존:
```java
Path find(Path file) {
    Path current = Files.isDirectory(file) ? file : file.getParent();
    while (current != null && current.startsWith(workspaceRoot)) {
        if (Files.exists(current.resolve("pom.xml"))) {
            return current;
        }
        current = current.getParent();
    }
    return null;
}
```
교체:
```java
Path find(Path file) {
    Path current = Files.isDirectory(file) ? file : file.getParent();
    while (current != null && current.startsWith(workspaceRoot)) {
        if (isModuleRoot(current)) {
            return current;
        }
        current = current.getParent();
    }
    return null;
}

private static boolean isModuleRoot(Path dir) {
    return Files.exists(dir.resolve("pom.xml"))
            || Files.exists(dir.resolve("build.gradle"))
            || Files.exists(dir.resolve("build.gradle.kts"));
}
```

- [ ] **Step 6: 테스트 통과 확인**

```bash
mvn -q -Dtest=mutate4java.project.ModuleRootFinderTest test 2>&1 | tail -20
```

- [ ] **Step 7: Maven 회귀 diff — mutation 재실행**

```bash
cd /Users/msbaek/git/coding-dojo/unit-testing
java -jar ~/git/uncle-bob/mutate4java/target/mutate4java-0.1.0-SNAPSHOT.jar \
    src/main/java/victor/testing/design/purity/PriceService.java --mutate-all > /tmp/mutate4java-after-task3.txt
diff <(grep -E "^(KILLED|UNCOVERED|Summary)" /tmp/mutate4java-baseline.txt 2>/dev/null || true) \
     <(grep -E "^(KILLED|UNCOVERED|Summary)" /tmp/mutate4java-after-task3.txt)
```
`/tmp/mutate4java-baseline.txt`가 없으면 plan 문서 "3차 검증" 절의 mutation 출력을 그 파일로 먼저 저장한 뒤 diff. Expected: 일치. **주의**: `git status --short`로 mutate4java 저장소가 clean인지 확인(manifest 주석 부작용 재확인 — Task 3 자체는 소스에 manifest를 남기지 않지만 `--mutate-all` 실행은 대상 프로젝트(`unit-testing`)에 남길 수 있으므로 실행 후 `cd /Users/msbaek/git/coding-dojo/unit-testing && git checkout -- .`으로 즉시 원복).

- [ ] **Step 8: 커밋**

```bash
cd ~/git/uncle-bob/mutate4java
git add src/mutate4java/project/ModuleRootFinder.java test/mutate4java/project/ModuleRootFinderTest.java
git commit -m "feat: recognize Gradle projects in module root detection

Why: ModuleRootFinder only matched pom.xml, so mutation testing on Gradle
projects silently found no module root. No prior test coverage existed
for this class — added ModuleRootFinderTest alongside the fix.

Maven regression check: mutation output on unit-testing/PriceService.java
identical before/after (diff clean)."
```

---

### Task 4: mutate4java — Gradle 커버리지 실행 경로 신설

**Files:**
- Create: `~/git/uncle-bob/mutate4java/src/mutate4java/coverage/GradleInitScript.java`
- Create: `~/git/uncle-bob/mutate4java/src/mutate4java/coverage/GradleWrapperLocator.java`
- Modify: `~/git/uncle-bob/mutate4java/src/mutate4java/coverage/CoverageRunner.java`
- Test: `~/git/uncle-bob/mutate4java/test/mutate4java/TestProjectFactory.java` (기존 파일 — `createGradleProject` 메서드 추가)
- Test: `~/git/uncle-bob/mutate4java/test/mutate4java/CoverageRunnerTest.java` (기존 파일 — Gradle 케이스 추가, 기존 Maven 케이스는 그대로)

**Interfaces:**
- Consumes: Task 3의 확장된 `ModuleRootFinder`
- Produces: `CoverageRunner.generateCoverage(Path, boolean)` — 시그니처 무변경

- [ ] **Step 1: `~/git/uncle-bob/mutate4java`에서 clean 상태 확인**

```bash
cd ~/git/uncle-bob/mutate4java && git status --short
```

- [ ] **Step 2: `TestProjectFactory.java`에 Gradle 픽스처 생성 메서드 추가**

기존 `createProject(String name)` 메서드 뒤에 추가:
```java
static Path createGradleProject(String name) throws IOException {
    Path projectRoot = Files.createTempDirectory(name);
    Files.writeString(projectRoot.resolve("build.gradle"), """
            plugins {
                id 'java'
            }
            repositories { mavenCentral() }
            dependencies {
                testImplementation platform('org.junit:junit-bom:5.10.2')
                testImplementation 'org.junit.jupiter:junit-jupiter'
            }
            test { useJUnitPlatform() }
            sourceSets {
                main { java.srcDirs = ['src/mutate4java'] }
                test { java.srcDirs = ['test/mutate4java'] }
            }
            """);
    Path sourceRoot = projectRoot.resolve("src/mutate4java");
    Path testRoot = projectRoot.resolve("test/mutate4java");
    Files.createDirectories(sourceRoot);
    Files.createDirectories(testRoot);
    Files.writeString(sourceRoot.resolve("Sample.java"), """
            package mutate4java;

            class Sample {
                boolean truth() {
                    return true;
                }
            }
            """);
    Files.writeString(testRoot.resolve("SampleTest.java"), """
            package mutate4java;

            import org.junit.jupiter.api.Test;

            import static org.junit.jupiter.api.Assertions.assertTrue;

            class SampleTest {
                @Test
                void truthIsTrue() {
                    assertTrue(new Sample().truth());
                }
            }
            """);
    return projectRoot;
}
```
**주의**: 이 픽스처는 `gradle`(시스템 설치본, wrapper 없음)로 실행된다 — 실행 환경에 Gradle이 설치돼 있어야 이 테스트가 통과한다. `mvn test`를 CI 없이 로컬에서 돌릴 때만 검증 가능. Gradle 미설치 환경이면 이 통합 테스트를 `@Disabled`로 표시하는 대신, Step 8에서 실제로 실행해 확인한다(설치 여부를 이 단계에서 판단).

- [ ] **Step 3: Gradle 설치 여부 확인**

```bash
which gradle || echo "MISSING — brew install gradle 또는 SDKMAN 필요"
gradle --version 2>/dev/null | head -3
```
없으면 사용자에게 설치를 요청하고 대기(추측으로 건너뛰지 않는다).

- [ ] **Step 4: 실패하는 테스트 작성 — `CoverageRunnerTest.java`에 추가**

기존 테스트들 뒤, 마지막 테스트 다음에 추가:
```java
@Test
void generatesCoverageByRunningGradleAndParsingJacocoXml() throws Exception {
    Path projectRoot = TestProjectFactory.createGradleProject("coverage-runner-gradle");

    CoverageRun run = new CoverageRunner(new ProcessCommandExecutor()).generateCoverage(projectRoot, false);

    assertEquals(0, run.baseline().exitCode());
    assertFalse(run.reused());
    assertTrue(run.reportAvailable());
    assertTrue(run.report().covers("mutate4java/Sample.java", 5));
}
```

- [ ] **Step 5: 테스트 실패 확인**

```bash
mvn -q -Dtest=mutate4java.CoverageRunnerTest#generatesCoverageByRunningGradleAndParsingJacocoXml test 2>&1 | tail -30
```

- [ ] **Step 6: `GradleInitScript.java`·`GradleWrapperLocator.java` — crap4java Task 2와 동일 내용(패키지만 `mutate4java.coverage`)**

```java
package mutate4java.coverage;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

final class GradleInitScript {

    private static final String CONTENT = """
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
            """;

    static Path materialize() throws IOException {
        Path script = Files.createTempFile("mutate4java-jacoco-init", ".gradle");
        Files.writeString(script, CONTENT);
        script.toFile().deleteOnExit();
        return script;
    }
}
```
```java
package mutate4java.coverage;

import java.nio.file.Files;
import java.nio.file.Path;

final class GradleWrapperLocator {

    static String commandFor(Path projectRoot) {
        String wrapperName = isWindows() ? "gradlew.bat" : "gradlew";
        Path wrapper = projectRoot.resolve(wrapperName);
        if (Files.isExecutable(wrapper)) {
            return wrapper.toAbsolutePath().toString();
        }
        return "gradle";
    }

    private static boolean isWindows() {
        return System.getProperty("os.name", "").toLowerCase().contains("win");
    }
}
```
(두 저장소가 독립 Maven 모듈이라 코드 공유 불가 — 의도된 중복. spec의 "리소스 공유 검토" 결론: 공유 안 함)

- [ ] **Step 7: `CoverageRunner.java`(mutate4java) 리팩터링**

기존 `generateCoverage(Path, boolean)`에서 Maven 커맨드 실행 부분만 build-tool 분기:

기존:
```java
CommandResult result = executor.run(List.of(
        "mvn", "-q",
        "org.jacoco:jacoco-maven-plugin:0.8.12:prepare-agent",
        "test",
        "org.jacoco:jacoco-maven-plugin:0.8.12:report"
), projectRoot, COVERAGE_TIMEOUT_MILLIS);
```
교체:
```java
List<String> coverageCommand = BuildTool.detect(projectRoot) == BuildTool.GRADLE
        ? gradleCoverageCommand(projectRoot)
        : List.of(
                "mvn", "-q",
                "org.jacoco:jacoco-maven-plugin:0.8.12:prepare-agent",
                "test",
                "org.jacoco:jacoco-maven-plugin:0.8.12:report");
CommandResult result = executor.run(coverageCommand, projectRoot, COVERAGE_TIMEOUT_MILLIS);
```
새 private 메서드 추가:
```java
private List<String> gradleCoverageCommand(Path projectRoot) throws IOException {
    Path initScript = GradleInitScript.materialize();
    return List.of(
            GradleWrapperLocator.commandFor(projectRoot),
            "--init-script", initScript.toString(),
            "test", "jacocoTestReport",
            "--console=plain", "-q");
}
```
`jacocoDir`/`jacocoXml`/`jacocoExec` 경로 계산부도 build-tool 분기 필요 — 기존:
```java
Path jacocoDir = projectRoot.resolve("target/site/jacoco");
Path jacocoExec = projectRoot.resolve("target/jacoco.exec");
Path jacocoXml = jacocoDir.resolve("jacoco.xml");
```
교체:
```java
BuildTool tool = BuildTool.detect(projectRoot);
Path jacocoDir = tool == BuildTool.GRADLE
        ? projectRoot.resolve("build/reports/jacoco/test")
        : projectRoot.resolve("target/site/jacoco");
Path jacocoExec = tool == BuildTool.GRADLE
        ? projectRoot.resolve("build/jacoco/test.exec")
        : projectRoot.resolve("target/jacoco.exec");
Path jacocoXml = tool == BuildTool.GRADLE
        ? jacocoDir.resolve("jacocoTestReport.xml")
        : jacocoDir.resolve("jacoco.xml");
```
그리고 `mutate4java.coverage` 패키지에 Task 1과 동일한 `BuildTool` enum을 신설(이 파일도 Create 목록에 추가):
```java
package mutate4java.coverage;

import java.nio.file.Files;
import java.nio.file.Path;

enum BuildTool {
    MAVEN, GRADLE;

    static BuildTool detect(Path moduleRoot) {
        if (Files.exists(moduleRoot.resolve("build.gradle"))
                || Files.exists(moduleRoot.resolve("build.gradle.kts"))) {
            return GRADLE;
        }
        return MAVEN;
    }
}
```
(mutate4java 프로젝트 패키지의 `ModuleRootFinder`가 이미 판정 로직을 갖고 있지만 package-private이라 `coverage` 패키지에서 재사용 불가 — 중복이 아니라 다른 패키지의 독립 책임으로 판단. 리팩터링 여지는 있으나 이 계획에서는 최소 변경 원칙에 따라 중복 허용)

- [ ] **Step 8: 테스트 통과 확인 (Gradle 설치 필요, Step 3에서 확인됨)**

```bash
cd ~/git/uncle-bob/mutate4java && mvn -q test 2>&1 | tail -40
```

- [ ] **Step 9: Maven 회귀 diff**

Task 3의 Step 7과 동일 절차로 `PriceService.java` mutation 재실행, `/tmp/mutate4java-after-task3.txt`와 diff. 완전 일치 확인.

- [ ] **Step 10: Gradle 신규 동작 확인**

```bash
cd <CouponUsageLimit 저장소 경로, tdd-agent-verifiyer>
java -jar ~/git/uncle-bob/mutate4java/target/mutate4java-0.1.0-SNAPSHOT.jar \
    src/main/java/com/example/coupon/CouponUsageLimit.java --mutate-all
```
Expected: exit 0, KILLED/SURVIVED/UNCOVERED 요약 출력. 실행 후 `git checkout -- .`으로 대상 저장소 원복 확인.

- [ ] **Step 11: 커밋**

```bash
cd ~/git/uncle-bob/mutate4java
git add src/mutate4java/coverage/GradleInitScript.java src/mutate4java/coverage/GradleWrapperLocator.java src/mutate4java/coverage/BuildTool.java src/mutate4java/coverage/CoverageRunner.java test/mutate4java/TestProjectFactory.java test/mutate4java/CoverageRunnerTest.java
git commit -m "feat: run mutation coverage analysis on Gradle projects via init script

Why: mirrors crap4java's approach (see crap4java commit for the same
Task) — coverage generation was Maven-only, baseline/mutant test
execution was already pluggable via --test-command but coverage
collection was not.

Maven regression check: mutation output on unit-testing/PriceService.java
identical before/after (diff clean). New Gradle capability verified
against CouponUsageLimit."
```

---

### Task 5: mutate4java — 기본 baseline 명령 build-tool 분기 + `-DexcludeTags` 경고

**Files:**
- Modify: `~/git/uncle-bob/mutate4java/src/mutate4java/exec/ProcessTestCommandExecutor.java:16`
- Modify: `~/git/uncle-bob/mutate4java/src/mutate4java/engine/ExecutionContext.java` (기본 커맨드 선택 지점)
- Test: `~/git/uncle-bob/mutate4java/test/mutate4java/exec/ProcessTestCommandExecutorTest.java` (기존 파일 있으면 케이스 추가, 없으면 신설)

**Interfaces:**
- Consumes: Task 3의 `ModuleRootFinder`가 이미 판정 가능한 build tool 정보(단, `ExecutionContext`가 프로젝트 루트를 알고 있으므로 여기서 직접 `mutate4java.coverage.BuildTool`을 재사용하지 않고 — 패키지 분리 원칙에 따라 `exec` 패키지에 최소 판정 로직을 별도로 둠. 상세는 Step 4)

- [ ] **Step 1: `~/git/uncle-bob/mutate4java`에서 clean 상태 확인 + 기존 테스트 존재 확인**

```bash
cd ~/git/uncle-bob/mutate4java && git status --short
find test -iname "ProcessTestCommandExecutorTest.java"
```

- [ ] **Step 2: `ExecutionContext.java` 현재 로직 확인**

```bash
sed -n '1,50p' src/mutate4java/engine/ExecutionContext.java
```
Step 37 부근의 `executor.withCommand(parsed.testCommand())` 분기를 정확히 확인한 뒤 다음 Step 진행(구현 중 실제 코드를 보고 아래 변경을 맞춰 적용 — 이 계획은 개념만 고정, 정확한 삽입 위치는 구현 시점 확인).

- [ ] **Step 3: 실패하는 테스트 작성**

```java
package mutate4java.exec;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertTrue;

class ProcessTestCommandExecutorTest {

    @TempDir
    Path tempDir;

    @Test
    void defaultCommandUsesGradleWrapperWhenBuildGradlePresent() throws Exception {
        Files.writeString(tempDir.resolve("build.gradle"), "");

        List<String> command = ProcessTestCommandExecutor.defaultCommandFor(tempDir);

        assertTrue(command.get(0).endsWith("gradlew") || command.get(0).equals("gradle"));
        assertTrue(command.contains("test"));
    }

    @Test
    void defaultCommandStaysMavenWhenPomXmlPresent() throws Exception {
        Files.writeString(tempDir.resolve("pom.xml"), "<project/>");

        List<String> command = ProcessTestCommandExecutor.defaultCommandFor(tempDir);

        assertTrue(command.contains("mvn"));
        assertTrue(command.contains("-DexcludeTags=no-mutate"));
    }
}
```
(import 목록은 구현 시 IDE/컴파일러 오류에 맞춰 보완 — `List` import 등 누락분 포함)

- [ ] **Step 4: `ProcessTestCommandExecutor.java` 수정 — 정적 팩토리 메서드 추가**

`DEFAULT_COMMAND` 상수를 프로젝트 루트 기준 동적 계산으로 전환:
```java
static List<String> defaultCommandFor(Path projectRoot) {
    boolean gradle = Files.exists(projectRoot.resolve("build.gradle"))
            || Files.exists(projectRoot.resolve("build.gradle.kts"));
    if (gradle) {
        String wrapperName = System.getProperty("os.name", "").toLowerCase().contains("win")
                ? "gradlew.bat" : "gradlew";
        Path wrapper = projectRoot.resolve(wrapperName);
        String gradleCommand = Files.isExecutable(wrapper) ? wrapper.toAbsolutePath().toString() : "gradle";
        return List.of(gradleCommand, "test");
    }
    return DEFAULT_COMMAND;
}
```
`DEFAULT_COMMAND` 상수(`mvn test -DexcludeTags=no-mutate`)는 그대로 유지(Maven 기본값·기존 회귀 대상).

**주의(Global Constraints 4 — `-DexcludeTags` 리스크)**: Gradle 기본 커맨드에는 `-DexcludeTags` 상당 옵션을 넣지 않는다(Gradle `test` 태스크가 자동으로 해석하지 않으므로 넣어봐야 무시됨). 대신 `ExecutionContext`(Step 5)에서 Gradle 경로 선택 시 stderr에 한 줄 경고를 출력한다:
```
경고: Gradle 프로젝트는 -DexcludeTags=no-mutate가 자동 적용되지 않습니다.
      build.gradle에 useJUnitPlatform { excludeTags System.getProperty('excludeTags') }를
      직접 배선하지 않으면 no-mutate 태그가 붙은 테스트도 뮤테이션 대상에 포함됩니다.
```

- [ ] **Step 5: `ExecutionContext.java`에서 기본 커맨드 선택 지점 연결**

Step 2에서 확인한 실제 코드 구조에 맞춰, `parsed.testCommand() == null`일 때 `new ProcessTestCommandExecutor()` 대신 `new ProcessTestCommandExecutor(ProcessTestCommandExecutor.defaultCommandFor(projectRoot))`를 쓰도록 수정. Gradle 분기 진입 시 위 경고 메시지를 `err` 스트림(또는 기존 `ExecutionMessages` 클래스 관례를 따라)에 출력.

- [ ] **Step 6: 테스트 통과 확인**

```bash
cd ~/git/uncle-bob/mutate4java && mvn -q test 2>&1 | tail -40
```

- [ ] **Step 7: Maven 회귀 diff**

Task 3·4와 동일 절차로 `unit-testing/PriceService.java` mutation 재실행, 이전 결과와 diff. `DEFAULT_COMMAND` 자체는 안 바뀌었으므로 Maven 프로젝트에서는 커맨드 리스트도 완전 동일해야 한다(문자열 비교까지 포함).

- [ ] **Step 8: Gradle 경로에서 경고 메시지 실제 출력 확인**

```bash
cd <CouponUsageLimit 경로>
java -jar ~/git/uncle-bob/mutate4java/target/mutate4java-0.1.0-SNAPSHOT.jar \
    src/main/java/com/example/coupon/CouponUsageLimit.java --scan 2>&1 | grep -i "excludeTags"
```
Expected: 경고 문구 출력 확인.

- [ ] **Step 9: 커밋**

```bash
cd ~/git/uncle-bob/mutate4java
git add src/mutate4java/exec/ProcessTestCommandExecutor.java src/mutate4java/engine/ExecutionContext.java test/mutate4java/exec/ProcessTestCommandExecutorTest.java
git commit -m "feat: default to Gradle wrapper for baseline tests on Gradle projects

Why: --test-command already let users override the baseline/mutant test
command manually, but the zero-config default only worked for Maven.
Gradle's test task doesn't auto-translate -DexcludeTags the way Maven
Surefire does, so this surfaces that gap as a warning instead of
silently running every mutant regardless of no-mutate tags.

Maven regression check: default command string on unit-testing unchanged
byte-for-byte, mutation output identical before/after."
```

---

## Self-Review 결과

- **Spec coverage**: spec의 5개 구현 순서 항목이 Task 1~5로 1:1 대응. Constraint 1(무회귀 diff)이 Task 1·2·3·4·5 전부에 개별 Step으로 반영. Constraint 2(대상 프로젝트 무수정)는 init script 방식으로 Task 2·4에 반영. Constraint 3(파서 무수정)은 Task 2·4 어디에서도 `JacocoCoverageParser`/`JacocoLineCoverageParser`를 건드리지 않음으로 충족. Constraint 4(`-DexcludeTags` 경고)는 Task 5에 명시적 Step. Constraint 5(crap4java 신규 추상화)는 Task 1·2에서 기존 확장점 없이 처음부터 설계.
- **Placeholder scan**: Task 5의 Step 2·5만 "구현 시점 실제 코드 확인 후 정확한 삽입 위치 결정"으로 열어뒀다 — 이는 방치가 아니라, `ExecutionContext.java`의 정확한 현재 구조를 이 계획 작성 시점에 전부 읽지 못한 데 대한 **정직한 한계 표시**다(지어내지 않음 원칙). Step 2에서 실제 코드를 먼저 읽게 강제해 즉흥 결정이 아니라 확인 후 결정이 되도록 구성했다.
- **Type consistency**: `BuildTool` enum이 crap4java(`crap4java.BuildTool`)와 mutate4java(`mutate4java.coverage.BuildTool`)에 각각 독립 존재 — 같은 이름이지만 다른 저장소·다른 패키지라 충돌 없음. `CoverageRunner.generateCoverage` 시그니처는 두 저장소 모두 기존과 동일하게 유지(회귀 검증의 전제 조건).
- **Scope check**: 5개 Task, 2개 저장소로 나뉘지만 각 Task가 단일 저장소·단일 커밋 단위로 완결돼 있어 분리 실행 가능. msbaek-tdd 플러그인 문서(`hardening-gate.md`) 갱신은 사용자 확정대로 이 계획 범위 밖.
