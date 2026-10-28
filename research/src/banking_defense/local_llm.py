from __future__ import annotations
import ipaddress
import json
import time
import urllib.request
from collections.abc import Sequence
from typing import Any
from urllib.parse import urlsplit
import httpx
import openai
from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM, _function_to_openai, _message_to_openai, _openai_to_assistant_message
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionsRuntime
from agentdojo.types import ChatMessage

DEFAULT_LOCAL_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_LOCAL_MODEL = "banking-qwen35-9b:latest"


def validate_local_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.hostname or ""
    try:
        local = host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        local = False
    if not local or parts.scheme != "http" or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Only an HTTP loopback inference endpoint is allowed for this free local experiment.")
    if parts.path.rstrip("/") != "/v1":
        raise ValueError("Expected the local Ollama /v1 endpoint.")
    return url.rstrip("/")


class LocalOpenAILLM(OpenAILLM):
    def __init__(self, model: str = DEFAULT_LOCAL_MODEL, base_url: str = DEFAULT_LOCAL_BASE_URL,
                 temperature: float = 0.7, max_tokens: int = 1024, seed: int = 42,
                 top_p: float = 0.8, reasoning_effort: str | None = "none", presence_penalty: float = 0.0):
        base_url = validate_local_url(base_url)
        if "cloud" in model.casefold():
            raise ValueError("Cloud model tags are disallowed.")
        transport = httpx.Client(trust_env=False, follow_redirects=False, timeout=httpx.Timeout(300, connect=5))
        super().__init__(client=openai.OpenAI(api_key="ollama-local-placeholder", base_url=base_url,
                                             max_retries=0, http_client=transport), model=model, temperature=temperature)
        self.base_url, self.max_tokens, self.seed = base_url, max_tokens, seed
        self.top_p, self.reasoning_effort = top_p, reasoning_effort
        self.presence_penalty=presence_penalty
        self.call_log: list[dict] = []
        self.agent_messages: list = []
        self.identity: dict = {}

    def native(self, path: str, payload: dict | None = None) -> dict:
        origin = self.base_url.removesuffix("/v1")
        request = urllib.request.Request(origin + path, data=None if payload is None else json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=15) as response:
            return json.load(response)

    def inspect_model(self) -> dict:
        tags = self.native("/api/tags")["models"]
        matches = [m for m in tags if m["name"] == self.model or m.get("model") == self.model]
        if len(matches) != 1:
            raise RuntimeError(f"Local model {self.model} is not installed; no inference started.")
        model = matches[0]
        details = self.native("/api/show", {"model": self.model})
        if model.get("remote_host") or model.get("remote_model") or details.get("remote_model"):
            raise RuntimeError("Remote-backed models are not allowed.")
        if "tools" not in details.get("capabilities", []):
            raise RuntimeError("This installed local model does not advertise tool support.")
        self.identity = {"backend": "ollama_local", "model": self.model, "digest": model["digest"],
                         "details": model.get("details"), "parameters": details.get("parameters"),
                         "modelfile": details.get("modelfile"), "server_version": self.native("/api/version"),
                         "base_url": self.base_url, "temperature": self.temperature, "seed": self.seed,
                         "max_tokens": self.max_tokens, "http_retries": 0, "timeout_seconds": 300,
                         "top_p": self.top_p, "reasoning_effort": self.reasoning_effort,
                         "preserve_reasoning_between_tool_turns": True,
                         "presence_penalty":self.presence_penalty,
                         "context_length": 8192, "paid_api_calls": 0}
        return self.identity

    def reset_run(self):
        self.call_log = []
        self.agent_messages = []
        self.latest_meta = {}

    def query(self, query: str, runtime: FunctionsRuntime, env: Env = EmptyEnv(),
              messages: Sequence[ChatMessage] = (), extra_args: dict[str, Any] | None = None):
        metadata = dict(extra_args or {})
        self.latest_meta = metadata
        self.agent_messages = list(messages)
        api_messages = [_message_to_openai(message, self.model) for message in messages]
        for source, message in zip(messages,api_messages):
            if message.get("role") == "developer":
                message["role"] = "system"
            # Ollama's OpenAI compatibility API calls this field `reasoning`.
            # Preserve the model-produced value in assistant history, without
            # reclassifying it as user input or adding evaluator information.
            if source.get('role')=='assistant' and source.get('ollama_reasoning'):
                message['reasoning']=source['ollama_reasoning']
        schemas = [_function_to_openai(tool) for tool in runtime.functions.values()]
        record = {"requested_model": self.model, "base_url": self.base_url,
                  "request": {"messages": api_messages, "tools": schemas, "temperature": self.temperature,
                              "seed": self.seed, "max_tokens": self.max_tokens, "top_p": self.top_p,
                              "presence_penalty":self.presence_penalty,
                              **({"reasoning_effort": self.reasoning_effort} if self.reasoning_effort else {})}}
        started = time.perf_counter()
        self.call_log.append(record)
        try:
            completion = self.client.chat.completions.create(model=self.model, messages=api_messages,
                        tools=schemas, tool_choice="auto", temperature=self.temperature, seed=self.seed,
                        max_tokens=self.max_tokens, top_p=self.top_p,
                        presence_penalty=self.presence_penalty,
                        **({"reasoning_effort": self.reasoning_effort} if self.reasoning_effort else {}))
            record.update({"returned_model": completion.model, "usage": completion.usage.model_dump() if completion.usage else None,
                           "finish_reason": completion.choices[0].finish_reason,
                           "response": completion.choices[0].message.model_dump(), "response_id": completion.id})
            output = _openai_to_assistant_message(completion.choices[0].message)
            reasoning=record['response'].get('reasoning')
            if reasoning:output['ollama_reasoning']=reasoning
            self.agent_messages = [*messages, output]
        except Exception as error:
            record["error"] = {"type": type(error).__name__, "message": str(error)}
            raise
        finally:
            record["duration_seconds"] = time.perf_counter() - started
        metadata["model_calls"] = list(self.call_log)
        return query, runtime, env, self.agent_messages, metadata
