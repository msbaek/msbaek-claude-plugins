# Refactoring Skills 확장 설계

## 배경

현재 `/msbaek-tdd:tidy`(7단계)와 `/msbaek-tdd:system-wide-refactoring`(3개 기법)은 전체 리팩토링 지식의 약 25%만 커버한다. vault 검색 + 웹 리서치를 통해 추가할 기법을 조사하고, 필수/선택으로 분류하여 스킬을 확장한다.

## 설계 원칙

### 분류 기준

- **필수** = 코드를 읽다 보면 거의 항상 해야 할 일 (기계적 판단). tidy/system-wide 실행 시 자동 포함.
- **선택** = 상황에 따��� 적용 여부가 다른 것 (설계 판단 or 특수 상황). 개별 slash command로 호출.
- **레거시 대응** = 범위 밖. 별도 세션에서 `/legacy-strategy` 스킬로 설계 (WEWLC 참고).

### Normalize Symmetries와 Canonical Order 통합

동일 원칙("차이는 차이를 신호해야 한다")에 기반. Canonical Order(선언 순서 일관성)는 Normalize Symmetries의 하위 적용 사례.

### Split Phase와 Functional Core & Imperative Shell ��합

FCIS(빵속빵)는 "분리 기준이 purity인 Split Phase". Split Phase 하나로 두고, FCIS는 대표적 적용 패턴으로 설명.

### Encapsulate Collection��� First Class Collection 관계

Encapsulate Collection은 First Class Collection으로 가는 중간 단계. 별도 스킬로 유지하되 관계를 명시.

---

## 변경 1: tidy 필수 파이프라인 확장

### 변경 후 파이프라인 (7단계 → 9단계)

```
0. Guard Clauses (기존)
1. One Pile — inline, 조건부 (기존)
2. Reorder — Slide Statements (기존)
2.5 Normalize Symmetries ⭐ 신규
    - 동일 ��직을 동일 방식으로 표현 통일
    - Canonical Order 포함: 필드/변수/파라미터 선언 순서 일관성
    - 원칙: "차이는 차이를 신호해야 한다"
3. Chunk Statements (기존)
4. Explaining Comment (기존)
5. Extract Variable (기존)
5.5 Split Loop ⭐ 신규
    - ���프가 2가지 이상 일을 하면 각각의 루프로 분리
    - Extract Variable/Method의 전제 조건
6. Trimming (기존)
7. 품질 게이트 (기존)
```

### 수정 대상 파일

- `msbaek-tdd/agents/tdd-blue.md` — Tidying Process에 2.5, 5.5 단계 추가
- `msbaek-tdd/skills/tdd-tidy/SKILL.md` — tdd-blue 호출 시 전달하는 단계 목록 업데이트

---

## 변경 2: system-wide 필수 기법 확장

### 변경 후 기법 목록 (3개 → 6개)

| 카테고리 | 기법 | ��경 |
|----------|------|------|
| 구조 | Extract Method | ���존 유지 |
| 구조 | Extract Delegate | 기존 유지 |
| 도메인 | Domain Logic 이동 (Feature Envy) | 기존 유지 |
| SoC | **Split by Abstraction Layer** ⭐ | 신규 — High/Low level 혼재 시 |
| SoC | **Split by Unrelated Complexity** ⭐ | 신규 — 무관한 복잡성 혼재 시 |
| SoC | **Split Phase** ⭐ | 신규 — 서로 다른 단계 혼재 시. FCIS(빵속빵)는 대표 패턴 |

### Split Phase 적용 패턴

```
Split Phase
├── 패턴 1: Functional Core & Imperative Shell (빵속빵)
│   └── I/O(impure) → 순수 로직(pure) → I/O(impure)
├── 패턴 2: 계산 단계 분리
│   └── 가격계산 → 중간DS → 배송계산
└── 패턴 3: 파싱 → 처리
    └��─ tokenize → parse → generate
```

### 수정 대상 파일

- `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` — ��드 분석 섹션에 3개 SoC 패턴 추가

---

## 변경 3: 선택 slash command 스킬 신규 생성

### tidy 계열 (5개)

| slash command | 기법 | tidy 실행 후 제안 징후 |
|---------------|------|------------------------|
| `/replace-temp-with-query` | Replace Temp with Query | 임시 변수가 여러 메서드에서 반복 계산됨 |
| `/explicit-parameters` | Explicit Parameters | 전역변수/필드에 암묵적 의존하는 메서드 발견 |
| `/decompose-conditional` | Decompose Conditional | 복잡한 if/then/else가 Guard Clauses로 해결 안 됨 |
| `/naming-process` | Naming as a Process | 이름만으로 의도 파악이 어려��� 코드가 남아있음 |
| `/encapsulate-collection` | Encapsulate Collection | 컬렉션 getter가 내부 상태를 직접 노출 |

### system-wide 계열 (7개)

