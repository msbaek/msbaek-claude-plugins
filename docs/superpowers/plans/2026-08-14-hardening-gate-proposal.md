# Hardening Gate(제안만) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** tdd-feature 완료 보고에 "하드닝 제안" 블록을 추가한다 — CRAP·DRY는 즉시 실행 가능한 명령으로, mutation은 비용 경고와 함께 제안만 하고, 실행 여부는 사용자가 결정한다.

**Architecture:** SwarmForge의 hardener 역할을 msbaek-tdd 라이프사이클에 편입하되, 에이전트를 신설하지 않고(Task 4 전례 — 전역 에이전트 재사용) 기존 전역 자산(`crap4java-analyzer`·`dry4java-analyzer`·`mutate4java-runner`)에 위임하는 **제안 생성 규칙 정본** 1개를 references로 신설하고, tdd-feature 완료 보고가 이를 경로 참조한다. 자동 실행은 하지 않는다(사용자 결정: "제안만" 모드).

**Tech Stack:** Markdown (플러그인 스킬·references), JSON (버전 bump)

**Spec:** 이 계획의 배경 조사는 vault 문서 `003-RESOURCES/AI/AI-AGENTS/unclebobswarm-forge A simple tool for coordinating several AI agents..md`(SwarmForge six-pack의 cleaner/hardener 역할)와 본 세션 대화 합의(2026-08-14). 별도 spec 문서 없음 — 합의 사항은 아래 Global Constraints에 전문 수록.

## Global Constraints

- **제안만 모드**: 하드닝 도구를 자동 실행하지 않는다. 완료 보고에 제안 블록만 추가한다. (사용자 결정 2026-08-14)
- **도구 우선순위**: CRAP·DRY는 빠른 2종으로 제안 1순위(변경 파일 한정 명령 제시), mutation은 실행 비용이 크므로 비용 경고와 함께 별도 표기. (사용자 결정 2026-08-14)
- **에이전트 신설 금지**: 전역 `crap4java-analyzer`·`dry4java-analyzer`·`mutate4java-runner`(모두 `~/.claude/agents/`, sonnet, 읽기+Bash)를 재사용한다. 플러그인 로컬 중복 에이전트를 만들면 같은 트리거를 두고 경쟁한다 — 2026-08-13 plan의 Task 4 정정과 동일 원칙.
- **Maven 전용**: 3종 도구 모두 Maven JAR 기반(`crap4java`는 pom.xml+JaCoCo 필수). Gradle 프로젝트에서는 제안 블록을 생략하고 생략 사실을 한 줄 보고한다.
- **절차 지식은 references에**: 스킬 본문(tdd-feature)은 제안 규칙을 재기술하지 않고 정본 경로만 참조한다. 정본 위치는 기존 관례에 따라 `skills/tdd-rgb/references/`(adversarial-review.md 등 tdd-feature가 소비하는 정본들이 이미 이곳에 있음).
- **버전은 두 곳 함께 bump**: `msbaek-tdd/.claude-plugin/plugin.json`과 루트 `.claude-plugin/marketplace.json` 모두 1.36.0 → **1.37.0** (marketplace.json 15행의 플러그인 entry version. 8행의 marketplace 자체 version 1.2.0은 건드리지 않는다).
- **커밋 표준**: `docs/reviewable-commits.md`(없으면 `~/.claude/docs/reviewable-commits.md`)를 따른다. 한글 메시지는 temp 파일 → `git commit -F` (heredoc 금지).

---

### Task 1: 하드닝 제안 정본 신설 — `hardening-gate.md`

**Files:**
- Create: `msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md`

**Interfaces:**
- Consumes: 없음 (신규 정본)
- Produces: Task 2의 tdd-feature SKILL.md가 상대경로 `../tdd-rgb/references/hardening-gate.md`로 Read 참조. 정본이 정의하는 것 = ①적용 조건 판정 ②제안 블록 형식 ③위임 대상 에이전트 이름 3개.

- [ ] **Step 1: 정본 파일 작성**

아래 내용 그대로 생성:

