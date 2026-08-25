#!/usr/bin/env bash
# PostToolUse hook — msbaek-tdd 에이전트 호출 1건을 반복 레코드로 기록한다 (관측 계층, 2/2)
#
# observe-agent-start.sh 가 적재한 시작 시각을 pop 해 소요 시간을 계산하고,
# ${CLAUDE_PROJECT_DIR}/.claude/tdd-observability/agent-log.jsonl 에 append-only 로 남긴다.
# 에이전트 컨텍스트를 전혀 쓰지 않으므로 토큰 비용은 0이다 (harness-delta.md B-4).
#
# 담는 필드 — 신뢰성 있게 얻을 수 있는 것만: agent(subagent_type) · description ·
# duration_s(초 단위, PreToolUse 대응 hook 과의 wall-clock 차) · success(best-effort).
# 토큰(input/output/cache)은 여기서 담지 않는다 — PostToolUse hook 입력에 없다.
# 토큰·단계별 분해는 사후 분석 스크립트 bin/tdd-profile.py 가 세션 transcript 와
# <session>/subagents/agent-*.jsonl(+ .meta.json)을 읽어 계산한다.
#
# 이 로그로 답할 수 있는 질문: 어떤 에이전트가 자주 호출되는가 · 어떤 에이전트가
# 오래 걸리는가(추세) · 실패가 어디서 반복되는가. 답할 수 없는 질문(토큰 비용 등)은
# 없는 데이터를 지어내지 않고 비워 둔다.
#
# 모든 실패는 silent(계속 진행) — hook 오류가 정상 작업을 막지 않는다.

INPUT=$(cat 2>/dev/null) || exit 0

SUBAGENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null) || exit 0
case "$SUBAGENT" in
  msbaek-tdd:tdd-*|tdd-red|tdd-green|tdd-blue) ;;
  *) exit 0 ;;
esac

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null) || exit 0
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/tdd-observability"
STACK_FILE="$STATE_DIR/.stack-$SESSION_ID"

END_S=$(date +%s 2>/dev/null) || exit 0

DURATION_S=""
if [ -s "$STACK_FILE" ]; then
  START_S=$(tail -n1 "$STACK_FILE" 2>/dev/null)
  # pop: 마지막 줄 제거
  sed -i '' -e '$d' "$STACK_FILE" 2>/dev/null || true
  if [ -n "$START_S" ] && [ "$START_S" -eq "$START_S" ] 2>/dev/null; then
    DURATION_S=$((END_S - START_S))
  fi
fi

DESCRIPTION=$(printf '%s' "$INPUT" | jq -r '.tool_input.description // empty' 2>/dev/null)
# tool_response(또는 tool_result) 에 명시적 오류 신호가 있으면 실패로, 없으면 성공으로 간주
# (PostToolUse 는 대부분 성공 완료 시 발화하므로 이 기본값이 합리적 근사).
IS_ERROR=$(printf '%s' "$INPUT" | jq -r '(.tool_response.is_error // .tool_result.is_error // false)' 2>/dev/null)
SUCCESS="true"
[ "$IS_ERROR" = "true" ] && SUCCESS="false"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)

mkdir -p "$STATE_DIR" 2>/dev/null || exit 0
jq -nc \
  --arg ts "$TS" \
  --arg session_id "$SESSION_ID" \
  --arg agent "$SUBAGENT" \
  --arg description "$DESCRIPTION" \
  --argjson duration_s "${DURATION_S:-null}" \
  --argjson success "$SUCCESS" \
  '{ts:$ts, session_id:$session_id, agent:$agent, description:$description, duration_s:$duration_s, success:$success}' \
  >> "$STATE_DIR/agent-log.jsonl" 2>/dev/null

exit 0
