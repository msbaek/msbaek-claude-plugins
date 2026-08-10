# msbaek-tdd: vault 기법 반영 — Getting Stuck 복구 + tdd-legacy 설계

- 날짜: 2026-08-10
- 배경: vault 전수 조사(scout 팬아웃 + 정독 + 적대적 검증)에서 살아남은 후보 중
  사용자가 선택한 2건. 조사 리포트의 후보 1(confirmed)·2(weaken, 출처 교체 조건)에 해당.
- 상태: 설계 승인됨 (구현 전)

## Goal (testable)

1. Getting Stuck 상황의 복구 경로가 2단계(① 더 단순한 테스트로 후퇴 ② Fake it)로
   명시되고, tdd-rgb Red phase가 이를 참조한다.
2. tdd-plan의 unit test 목록 단계에 degenerate-first 순서의 **도출 절차**
   (중요 테스트 → stair-step 역추적 → reverse order 정렬)가 명시된다.
3. `/tdd-legacy` 스킬이 신설되어 Characterization → Approval → Mutation 3단계로
   안전망을 구축하고, 완료 시 기존 개선 스킬로 핸드오프한다.

## Constraints (non-negotiable)

- 스킬 이름: `tdd-legacy`. 범위: 안전망 구축 + 핸드오프까지 — seam 생성·의존성 깨기·
  리팩토링 실행은 범위 밖(기존 tdd-tidy/system-wide-refactoring 안내로 대체).
- mutation 도구: `mutate4java` agent가 환경에 있으면 1순위 사용, 없으면 스킬에
  내장된 PIT(gradle/maven) 설정·실행 가이드로 fallback (기어 모델의
  adversarial-reviewer fallback과 같은 이식성 패턴).
- 1차 출처 우선: `997-BOOKS/clean-coders-my-youtube/27_레거시코드에_테스트_추가를_위한_3가지_기법.md`
  (본인 콘텐츠, PIT 수치 포함) + WEWLC 챕터. Emily Bache 노트는 보조.
- "ApprovalTests가 기본 선택"으로 서술하지 않는다 — 설계 품질에 따른
  unit test vs approval 트레이드오프로 서술 (검증 게이트의 weaken 권고).
- 작업 브랜치: `feat/vault-techniques`.

## 설계 A — Getting Stuck 복구 + 테스트 목록 역순 정렬 (델타)

출처: `003-RESOURCES/TDD/As the Tests Get More Specific, the Code Gets More Generic.md`
(§6.4 Getting Stuck, §6.5 Most Degenerate First)

### A-1. tdd-green 복구 경로 2단계화 (`agents/tdd-green.md`)

현재 "Getting Stuck 위험 - 막히면 즉시 Fake it으로 전환"(단일 경로)을 2단계로 교체:

1. **테스트가 너무 큰 도약인지 먼저 판단** — 그렇다면 **Write a simpler test**:
   현재 테스트를 잠시 치우고 더 단순한 테스트로 후퇴(Red로 복귀, tdd-red 인계).
   근거: Getting Stuck의 원인은 잘못된(너무 구체적인) 테스트 또는 너무 일반적인
   코드이므로 Fake it으로 해결되지 않는 경우가 있다.
2. **테스트 크기가 적절한데 구현이 안 보이면** — Fake it (기존 경로 유지).

### A-2. tdd-rgb Red phase 가드레일 (`skills/tdd-rgb/SKILL.md`)

Red 단계 설명에 1줄 추가: 실패 테스트 추가 후 구현 방향이 즉시 떠오르지 않으면
Getting Stuck으로 간주하고 tdd-green의 2단계 복구 경로를 따른다(더 단순한 테스트로
후퇴하는 결정은 Red/Green 경계를 넘으므로 오케스트레이터가 인지해야 함).

### A-3. tdd-plan 목록 도출 알고리즘 (`skills/tdd-plan/SKILL.md` 단계 3)

기존 "Degenerate → Simple → General 정렬" 요구(결과)에 도출 절차를 추가:

1. 가장 중요한 테스트(핵심 시나리오)를 먼저 적는다
2. 거기 도달하기 위한 징검다리(stair-step) 테스트를 거슬러 내려간다
3. most degenerate 테스트를 발견할 때까지 반복한다
4. 목록을 **reverse order로 정렬**해 degenerate-first 순서를 만든다

## 설계 B — 신규 스킬 `/tdd-legacy` (안전망 + 핸드오프)

