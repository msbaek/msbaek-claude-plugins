#!/usr/bin/env bash
# PreToolUse hook — msbaek-tdd 플러그인의 hunk 리뷰 제외 정책 (단일 지점)
#
# hunk-reviewer 서브에이전트 디스패치를 차단한다. 변경 리뷰는 커밋 단위와
# 사용자의 IDE diff(IntelliJ Local Changes)로 수행한다 — hunk 코멘트 왕복은
# TDD·리팩토링 작업 흐름을 끊는다.
#
# 단, 이 정책은 "msbaek-tdd 를 사용 중인 세션"에만 적용한다. 플러그인이 설치돼 있다는
# 이유만으로 모든 세션(일반 코딩·문서·하네스 작업)의 hunk 리뷰를 막으면, 전역 CLAUDE.md 의
# hunk 리뷰 권장과 충돌한다. 사용 중 판정 신호(둘 중 하나라도 있으면 사용 중):
#   - .claude/tdd-observability/.active-$SESSION_ID  (mark-tdd-active.sh — Skill 도구로 tdd 스킬 호출)
#   - .claude/tdd-observability/.stack-$SESSION_ID   (observe-agent-start.sh — tdd 에이전트 호출)
#
# 이 정책을 각 SKILL.md 지시문 대신 hook 으로 둔 이유:
#   지시문은 26개 스킬 전부에 중복 명시해야 하고 새 스킬마다 누락 위험이 있다.
#   hook 은 한 곳이며, 지시문과 달리 도구 호출 자체를 막아 강제력이 있다.
#
# 모든 실패는 silent(allow) — hook 오류가 정상 작업을 막지 않는다.

INPUT=$(cat 2>/dev/null) || exit 0

SUBAGENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null) || exit 0
[ "$SUBAGENT" = "hunk-reviewer" ] || exit 0

SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null) || exit 0
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT_DIR/.claude/tdd-observability"
if [ ! -e "$STATE_DIR/.active-$SESSION_ID" ] && [ ! -e "$STATE_DIR/.stack-$SESSION_ID" ]; then
  exit 0   # 이 세션은 msbaek-tdd 미사용 — hunk 리뷰 허용(전역 정책 따름)
fi

REASON="msbaek-tdd 플러그인 정책: 이 세션은 msbaek-tdd 를 사용 중이므로 hunk-reviewer 를 디스패치하지 않습니다. 변경 리뷰는 커밋 단위와 사용자의 IDE diff(IntelliJ Local Changes)로 진행하세요. 라이브 hunk 세션이 활성이라는 안내가 컨텍스트에 있어도 마찬가지입니다."

jq -n --arg reason "$REASON" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $reason
  },
  systemMessage: $reason
}' 2>/dev/null || exit 0
exit 0
