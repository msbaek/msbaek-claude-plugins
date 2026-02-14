# Canon TDD → TDD Plugin 통합 설계

## 목표

Canon TDD(Kent Beck) 문서의 핵심 개념들을 msbaek-tdd 플러그인에 반영하여,
Interface/Implementation Split을 중심으로 TDD의 각 단계가 어떤 설계 결정을 다루는지 명확히 한다.

## 접근법: 계층적 배치 (A)

- `tdd-rgb` skill: "왜(Why)" — Interface/Implementation Split 핵심 철학
- `tdd-red` agent: "어떻게(How)" — 인터페이스 설계 구체적 지침
- `tdd-green` agent: "어떻게(How)" — 빠른 동작 달성 지침
- `tdd-blue` agent: "어떻게(How)" — 구현 설계 구체적 지침

## 변경 파일 목록

### 1. msbaek-tdd/skills/tdd-rgb/SKILL.md

**추가 위치**: "## TDD 규칙" 다음, "## Test Desiderata" 앞

**추가 내용**: "## Interface/Implementation Split — TDD 설계의 두 축"
- Kent Beck 인용: "모든 설계를 하나로 묶어야 한다는 오해"
- 인터페이스 설계 vs 구현 설계 테이블
- Red = 인터페이스 설계, Green = 동작에 집중, Blue = 구현 설계
- Model Client 개념 소개

### 2. msbaek-tdd/agents/tdd-red.md

**추가 위치**: "## Core Focus: Red Phase Only" 다음

**추가 내용**: "## 인터페이스 설계 원칙 (Canon TDD Step 2)"
- Model Client 원칙: 완벽한 인터페이스를 상상, 최선의 API에서 시작
- Assert → Act → Arrange 순서: 기대값 먼저 작성, 이중 부기 원칙
- Step 2 흔한 실수들: assert 없는 테스트, 모든 테스트 한번에 변환, 실패 확인 건너뜀

### 3. msbaek-tdd/agents/tdd-green.md

**추가 위치**: "## Core Focus: Green Phase Only" 다음

**추가 내용**: "## Canon TDD Step 3 원칙"
- Append-only 테스트 목록: 새 테스트 발견 시 목록에만 추가
- 테스트 순서 변경 전략: 현재 구현 무효화 시 순서 변경
- Step 3 흔한 실수들: assert 삭제, 계산값 복사, 구현과 리팩토링 혼합
- Duct Tape Programming 맥락 보강

### 4. msbaek-tdd/agents/tdd-blue.md

**추가 위치**: "## Core Focus: Blue Phase Only" 다음

**추가 내용**: "## 구현 설계 원칙 (Canon TDD Step 4)"
- 80% 규칙: 할 수 있는 수준의 80% 이하로 리팩토링
- Step 4 흔한 실수들: 과도한 리팩토링, 조기 추상화, 리팩토링 건너뜀
- 두 가지 가치(동작/구조): 다음 동작 전 반드시 구조 개선
- Ian Cooper 인용: "리팩토링을 많이 안 하면 upfront 설계를 너무 많이 한 것"

## 설계 원칙

1. **기존 내용 변경 없음** — 새로운 섹션만 추가 (append only)
2. **정보가 필요한 곳에 배치** — 각 agent가 해당 단계의 Canon TDD 지혜를 직접 참조
3. **중복 최소화** — tdd-rgb에서 전체 철학, agent에서 해당 단계의 구체적 지침
4. **Canon TDD 원문 톤 유지** — Kent Beck, Ian Cooper 인용 활용