### 목적과 위치

테스트 없는 기존 코드에 행위 보존 안전망을 구축한 뒤 기존 개선 스킬로 핸드오프.
신규 코드 전제인 tdd-plan/tdd-rgb/tdd-feature와 상보적. 파일 위치:
`msbaek-tdd/skills/tdd-legacy/SKILL.md`. 신규 agent는 만들지 않는다(오케스트레이터가
직접 진행하거나 기존 agent 재사용 없음 — 단일 스킬 문서).

### 3단계 워크플로우

**1단계. Characterization** — 현재 행위를 있는 그대로 고정:

- 대상 메소드/클래스 선정(변경 예정 지점 우선 — WEWLC 11장 관점)
- golden master 방식으로 현재 출력을 그대로 어설션에 고정 (옳은 행위가 아니라
  현재 행위를 기록한다는 원칙 명시)
- **어설션 정확성 검증: SUT sabotage** — 통과하는 어설션마다 SUT를 일시적으로
  깨서 실제로 실패하는지 개별 확인 후 되돌림 (동어반복 어설션 방지)
- **비결정 출력은 scrubber로 정규화** (타임스탬프·랜덤·순서 등)

**2단계. Approval** — 조합 폭발 구간 커버리지 확장:

- 입력 조합이 많은 구간은 `CombinationApprovals.verifyAllCombinations()`로 확장
- 판단 기준(트레이드오프)을 명시: 설계가 매우 나쁠 때는 approval이 효율적,
  설계가 좋거나 리팩토링이 진행되면 composable한 unit test가 낫다 — 둘은 공존 가능

**3단계. Mutation 검증** — 안전망이 실제로 작동하는지 확인:

- 환경에 `mutate4java` agent가 있으면 dispatch (1순위)
- 없으면 내장 가이드로 PIT를 gradle/maven에 설정하고 대상 클래스에 실행
- 살아남은 뮤턴트는 안전망의 구멍 — 테스트를 보강해 죽인다
- DoD: 대상 메소드 기준 mutation score 100% 또는 사용자 합의 임계값

### 완료와 핸드오프

3단계 통과 시: "안전망 완료 — 이제 `/tdd-tidy`(정리) 또는
`/system-wide-refactoring`(구조 개선)으로 진행하세요" 안내를 출력하고 종료.
개선 실행은 이 스킬 범위 밖.

### 피드백 규칙

단계(1→2→3) 경계마다 사용자 검토 후 진행. 기어 모델 통합은 이번 범위 제외 —
레거시는 정의상 확신이 낮은 상황이므로 low 상당의 밀도로 고정.

### 커밋

단계별 커밋: `test:` (characterization/approval 테스트 추가), `test:` (뮤턴트 킬
보강). 커밋 메시지는 reviewable-commits 표준 참조(기존 스킬과 동일 패턴).

## 문서 동기화

- `README.md`: 핵심 워크플로우에 `/tdd-legacy` 절 추가, 디렉토리 트리·관계도 갱신
- `plugin.json`·`marketplace.json` 버전 범프는 머지·배포 시점에 별도 커밋(1.11.0)

## 검증(승인 조건)

1. tdd-green에 2단계 복구 경로가 있고 "즉시 Fake it" 단일 경로가 남아있지 않다
2. tdd-plan 단계 3에 4단계 도출 절차가 있다
3. `/tdd-legacy` 스킬 파일이 존재하고 3단계 + sabotage + scrubber + 트레이드오프
   + mutate4java/PIT fallback + 핸드오프 문구를 포함한다
4. "ApprovalTests가 기본"이라는 단정 서술이 없다
5. 기존 25개 스킬·agents 3개는 A-1/A-2/A-3 대상 파일 외 무변경

## 버린 대안

- **후보 3~6(테스트 diff 우선 읽기, 셀프 체크 게이트, sabotage Green 통합, Fun List)**:
  사용자가 1·2번만 선택. 추후 소규모 델타로 추가 가능.
- **레거시 스킬에 리팩토링까지 통합**: 기존 스킬과 중복, 스킬 비대화. 핸드오프로 대체.
- **PIT 직접 내장만(mutate4java 미언급)**: 사용자 환경 최적화 포기라 기각 —
  있으면 사용 + fallback 패턴 채택.
- **sabotage를 Blue phase에 배치**: Blue는 동작 불변 전제라 충돌(검증 게이트 지적).
  tdd-legacy의 characterization 단계 내 절차로만 채택.
