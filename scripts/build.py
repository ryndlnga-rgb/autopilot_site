#!/usr/bin/env python3
"""Build the public, self-contained CONTINUE? research arcade from read-only exports."""
from __future__ import annotations
import argparse
import base64
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import re
from statistics import fmean
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'sites'
SOURCES = {}

def source(path):
    path = Path(path)
    raw = path.read_bytes()
    SOURCES[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return raw

def rows(path):
    return list(csv.DictReader(source(path).decode().splitlines()))

def number(value):
    if value in ('', None): return None
    value = float(value)
    if not math.isfinite(value): return None
    return value

def js(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')

def sequence(value):
    return [x.strip() for x in (value or '').split(' -> ') if x.strip()]

def svg_asset(path):
    raw = source(path)
    root = ET.fromstring(raw)
    for el in root.iter():
        if el.tag.rsplit('}', 1)[-1] == 'script': raise ValueError(f'Executable SVG: {path}')
        for key, value in el.attrib.items():
            if key.rsplit('}', 1)[-1] in {'href', 'src'} and not value.startswith(('#', 'data:')):
                raise ValueError(f'External SVG dependency: {path}')
    text = raw.decode()
    if '@import' in text: raise ValueError(f'External SVG CSS: {path}')
    for target in re.findall(r'url\([\s\"\']*([^\)\"\'\s]+)', text):
        if not target.startswith(('#', 'data:')): raise ValueError(f'External SVG CSS: {path}')
    return base64.b64encode(raw).decode()

def load_data():
    graphs = {}; lookup = {}; routes = {'e1': [], 'e2': [], 'e3': []}
    for path in sorted((ROOT/'data_analysis/20260923_expr/all_models').glob('*/*/graph_data.json')):
        g = json.loads(source(path)); key = g['key']
        kind = {'strata': 'Foundational task', 'composed_task_chains': 'Linked tasks', 'composed_task_medium_strata': 'Linked choices'}[g['category']]
        graph = dict(id=key, api=g['api'], identifier=g['identifier'], category=kind,
                     name=f"{g['api']} · {kind.lower()} · {g['identifier'].replace('id_', '')[-4:]}",
                     rpcs=g['rpc_count'], nodes=g['node_count'], svg=svg_asset(path.parent/g['original_svg']))
        graphs[key] = graph
        lookup[(g['api'],g['identifier'].removeprefix('id_'))] = key
        for model, ts in g['traces'].items():
            outcomes = [dict(sequence=t['path'], n=t['count'], goal=t['goal'], correct=t['stats']['clean_goal_runs']) for t in ts]
            routes['e1'].append(dict(graph=key,model=model,variant='agent',prefix=[],resources=['Empty'],n=sum(t['n'] for t in outcomes),outcomes=outcomes))
    e1 = []
    for r in rows(ROOT/'experiment01/output/20260923_expr/analysis/e1_model_graph_metrics.csv'):
        e1.append(dict(graph=r['path_universe_key'],model=r['model'],variant='agent',n=int(r['number_of_runs']),
                       correct=int(r['N_corr_mg']),goal=int(r['number_of_sequences_reached_goal']),
                       entropy=number(r['rpc_sequence_normalized_entropy']),coverage=number(r['C_path_mg']),
                       distance=number(r['D_seq_mg']),latency=number(r['average_latency_seconds']),
                       cost=number(r['average_dollar_cost']),observed=int(r['O_mg_size']),universe=int(r['U_g_size'])))
    for cell in e1:
        trace=next(t for t in routes['e1'] if t['graph']==cell['graph'] and t['model']==cell['model'])
        assert trace['n']==cell['n'] and sum(p['correct'] for p in trace['outcomes'])==cell['correct'], 'E1 graph data is stale'
    meta=json.loads(source(ROOT/'experiment01/output/20260923_expr/analysis/e1_methodology_summary.json'))
    decomposition={k:meta['entropy_decomposition'][k] for k in ('phi_G','phi_M','phi_R','models','excluded_models')}
    e2root=ROOT/'experiment02/output/20260923_expr2'; e3root=ROOT/'experiment03/output/20260923_expr'
    e2=[]; e3=[]
    plans={(r['model'],r['api'],r['graph_id'],r['agent_variant']):r for r in rows(e2root/'analysis/e2_plan_deviation_summary.csv')}
    for r in rows(e2root/'analysis/e2_methodology_metrics/condition_metrics.csv'):
        parts=r['graph'].split('/');api,identifier=parts[-2:];g=lookup[(api,identifier)]
        plan=plans.get((r['model'],api,identifier,r['agent_variant']))
        psi=number(plan['exact_post_crash_plan_match_rate']) if plan else 1-number(r['H_post_norm'])
        e2.append(dict(graph=g,model=r['model'],variant=r['agent_variant'],n=int(float(r['Q_recoveries_from_number_of_runs'])),
                       correct=int(float(r['overall_correctness_count'])),goal=round(float(r['full_goal_rate'])*float(r['Q_recoveries_from_number_of_runs'])),
                       psi=psi,agreement=number(r['A_post_exact_agreement']),distance=number(r['D_seq_post_rpc_edits']),coverage=number(r['C_path_post']),
                       model_ms=number(r['post_crash_latency_mean_ms']),cost=number(r['dollar_cost_mean_priced_recovery']),
                       paired=int(float(r['Q_recoveries_from_number_of_runs'])),singletons=0))
    correct_e3={}
    for r in rows(e3root/'analysis/e3_methodology_metrics/run_correctness.csv'):
        k=(r['model'],r['api_name'],r['identifier'].removeprefix('id_'),r['agent_variant'],r['run'])
        correct_e3[k]=r['valid_non_repeating']=='True'
    for r in rows(e3root/'analysis/e3_methodology_metrics/condition_metrics.csv'):
        e3.append(dict(graph=lookup[(r['api_name'],r['identifier'].removeprefix('id_'))],model=r['model'],variant=r['agent_variant'],n=int(r['trials']),
                       correct=int(r['correct_count']),goal=int(r['goal_count']),psi=number(r['psi_cont']),agreement=number(r['A_post']),distance=number(r['D_seq_post']),coverage=number(r['C_path_post']),
                       model_ms=number(r['post_crash_model_ms_mean']),system_ms=number(r['post_crash_system_ms_mean']),
                       cost=float(r['cost_usd_total'])/int(r['cost_observed']),paired=int(r['paired_trials']),singletons=int(r['singleton_trials']),
                       model_times=[],system_times=[]))
    for exp,root,pattern,cells in [('e2',e2root,'*/*/*/*/results.csv',e2),('e3',e3root,'*/*/*/*/*/*/results.csv',e3)]:
        for path in sorted(root.glob(pattern)):
            parts=path.relative_to(root).parts
            if exp=='e2': model,api,identifier,variant=parts[:4]
            else: _,model,_,api,identifier,variant=parts[:6];identifier=identifier.removeprefix('id_')
            graph=lookup[(api,identifier)]; groups={}
            cell=next(c for c in cells if (c['model'],c['graph'],c['variant'])==(model,graph,variant))
            records=rows(path)
            if exp=='e2': records=[r for r in records if r.get('Phase')=='recovery' and r.get('Capture ID') in {'run_001','run_002','run_003'}]
            assert len(records)==cell['n']==30
            for r in records:
                pre=sequence(r['Actual RPC sequence (pre-crash agent)']);post=sequence(r['Actual RPC sequence (post-crash agent)'])
                phases=json.loads(r['Actual RPC trace JSON'])['phases'];resources=next(p for p in phases if p['name']=='post_crash')['initial_resources']
                key=(tuple(pre),tuple(sorted(resources)))
                group=groups.setdefault(key,dict(graph=graph,model=model,variant=variant,prefix=pre,resources=sorted(resources),n=0,outcomes={}))
                if exp=='e3':
                    valid=correct_e3[(model,api,identifier,variant,r['Run'])]
                    cell['model_times'].append(float(r['Post-crash model latency (milliseconds)']))
                    cell['system_times'].append(float(r['Post-crash system latency (milliseconds)']))
                else:
                    calls=pre+post
                    valid=all(r.get(k,'True')=='True' for k in ('Overall RPC sequence valid','Pre-crash RPC sequence valid','Post-crash RPC sequence valid','Goal produced')) and len(calls)==len(set(calls)) and r['Overall RPC sequence has extraneous calls']!='True' and not r['Error'].strip() and not r['Post-crash Error'].strip() and r['Status']!='error' and r['Post-crash Status']!='error'
                outcome=group['outcomes'].setdefault(tuple(post),dict(sequence=post,n=0,goal=0,correct=0))
                group['n']+=1;outcome['n']+=1;outcome['goal']+=r['Goal produced']=='True';outcome['correct']+=valid
            assert sum(p['correct'] for g in groups.values() for p in g['outcomes'].values())==cell['correct'],f'Stale correctness: {path}'
            for group in groups.values():
                group['outcomes']=sorted(group['outcomes'].values(),key=lambda p:-p['n']);routes[exp].append(group)
    for exp,cells,want in [('e1',e1,5400),('e2',e2,3600),('e3',e3,1800)]:
        assert sum(c['n'] for c in cells)==want
        assert sum(t['n'] for t in routes[exp])==want
    for path in sorted((ROOT/'latexs').glob('*.tex')):source(path)
    return dict(graphs=graphs,e1=e1,e2=e2,e3=e3,routes=routes,decomposition=decomposition,
                counts={'e1':5400,'e2':3600,'e3':1800},snapshot='September 2026',schema=1)

PAGES={
 'index':('CONTINUE? — The Last Delivery','An interactive research arcade about choices, crashes, and what comes next.'),
 'e1':('World 1 · The Maze','Same task. Same model. Same route?'),
 'e2':('World 2 · Save Point','We saved the past. Did we save what comes next?'),
 'e3':('World 3 · Player Two','A new process. An unfinished promise.'),
 'theatre':('Route Theatre','Watch the actual recorded paths play together.'),
 'lab':('Crash Lab · The Last Delivery','A courier can turn back. The world does not rewind.'),
 'field-guide':('Research Log','The science behind the arcade, with evidence and limits.'),
}

def build(out):
    legacy=[ROOT/f'experiment0{i}/output/{"20260923_expr2" if i==2 else "20260923_expr"}/analysis/e{i}_analysis.html' for i in (1,2,3)]
    protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in legacy+list((ROOT/'latexs').rglob('*.tex')) if p.exists()}
    source(Path(__file__));data=load_data();out.mkdir(parents=True,exist_ok=True)
    css=source(SITE/'src/style.css').decode();script=source(SITE/'src/app.js').decode();frame=source(SITE/'src/frame.html').decode()
    animation=source(ROOT/'data_analysis/templates/path_animation.js').decode()
    outputs={}
    for page,(title,description) in PAGES.items():
        payload={k:data[k] for k in ('counts','snapshot','schema','decomposition')}
        payload['graphs']={k:{x:v for x,v in g.items() if x!='svg'} for k,g in data['graphs'].items()}
        if page in ('index','e1','e2','e3','theatre'):
            experiments=('e1','e2','e3') if page in ('index','theatre') else (page,)
            payload.update(graphs=data['graphs'],experiments={e:dict(cells=data[e],routes=data['routes'][e],summary=summarize(data[e])) for e in experiments})
        else:
            payload['summaries']={exp:summarize(data[exp]) for exp in ('e1','e2','e3')}
        body=source(SITE/f'src/{page}.html').decode()
        game_css=game_script=''
        if '{{DELIVERY_GAME}}' in body:
            game=source(SITE/'src/game-tabs.html').decode()
            game=game.replace('{{TUTORIAL_GAME}}',source(SITE/'src/tutorial-game.html').decode())
            game=game.replace('{{EXPERT_GAME}}',source(SITE/'src/delivery-game.html').decode())
            sprite='data:image/png;base64,'+base64.b64encode(source(SITE/'src/assets/pip-parcel-robot.png')).decode()
            body=body.replace('{{DELIVERY_GAME}}',game.replace('{{PIP_SPRITE}}',sprite))
            game_css=source(SITE/'src/tutorial-game.css').decode()+source(SITE/'src/delivery-game.css').decode()
            game_script=''.join(source(SITE/f'src/{name}.js').decode() for name in ('tutorial-game','delivery-game','game-tabs'))
        nav=''.join(f'<a href="{key}.html"'+(' aria-current="page"' if key==page else '')+f'>{label}</a>' for key,label in [('e1','01 / The Maze'),('e2','02 / Save Point'),('e3','03 / Player Two')])
        values={'TITLE':html.escape(title),'DESCRIPTION':html.escape(description),'PAGE':page,'NAV':nav,'BODY':body,'CSS':css+game_css,'DATA':js(payload),'SCRIPT':script+game_script,'ANIMATION':animation if page in ('index','e1','e2','e3','theatre') else ''}
        rendered=frame
        for key,value in values.items():rendered=rendered.replace('{{'+key+'}}',value)
        assert not re.search(r'\{\{[A-Z_]+\}\}',rendered),page
        path=out/f'{page}.html';path.write_text(rendered,encoding='utf-8');outputs[path.name]=hashlib.sha256(rendered.encode()).hexdigest()
    for p,digest in protected.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,f'Existing source changed: {p}'
    manifest=dict(schema=1,pages=outputs,sources=dict(sorted(SOURCES.items())),trials=data['counts'],models={e:sorted({c['model'] for c in data[e]}) for e in ('e1','e2','e3')},self_contained=True)
    (out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(outputs)} self-contained pages in {out}; verified 10,800 trials and unchanged existing sites/manuscript.')

def summarize(cells):
    groups={}
    for c in cells:groups.setdefault(c['variant'] if c['variant']!='agent' else c['model'],[]).append(c)
    return {k:dict(n=sum(c['n'] for c in rows),correct=sum(c['correct'] for c in rows),goal=sum(c['goal'] for c in rows),**{field:fmean(c[field] for c in rows if c.get(field) is not None) for field in ('psi','entropy','agreement','distance','coverage','model_ms','system_ms','cost') if any(c.get(field) is not None for c in rows)}) for k,rows in groups.items()}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=SITE);args=parser.parse_args();build(args.out.resolve())
