# Parallel Change (Expand → Migrate → Contract)

> 리팩터링 스킬 공통 참조. 호환성을 깨는 변경(breaking change)을 호환성을 유지하는 여러
> 작은 단계로 분해한다. 시그니처·파라미터 순서·필드·API·스키마 변경에 적용한다.

## 절차

1. **Expand(확장)**: 새 요소(메서드·파라미터·필드·컬럼·API)를 추가한다. 기존 요소는
   삭제하지 않고 유지한다. 두 요소가 공존한다. 기존 호출자는 영향을 받지 않는다.
2. **Migrate(전환)**: 호출자를 새 요소로 하나씩 옮긴다. 데이터가 있으면 dual-write(신·구
   양쪽 기록)와 read fallback(신규 없으면 기존 읽기)으로 정합성을 유지한다. 커밋 단위는
   호출자 그룹별로 나눈다.
3. **Contract(수축)**: 기존 요소의 사용처가 0임을 확인한 뒤 기존 요소를 제거한다.
   Migrate 없이 Expand → Contract로 직행하지 않는다.

## Contract 진입 판단

- 기존 요소를 참조하는 코드가 0건이다 (IDE Find Usages, 컴파일)
- 배포 단위가 여러 개면 기존 요소 접근 카운터가 관측 기간 동안 0이다

## 코드 수준 예 — 파라미터 순서 정규화(Canonical Order)

```java
// Expand: 정규 순서(needle, haystack)의 새 메서드 추가. 기존 find(haystack, needle) 유지
int find(Haystack haystack, Needle needle) { return find2(needle, haystack); }
int find2(Needle needle, Haystack haystack) { ... }

// Migrate: 호출자를 find2로 하나씩 전환 (그룹별 커밋)

// Contract: find 삭제 후 find2 → find로 rename
```

## 대규모 교체 — Branch by Abstraction

모듈·라이브러리·프레임워크 등 공급자(provider) 교체에 적용한다. 트렁크 기반 개발을 유지한다.
점진적으로 전환한다.

1. 클라이언트 코드와 현재 공급자 사이에 추상화 계층(interface)을 만든다
2. 클라이언트를 한 섹션씩 추상화 계층 호출로 전환한다
3. 새 공급자 구현을 추상화 계층 뒤에 만든다. feature flag로 전환·검증한다
4. 기존 공급자와 (필요하면) 추상화 계층을 제거한다

공통 원칙: 추상화 계층으로 다중 구현이 공존한다. 항상 빌드·정상 실행 상태를 유지한다.

## 제약

- 한 커밋에 Expand와 Contract를 함께 넣지 않는다
- Migrate 중 테스트가 실패하면 그 호출자 전환만 되돌린다
