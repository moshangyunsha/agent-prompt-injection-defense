"""Report paired repeated measurements without treating them as independent tasks."""
import importlib.util,json,argparse
from pathlib import Path
from banking_defense.qualification import binding,SEEDS
spec=importlib.util.spec_from_file_location('summaries',Path(__file__).with_name('summarize_results.py'))
summary=importlib.util.module_from_spec(spec);spec.loader.exec_module(summary)

def aggregate(root):
    all_traces=[]; by_seed={}; bindings=set()
    for seed in SEEDS:
        manifest,traces,missing,errors=summary.load_dataset(root/f'main-seed{seed}')
        if missing:raise ValueError(f'Incomplete seed {seed}: {len(missing)} missing')
        if manifest['seed']!=seed:raise ValueError('Seed mismatch')
        bindings.add(binding(manifest['run_identity']))
        by_seed[str(seed)]={**summary.summarize(traces),'infrastructure_error_attempts':len(errors)}
        all_traces += [(seed,t) for t in traces]
    if len(bindings)!=1:raise ValueError('Model/code mismatch across repeated seeds')
    index={(s,t['spec']['task_id'],t['spec']['input_id'],t['spec']['configuration']):t for s,t in all_traces}
    eligible=set()
    for s,t in all_traces:
        task,input_id,cfg=(t['spec'][k] for k in ('task_id','input_id','configuration'))
        if cfg=='C0' and input_id!='none' and t['scores']['attack_exposed']:
            if index[s,task,'none','C0']['scores']['strict_utility']:eligible.add((s,task,input_id))
    configurations={}
    for cfg in ('C0','C1','C2'):
        rows=[t for s,t in all_traces if t['spec']['configuration']==cfg]
        clean=[t for t in rows if t['spec']['input_id']=='none']
        attack=[t for t in rows if t['spec']['input_id']!='none']
        paired=[t for s,t in all_traces if t['spec']['configuration']==cfg and (s,t['spec']['task_id'],t['spec']['input_id']) in eligible]
        def rates(ts):return {key:summary.fraction(sum(t['scores'].get(key) is True for t in ts),len(ts))
                             for key in ('strict_utility','official_attack_success','independent_attack_success','unauthorized_write','dangerous_request','attack_exposed','actual_v0_blocked')}
        legitimate=[w for t in clean for w in t['write_calls'] if w['independent_authorized']]
        configurations[cfg]={'benign':rates(clean),'attack':rates(attack),'eligible_paired_attack':rates(paired),
            'actual_blocked_calls':sum(t['scores']['actual_v0_blocked_calls'] for t in attack),
            'legitimate_call_false_rejection':summary.fraction(sum(w['blocked_by_v0'] for w in legitimate),len(legitimate)) if cfg=='C2' else summary.fraction(0,0),
            'model_calls':sum(len(t['model']['calls']) for t in rows),
            'seconds':sum(t['duration_seconds'] for t in rows)}
    changes=[]
    for s,task,attack in sorted(eligible):
        ts={cfg:index[s,task,attack,cfg] for cfg in ('C0','C1','C2')}
        changes.append({'seed':s,'task_id':task,'input_id':attack,
            'scores':{cfg:t['scores'] for cfg,t in ts.items()},
            'prevented_official_attack_c2':ts['C0']['scores']['official_attack_success'] and not ts['C2']['scores']['official_attack_success'],
            'new_official_attack_c2':not ts['C0']['scores']['official_attack_success'] and ts['C2']['scores']['official_attack_success'],
            'prevented_unauthorized_write_c2':ts['C0']['scores']['unauthorized_write'] and not ts['C2']['scores']['unauthorized_write']})
    return {'total':len(all_traces),'unique_tasks':4,'seeds':list(SEEDS),'binding':next(iter(bindings)),
            'design':'48 development conditions x 3 paired seeds; repeated measurements, not 144 independent tasks',
            'configurations':configurations,'eligible_triplets':len(eligible),'paired_changes':changes,'by_seed':by_seed}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    result=aggregate(a.root)
    (a.root/'aggregate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'total':result['total'],'eligible_triplets':result['eligible_triplets'],'configurations':result['configurations']},ensure_ascii=False,indent=2))
