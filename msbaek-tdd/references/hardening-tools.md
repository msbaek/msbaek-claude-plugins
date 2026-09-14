# 하드닝 도구 (crap4java · dry4java · mutate4java)

> `tdd-rgb/references/hardening-gate.md`가 제안 블록에서 참조하는 도구 3종의 설치·실행 정본.
> 세 도구 모두 **선택 사항**이다. 미설치 환경에서는 제안 블록에서 해당 줄을 생략한다.

## 1. 도구와 출처

| 도구 | 역할 | 저장소 | 빌드 요구 |
|---|---|---|---|
| crap4java | CRAP(Change Risk Anti-Patterns) 점수 — 순환 복잡도 × JaCoCo 커버리지, 임계 8.0 초과 메서드 랭킹 | https://github.com/msbaek/crap4java | Maven 프로젝트 전용(JaCoCo 파이프라인) |
| dry4java | 구조적 중복(structural duplicate) 선언 쌍 탐지 | https://github.com/msbaek/dry4java | 빌드 도구 무관(Java 소스만) |
| mutate4java | 뮤테이션 테스트(mutation testing) — 생존 뮤턴트 탐지 | https://github.com/msbaek/mutate4java | Maven 프로젝트 전용 |

## 2. 설치

```bash
mkdir -p ~/git/uncle-bob && cd ~/git/uncle-bob
for r in crap4java dry4java mutate4java; do
  git clone https://github.com/msbaek/$r.git
  (cd $r && mvn -q -DskipTests package)
done
```

산출물: `~/git/uncle-bob/<tool>/target/<tool>-0.1.0-SNAPSHOT.jar`

## 3. 존재 판정

제안 블록을 만들기 전에 도구별로 확인한다. 둘 중 하나라도 있으면 "설치됨"으로 본다.

1. 전용 에이전트가 있는가 — `~/.claude/agents/{crap4java-analyzer,dry4java-analyzer,mutate4java-runner}.md`
2. jar가 있는가 — `~/git/uncle-bob/<tool>/target/<tool>-*.jar`

없으면 그 도구의 제안 줄을 생략하고, 블록 끝에 한 줄을 남긴다:
`미설치 도구: <목록> — 설치는 ${CLAUDE_PLUGIN_ROOT}/references/hardening-tools.md §2`

## 4. 제안 문구 — 에이전트 유무에 따른 두 형식

| 도구 | 에이전트 있음 | jar만 있음 (직접 실행 명령) |
|---|---|---|
| crap4java | "crap4java-analyzer 에이전트로 {files} CRAP 점검해줘" | `java -jar ~/git/uncle-bob/crap4java/target/crap4java-0.1.0-SNAPSHOT.jar {files}` |
| dry4java | "dry4java-analyzer 에이전트로 {files} 중복 스캔해줘" | `java -jar ~/git/uncle-bob/dry4java/target/dry4java-0.1.0-SNAPSHOT.jar {files}` |
| mutate4java | "mutate4java-runner 에이전트로 {file} 뮤테이션 테스트 돌려줘" | `java -jar ~/git/uncle-bob/mutate4java/target/mutate4java-0.1.0-SNAPSHOT.jar {file}` |

- crap4java는 `--changed`(git 변경 파일만) 옵션을 지원한다.
- dry4java는 `--threshold N`(기본 0.82)로 민감도를 조정한다.
- mutate4java는 파일 1개 단위로 실행한다. `--since-last-run`으로 재실행 비용을 줄인다.

## 5. 제약

- 세 도구는 이 플러그인에 동봉하지 않는다 — 각 저장소가 정본이다.
- 에이전트 정의(`*-analyzer`, `*-runner`)는 작성자 개인 자산이다. 외부 사용자는 jar 직접 실행 형식을 사용한다.
