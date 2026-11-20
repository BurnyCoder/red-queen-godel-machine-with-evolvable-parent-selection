"""Generate all empirical values from event and per-paper result files."""
from __future__ import annotations

import numpy as np
from .data import load
from .search import run_name


def crossed_interval(left,right,labels,draws=10000,seed=1701):
    """Resample common seeds and common paper columns within their decision strata."""
    diffs=np.asarray(left,dtype=float)-np.asarray(right,dtype=float)
    labels=np.asarray(labels)
    if diffs.ndim!=2 or len(labels)!=diffs.shape[1] or set(labels)!={"accept","reject"}:
        raise ValueError("Expected paired binary predictions on both decision classes")
    rng=np.random.default_rng(seed)
    strata=[np.flatnonzero(labels==label) for label in ("accept","reject")]
    samples=[]
    for start in range(0,draws,200):
        batch=min(200,draws-start)
        rows=rng.integers(0,len(diffs),size=(batch,len(diffs)))
        cols=np.concatenate([rng.choice(s,size=(batch,len(s)),replace=True) for s in strata],axis=1)
        samples.extend(diffs[rows[:,:,None],cols[:,None,:]].mean(axis=(1,2))*100)
    low,high=np.quantile(samples,[.025,.975])
    return dict(mean_pp=float(diffs.mean()*100),low=float(low),high=float(high),pairs=diffs.shape[0],
                per_seed_pp=(diffs.mean(axis=1)*100).tolist())


def summary(project):
    """Include in-progress searches but count only terminal evaluations for inference."""
    runs=[load(p) for p in sorted((project/"results"/"runs").glob("*.json"))]
    evals=[load(p) for p in sorted((project/"results"/"evaluations").glob("*.json"))]
    table=[]
    for data in evals:
        rows=data["rows"]
        by_route={}
        for route in sorted({r["route"] for r in rows}):
            sub=[r for r in rows if r["route"]==route]
            by_route[route]=dict(n=len(sub),accuracy=sum(r["correct"] for r in sub)/len(sub))
        table.append(dict(name=data["name"],split=data["split"],arm=data["arm"],n=len(rows),
                          correct=sum(r["correct"] for r in rows),complete=data["complete"],routes=by_route,
                          compute=data.get("compute",{})))
    panels={e["name"]:e for e in evals if e["split"]=="test" and e["complete"]}
    contrasts={}
    for suffix in ("","-tokens"):
        left,right,seeds=[],[],[]
        labels=None
        for seed in range(1,9):
            keys=[run_name("confirm",seed,a)+suffix for a in ("editable","native")]
            if not all(k in panels for k in keys):
                continue
            a,b=[sorted(panels[k]["rows"],key=lambda x:x["id"]) for k in keys]
            if [(r["id"],r["label"]) for r in a]!=[(r["id"],r["label"]) for r in b]:
                raise ValueError("Mismatched paired papers")
            labels=[r["label"] for r in a]
            left.append([r["correct"] for r in a])
            right.append([r["correct"] for r in b])
            seeds.append(seed)
        if seeds:
            outcome=crossed_interval(left,right,labels)
            outcome["seeds"]=seeds
            outcome["interpretation"]="incomplete, descriptive" if len(seeds)<8 else (
                "supports superiority" if outcome["low"]>0 else "evidence against superiority" if outcome["high"]<=0 else "inconclusive")
            contrasts["matched_tokens" if suffix else "primary"]=outcome
    return runs,evals,table,contrasts
