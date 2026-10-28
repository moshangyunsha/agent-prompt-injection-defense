from __future__ import annotations
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_COMMIT = "089ed468cf3ed0322acc66b0211f26d9d90dbf60"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def code_identity() -> dict:
    import agentdojo
    source = Path(agentdojo.__file__).resolve().parent
    files = list((PROJECT_ROOT / "research/src/banking_defense").glob("*.py"))
    files += list((PROJECT_ROOT / "research/scripts").glob("*.py"))
    files += [PROJECT_ROOT / "research/pyproject.toml"]
    files += [PROJECT_ROOT / "research/requirements-lock.txt"]
    files += list((PROJECT_ROOT / "research/config").glob("*"))
    hashes = {p.relative_to(PROJECT_ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    upstream = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(source.rglob("*")) if p.is_file() and p.suffix in {".py", ".yaml", ".yml"}}
    return {"project_files": hashes, "agentdojo_tree_sha256": canonical_hash(upstream),
            "benchmark_commit": BENCHMARK_COMMIT, "python": platform.python_version(),
            "dependencies": {name: importlib.metadata.version(name) for name in ("agentdojo", "openai", "pydantic")}}


def make_identity(model: dict, pipeline: dict) -> dict:
    content = {"schema_version": 2, "model": model, "pipeline": pipeline, "code": code_identity()}
    return {**content, "fingerprint": canonical_hash(content)}


def reusable_trace(trace: dict, fingerprint: str, trace_id: str) -> bool:
    return (trace.get("trace_id") == trace_id and trace.get("run_fingerprint") == fingerprint
            and trace.get("status") == "completed" and trace.get("kind") == "real_model"
            and isinstance(trace.get("scores"), dict) and isinstance(trace.get("messages"), list)
            and trace.get("termination_reason") in {"final_answer", "step_limit", "model_protocol_error", "output_limit"})
