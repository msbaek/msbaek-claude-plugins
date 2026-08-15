---
name: tdd-rgb
description: TDD RGB 사이클 진행 - Red/Green/Blue agent 순차 위임. /tdd-rgb로 호출.
argument-hint: "[plan-doc-path] [--gear=low|mid|high]"
---

# TDD RGB 사이클 Skill

Red → Green → Blue 사이클을 조율하여 테스트 목록의 각 항목을 순차적으로 구현합니다.

## GOAL

- **성공 = 테스트 목록의 모든 항목이 `- [x]`로 완료되고, 모든 테스트가 통과하며, 작업 내역이 마크다운에 반영됨**
- 모든 테스트 케이스가 `- [x]`로 완료됨
- 모든 테스트가 통과함
- 작업 내역이 마크다운 파일에 반영됨
- (Web App의 경우) 모든 `.feature` 시나리오의 `@pending` 해제·green, JPA Repository 완성, DSL 개선까지 완료
- 검토 지점의 밀도는 기어(low/mid/high)가 정한다 — 아래 "기어(Gears)" 섹션 참조

## CONSTRAINTS

### Hard Rules

#### Three Laws of TDD

1. "Write NO production code except to pass a failing test."
2. "Write only ENOUGH of a test to demonstrate a failure."
3. "Write only ENOUGH production code to pass the test."

#### TDD 핵심 규칙

- don't write code without a failing test.
- only write the code necessary to get the test to pass (little golf game).
- never delete tests without express permission.
- 테스트를 추가할 때는 반드시 한번에 하나씩 추가. 실패하는 테스트가 있을 때는 절대 새로운 테스트를 추가할 수 없음.

#### 마이크로 사이클

각 단계는 **2-3분 이내** 작업으로 빠른 피드백을 받습니다.

- 복잡한 목표를 작은, 집중된, 검증 가능한 단계로 분해하여 순차적으로 실행
- **low·mid 기어**: 각 R/G/B 에이전트가 작업 완료 후 자체적으로 커밋을 수행 (커밋 → 피드백 → 다음 단계)
- **high 기어**: 에이전트는 커밋을 보류하고(stage까지만) 오케스트레이터가 use case 종료 시
  한 번 커밋한다 (아래 "진행 표기 규칙"의 기어별 커밋 단위)
- 좁은 범위의 태스크는 AI의 강점을 발휘하게 하고, 조기 검증은 복잡성 누적을 방지

#### 피드백 규칙

- **기어가 정의하는 검토 지점에서 반드시 사용자 피드백을 요청하고 대기** ("기어(Gears)" 섹션의 검토 지점 표 참조)
- 검토 지점에서는 사용자가 명시적으로 다음 단계로 진행을 결정해야만 진행
- 검토 지점이 아닌 phase 경계(mid/high 기어)에서는 대기 없이 다음 phase로 진행한다. 커밋은
  기어별 커밋 단위를 따른다 — low는 phase마다, mid는 사이클마다, high는 use case마다
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."

### 기어(Gears) — 검토 밀도 조절

Kent Beck의 "driving in gears": 이론에 대한 확신(confidence)이 검토 지점의 밀도를 정한다.
**기어는 검토 지점의 밀도를 바꾸고, 그에 맞춰 커밋 단위도 바뀐다** — TDD 3법칙, 한 번에
테스트 하나, 테스트 삭제 금지는 모든 기어에서 동일하지만, 커밋 단위는 low=phase,
mid=사이클, high=use case다.

**그래서 revert 단위도 기어를 따른다** — low·mid는 테스트 단위로 되돌릴 수 있지만
high는 use case 단위로만 되돌릴 수 있다. high는 확신이 높을 때 쓰는 기어이므로 이 손실을
감수하고, 대신 use case 커밋 하나가 "동작하는 기능 하나"라는 더 큰 단위의 원자성을 얻는다.
확신이 그만큼 높지 않으면 기어를 낮춘다.

#### 기어별 검토 지점

