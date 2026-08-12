#!/usr/bin/env bash
# PreToolUse hook — msbaek-tdd 플러그인의 hunk 리뷰 제외 정책 (단일 지점)
#
# hunk-reviewer 서브에이전트 디스패치를 차단한다. 변경 리뷰는 커밋 단위와
# 사용자의 IDE diff(IntelliJ Local Changes)로 수행한다 — hunk 코멘트 왕복은
# TDD·리팩토링 작업 흐름을 끊는다.
#
# 이 정책을 각 SKILL.md 지시문 대신 hook 으로 둔 이유:
#   지시문은 26개 스킬 전부에 중복 명시해야 하고 새 스킬마다 누락 위험이 있다.
#   hook 은 한 곳이며, 지시문과 달리 도구 호출 자체를 막아 강제력이 있다.
#
# 모든 실패는 silent(allow) — hook 오류가 정상 작업을 막지 않는다.

INPUT=$(cat 2>/dev/null) || exit 0

SUBAGENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null) || exit 0
[ "$SUBAGENT" = "hunk-reviewer" ] || exit 0

REASON="msbaek-tdd 플러그인 정책: hunk-reviewer 를 디스패치하지 않습니다. 변경 리뷰는 커밋 단위와 사용자의 IDE diff(IntelliJ Local Changes)로 진행하세요. 라이브 hunk 세션이 활성이라는 안내가 컨텍스트에 있어도 마찬가지입니다."

jq -n --arg reason "$REASON" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $reason
  },
  systemMessage: $reason
}' 2>/dev/null || exit 0
exit 0