````markdown
# 하드닝 제안 규칙 (Hardening Gate — 제안만)

> 정본. `tdd-feature`의 완료 보고가 이 규칙으로 제안 블록을 생성한다.
> **자동 실행하지 않는다** — 제안만 하고 실행 여부는 사용자가 결정한다.
> 배경: SwarmForge six-pack의 cleaner/hardener 역할(CRAP·DRY 리뷰, mutation 하드닝)을
> 라이프사이클 완료 지점의 선택적 게이트로 편입. 실행은 전역 에이전트에 위임한다.

## 1. 적용 조건 판정

제안 블록을 만들기 전에 순서대로 확인한다:

1. **Java 프로젝트인가** — 아니면 제안 생략(도구 3종 모두 Java 전용).
2. **Maven인가** — 프로젝트 루트에 `pom.xml`이 있는지 확인한다.
   없으면(Gradle 등) 제안 블록을 생략하고 완료 보고에 다음 한 줄만 남긴다:
   `하드닝 제안 생략 — crap4java·dry4java·mutate4java는 Maven 전용 (이 프로젝트: Gradle)`
3. **변경 파일이 있는가** — Phase B 시작 커밋 해시부터 HEAD까지의 diff에
   `src/main/java` 변경이 없으면(테스트만 변경 등) 제안을 생략한다.

## 2. 제안 블록 형식

완료 보고 마지막에 아래 블록을 붙인다. `{changed-files}`는 Phase B diff의
`src/main/java/**/*.java` 목록으로 치환한다.

```markdown
### 하드닝 제안 (선택 — 실행하지 않았음)

빠른 2종 (변경 파일 한정, 수 초~수십 초):
- CRAP 점검: "crap4java-analyzer 에이전트로 변경 파일만 CRAP 점검해줘 (--changed)"
- DRY 점검: "dry4java-analyzer 에이전트로 {changed-files} 중복 스캔해줘"

느린 1종 (파일당 수 분 — 전체 테스트 스위트를 뮤턴트마다 재실행):
- mutation 하드닝: "mutate4java-runner 에이전트로 {가장 복잡했던 파일 1개} 뮤테이션 테스트 돌려줘"
```

- mutation 제안 대상은 **파일 1개**로 한정한다 — 완료 보고의 "표본 정독용 대표
  test"에 대응하는 프로덕션 파일(가장 복잡했거나 후퇴가 있었던 것)을 고른다.
- 제안 문구는 사용자가 그대로 복사해 요청할 수 있는 자연어 명령이어야 한다.

## 3. 위임 대상 (전역 에이전트 — 플러그인 로컬 신설 금지)

| 에이전트 | 역할 | 비용 |
|---|---|---|
| `crap4java-analyzer` | 복잡도×커버리지 CRAP 점수, 임계 8.0 초과 메서드 랭킹 | 낮음 |
| `dry4java-analyzer` | 구조적 중복 쌍 탐지 + 제거 우선순위 | 낮음 |
| `mutate4java-runner` | 생존 뮤턴트 탐지 + 뮤턴트 죽이는 테스트 작성 | 높음 |

세 에이전트 모두 `~/.claude/agents/`의 전역 자산이다. 부재 환경(다른 사용자의
설치)에서는 제안 블록에 "전역 에이전트 미설치 시 이 제안은 무시" 한 줄을 덧붙인다.
````

- [ ] **Step 2: 정본 파일 생성 확인**

Run: `ls -la msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md && head -5 msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md`
Expected: 파일 존재, 첫 줄 `# 하드닝 제안 규칙 (Hardening Gate — 제안만)`

- [ ] **Step 3: 커밋**

`/tmp` 대신 세션 scratchpad에 메시지 파일 작성 후:

```bash
git add msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md
git commit -F <메시지파일>
```

