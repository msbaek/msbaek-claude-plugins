# TDD 설계의 두 축과 Test Desiderata (정본)

사이클을 돌리는 규칙이 아니라 **왜 그 규칙인가**의 근거다. 처음 이해할 때, 또는
phase 구분이 흐려졌다고 느낄 때 읽는다.

## Interface/Implementation Split — TDD 설계의 두 축

> TDD를 논의할 때 사람들이 하는 **첫번째 오해**는 "모든 설계를 하나로 묶어야 한다"고
> 생각하는 것이다. TDD에는 **2가지 종류의 설계**가 있다. — Kent Beck

| 설계 유형 | 언제 | 누가 | 핵심 질문 |
|---|---|---|---|
| **인터페이스 설계** | 테스트 목록 작성, 테스트 코드 작성 시 | Red Phase | "이 행위가 외부에서 어떻게 호출되어야 하는가?" |
| **구현 설계** | 리팩토링 시 | Blue Phase | "이 행위를 내부적으로 어떻게 구현할 것인가?" |

### Red Phase = 인터페이스 설계 단계

- 테스트를 작성할 때 내리는 설계 결정은 주로 **인터페이스 설계(interface design)**
- 오퍼레이션의 **완벽한 인터페이스(Model Client)**를 상상
- 가능한 **최선(best possible)의 API에서 시작**해서 거꾸로 작업
- 지금 오퍼레이션이 **외부에서 어떤 식으로 보일 지**에 대한 이야기를 테스트 코드에 적는 것
- 처음부터 일을 복잡하고 보기 흉하며 "현실적"이게 하는 것보다 낫다

### Green Phase = 설계 없음, 오직 동작

- **문제를 이해**하고 **이슈를 파악**하는 단계
- **빠르게 성공시키는 것이 모든 것을 지배**
- Duct Tape Programming을 해서라도 빠르게 동작하도록
- 이렇게 구현을 해 봐야 문제를 제대로 이해할 수 있음

### Blue Phase = 구현 설계 단계

- 리팩토링 시 내리는 설계 결정은 **구현 설계(implementation design)**
- 테스트 목록 작성 시 구현 설계 결정을 혼합하면 안 됨
- **내부 구현을 어떻게 설계할 지 결정할 시간은 나중에 충분히 있음**
- 테스트 목록 작성에만 집중하면 테스트 목록을 더 잘 작성할 수 있음

## Test Desiderata

Kent Beck의 Test Desiderata — 좋은 테스트가 갖춰야 할 12가지 속성.
테스트 작성 시(Red phase) 이 속성들을 기준으로 품질을 검토한다.

> "Tests should be **coupled to the behavior of code** and **decoupled from the structure of code**."

| 속성 | 설명 |
|------|------|
| **격리성(Isolated)** | 실행 순서에 관계없이 동일한 결과 반환 |
| **조합 가능성(Composable)** | 1개든 1,000,000개든 동일한 결과 |
| **신속성(Fast)** | 빠르게 실행 |
| **신뢰성(Inspiring)** | 통과하면 배포 자신감 제공 |
| **작성 용이성(Writable)** | 테스트 작성 비용이 저렴 |
| **가독성(Readable)** | 테스트 작성 동기를 전달 |
| **동작 중심성(Behavioral)** | 동작 변화에 민감 |
| **구조 비민감성(Structure-insensitive)** | 구조 변경에 둔감 |
| **자동화(Automated)** | 인간 개입 없이 실행 |
| **구체성(Specific)** | 실패 시 원인이 명확 |
| **결정론적(Deterministic)** | 변경 없으면 결과도 불변 (shared fixture 주의) |
| **예측성(Predictive)** | 모든 테스트 통과 = 프로덕션 적합 |
