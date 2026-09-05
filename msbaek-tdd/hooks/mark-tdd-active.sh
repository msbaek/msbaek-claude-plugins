#!/usr/bin/env bash
# PreToolUse hook (matcher: Skill) — 이 세션이 msbaek-tdd 를 "사용 중"임을 표시한다.
#
# block-hunk-reviewer.sh 의 게이트 신호. hunk-reviewer 차단은 TDD·리팩토링 흐름을 끊지 않기
# 위한 정책이므로, msbaek-tdd 스킬을 한 번도 쓰지 않은 세션(일반 코딩·문서·하네스 작업)에는
# 적용되면 안 된다 — 그런 세션에서는 hunk 리뷰가 오히려 권장된다.
#
# 마커: $PROJECT_DIR/.claude/tdd-observability/.active-$SESSION_ID (내용 = 첫 사용 스킬명)
# 에이전트 경로(tdd-red/green/blue 등)는 observe-agent-start.sh 가 남기는 .stack-$SESSION_ID 가
# 같은 역할을 하므로 여기서는 Skill 도구만 본다.
#
# 모든 실패는 silent(allow) — hook 오류가 정상 작업을 막지 않는다.

INPUT=$(cat 2>/dev/null) || exit 0

SKILL=$(printf '%s' "$INPUT" | jq -r '.tool_input.skill // empty' 2>/dev/null) || exit 0
case "$SKILL" in
  msbaek-tdd:*|tdd|tdd-*|cucumber-acceptance) ;;
  *) exit 0 ;;
esac

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null) || exit 0
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/tdd-observability"
mkdir -p "$STATE_DIR" 2>/dev/null || exit 0

MARKER="$STATE_DIR/.active-$SESSION_ID"
[ -e "$MARKER" ] || printf '%s\n' "$SKILL" > "$MARKER" 2>/dev/null

exit 0