메시지 subject: `feat(msbaek-tdd): 하드닝 제안 정본 신설 (SwarmForge hardener 역할 편입)`
body는 reviewable-commits 표준(Why: SwarmForge six-pack 대조에서 기존 자산 crap4java·dry4java·mutate4java가 라이프사이클에 미연결임을 발견 / 버린 대안: ①자동 실행 — 사용자가 제안만 모드 선택, ②플러그인 로컬 hardener 에이전트 신설 — 전역 에이전트와 트리거 경쟁, Task 4 전례로 기각).

---

### Task 2: tdd-feature 완료 보고에 제안 단계 연결

**Files:**
- Modify: `msbaek-tdd/skills/tdd-feature/SKILL.md:214-216` (완료 보고 bullet) 및 `:226-229` 부근 (FAILURE CONDITIONS 표)

**Interfaces:**
- Consumes: Task 1의 `../tdd-rgb/references/hardening-gate.md` (상대경로 — tdd-feature의 기존 adversarial-review.md 참조와 동일 깊이)
- Produces: 없음 (최종 소비자)

- [ ] **Step 1: 완료 보고 bullet에 하드닝 제안 추가**

`SKILL.md` 214행 부근의 완료 보고 bullet:

```markdown
- **완료 보고**: 구현된 test 목록, 커밋 해시 목록(test:/feat:/refactor:), 통과 상태,
  적대적 리뷰 결과를 요약한다. 표본 정독용으로 대표 test 하나(가장 복잡했거나 후퇴가
```

이 bullet **바로 다음**에 새 bullet 추가:

```markdown
- **하드닝 제안 (실행 아님)**: 완료 보고 마지막에 `../tdd-rgb/references/hardening-gate.md`를
  `Read`로 읽어 그 규칙대로 제안 블록을 붙인다 — CRAP·DRY(빠름, 변경 파일 한정)와
  mutation(느림, 파일 1개)을 사용자가 복사해 실행할 수 있는 명령으로. 적용 조건
  (Java·Maven·src/main 변경 존재) 미충족 시 생략 사실만 한 줄 보고. **자동 실행 금지.**
```

- [ ] **Step 2: FAILURE CONDITIONS 표에 행 추가**

228행 부근 표(`| 시작 커밋 해시 미기록 | ...`)에 행 추가:

```markdown
| 하드닝 도구를 자동 실행함 | 제안만 모드 위반 — 실행을 중단하고 제안 블록으로 되돌린다 |
```

- [ ] **Step 3: 참조 경로 실재 검증**

Run: `grep -n "hardening-gate" msbaek-tdd/skills/tdd-feature/SKILL.md && ls msbaek-tdd/skills/tdd-rgb/references/hardening-gate.md`
Expected: SKILL.md에 참조 1건 이상 + 정본 파일 존재 (상대경로 `../tdd-rgb/references/`가 기존 adversarial-review.md 참조와 동일 형태인지 눈으로 대조)

- [ ] **Step 4: 커밋**

```bash
git add msbaek-tdd/skills/tdd-feature/SKILL.md
git commit -F <메시지파일>
```

subject: `feat(msbaek-tdd): tdd-feature 완료 보고에 하드닝 제안 단계 연결`

---

### Task 3: 릴리스 — 버전 bump + README

**Files:**
- Modify: `msbaek-tdd/.claude-plugin/plugin.json:3` (`"version": "1.36.0"` → `"1.37.0"`)
- Modify: `.claude-plugin/marketplace.json:15` (플러그인 entry `"version": "1.36.0"` → `"1.37.0"`. 8행의 marketplace 자체 버전 1.2.0은 유지)
- Modify: `README.md` — `#### /tdd-feature` 섹션(184행 부근)에 한 줄 추가

**Interfaces:**
- Consumes: Task 1·2 완료 상태
- Produces: 없음

- [ ] **Step 1: plugin.json 버전 bump**

`"version": "1.36.0"` → `"version": "1.37.0"`

- [ ] **Step 2: marketplace.json 플러그인 entry 버전 bump**

15행의 `"version": "1.36.0"` → `"version": "1.37.0"` (8행 1.2.0 아님 — 대상 확인 후 수정)

- [ ] **Step 3: 두 곳 일치 검증**

