# tdd-plan Spec Anchored 전환 설계

날짜: 2026-09-01
상태: 사용자 리뷰 대기
근거 자료: `~/DocumentsLocal/msbaek_vault/003-RESOURCES/AI/AI-DRIVEN-DEV/SDD, Kent Beck, and Martin Fowler - Why Spec-Anchored Development Wins.md`
실측 증거: `/Users/msbaek/temp/order-cancel-tdd/.../CancelOrder.md` (경량 도메인에 ~400줄 plan 문서, unit test 목록 0건 + 제외 근거 30줄, 승인 왕복 4회)

## 문제

현행 `/tdd-plan`은 Spec First처럼 동작한다 — 무거운 명세를 먼저 완성하고(3 에이전트 + critic + 단계별 승인), 이후 구현 단계에서 배움이 생겨도 명세로 되돌아가는 규약이 없다. 결과: 문서 장황, 느림, 경직.

플러그인은 이미 Spec Anchored의 핵심 요소를 갖고 있다 — `.feature`가 실행되는 정본(계약 테스트 = 피드백 센서), 체크박스-커밋 동기화. 없는 것은 ① 얇은 앵커, ② 배움 → 앵커 먼저 갱신 규약, ③ 무게 사다리다.

## Goal (검증 가능)

`/tdd-plan`이 얇은 앵커 문서를 만들고, 구현 내내 살아 있게 유지한다.

1. CancelOrder급 도메인에서 plan 산출 문서 **100줄 이하** (현행 실측 ~400줄)
2. plan 승인 왕복 기본 **1회** (앵커 초안 리뷰) + 미확정 사항 질문만
3. 구현 중 배움 발생 시 **앵커 갱신이 코드 변경과 같은 커밋**에 포함

## Constraints (양보 불가)

- **invent 금지 규율은 유지하되 위치 이동** — "예제 검산표 = 값의 정본, 파생 뷰는 옮겨 쓰기만" 규칙은 에이전트 지침으로 옮기고, 앵커 문서에는 산문 선언을 쓰지 않는다. 규율은 지키는 것이지 문서에 쓰는 것이 아니다.
- **`.feature` = 실행되는 정본 유지** — 인수 계층은 Cucumber가 담당, 계약 테스트가 앵커-코드 동기화를 강제한다 (Spec Anchored의 필요조건).
- **라이프사이클 후반부(5~10단계)와 정합** — Walking Skeleton·RGB·JPA·DSL·적대적 리뷰·하드닝 게이트는 그대로. plan 구간(현행 1~4단계)만 앵커 구조로 재정의된다 — 체크박스 문구·섹션 헤더가 바뀌며, "4. Unit Test 목록 작성"은 경량 기본에서 사라진다(`--full`에만 잔존). 단계 번호 재배열은 writing-plans에서 확정.
- **풀 프로세스 보존** — 현행 3 에이전트 + critic + 단계별 승인 플로우는 `--full` 플래그로 진입 (high-stakes·대형·다팀 작업용). 삭제하지 않는다.

## 설계

### 1. 앵커 문서 템플릿

plan 단계가 채우는 문서(= `/tdd`가 생성하는 템플릿의 §1~4)를 다음 구조로 교체:

```markdown
## 규칙
(도메인 규칙 — 한 줄씩. 계산·절사·상태·검증 순서)

## 예제 (검산표)
(값의 정본 — 표. 규칙 번호 참조)

## 미확정
(질문으로 해소할 항목 — 해소되면 규칙/예제로 이동)

## 진행 기록
기어: low
(체크박스·기어 전환 이력 — 현행과 동일)

## 배움 로그
(구현 중 발견 — 한 줄씩 append. 규칙이 바뀐 배움은 "규칙 N 변경:" 접두)
```

- **Gherkin 사본을 문서에 두지 않는다** — `.feature` 파일이 정본이므로 경로만 가리킨다. 현행 §2 코드블록 스냅샷은 drift 원천이라 제거.
- 산문 계층(정본 선언, 파생 뷰 선언, INVEST 점검, 제외 근거 나열) 없음.

### 2. 새 에이전트 `tdd-anchor-drafter`

1회 호출로 규칙 + 예제 검산표 + `.feature`용 Gherkin 초안을 산출한다. 기존 3 에이전트의 핵심 규율을 지침으로 흡수:

- 0층 검산 전개 (tdd-domain-modeler)
- 경계 조건 5종 스캔 — 수치·크기·상태·시간·집계 (tdd-example-designer)
- Degenerate→General 정렬 (tdd-test-list)
- invent 금지 — 원천 자료에 없는 값·규칙은 만들지 않고 "미확정"에 질문으로 남긴다

산출은 얇게: 앵커 문서 §규칙·§예제·§미확정 + `.feature` 초안.

### 3. 경량 플로우 (tdd-plan 기본)

```
tdd-anchor-drafter 1회 → 사용자 리뷰 1회 (미확정 질문 포함)
→ E-1 (/cucumber-acceptance: .feature + Runner + @pending)
→ E-2 (Walking Skeleton)
```

- critic 없음 — 사용자 리뷰 1회가 그 역할.
- **Unit Test 목록 단계 폐지** — CancelOrder 실측 채택 0건. Gherkin이 못 덮는 세밀 분기는 구현 중 발견 시 앵커 §규칙에 한 줄 추가로 대체.
- 현행 풀 단계 명세는 `skills/tdd-plan/references/full-plan.md`로 이동, `--full`로 진입.

### 4. 배움 반영 게이트 (tdd-rgb · tdd-feature)

구현 중 앵커와 어긋나는 배움 발견 시:

1. 멈추고 **앵커 먼저 갱신** (규칙/예제/배움 로그)
2. 그다음 코드 변경
3. 앵커 갱신 + 코드 변경을 **같은 커밋**에 (체크박스-커밋 동기화 규칙의 일반형)
4. **규칙이 바뀌는 배움만** 사용자에게 질문 — 나머지(구현 세부·기술 선택)는 배움 로그 한 줄로 자율 기록

연결 위치: tdd-red/green/blue 에이전트 지침 + tdd-rgb·tdd-feature 오케스트레이터의 FAILURE CONDITIONS에 "앵커와 어긋난 코드 변경을 앵커 갱신 없이 커밋" 추가.

### 5. 기존 자산 이동

| 자산 | 현행 | 변경 후 |
|---|---|---|
| tdd-domain-modeler · tdd-example-designer · tdd-test-list | tdd-plan 기본 플로우 | `--full` 전용 |
| tdd-plan-critic | plan 승인 전 필수 | `--full` 전용 |
| tdd-plan SKILL.md의 풀 단계 명세 | 본체 | `references/full-plan.md` |
| tdd-anchor-drafter | (신규) | 기본 플로우 전담 |

## Failure Conditions

- 앵커 문서에 산문 계층 부활 (정본 선언·INVEST 점검·제외 근거 나열)
- 배움을 코드에만 반영하고 앵커 미갱신, 또는 앵커 갱신을 다른 커밋으로 분리
- 앵커 문서 안에 Gherkin 사본 유지 (drift 재발)
- 경량 모드에서 3 에이전트 왕복 발생
- `--full` 플로우 삭제 또는 접근 불가
