---
name: tdd-rgb
description: TDD RGB 사이클 진행 - Red/Green/Blue agent 순차 위임. /tdd-rgb로 호출.
argument-hint: "[plan-doc-path]"
---

# TDD RGB 사이클 Skill

Red → Green → Blue 사이클을 조율하여 테스트 목록의 각 항목을 순차적으로 구현합니다.

## TDD 규칙

### Three Laws of TDD

1. "Write NO production code except to pass a failing test."
2. "Write only ENOUGH of a test to demonstrate a failure."
3. "Write only ENOUGH production code to pass the test."

### TDD 핵심 규칙

- don't write code without a failing test.
- only write the code necessary to get the test to pass (little golf game).
- never delete tests without express permission.
- 테스트를 추가할 때는 반드시 한번에 하나씩 추가. 실패하는 테스트가 있을 때는 절대 새로운 테스트를 추가할 수 없음.

---

## 실행 흐름

### Step 1: 현재 상태 확인

1. 템플릿 문서(*.md)에서 테스트 케이스 목록 확인
2. 첫 미완성 테스트(`- [ ]`) 식별
3. 현재 테스트 실행 상태 확인

### Step 2: RGB 사이클 실행

각 미완성 테스트(`- [ ]`)에 대해 다음 사이클을 반복:

#### Red 단계
- **tdd-red agent**에 위임
- 실패하는 테스트 작성
- approved.txt 파일 생성 (필요 시)
- 에이전트 내에서 `test:` 접두사로 커밋 수행
- **사용자 피드백 대기**

#### Green 단계
- **tdd-green agent**에 위임
- 최소 구현으로 테스트 통과
- TPP (Transformation Priority Premise) 적용
- Make-it-Work 전략 (Obvious / Fake it / Triangulation)
- 에이전트 내에서 `feat:` 접두사로 커밋 수행
- **사용자 피드백 대기**

#### Blue 단계
- **tdd-blue agent**에 위임
- Tidying 1-4단계 경량 리팩토링
  - Guard Clauses
  - Dead Code 제거
  - Normalize Symmetries
  - New Interface, Old Implementation
- 변경이 있는 경우 에이전트 내에서 `refactor:` 접두사로 커밋 수행
- **사용자 피드백 대기**

### Step 3: 완료 처리
- 체크박스 업데이트 (`- [ ]` → `- [x]`)
- 작업 내역을 마크다운 파일에 반영
- 다음 테스트 안내 또는 전체 완료

---

## 각 테스트 구현 절차 (Implement Each Test Rule)

새로운 테스트를 추가하고 코드를 구현할 때는 다음 절차를 따릅니다:

1. **실패하는 테스트 추가**
   - Test Desiderata 준수 (Isolated, Fast, Deterministic, Predictive, Specific)

2. **최소한의 코드로 테스트 성공** (Little Golf Game)
   - Make-it-Work 전략 준수
   - TPP 규칙 준수
   - 하나의 테스트가 성공하면 javadoc comment의 테스트 항목에 완료 표시('X')

3. **작업 내역을 마크다운 파일에 반영**
   - 각 테스트에 대한 작업 내역을 `### n.x` 레벨로 추가
   - multiline git commit message 수준으로 작성
   - "gutter test 추가"처럼 제목을 달고, 빈칸 넣고, 주목할 내용 2~3줄
   - code는 markdown 파일에 추가하지 않음

4. **중복 제거** (필요한 경우 리팩터링)

5. **피드백 요청**
   - "이 테스트 구현에 대한 피드백을 주시겠어요? 특히 [구현 방식/테스트 명확성/코드 품질] 부분에 대해서요."

---

## 단계별 검증 체크리스트 (Step Verification Rule)

### 1. 테스트 작성 후 확인

- [ ] 테스트가 명확한 하나의 동작만 검증하는가?
- [ ] 테스트 이름이 검증하려는 내용을 명확하게 설명하는가?
- [ ] approved.txt 파일이 필요한 경우 작성되었는가?
- [ ] 테스트가 실행되고 예상대로 실패하는가?

### 2. 구현 후 확인

- [ ] 테스트를 통과하는 가장 단순한 구현인가?
- [ ] make-it-work-strategy, TPP 규칙의 단계를 적절히 적용했는가?
- [ ] 불필요한 코드가 없는가?
- [ ] 모든 테스트가 통과하는가?

### 3. 리팩토링 후 확인

- [ ] 중복이 제거되었는가?
- [ ] 코드가 더 명확해졌는가?
- [ ] 모든 테스트가 여전히 통과하는가?

### 4. 전체 과정 후 확인

- [ ] 작업 내역이 마크다운 파일에 반영되었는가?
- [ ] 다음 단계 진행을 위한 피드백을 요청했는가?

---

## 마이크로 사이클

각 단계는 **2-3분 이내** 작업으로 빠른 피드백을 받습니다.

- 복잡한 목표를 작은, 집중된, 검증 가능한 단계로 분해하여 순차적으로 실행
- 각 R/G/B 에이전트가 작업 완료 후 자체적으로 커밋을 수행 (커밋 → 피드백 → 다음 단계)
- 좁은 범위의 태스크는 AI의 강점을 발휘하게 하고, 조기 검증은 복잡성 누적을 방지

---

## Web Usecase 추가 단계

> 모든 테스트(`- [ ]` → `- [x]`)가 완료된 후 진행합니다.

### High Level Test 활성화
- `@Disabled` 어노테이션 제거
- High Level Test가 성공하는지 확인
- 실패하는 경우 원인 분석 및 수정

### JPA Repository 전환

Fake Repository로 모든 기능이 동작하면 JPA Repository를 작성:

1. **JPA Mapping**: Entity, Value Object에 대해 JPA Mapping 작성. 필요 시 inner class를 outer class로 분리
2. **JPA Repository Interface**: JpaRepository를 상속받는 인터페이스 생성
3. **Repository Impl**: BasketRepository를 구현하고 JPA Repository에 위임하는 구현 클래스 작성
4. **테스트 전환**: @TestConfiguration 부분을 커멘트 처리하여 실제 Repository 사용
5. **클래스 다이어그램**: Repository 관련 클래스들에 대해 mermaid 다이어그램 작성

주의사항:
- @TestConfiguration이 있으면 FakeRepository 사용, 커멘트 처리하면 JPA Repository 사용
- H2 데이터베이스 미사용 (spring-boot-docker-compose로 연결)

### DSL 개선
- Protocol Driver 적용
- Test Data Builder 패턴 적용
- 가독성과 재사용성 향상

---

## 완료 조건

- 모든 테스트 케이스가 `- [x]`로 완료됨
- 모든 테스트가 통과함
- 작업 내역이 마크다운 파일에 반영됨
- (Web Usecase의 경우) High Level Test 활성화, JPA Repository 전환, DSL 개선까지 완료

## 피드백 규칙

- 한 단계에서 관련된 코드를 생성한 후에는 반드시 사용자에게 피드백을 요청
- 사용자가 명시적으로 다음 단계로 진행하는 것을 결정해야만 다음 단계로 진행
- 피드백 요청 형식: "이 [구현/테스트/설계]에 대한 피드백을 주시겠어요? 특히 [집중해야 할 부분]에 대해서요."