Run: `grep -n '"version"' msbaek-tdd/.claude-plugin/plugin.json .claude-plugin/marketplace.json`
Expected: plugin.json 1.37.0, marketplace.json 플러그인 entry 1.37.0 (marketplace 자체 1.2.0 유지)

- [ ] **Step 4: README에 하드닝 제안 한 줄 추가**

`README.md`의 `#### /tdd-feature` 섹션 본문 끝에:

```markdown
완료 보고 시 하드닝 제안(선택)을 함께 제시한다 — CRAP·DRY(빠름)·mutation(느림)을
전역 에이전트(crap4java-analyzer·dry4java-analyzer·mutate4java-runner)로 실행하는
명령을 제안만 하고, 실행 여부는 사용자가 결정한다 (Maven 프로젝트 한정).
```

- [ ] **Step 5: 커밋**

```bash
git add msbaek-tdd/.claude-plugin/plugin.json .claude-plugin/marketplace.json README.md
git commit -F <메시지파일>
```

subject: `chore(msbaek-tdd): 1.37.0 릴리스 — 하드닝 제안 게이트`

- [ ] **Step 6: plan 상위 문서에 결과 기록**

`docs/superpowers/plans/2026-08-13-harness-agent-lifecycle.md`의 "다음 단계" 절 아래에 완료 기록 추가(Phase L/R 항목은 건드리지 않음):

```markdown
- ~~hardener 게이트~~ → **완료 (1.37.0, 2026-08-14)**: SwarmForge six-pack 대조에서
  발견한 gap — 전역 crap4java·dry4java·mutate4java 에이전트를 tdd-feature 완료 보고의
  "제안만" 게이트로 편입 (자동 실행 없음, Maven 한정). 정본:
  `skills/tdd-rgb/references/hardening-gate.md`. plan: `2026-08-14-hardening-gate-proposal.md`
```

이 수정은 Step 5 커밋에 포함하거나 별도 `docs:` 커밋 — 실행자가 판단.

---

## Self-Review 결과

- **Spec coverage**: 합의 3요소(제안만 / CRAP·DRY 우선 + mutation 비용 표기 / 전역 에이전트 재사용) 모두 Task 1 정본에 반영. Maven 제약·Gradle skip은 정본 §1. ✓
- **Placeholder scan**: 제안 블록·bullet·표 행 모두 실제 텍스트 수록. `{changed-files}` 치환 규칙은 정본에 정의됨(플레이스홀더 아님 — 런타임 치환 변수). ✓
- **Type consistency**: 정본 파일명 `hardening-gate.md`와 참조 경로 `../tdd-rgb/references/hardening-gate.md`가 Task 1·2·상위 plan 기록에서 일치. 버전 1.37.0 세 곳 일치. ✓

## 크로스세션 실증 검증 (2026-08-14, 최종 리뷰 fix 반영 후)

`tdd-agent-verifiyer` 저장소(CouponUsageLimit 도메인, **Gradle** 프로젝트 — 최종 리뷰 Finding 2를
정확히 재현하는 케이스)에서 별도 세션(`tdd-agent-verifier`)에 위임해 검증했다. 그 세션은
`/reload-plugins`로 1.37.0을 실제 로드한 뒤, `/tdd-feature` Phase B를 실제로 진행(G-E5·E6·E8
커밋, `6e7f1db~137c190`)시켜 진짜 완료 보고를 만들어냈다.

검증 항목과 결과:
- **Gradle 시 CRAP·mutation 생략 + DRY 유지 (Finding 2 수정)**: 완료 보고에 `hardening-gate.md
  §1-2` 문구와 정확히 일치하는 `CRAP·mutation 제안 생략 — Maven 전용 (이 프로젝트: Gradle).
  DRY 제안은 계속 진행`이 그대로 출력됨. 이 저장소에 `pom.xml`이 없음을 직접 확인.
- **`{changed-files}` 명시적 치환 (Finding 1 수정)**: DRY 제안 줄이 Phase B 시작 커밋~HEAD diff
  기준 실제 변경 파일 2개(`CouponUsageLimit.java`, `RejectionReason.java`)로 정확히 치환됨.
