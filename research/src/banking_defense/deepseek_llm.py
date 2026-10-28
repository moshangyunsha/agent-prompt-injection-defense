from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

import openai
from openai._types import NOT_GIVEN

from agentdojo.agent_pipeline.llms.openai_llm import (
    OpenAILLM,
    _function_to_openai,
    _message_to_openai,
    _openai_to_assistant_message,
)
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionsRuntime
from agentdojo.types import ChatMessage


class DeepSeekFlashLLM(OpenAILLM):
    """AgentDojo pipeline element for DeepSeek's current OpenAI-compatible API."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("DEEPSEEK_API_KEY is required")
        super().__init__(
            client=openai.OpenAI(api_key=key, base_url="https://api.deepseek.com"),
            model="deepseek-flash",
            temperature=0.0,
        )

    def query(
        self,
        query: str,
        runtime: FunctionsRuntime,
        env: Env = EmptyEnv(),
        messages: Sequence[ChatMessage] = (),
        extra_args: dict[str, Any] | None = None,
    ) -> tuple[str, FunctionsRuntime, Env, Sequence[ChatMessage], dict[str, Any]]:
        run_meta = dict(extra_args or {})
        api_messages = [_message_to_openai(message, self.model) for message in messages]
        for message in api_messages:
            if message.get("role") == "developer":
                message["role"] = "system"  # DeepSeek Chat Completions uses the system role.
        tools = [_function_to_openai(tool) for tool in runtime.functions.values()]
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            tools=tools or NOT_GIVEN,
            tool_choice="auto" if tools else NOT_GIVEN,
            temperature=self.temperature,
            extra_body={"thinking": {"type": "disabled"}},
        )
        usage = completion.usage
        run_meta.setdefault("model_calls", []).append(
            {
                "requested_model": self.model,
                "returned_model": completion.model,
                "usage": None if usage is None else usage.model_dump(),
            }
        )
        output = _openai_to_assistant_message(completion.choices[0].message)
        return query, runtime, env, [*messages, output], run_meta

