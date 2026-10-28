from __future__ import annotations
import argparse,json
from pathlib import Path
from banking_defense.local_llm import LocalOpenAILLM, DEFAULT_LOCAL_MODEL
from banking_defense.runner import ExperimentSpec, run_one, save_json
from banking_defense.pipelines import PIPELINE_SETTINGS
from banking_defense.reproducibility import make_identity,reusable_trace
from banking_defense.qualification import SEEDS,TASKS,assess,binding

def main():
    p=argparse.ArgumentParser(description='Benign-only admission before defense experiments')
    p.add_argument('--model',default=DEFAULT_LOCAL_MODEL)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reasoning-effort',default='none')
    p.add_argument('--temperature',type=float,default=0.7)
    p.add_argument('--top-p',type=float,default=0.8)
    p.add_argument('--max-tokens',type=int,default=1024)
    a=p.parse_args()
    traces=[]; identity=None
    for seed in (42,17,73):
        llm=LocalOpenAILLM(model=a.model,seed=seed,reasoning_effort=a.reasoning_effort,
                         temperature=a.temperature,top_p=a.top_p,max_tokens=a.max_tokens)
        current=make_identity(llm.inspect_model(),PIPELINE_SETTINGS)
        if identity is None:
            identity=current
            save_json(a.output/'identity.json',identity)
        elif binding(current)!=binding(identity):raise RuntimeError('Qualification identity changed')
        for task in TASKS:
            spec=ExperimentSpec(task,'none','C0')
            path=a.output/'traces'/f'{task}__seed{seed}.json'
            if path.exists():
                trace=json.loads(path.read_text(encoding='utf-8'))
                if not reusable_trace(trace,current['fingerprint'],spec.trace_id):raise RuntimeError('Changed qualification trace')
            else:
                trace=run_one(spec,llm,current)
                save_json(path,trace)
            traces.append(trace)
            print(json.dumps({'task':task,'seed':seed,'success':trace['scores']['strict_utility'],
                              'status':trace['status'],'calls':len(trace['model']['calls']),
                              'seconds':round(trace['duration_seconds'],1)}),flush=True)
    result={**assess(traces),'binding':binding(identity),'identity':identity,
            'trace_files':[str(p) for p in sorted((a.output/'traces').glob('*.json'))]}
    save_json(a.output/'qualification.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in {'identity','trace_files'}}),flush=True)
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
