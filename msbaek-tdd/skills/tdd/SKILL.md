---
name: tdd
description: TDD 오케스트레이터 - /tdd <type> <FQCN>으로 프로젝트 생성 및 워크플로우 안내
argument-hint: "<general|web-usecase> <FQCN>"
---

# TDD 오케스트레이터

TDD 프로젝트 생성 및 진행 상황을 관리하는 진입점입니다.

## GOAL

- **성공 = TDD 유형에 맞는 템플릿 문서가 생성되거나, 기존 프로젝트의 진행 상황이 분석되어 다음 단계가 안내됨**
- 프로젝트 생성: 템플릿 문서 + 빈 테스트 클래스 생성 후 "/tdd-plan 실행하세요" 안내
- 진행 상황 분석: 체크박스 기반 현재 단계 파악 후 적절한 다음 명령어 안내

## CONSTRAINTS

### Hard Rules

#### Ground Rule

- 모르는 정보면 모른다고 확실히 대답
- 요청에 답변하기 위해 필요한 정보가 있으면 먼저 질문
- 코드는 최신 Java, Spring Boot 기준으로 작성
- 요청하지 않는 한 리팩터링하지 않고, 절차적/명령형 스타일로 하나의 메소드로 직관적이게 작성
- 메소드 추출(extract method)이나 변수 추출(extract variable/field) 최소화
- 금액, 거리, 무게 등은 대한민국 기준
- getter/setter는 lombok 활용, 최대한 record 활용
- 마크다운 문서는 한글로 작성
- Class 파일에서 중요한 public method가 먼저, private 메소드가 나중에

#### 피드백 규칙

- 한 단계에서 관련된 코드를 생성한 후에는 반드시 사용자에게 피드백을 요청
- 사용자가 명시적으로 다음 단계로 진행하는 것을 결정해야만 다음 단계로 진행
- 피드백이 필요할 때마다 다음 형식으로 질문:

```
[피드백 요청]

- 대상: [테스트/구현/설계/리팩토링]
- 초점: [특정 관심 영역]
- 맥락: [현재까지의 작업 요약]
- 구체적 질문: [구체적인 피드백 요청 사항]
```

## OUTPUT FORMAT

### 호출 형식

```
/tdd $1 $2
```

- `$1` = `general` | `web-usecase` (TDD 유형)
- `$2` = FQCN (예: `com.example.bowling.BowlingGame`)

FQCN에서 패키지명과 클래스명을 자동 파싱합니다.
패키지명 없이 입력 시 예시를 보여주며 재입력 요청합니다.

```
예: /tdd general com.example.bowling.BowlingGame
예: /tdd web-usecase com.example.basket.CreateShoppingBasket
```

---

### 프로젝트 탐색 로직

#### 1. 빌드 시스템 탐색
- 현재 디렉토리에서 Gradle(`build.gradle`, `build.gradle.kts`) 또는 Maven(`pom.xml`) 프로젝트 루트 탐색
- 프로젝트 루트를 기준으로 경로 결정

#### 2. FQCN 기반 경로 결정

FQCN을 기반으로 다음 경로를 결정합니다:

- **템플릿 문서**: `src/test/java/{package_path}/{ClassName}.md`
- **테스트 클래스**: `src/test/java/{package_path}/{ClassName}Test.java`

예: `com.example.bowling.BowlingGame` →
- 문서: `src/test/java/com/example/bowling/BowlingGame.md`
- 테스트: `src/test/java/com/example/bowling/BowlingGameTest.java`

---

### 상태 판단

#### Case A: 템플릿 없음 → 프로젝트 생성

1. TDD 유형에 따라 템플릿 문서 생성
2. 빈 테스트 클래스 생성
3. **"/tdd-plan 실행하세요"** 안내

#### Case B: 템플릿 있음 → 진행 상황 분석

1. 체크박스 분석으로 현재 단계 파악
2. 완료된 단계와 다음 단계 안내
3. 적절한 다음 명령어 안내:
   - SRS/예제/테스트목록 미완성 → **"/tdd-plan 실행하세요"**
   - 테스트 구현 단계 → **"/tdd-rgb 실행하세요"**

---

### General TDD 템플릿 (4단계)

```markdown
# {ClassName} TDD 구현

## 절차
- [ ] 1. SRS 작성
- [ ] 2. 예제 작성
- [ ] 3. 테스트 케이스 목록 작성
- [ ] 4. 테스트 구현 (RGB 사이클)

## 1. SRS

## 2. 예제

## 3. 테스트 케이스 목록

## 4. 진행 기록
```

---

### Web Usecase TDD 템플릿 (9단계)

```markdown
# AI와 Pair로 {ClassName} Usecase를 TDD로 구현하기

## 전체적인 절차
- [ ] 1. SRS 작성
- [ ] 2. 예제 작성
- [ ] 3. High Level Test 작성
- [ ] 4. 테스트 케이스 목록 작성
- [ ] 5. Walking Skeleton 구현
- [ ] 6. 테스트 구현 (RGB 사이클)
- [ ] 7. High Level Test 활성화
- [ ] 8. JPA Repository 구현
- [ ] 9. DSL 개선

## 1. SRS

## 2. 예제

## 3. High Level Test

## 4. 테스트 케이스 목록

## 5. Walking Skeleton

## 6. 진행 기록

## 7. High Level Test 활성화

## 8. JPA Repository

## 9. DSL 개선
```

## FAILURE CONDITIONS

### 에러 대처

1. **요구사항 이해 실패** → "요구사항에 대해 제가 이해한 것이 맞는지 확인해주세요."
2. **컨텍스트 혼란** → "지금까지의 작업을 요약해주세요."
3. **구현 방향성 혼란** → "더 단순한 방법으로 목표를 달성할 수 있을까요?"
4. **테스트 실패 원인 파악 어려움** → "가능한 원인을 모두 나열해주세요."
5. **테스트 품질 저하** → Programmer Test 규칙 기준으로 품질 평가
