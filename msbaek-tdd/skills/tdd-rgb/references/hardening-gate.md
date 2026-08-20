# 하드닝 제안 규칙 (Hardening Gate — 제안만)

> 정본. `tdd-feature`의 완료 보고와 `tdd-rgb`의 전체 완료 처리(Step 3 최종 검토 보고)가
> 이 규칙으로 제안 블록을 생성한다.
> **자동 실행하지 않는다** — 제안만 하고 실행 여부는 사용자가 결정한다.
> 배경: SwarmForge six-pack의 cleaner/hardener 역할(CRAP·DRY 리뷰, mutation 하드닝)을
> 라이프사이클 완료 지점의 선택적 게이트로 편입. 실행은 전역 에이전트에 위임한다.
> 시점: 제안은 구현 완료 보고 한 곳에서 하되, **블록 안에 파이프라인 순서를 담는다** —
> CRAP·DRY(정리할 곳 찾기) → `/system-wide-refactoring`(정리) → mutation(정리된 코드의
> 테스트 강화). 이 순서는 Uncle Bob의 Coder→Cleaner→Hardener 파이프라인과 같다.

## 1. 적용 조건 판정

제안 블록을 만들기 전에 순서대로 확인한다:

1. **Java 프로젝트인가** — 아니면 제안 생략(도구 3종 모두 Java 전용).
2. **Maven인가** — CRAP·mutation은 Maven 전용(pom.xml 필요)이다. 프로젝트 루트에 `pom.xml`이
   없으면(Gradle 등) 이 둘은 생략하고 한 줄만 남긴다:
   `CRAP·mutation 제안 생략 — Maven 전용 (이 프로젝트: Gradle). DRY 제안은 계속 진행`
   (dry4java는 Maven·Gradle 무관하게 임의 Java 소스에 동작하므로 생략하지 않는다)
3. **변경 파일이 있는가** — 시작 커밋부터 HEAD까지의 diff에 `src/main/java` 변경이
   없으면(테스트만 변경 등) 제안을 생략한다. 시작 커밋은 호출한 스킬의 기준을 따른다 —
   `tdd-feature`: Phase B 시작 커밋 해시, `tdd-rgb`: 진행 기록의 적대적 리뷰 diff
   기준점(없으면 이 작업 첫 커밋의 부모).

## 2. 제안 블록 형식

완료 보고 마지막에 아래 블록을 붙인다. `{changed-files}`는 위 §1-3 기준 diff의
`src/main/java/**/*.java` 목록으로 치환한다.

```markdown
### 하드닝 제안 (선택 — 실행하지 않았음)

순서대로 진행한다 — ②의 구조 변경이 ③의 뮤턴트 지점을 바꾸므로 ③은 마지막이다.

**① 정리할 곳 찾기** (변경 파일 한정, 수 초~수십 초)
- CRAP 점검: "crap4java-analyzer 에이전트로 {changed-files} CRAP 점검해줘"
- DRY 점검: "dry4java-analyzer 에이전트로 {changed-files} 중복 스캔해줘"

**② 구조 정리** (①의 결과가 대상 목록이 된다)
- "/system-wide-refactoring" — ①이 지목한 메서드·중복 쌍을 기법별 커밋으로 정리

**③ 테스트 강화** (②를 마친 뒤. 파일당 수 분 — 전체 스위트를 뮤턴트마다 재실행)
- mutation 하드닝: "mutate4java-runner 에이전트로 {가장 복잡했던 파일 1개} 뮤테이션 테스트 돌려줘"

②를 건너뛸 거면 ③을 지금 실행해도 된다.
```

- **순서는 비용순이 아니라 파이프라인순이다.** ②의 tidying은 동작을 보존하므로
  테스트는 그대로지만 **뮤테이션 지점은 바뀐다** — 메서드를 추출하면 새 뮤턴트 자리가
  생겨서, ② 이전에 얻은 "전부 죽였다"는 결론이 ② 이후에는 성립하지 않는다. 곧
  재구조화될 코드에 파일당 수 분을 쓰는 것도 그 비용이 버려지는 것이다.
  (근거: Uncle Bob의 실제 파이프라인 Coder→**Cleaner**(CRAP+정리)→**Hardener**(mutation)
  순서. `001-INBOX/LIVE Uncle Bob on Software Fundamentals in the Age of AI.md` [18:01-24:03])
- mutation 제안 대상은 **파일 1개**로 한정한다 — 완료 보고의 "표본 정독용 대표
  test"에 대응하는 프로덕션 파일(가장 복잡했거나 후퇴가 있었던 것)을 고른다.
  (Uncle Bob의 Hardener는 100% 커버리지·전 뮤턴트 소멸을 목표로 무자비하게 돌리지만,
  여기서는 사람이 결과를 읽고 판단하는 비용을 고려해 1개로 좁힌다.)
- 제안 문구는 사용자가 그대로 복사해 요청할 수 있는 자연어 명령이어야 한다.
- Gradle이면(§1-2) ①의 CRAP 줄과 ③ 전체를 빼고 DRY 점검 + ② 구조 정리만 남긴다.

## 3. 위임 대상 (전역 에이전트 — 플러그인 로컬 신설 금지)

| 에이전트 | 역할 | 비용 |
|---|---|---|
| `crap4java-analyzer` | 복잡도×커버리지 CRAP 점수, 임계 8.0 초과 메서드 랭킹 | 낮음 |
| `dry4java-analyzer` | 구조적 중복 쌍 탐지 + 제거 우선순위 | 낮음 |
| `mutate4java-runner` | 생존 뮤턴트 탐지 + 뮤턴트 죽이는 테스트 작성 | 높음 |

세 에이전트 모두 `~/.claude/agents/`의 전역 자산이다. 부재 환경(다른 사용자의
설치)에서는 제안 블록에 "전역 에이전트 미설치 시 이 제안은 무시" 한 줄을 덧붙인다.