| 기어 | 검토 지점(사용자 피드백 대기) | 이해 채널(사용자가 코드를 이해하는 방법) | 대응 상황 |
|---|---|---|---|
| **low** (기본) | Red 후 · Green 후 · Blue 후 | 편집 하나하나 직접 읽기, 리팩터링도 직접 지시 (이해 체화) | 이론에 확신 없음, 낯선 도메인·기술, 학습 목적 |
| **mid** | 테스트 1개의 R→G→B 사이클 완료 후 1회 | 사이클 경계의 diff 검토 + tidying 방향 지목·승인 (실행은 위임하되 판단은 유지) | 유사 문제 경험 있음, 작동하는 이론을 빠르게 확보할 것으로 기대 |
| **high** | 전체 테스트 목록 완료 + 적대적 리뷰 통과 후 최종 1회 | 행동 명세(테스트 목록·Gherkin)로 이해 + 최종 검토에서 대표 슬라이스 하나를 골라 표본 정독 | 이론이 상용구(boilerplate) 수준으로 명확 |

#### 기어 운용 — 호출 형식·전환 신호·폭발 반경·기어 기록

사이클마다 필요한 것은 위 검토 지점 표와 아래 진행 표기 규칙 둘뿐이다. 나머지는
**시작 시 1회**(호출 형식 해석, 폭발 반경 점검, 기어 기록)와 **사이클 경계 점검 시**
(업/다운시프트 신호)에만 필요하므로 이 스킬 디렉터리의 `references/gears.md`가
정본이다. 아래 시점에 `Read`로 읽는다:

- Step 1 시작 시 — 기어 결정, 폭발 반경 점검, 기어 기록 형식
- 사이클 완료 시 — 업/다운시프트 신호 점검
- `/tdd-feature`와의 경계가 궁금할 때

기억할 최소한: **기어는 검토 밀도를 정하고, 폭발 반경은 틀렸을 때의 비용을 정한다 —
다른 축이다.** 그래서 폭발 반경 high-stakes(인증·인가, 결제·금액 계산, 데이터 삭제·변경,
외부 API, 동시성)가 감지되면 기어 권장과 별개로 **적대적 리뷰 1회가 기어와 무관하게**
실행되고, 그 diff 기준점이 될 HEAD 해시를 진행 기록에 남겨야 한다.

#### 진행 표기 규칙 (기어 무관 — 정본)

**체크박스는 커밋과 동기화된다: 표기는 그 커밋과 같은 커밋에 들어가고, 그 커밋에 담긴
만큼만 표기한다.** 기어별로 다른 규칙 세 개가 아니라 규칙 하나다 — 기어마다 커밋
단위가 달라서 결과가 달라 보일 뿐이다.

| 기어 | 커밋 단위 | 그래서 표기 |
|---|---|---|
| low | R / G / B 각각 별도 커밋 | 각 커밋에서 그 단계를 표기 |
| mid | 테스트 1개의 RGB가 한 커밋 | 그 커밋에서 R·G·B를 한 번에 표기 |
| high | **use case(User Story) 1개가 한 커밋** | 그 커밋에서 use case의 모든 테스트를 한 번에 표기 |

**high의 커밋 단위는 use case다** — 그 use case에 속한 모든 테스트의 R/G/B 변경을 한
커밋에 담는다. 따라서 에이전트는 커밋하지 않고 `git add`까지만 수행하며(커밋 보류),
use case의 마지막 테스트가 Blue까지 끝난 시점에 오케스트레이터가 한 번 커밋한다.
subject는 `feat:` 계열로 use case를 지칭하고, body에는 그 use case에서 내린 결정들을
`docs/reviewable-commits.md` 표준대로 담는다.

이 규칙은 "Red 커밋에 테스트 파일과 문서 갱신을 같은 커밋에"(`tdd-red`)의 일반형이다 —
그쪽이 low 기어의 사례이고, 이쪽이 모든 기어로 넓힌 것이다. 표기가 커밋과 갈라지는
순간 진행 기록이 실제와 어긋나고(드리프트), 나중에 대조해 고쳐도 그 사이 구간은 틀린
상태로 히스토리에 남는다.

