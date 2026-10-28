from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from banking_defense.reproducibility import reusable_trace


def fraction(n: int, d: int) -> dict:
    return {"numerator":n, "denominator":d, "rate":n/d if d else None}


def summarize(traces: list[dict[str, Any]]) -> dict:
    fingerprints = {t.get("run_fingerprint") for t in traces}
    if len(fingerprints) > 1:
        raise ValueError("Mixed experiment fingerprints cannot be aggregated.")
    ids = [t["trace_id"] for t in traces]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate trace IDs cannot be counted twice.")
    groups = defaultdict(list)
    for trace in traces:
        groups[trace["spec"]["configuration"]].append(trace)
    results = {}
    for configuration, items in sorted(groups.items()):
        clean = [t for t in items if t["spec"]["input_id"] == "none"]
        attacked = [t for t in items if t["spec"]["input_id"] != "none"]
        def rate(rows, key):
            return fraction(sum(t["scores"].get(key) is True for t in rows), len(rows))
        valid_legit = [w for t in clean for w in t.get("write_calls", [])
                       if w.get("independent_authorized") and configuration == "C2"]
        block_count = sum(bool(a.get("blocked")) for t in attacked for a in t.get("v0_audit_log", []))
        call_count = sum(len(t.get("model", {}).get("calls", [])) for t in items)
        usages = [c["usage"] for t in items for c in t.get("model", {}).get("calls", []) if isinstance(c.get("usage"),dict)]
        results[configuration] = {
            "total_runs":len(items),
            "benign":{"total":len(clean), "official_utility":rate(clean,"official_utility"),
                      "strict_utility":rate(clean,"strict_utility"),
                      "legitimate_call_false_rejection":fraction(sum(w.get("blocked_by_v0") is True for w in valid_legit),len(valid_legit))},
            "attack":{"total":len(attacked), "official_attack_success":rate(attacked,"official_attack_success"),
                      "independent_attack_success":rate(attacked,"independent_attack_success"),
                      "attack_exposed":rate(attacked,"attack_exposed"),
                      "dangerous_request":rate(attacked,"dangerous_request"),
                      "unauthorized_write":rate(attacked,"unauthorized_write"),
                      "utility_under_attack":rate(attacked,"strict_utility"),
                      "actual_blocked_runs":rate(attacked,"actual_v0_blocked"),
                      "actual_blocked_calls":block_count,
                      "counterfactual_v0_rule_violation":rate(attacked,"v0_policy_violation")},
            "performance":{"model_calls":call_count, "calls_with_usage":len(usages),
                           "prompt_tokens":sum(u.get("prompt_tokens",0) for u in usages),
                           "completion_tokens":sum(u.get("completion_tokens",0) for u in usages),
                           "total_tokens":sum(u.get("total_tokens",0) for u in usages),
                           "duration_seconds":sum(t.get("duration_seconds",0) for t in items)},
        }
    return {"total_traces_found":len(traces), "run_fingerprint":next(iter(fingerprints),None), "configurations":results}


def load_dataset(directory: Path):
    manifest = json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("planned"):
        raise ValueError("The manifest is only a dry-run plan.")
    fingerprint = manifest["run_fingerprint"]
    expected = {row["trace_id"]:row for row in manifest["runs"]}
    traces = []
    for path in sorted((directory/"traces").glob("*.json")):
        trace = json.loads(path.read_text(encoding="utf-8"))
        if path.stem not in expected or not reusable_trace(trace,fingerprint,path.stem):
            raise ValueError(f"Unexpected, incomplete or mismatching trace: {path.name}")
        if trace["spec"] != {k:v for k,v in expected[path.stem].items() if k != "trace_id"}:
            raise ValueError("Trace specification differs from frozen manifest.")
        traces.append(trace)
    found = {t["trace_id"] for t in traces}
    missing = sorted(set(expected)-found)
    errors = [json.loads(p.read_text(encoding="utf-8")) for p in (directory/"infrastructure-errors").glob("*.json")]
    return manifest, traces, missing, errors


def format_fraction(value: dict) -> str:
    rate = value["rate"]
    return f'{value["numerator"]}/{value["denominator"]} (' + ("N/A" if rate is None else f"{rate:.1%}") + ")"


def print_table(result):
    print("| Configuration | Clean completion | Attack completion | Official attack success | Unauthorized writes | Actual blocked calls |")
    print("|---|---|---|---|---|---|")
    for configuration, row in result["configurations"].items():
        print("| "+configuration+" | "+format_fraction(row["benign"]["strict_utility"])+" | "
              +format_fraction(row["attack"]["utility_under_attack"])+" | "
              +format_fraction(row["attack"]["official_attack_success"])+" | "
              +format_fraction(row["attack"]["unauthorized_write"])+" | "
              +str(row["attack"]["actual_blocked_calls"])+" |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=Path("research/runs/rebuild-20261027/main"))
    args = parser.parse_args()
    manifest, traces, missing, errors = load_dataset(args.run_dir)
    result = summarize(traces)
    result.update({"planned_runs":len(manifest["runs"]), "missing":missing, "infrastructure_error_attempts":len(errors),
                   "by_task":{task:summarize([t for t in traces if t["spec"]["task_id"]==task])
                              for task in sorted({t["spec"]["task_id"] for t in traces})},
                   "by_attack":{attack:summarize([t for t in traces if t["spec"]["input_id"]==attack])
                                for attack in sorted({t["spec"]["input_id"] for t in traces})}})
    (args.run_dir/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    with (args.run_dir/"results.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        names=["trace_id","task_id","input_id","configuration","termination_reason","official_utility","strict_utility",
               "official_attack_success","dangerous_request","unauthorized_write","actual_v0_blocked_calls","duration_seconds"]
        writer=csv.DictWriter(stream,fieldnames=names); writer.writeheader()
        for t in traces:
            writer.writerow({k:({**t,**t["spec"],**t["scores"]}).get(k) for k in names})
    print_table(result)
    print(json.dumps({"valid":len(traces),"planned":len(manifest["runs"]),"missing":missing,"infrastructure_error_attempts":len(errors)}))
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
