# Tidying Chaining — 정리가 정리를 유발하는 연쇄

> `tidying-process.md`의 보조 자료. 절차 순서를 대체하지 않는다. 한 단계를 마친 뒤
> "다음에 무엇이 가능해졌는가"를 확인하는 용도다.

정리 단계의 크기는 최대한 작게 유지한다. 하나의 정리는 다른 정리를 가능하게 하며,
정리하고 싶은 충동을 관리하는 것이 핵심 기술이다(80% 규칙).

## 연쇄 표

표의 기법명은 Tidy First 원서 명칭이다. 정본 절 대응: Guard Clause → 0. Guard Clauses, Dead Code → 6. Trimming, Explaining Variable / Explaining Constant / Extract Helper → 5. Extract Variable, Reading Order / Cohesion Order → 2. Reorder, Delete Redundant Comment → 6. Trimming, Explicit Parameters → `explicit-parameters` 스킬.

| 이 정리를 하면 | 다음이 가능해진다 |
|---|---|
| Guard Clause | 남은 조건문을 Explaining Variable / Extract Helper로 전환 |
| Dead Code(Trimming) | Reading Order / Cohesion Order로 재배치(Slide Statements) |
| Normalize Symmetries | 유사해진 병렬 코드를 Reading Order로 그룹화 (파일 상단이 목차가 된다) |
| New Interface, Old Implementation | 호출자를 하나씩 새 인터페이스로 전환 (팬아웃) |
| Reading Order | 멀리 떨어져 있어 보이지 않던 유사성이 드러나 Normalize Symmetries 가능 |
| Cohesion Order | 함께 묶인 요소가 Extract Helper / 하위 요소 추출 후보가 된다 |
| Explaining Variable | 할당의 우변이 Extract Helper 후보. 변수 이름이 중복 주석을 대체 |
| Explaining Constant | 함께 변경되는 상수를 묶어 Cohesion Order 도출 |
| Explicit Parameters | 파라미터 집합을 Parameter Object로 묶고 코드를 그 객체로 이동(system-wide 범위) |
| Chunk Statements | 각 블록에 Explaining Comment 추가 또는 Extract Helper |
| Extract Helper | 헬퍼 내부에 Guard Clause, Explaining Constant/Variable, Delete Redundant Comment |
| One Pile | 합친 뒤 Chunk Statements → Explaining Comment → Extract Helper로 재정리 |
| Explaining Comment | 주석 정보를 Explaining Variable / Constant / Helper로 코드에 이전 |
| Delete Redundant Comment | 잡음이 사라져 Reading Order와 Explicit Parameters 기회가 보인다 |

## 참조 전용 기법 — New Interface, Old Implementation

**정의**: 호출해야 하는 루틴의 인터페이스가 복잡하거나 혼란스러울 때, 원하는 형태의
새 인터페이스를 만들고 그 구현이 기존 인터페이스를 호출하게 한다(pass-through).
호출자를 새 인터페이스로 전환한 뒤 필요하면 inline한다.

**절차**:
1. 호출자 관점에서 원하는 시그니처로 새 메서드를 선언한다
2. 새 메서드 본문에서 기존 메서드를 호출한다
3. 호출자를 하나씩 새 메서드로 전환한다 (커밋 단위: 호출자 그룹별)
4. 기존 메서드의 호출자가 0이 되면 기존 메서드를 inline하거나 삭제한다

**제약**: tidying 기본 절차에 포함하지 않는다. pass-through 메서드는 Middle Man 냄새
(불필요한 간접 호출, 의미 없는 계층)를 만들 수 있다. 3단계에서 전환이 멈추면 4단계 대신
`system-wide-refactoring`의 Remove Middle Man을 적용한다.