**단, 완료 판정에 그대로 쓰지 않는다.** 현재 포맷은 테스트당 체크박스가 하나라 R/G/B를
구분해 적을 자리가 없다 — low 기어에서는 Red 커밋이 그 하나를 채우므로, **마지막
테스트가 Red만 된 상태에서도 "모두 `[x]`"가 성립한다.** 완료는 체크박스가 아니라
**전체 스위트 green**으로 판정한다(mid·high는 한 커밋에 G·B가 함께 담기므로 이 간극이
없다 — 특히 high는 use case가 green이 되어야 비로소 커밋되므로, 커밋 존재 자체가
green의 증거다).

### Principles

#### 설계의 두 축과 Test Desiderata

**phase마다 다른 설계를 한다**: Red = 인터페이스 설계("이 행위가 외부에서 어떻게
호출되어야 하는가"), Green = 설계 없음·오직 동작, Blue = 구현 설계("내부적으로 어떻게
구현할 것인가"). 이 셋을 섞지 않는 것이 사이클을 도는 이유다.

**테스트 품질의 기준**: "Tests should be coupled to the **behavior** of code and
decoupled from the **structure** of code."

Kent Beck 인용 원문, phase별 상세, Test Desiderata 12가지 속성 전체 표는 이 스킬
디렉터리의 `references/test-design-principles.md`가 정본이다 — 처음 이해할 때, 또는
phase 구분이 흐려졌다고 느낄 때 `Read`로 읽는다. (`tdd-plan`이 참조하는 정본이기도 하다.)

---

#### Mocking 가이드라인

판단에 바로 쓰는 규칙만 둔다. 근거·인용·안티패턴 전체 목록·테스트 더블 분류는
이 스킬 디렉터리의 `references/mocking-guide.md`를 `Read`로 읽는다.

**무엇을 대체하는가 — 역할(role)이지 객체가 아니다.**

| 대체해도 되는 것 | 대체하면 안 되는 것 |
|---|---|
| 다른 application service | 내부 구현(리팩토링으로 생긴 협력자) |
| driven port(경계 인터페이스) | adapter — port를 대체하지 adapter를 대체하지 않는다 |
| 아직 구현 안 된 API 경계(설계 목적) | 소유하지 않은 타입(3rd party) — 얇은 추상화로 감싼다 |
| 생성 비용이 크거나 공유되는 자원 | 데이터 객체(Entity·Value Object) — 실제 객체를 쓴다 |

**무엇으로 대체하는가 — Fake를 먼저 고려한다.** stubbing(when) 대신 `save()`,
verify 대신 `findAll()`로 실제 결과를 검증한다. 영속성 계층에서 특히 그렇다.
Mock은 상호작용 검증이 요구사항일 때만 쓴다.

**경계 객체 자체는 모킹하지 않고 통합 테스트한다.** UserService를 테스트할 때
UserRepository를 대체하고, UserRepositoryImpl은 실제 DB로 테스트한다.

**단위(unit)는 동작(behavior)의 단위다.** 격리 대상은 SUT가 아니라 테스트다
("the unit of isolation is the test not the thing under test"). 테스트끼리
격리되어 있다면 단위 테스트가 DB나 파일시스템과 통신해도 된다.

**아래가 보이면 설계 신호다 — 테스트가 아니라 대상을 고친다.**

- mock이 mock을 반환한다 / mock이 너무 많다 → code smell
- static 메서드를 모킹해야 한다 → 그건 static이 아니어야 한다
- stub한 메서드를 verify한다 / 호출 횟수를 검증한다 → CQS 위반 의심
- 클래스 격리를 위해 모든 의존성을 mock으로 채운다 → 단위 개념 오해

**모킹 자체를 줄이는 설계**: 복잡한 로직을 순수 함수로 분리하면 stubbing·verify가
사라진다 (`segregate-functional-core` 스킬 참조).

## OUTPUT FORMAT

### 실행 흐름

#### Step 1: 현재 상태 확인

1. 템플릿 문서(*.md)에서 unit test 목록 확인 (Cucumber 미사용 시 Gherkin 시나리오도 포함되어 programmer test와 섞임)
2. 첫 미완성 테스트(`- [ ]`) 식별
3. 현재 테스트 실행 상태 확인
4. **기어 결정**: `--gear` 파라미터 > 템플릿 문서의 기어 기록 > 기본 low 순으로 결정.
   `references/gears.md`를 `Read`로 읽어 폭발 반경 점검을 수행하고, high-stakes 영역이면 두 처방을 함께
   출력한다 — 한 단 낮은 기어 **권장**(사용자 결정)과 완료 시 적대적 리뷰 1회 **실행**
   (기어 무관). 경고를 출력한 경우 사용자의 기어 확정 응답을 기다린 뒤 진행한다.
   **적대적 리뷰가 예정되면**(high 기어이거나 폭발 반경 high-stakes) 현재 HEAD 해시를
   진행 기록에 남긴다 — 리뷰 diff 기준점이다.
   `--gear`로 명시 지정되었거나 문서의 기존 기록과 다를 때만 진행 기록을 갱신 —
   `--gear` 미지정 + 기록 없음이면 low로 동작하되 문서는 변경하지 않는다(하위 호환).

#### Step 2: RGB 사이클 실행

각 미완성 테스트(`- [ ]`)에 대해 다음 사이클을 반복:

##### Red 단계
- **tdd-red agent**에 위임
- 실패하는 테스트 작성 — Test Desiderata 준수
  (12가지 속성 전체는 `references/test-design-principles.md`)
- 테스트 추가 후 구현 방향이 즉시 떠오르지 않으면 Getting Stuck으로 간주 —
  tdd-green의 "Getting Stuck 복구 경로"(더 단순한 테스트로 후퇴 우선)를 따른다.
  후퇴 결정은 Red/Green 경계를 넘으므로 오케스트레이터가 인지하고 조율한다.
  후퇴가 발생하면 진행 기록에 남긴다(특히 mid/high 기어 자율 진행 중에는
  사용자가 최종 검토에서 볼 수 있도록)
- approved.txt 파일 생성 (필요 시)
- **low·mid**: 에이전트 내에서 `test:` 접두사로 커밋 수행 / **high**: 커밋 보류(`git add`까지만)
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### Green 단계
- **tdd-green agent**에 위임
- 최소 구현으로 테스트 통과 (Little Golf Game)
- TPP (Transformation Priority Premise) 적용
- Make-it-Work 전략 (Obvious / Fake it / Triangulation)
- 테스트가 성공하면 javadoc comment의 테스트 항목에 완료 표시('X')
- **low·mid**: 에이전트 내에서 `feat:` 접두사로 커밋 수행 / **high**: 커밋 보류(`git add`까지만)
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### Blue 단계
- **tdd-blue agent**에 위임
- Tidying Process — Composed Method 지향 리팩토링
  - 0. Guard Clauses (중첩 제거)
  - 1. One Pile (조건부 — Composed Method 위배 시)
  - 2. Reorder (Slide Statements)
  - 3. Chunk Statements
  - 4. Explaining Comment ← 필수1
  - 5. Extract Variable/Method ← 필수2
  - 6. Domain Logic 이동 (Advanced)
  - 7. Trimming (Advanced)
  - 8. 품질 게이트 (이해하기 어려워졌나? → One Pile 복귀)
- 변경이 있는 경우 **low·mid**는 에이전트 내에서 `refactor:` 접두사로 커밋 수행 /
  **high**는 커밋 보류(`git add`까지만)
- **검토 지점이면 사용자 피드백 대기** (low: 매 phase 후 / mid·high: 대기 없이 다음 phase)

##### 사이클 완료 시 (테스트 1개의 R→G→B 종료)

- **mid 기어**: 여기가 검토 지점 — 사이클 요약(테스트·구현·리팩토링)과 사이클 diff를 함께
  제시하고 사용자 피드백 대기. tidying 방향 지시(추가 리팩터링 지목)를 받으면 반영 후 재보고
- **high 기어**: 대기 없이 다음 테스트로 진행 (커밋하지 않는다 — 아래 "use case 완료 시")
- **기어 전환 점검** (모든 기어): `references/gears.md`의 업/다운시프트 신호를 점검하고,
  감지 시 전환을 제안 — 전환을 제안한 경우 사용자 응답을 기다린 뒤 진행한다(제안만
  출력하고 지나가지 않는다). 사용자가 수락하면 템플릿 문서의 기어 기록을 갱신하고
  다음 사이클부터 새 기어 적용
- **폭발 반경이 사이클 도중 처음 감지되면**(그 영역에 이제야 진입) 두 처방을 그때
  적용하고, diff 기준점은 **이 작업의 첫 커밋의 부모**를 남긴다 — 감지 시점 HEAD를
  남기면 리뷰 diff가 그 이전 구현을 놓친다("리뷰 diff가 전체 구현을 포함해야 한다").
  이미 기록된 기준점이 있으면 갱신하지 않는다

##### use case 완료 시 (high 기어 전용 — 커밋 지점)

use case(User Story) 하나에 속한 모든 테스트가 R→G→B를 마치면 오케스트레이터가 커밋한다.

1. **전체 스위트 green 확인** — 실패가 있으면 커밋하지 않고 원인부터 해결한다
2. **진행 기록 표기** — 그 use case의 모든 체크박스와 작업 내역을 갱신해 **같은 커밋에** 담는다
3. **커밋** — `git add` 누락분 확인 후 한 번 커밋.
   - subject: `feat(<범위>): <use case 이름>` (순수 리팩터링 use case면 `refactor:`)
   - body: `docs/reviewable-commits.md` 표준. 그 use case에서 내린 결정을 **테스트별로 나열하지
     말고 결정별로** 적는다 — 어떤 테스트를 왜 그 순서로 골랐는지, 구현에서 무엇을 버렸는지,
     tidying이 무엇을 드러냈는지
   - 한글 메시지는 임시 파일 + `git commit -F` (`-m "한글"` 금지 — 깨짐)
4. **use case 경계를 넘겨 합치지 않는다** — 두 use case를 한 커밋에 담으면 "동작하는 기능
   하나"라는 원자성이 깨진다. 이것이 high 기어가 지키는 유일한 커밋 경계다

**기어가 use case 도중 바뀌면**: high→다운시프트 시 그때까지 stage된 변경을 그 자리에서
한 번 커밋하고(불완전한 use case임을 body에 명시) 낮은 기어의 커밋 단위로 이어간다.
→high 업시프트는 이미 커밋된 것을 그대로 두고, 그 시점 이후 변경부터 use case 커밋으로 모은다.

#### Step 3: 완료 처리
- 체크박스 확인 (`- [x]`) — 표기는 각 커밋에서 이미 끝났어야 한다("진행 표기 규칙"
  참조). 아직 `- [ ]`인데 대응 커밋이 있으면 그 커밋에서 누락된 것이므로 여기서 채우고,
  왜 갈라졌는지 확인한다
- **완료 판정은 체크박스만으로 하지 않는다** — low 기어에서는 마지막 테스트가 Red만
  된 상태에서도 "모두 `[x]`"가 성립한다. 전체 스위트 green을 함께 확인한다
- **high 기어면 미커밋 변경이 없는지 확인한다** — `git status`가 깨끗해야 한다. 남아 있으면
  마지막 use case의 커밋이 누락된 것이므로 여기서 커밋한다
- 작업 내역을 마크다운 파일에 반영
- **진행 기록 대조 (모든 기어)** — 전체 완료 시, 체크된 항목과 실제 테스트 코드를
  한 번 맞춰 본다. 체크 안 된 항목을 덮는 테스트가 이미 있거나, 체크됐는데 대응
  테스트가 없으면 그 자리에서 바로잡는다. 1차 방어는 Red 커밋의 원자성이지만
  (`tdd-red`의 "테스트 파일과 체크박스 갱신을 같은 커밋에"), 리팩터링 중 테스트가
  이동·통합되면서도 어긋나므로 완료 시점에 한 번 더 본다. **드리프트는 기어와
  무관하게 발생하므로 이 대조는 low·mid·high 모두에서 수행한다**
- **Web App이면** 추가 단계(인수 테스트 완료 확인·JPA Repository 완성·DSL 개선)를
  수행한다 — `references/web-app-finish.md`
- **high 기어였거나 폭발 반경 high-stakes였다면**: 최종 사용자 검토 **전에** 적대적
  리뷰를 실행한다 — `references/adversarial-review.md`. Web App이면 위 추가 단계를
  마친 뒤에 실행한다(리뷰 diff가 전체 구현을 포함해야 하기 때문). green 스위트 +
  적대적 리뷰 통과가 이 경우의 Definition of Done. high 기어라면 최종 검토 보고에
  표본 정독 대상으로 대표 슬라이스 하나(가장 복잡했거나 후퇴가 있었던 것)를 추천해 함께 제시
- 다음 테스트 안내 또는 전체 완료

---

### 작업 내역 기록 형식

각 테스트를 구현할 때마다 템플릿 문서에 작업 내역을 남긴다 (Step 2의 사이클과 함께 수행):

- 각 테스트에 대한 작업 내역을 `### n.x` 레벨로 추가
- multiline git commit message 수준으로 작성
- "gutter test 추가"처럼 제목을 달고, 빈칸 넣고, 주목할 내용 2~3줄
- code는 markdown 파일에 추가하지 않음

---

### 조건부 절차 — references

두 절차는 조건이 맞을 때만 실행되므로 본문에 두지 않는다. 해당 시점에 `Read`로 읽는다.

| 절차 | 언제 | 정본 |
|---|---|---|
| **적대적 리뷰** | high 기어 **또는** 폭발 반경 high-stakes. 전체 green 후, 최종 사용자 검토 **전** | `references/adversarial-review.md` |
| **Web App 추가 단계** | Web App이고 모든 테스트 완료 후 (인수 테스트 확인·JPA Repository 완성·DSL 개선) | `references/web-app-finish.md` |

둘 다 해당하면 **Web App 추가 단계를 먼저** 마친 뒤 적대적 리뷰를 실행한다 — 리뷰
diff가 전체 구현을 포함해야 하기 때문이다.

`references/adversarial-review.md`는 `tdd-feature`가 그대로 참조하는 정본이기도 하다.

## FAILURE CONDITIONS

### 단계별 검증 체크리스트

#### 1. 테스트 작성 후 확인

- [ ] 테스트가 명확한 하나의 동작만 검증하는가?
- [ ] 테스트 이름이 검증하려는 내용을 명확하게 설명하는가?
- [ ] approved.txt 파일이 필요한 경우 작성되었는가?
- [ ] 테스트가 실행되고 예상대로 실패하는가?

#### 2. 구현 후 확인

- [ ] 테스트를 통과하는 가장 단순한 구현인가?
- [ ] make-it-work-strategy, TPP 규칙의 단계를 적절히 적용했는가?
- [ ] 불필요한 코드가 없는가?
- [ ] 모든 테스트가 통과하는가?

#### 3. 리팩토링 후 확인

- [ ] 중복이 제거되었는가?
- [ ] 코드가 더 명확해졌는가?
- [ ] 모든 테스트가 여전히 통과하는가?

#### 4. 전체 과정 후 확인

- [ ] 작업 내역이 마크다운 파일에 반영되었는가?
- [ ] 다음 단계 진행을 위한 피드백을 요청했는가?
- [ ] (모든 기어) 진행 기록의 체크박스와 실제 테스트가 일치하는가?
- [ ] (high 기어 **또는** 폭발 반경 high-stakes) 적대적 리뷰를 실행하고 결과를 보고했는가?
- [ ] (high 기어 **또는** 폭발 반경 high-stakes) 시작 커밋 해시가 진행 기록에 있는가?
- [ ] (high 기어) 커밋이 use case 단위로 하나씩 남았고, `git status`에 미커밋 변경이 없는가?