- **DRY 제안 명령 실제 실행**: `dry4java-analyzer` 에이전트로 그 명령을 그대로 실행 — Gradle
  프로젝트인데도 `pom.xml` 요구 없이 두 파일 스캔 성공(중복 0건). Finding 2의 핵심 주장
  (dry4java는 빌드 도구 무관)이 실동작으로 증명됨.
- **CRAP `--changed`→명시적 파일 목록 (Finding 1)**: 이 저장소는 Maven이 아니라 직접 재현
  불가 — `hardening-gate.md §2`의 `{changed-files}` 문구 대조로만 확인(내용 일치).

3건의 수정 중 2건(Gradle skip 정확성, DRY 실동작)은 실제 실행까지, 1건(CRAP 명시적 목록)은
문서 대조로 검증 완료. 부작용: 검증 과정에서 그 세션의 CouponUsageLimit feature가 일부
진행됨(별도 프로젝트 — 완료·되돌림 여부는 그 세션에서 판단).

## 크로스세션 실증 검증 2차 — CRAP·mutation 실동작 (2026-08-14)

1차 검증은 Gradle 프로젝트라 DRY만 실제 실행했고, CRAP·mutation(둘 다 Maven 전용)은 문서
대조로만 확인했다. "게이트가 조건을 맞게 판단하는 것"과 "제안된 명령이 실제로 결함을
잡아내는 것"은 다른 질문이라는 지적을 받아, 같은 `tdd-agent-verifier` 세션에 Maven
프로젝트(`/Users/msbaek/git/coding-dojo/unit-testing`, Spring Boot 3.1.4, 학습용 저장소라
코드·커밋 변경 없이 분석만)로 전환해 나머지 2종을 실행시켰다.

검증 항목과 결과:
- **CRAP 점검**: `hardening-gate.md`가 제안하는 정확한 형태(`{changed-files}` 명시적 목록,
  `--changed` 아님)로 3개 파일(`PriceService`·`ExcelExporter`·`BigService`)을 실제 실행.
  유의미한 실제 점수 산출 확인 — `exportExcel` CC 4/coverage 0%/**CRAP 20.0**(임계 8.0 초과,
  테스트 없음 직접 확인), `doComputePrices` CC 6/coverage 100%/**CRAP 6.0**(양호). 동일 명령
  재실행으로 수치 완전 일치 확인. N/A는 극소 메서드 1건뿐, 정직하게 표시됨.
- **mutation 하드닝**: 테스트 없는 파일(`ExcelExporter`, CRAP 최고)로 먼저 시도 → 12개 사이트
  전부 UNCOVERED(정직한 결과지만 탐지력 증명은 못 함). 테스트 있는 파일(`PriceService`)로
  재시도 → 커버된 5개 뮤턴트 전부 KILLED(`&&`↔`||`, null 대입, `!contains`↔`contains` 등) —
  도구가 실제 결함을 잡아낸다는 것을 증명(생존 뮤턴트였다면 커버리지는 있어도 assertion이
  약하다는 뜻이었을 것).
- **부수 발견**: `~/git/uncle-bob/mutate4java` 저장소가 존재하지 않는 parent POM을 참조해
  standalone 빌드가 원래도 안 되는 구조(원본 GitHub도 동일 — crap4java·dry4java와 달리
  모노레포 전제 설계). 검증 세션이 `<parent>` 블록을 임시로 groupId/version 직접 명시로
  치환해 빌드 후 `git checkout`으로 원복(현재 clean, origin과 일치) — 이 계획의 범위 밖
  이슈이며 하드닝 게이트 자체와 무관.

이로써 하드닝 게이트가 제안하는 CRAP·DRY·mutation **3종 모두** 실제 명령 실행까지 검증
완료됐다 — 앞서 "게이트가 맞는 조건에서 맞는 명령을 제안하는가"만 확인됐던 것에서,
"그 명령들이 실전에서 진짜 결함을 잡아내는가"까지 확인됨.
