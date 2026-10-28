from __future__ import annotations
import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from banking_defense.local_llm import DEFAULT_LOCAL_BASE_URL, DEFAULT_LOCAL_MODEL, LocalOpenAILLM
from banking_defense.runner import build_matrix, build_smoke_matrix, run_one, save_json, validate_suite
from banking_defense.pipelines import PIPELINE_SETTINGS
from banking_defense.reproducibility import make_identity, reusable_trace
from banking_defense.qualification import binding, assess


def parse_args():
    parser = argparse.ArgumentParser(description="Frozen, local-only AgentDojo banking experiments.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true", help="Archive and repeat matching existing results.")
    parser.add_argument("--model", default=DEFAULT_LOCAL_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_LOCAL_BASE_URL)
    parser.add_argument("--seed",type=int,default=42)
    parser.add_argument("--reasoning-effort",default="none")
    parser.add_argument("--qualification",type=Path,help="Required passed benign-only qualification.json")
    parser.add_argument('--temperature',type=float,default=0.7)
    parser.add_argument('--top-p',type=float,default=0.8)
    parser.add_argument('--max-tokens',type=int,default=1024)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive.")
    suite_info = validate_suite()
    matrix = build_smoke_matrix() if args.smoke_test else build_matrix()
    if not args.smoke_test:
        random.Random(args.seed).shuffle(matrix)
    selected = matrix if args.limit is None else matrix[:args.limit]
    output = args.output or Path("research/runs/qualified-20261027") / ("smoke" if args.smoke_test else f"main-seed{args.seed}")
    llm = LocalOpenAILLM(model=args.model, base_url=args.base_url,seed=args.seed,reasoning_effort=args.reasoning_effort,
                        temperature=args.temperature,top_p=args.top_p,max_tokens=args.max_tokens)
    model_info = ({"backend":"ollama_local", "model":args.model, "base_url":args.base_url, "verified":False}
                  if args.dry_run else llm.inspect_model())
    identity = make_identity(model_info, PIPELINE_SETTINGS)
    if not args.dry_run:
        if not args.qualification:
            raise RuntimeError("Formal inference requires a passed benign-only qualification.json; no inference started.")
        qualification=json.loads(args.qualification.read_text(encoding="utf-8"))
        checks=[json.loads(Path(p).read_text(encoding="utf-8")) for p in qualification["trace_files"]]
        if not assess(checks)["passed"] or qualification.get("binding") != binding(identity):
            raise RuntimeError("Model/code does not match a passed complete qualification. No formal inference started.")
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        has_traces = any((output / "traces").glob("*.json"))
        if has_traces and previous.get("run_fingerprint") != identity["fingerprint"]:
            raise RuntimeError("Model/config/code fingerprint mismatch. Use a new output directory; existing data is preserved.")
    manifest = {**suite_info, "schema_version":2, "kind":"real_model", "run_mode":"smoke" if args.smoke_test else "main",
                "run_identity":identity, "run_fingerprint":identity["fingerprint"], "planned":args.dry_run,
                "model_backend":"local_open_source", "model_requested":args.model, "base_url":args.base_url,
                "seed":args.seed,"qualification":str(args.qualification) if args.qualification else None,
                "selected_runs":len(selected), "matrix_size":len(matrix),
                "runs":[spec.__dict__ | {"trace_id":spec.trace_id} for spec in matrix]}
    save_json(manifest_path, manifest)
    if args.dry_run:
        print(json.dumps({"status":"planned", "matrix":len(matrix), "selected":len(selected), "model_verified":False}))
        return 0
    completed = skipped = failed = 0
    for index, spec in enumerate(selected, 1):
        path = output / "traces" / (spec.trace_id + ".json")
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not reusable_trace(existing, identity["fingerprint"], spec.trace_id):
                raise RuntimeError(f"Invalid or mismatching existing trace: {spec.trace_id}; no overwrite performed.")
            if not args.force:
                skipped += 1
                continue
        # Detect a changed local model or edited research code before each new experiment.
        current = make_identity(llm.inspect_model(), PIPELINE_SETTINGS)
        if current["fingerprint"] != identity["fingerprint"]:
            raise RuntimeError("Frozen code/model changed during the batch. Stopping before further inference.")
        attempt = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        trace = run_one(spec, llm, identity)
        save_json(output / "attempts" / spec.trace_id / (attempt + ".json"), trace)
        if trace["status"] == "completed":
            save_json(path, trace)
            completed += 1
        else:
            failed += 1
            save_json(output / "infrastructure-errors" / (spec.trace_id + "__" + attempt + ".json"), trace)
        print(json.dumps({"index":index, "total":len(selected), "trace_id":spec.trace_id,
                          "status":trace["status"], "termination":trace["termination_reason"],
                          "utility":trace["scores"]["strict_utility"],
                          "attack_success":trace["scores"]["official_attack_success"],
                          "blocked_calls":trace["scores"]["actual_v0_blocked_calls"],
                          "seconds":round(trace["duration_seconds"],2)}), flush=True)
    save_json(output / "batch-status.json", {"completed_this_invocation":completed, "skipped":skipped, "failed":failed,
                                           "run_fingerprint":identity["fingerprint"], "planned_matrix":len(matrix)})
    print(json.dumps({"completed":completed, "skipped":skipped, "failed":failed}), flush=True)
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
