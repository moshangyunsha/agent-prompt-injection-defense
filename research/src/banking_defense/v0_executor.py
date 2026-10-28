from __future__ import annotations

from ast import literal_eval
from collections.abc import Callable, Sequence
from typing import Any

from agentdojo.agent_pipeline.llms.google_llm import EMPTY_FUNCTION_NAME
from agentdojo.agent_pipeline.tool_execution import ToolsExecutor, is_string_list
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionReturnType, FunctionsRuntime
from agentdojo.functions_runtime import FunctionCall
from agentdojo.agent_pipeline.tool_execution import tool_result_to_str
from agentdojo.types import ChatMessage, ChatToolResultMessage, text_content_block_from_string

from .policies import WRITE_TOOLS, check_v0_call


def contains_nested_call(value: Any) -> bool:
    if isinstance(value, FunctionCall):
        return True
    if isinstance(value, dict):
        return any(contains_nested_call(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_nested_call(item) for item in value)
    return False


class V0GuardedToolsExecutor(ToolsExecutor):
    """Execute tool calls only after the task-level V0 policy allows them."""

    def __init__(
        self,
        task_id: str,
        tool_output_formatter: Callable[[FunctionReturnType], str] = tool_result_to_str,
    ) -> None:
        super().__init__(tool_output_formatter)
        self.task_id = task_id

    def query(
        self,
        query: str,
        runtime: FunctionsRuntime,
        env: Env = EmptyEnv(),
        messages: Sequence[ChatMessage] = (),
        extra_args: dict[str, Any] | None = None,
    ) -> tuple[str, FunctionsRuntime, Env, Sequence[ChatMessage], dict[str, Any]]:
        run_meta = dict(extra_args or {})
        if not messages or messages[-1]["role"] != "assistant" or not messages[-1]["tool_calls"]:
            return query, runtime, env, messages, run_meta

        counts = run_meta.setdefault("v0_completed_write_counts", {})
        audit_log = run_meta.setdefault("v0_audit_log", [])
        results = []

        for tool_call in messages[-1]["tool_calls"] or []:
            if tool_call.function == EMPTY_FUNCTION_NAME:
                results.append(self._error_result(tool_call, "Empty function name provided."))
                continue
            if tool_call.function not in (tool.name for tool in runtime.functions.values()):
                results.append(self._error_result(tool_call, f"Invalid tool {tool_call.function} provided."))
                continue

            for key, value in tool_call.args.items():
                if isinstance(value, str) and is_string_list(value):
                    tool_call.args[key] = literal_eval(value)

            decision = check_v0_call(self.task_id, tool_call.function, tool_call.args, counts)
            if contains_nested_call(tool_call.args):
                from .policies import Decision
                decision = Decision(False, "nested_call_not_authorized", "Nested function calls are not accepted by this banking interface.")
            audit_log.append(
                {
                    "call_id": tool_call.id,
                    "task_id": self.task_id,
                    "function": tool_call.function,
                    "args": dict(tool_call.args),
                    "allowed": decision.allowed,
                    "code": decision.code,
                    "reason": decision.reason,
                    "blocked": not decision.allowed,
                }
            )
            if not decision.allowed:
                results.append(self._error_result(tool_call, f"SecurityPolicyViolation: {decision.reason}"))
                continue

            tool_result, error = runtime.run_function(env, tool_call.function, tool_call.args)
            if error is None and tool_call.function in WRITE_TOOLS:
                counts[tool_call.function] = counts.get(tool_call.function, 0) + 1
            results.append(
                ChatToolResultMessage(
                    role="tool",
                    content=[text_content_block_from_string(self.output_formatter(tool_result))],
                    tool_call_id=tool_call.id,
                    tool_call=tool_call,
                    error=error,
                )
            )

        return query, runtime, env, [*messages, *results], run_meta

    @staticmethod
    def _error_result(tool_call: Any, message: str) -> ChatToolResultMessage:
        return ChatToolResultMessage(
            role="tool",
            content=[text_content_block_from_string("")],
            tool_call_id=tool_call.id,
            tool_call=tool_call,
            error=message,
        )