| slash command | 기법 | system-wide 실행 후 제안 징후 |
|---------------|------|-------------------------------|
| `/extract-method-object` | Extract Method Object | 지역 변수 얽힘으로 Extract Method 불가 |
| `/replace-conditional-with-poly` | Replace Conditional with Polymorphism | 동일 switch/if-else가 여러 곳에 반복 |
| `/introduce-parameter-object` | Introduce Parameter Object | 3개 이상 파라미터가 함께 전달되는 패턴 반복 |
| `/discover-value-object` | Discover Value Object | primitive 타���에 로직이 집중됨 |
| `/first-class-collection` | First Class Collection | 컬렉션 + 관련 로직이 여러 클래스에 산재 |
| `/lift-up-conditional` | Lift Up Conditional | 동일 조건문이 여러 메서드에 중복 |
| `/separate-query-modifier` | Separate Query from Modifier (CQS) | 값 반환과 부수효과가 한 메서드에 혼재 |

### 선택 스킬 ��통 워크플로우

```
1. 사용자가 slash command 호출 (또는 필수 스킬 완료 후 제안에서 선택)
2. git diff로 대상 파일 수집 (또는 사용자 지정)
3. 해당 기법 적용 후보 식별 및 제시
4. 사용자 확인
5. 적용 → 테스트 → 커밋
```

---

## 변경 4: 필수 스킬 완료 후 선택 기법 제안

### tidy 완료 후

파이프라인 실행 중 발견된 징후를 기반으로 적용 가능�� 선택 기법을 제안:

```
"다음 기법을 추가로 적용할 수 있습니다:
 1. /decompose-conditional — processOrder()의 if/else 복잡
 2. /naming-process — calculateX() 등 의도 불분명한 이름 3건
 적용할 기법을 선택하세요 (번호 또는 skip)"
```

### system-wide 완료 후

필수 분석 과정에서 발견된 징후를 기반으로 제안:

```
"추가로 발견된 개선 기회:
 1. /discover-value-object — Money 관련 primitive 3곳
 2. /replace-conditional-with-poly — OrderType switch 2곳 반복
 적용할 기법을 선택하세요 (번호 또는 skip)"
```

---

## 변경 5: naming-process 스킬 내용

### 포함 내용

```
1. Naming as a Process (Arlo Belshee / Emily Bache)
   - 6단계: Nonsense → Honest → Completely Honest
     → Does the Right Thing → Intent → Domain Abstraction

2. The Scope Rule (Robert C. Martin)
   - 변수: scope ↑ → 이름 길이 ↑
   - 함수/클래스: scope ↑ → 이름 길이 ↓

3. Parts of Speech — Well-Written Prose (Grady Booch)
   - 클래스=명사, 메소드=동사, boolean=서술어

4. System of Names (Clean Code 2nd Ed.)
   - 이름들의 체계가 도메인을 전달

5. Write for Your Audience (Clean Code 2nd Ed.)
   - 작성자가 아닌 독자 경험 중심

6. 실천 규칙
   - 동일 개념에 한 단어만 (Ubiquitous Language)
   - 검색 가능한 이름 (매직 넘버 → 상수)
   - 인코딩 금지 (HN, m_, I 접두사)
   - Solution Domain Names vs Problem Domain Names

7. Naming Smells (탐지 기준)
   - 라이프사이클 이벤트 이름, -er/-Utils 접미사, 불용어 등
```

---

## 범위 밖 (별도 세션)

- **레거시 대응 전략**: Sprout Method/Class, Wrap Method/Class, New Interface Old Implementation, Parallel Change, Strangler Fig, Characterization Tests → `/legacy-strategy` 스킬로 별도 설계 (참고: `997-BOOKS/WEWLC/`)

---

## 파일 영향 범위

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `msbaek-tdd/agents/tdd-blue.md` | Modify | Tidying Process에 2.5, 5.5 단계 추가 |
| `msbaek-tdd/skills/tdd-tidy/SKILL.md` | Modify | 단계 목록 업데이트, 완료 후 선택 기법 제안 추가 |
| `msbaek-tdd/skills/system-wide-refactoring/SKILL.md` | Modify | SoC 3개 기법 추가, 완료 후 선택 기법 제안 추가 |
| `msbaek-tdd/skills/replace-temp-with-query/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/explicit-parameters/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/decompose-conditional/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/naming-process/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/encapsulate-collection/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/extract-method-object/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/replace-conditional-with-poly/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/introduce-parameter-object/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/discover-value-object/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/first-class-collection/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/lift-up-conditional/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/skills/separate-query-modifier/SKILL.md` | Create | 선택 스킬 |
| `msbaek-tdd/.claude-plugin/plugin.json` | Modify | 버전 범프, 새 스킬 등록 |

## Failure Conditions

- ❌ 필수 기법이 기존 동작을 변경 (구조 개선만 수행해야 함)
- ❌ 선택 스킬이 사용자 확인 없이 자동 실행
- ❌ tidy 선택 스킬이 system-wide 수준의 변경을 수행 (범위 초과)
- ❌ 레거시 대응 기법��� tidy/system-wide에 포함
- ❌ plugin.json에 새 스킬이 누락되어 slash command가 동작하지 않음
