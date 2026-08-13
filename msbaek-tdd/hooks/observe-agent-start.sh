#!/usr/bin/env bash
# PreToolUse hook — msbaek-tdd 에이전트 호출의 시작 시각을 기록한다 (관측 계층, 1/2)
#
# 하네스 엔지니어링(delta B-4)의 "반복 레코드" 원칙: 에이전트 컨텍스트를 전혀 쓰지 않고
# append-only 로그를 남긴다. 토큰 비용은 0이다.
#
# 이 hook 은 시작 시각만 stack 파일에 적재한다(순수 side-effect, allow/deny 판단 없음).
# 실제 로그 기록은 observe-agent-end.sh(PostToolUse)가 종료 시 duration 을 계산해 수행한다.
#
# 정확도 한계: 같은 세션에서 Agent 호출이 완전히 병렬로 실행되면(현재 관측된 실사용 패턴은
# 순차) stack 순서가 어긋날 수 있다 — 토큰 0 비용의 경량 신호이므로 이 정도 근사는 허용한다.
#
# 모든 실패는 silent(allow) — hook 오류가 정상 작업을 막지 않는다.

INPUT=$(cat 2>/dev/null) || exit 0

SUBAGENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null) || exit 0
case "$SUBAGENT" in
  msbaek-tdd:tdd-*|tdd-red|tdd-green|tdd-blue) ;;
  *) exit 0 ;;
esac

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null) || exit 0
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/tdd-observability"
mkdir -p "$STATE_DIR" 2>/dev/null || exit 0

START_S=$(date +%s 2>/dev/null) || exit 0
printf '%s\n' "$START_S" >> "$STATE_DIR/.stack-$SESSION_ID" 2>/dev/null

exit 0
