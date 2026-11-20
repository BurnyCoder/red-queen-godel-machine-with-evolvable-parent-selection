"""Freeze reviewer identities independently of the sealed paper outcomes."""
from __future__ import annotations

import time
from .data import canonical, digest, dump, load, read_split
from .inference import now
from .search import run_name
from .workspace import ROOT


def roster():
    """Order primary pairs before secondary controls; fork is attached to seed one."""
    return [(s,a) for s in range(1,9) for a in ("editable","native")] + [(s,a) for s in range(1,6) for a in ("uniform","handcrafted")] + [(1,"fork-native")]


def frozen_entry(run, endpoint=None):
    """The selected source and validation checkpoint fully identify a reviewer."""
    ep=endpoint or run["endpoints"][-1]
    workspace=next(n["workspace"] for n in run["nodes"] if n["id"]==ep["node"])
    if digest(workspace["reviewer"])!=ep["key"]:
        raise ValueError("Endpoint program identity failed verification")
    return dict(name=run["name"],seed=run["seed"],arm=run["arm"],source=workspace["reviewer"],
                key=ep["key"],n=ep["n"],compute=ep["compute"])


def freeze(project,allow_incomplete=False):
    """Build the entire endpoint manifest before opening any test manuscript."""
    path=project/"results"/"freeze.json"
    if path.exists():
        return load(path)
    budget=load(project/"results"/"budget.json")
    if allow_incomplete and time.time()<budget["deadline"]:
        raise ValueError("An incomplete cohort may be frozen only at the registered deadline")
    entries={"root":dict(name="root",seed=0,arm="root",source=ROOT["reviewer"],key=digest(ROOT["reviewer"]),n=0)}
    runs={}
    missing=[]
    for seed,arm in roster():
        name=run_name("confirm",seed,arm)
        source=project/"results"/"runs"/(name+".json")
        data=load(source) if source.exists() else {}
        if data.get("complete") and data["budget"]==budget["budget"]:
            runs[name]=data
            entries[name]=frozen_entry(data)
        else:
            missing.append(name)
    if missing and not allow_incomplete:
        raise ValueError("Pending confirmatory endpoints: "+", ".join(missing))
    # Token sensitivity uses a cutoff fixed without consulting any test predictions.
    for seed in range(1,9):
        pair=[run_name("confirm",seed,a) for a in ("editable","native")]
        if not all(name in runs for name in pair):
            continue
        def tokens(ep):
            return ep["compute"]["input"]+ep["compute"]["output"]
        cutoff=min(tokens(runs[name]["endpoints"][-1]) for name in pair)
        for name in pair:
            eligible=[ep for ep in runs[name]["endpoints"] if tokens(ep)<=cutoff]
            entry=frozen_entry(runs[name],eligible[-1]) if eligible else dict(entries["root"],seed=seed,arm=runs[name]["arm"])
            entries[name+"-tokens"]=dict(entry,cutoff=cutoff)
    manifest=dict(frozen_at=now(),split_sha=load(project/"results"/"split-manifest.json")["splits"]["test"]["sha256"],
                  budget=budget["budget"],missing=missing,entries=entries,entries_sha=digest(canonical(entries)))
    dump(path,manifest)
    return manifest


def score(project,domain,split,name,entry=None):
    """Score only frozen test programs; interrupted item scoring resumes idempotently."""
    if split=="test":
        manifest=load(project/"results"/"freeze.json")
        if digest(canonical(manifest["entries"]))!=manifest["entries_sha"] or name not in manifest["entries"]:
            raise ValueError("Missing or corrupt frozen endpoint")
        entry=manifest["entries"][name]
    elif split=="pilot":
        if entry is None and name=="root":
            entry=dict(name=name,seed=0,arm="root",key=digest(ROOT["reviewer"]),source=ROOT["reviewer"],n=0)
        elif entry is None:
            run=load(project/"results"/"runs"/(name+".json"))
            if not run["complete"] or run["stage"]!="pilot":
                raise ValueError("Only completed pilot searches may access the pilot evaluation")
            entry=frozen_entry(run)
    else:
        raise ValueError("Unknown evaluation split")
    if digest(entry["source"])!=entry["key"]:
        raise ValueError("Frozen source hash mismatch")
    papers=read_split(project,split)
    path=project/"results"/"evaluations"/f"{split}-{name}.json"
    out=load(path) if path.exists() else dict(split=split,name=name,seed=entry["seed"],arm=entry["arm"],
            key=entry["key"],checkpoint=entry["n"],rows=[],elapsed=0.0,started=now(),complete=False)
    if out["key"]!=entry["key"]:
        raise ValueError("Endpoint changed during evaluation")
    done={r["id"] for r in out["rows"]}
    for paper in papers:
        if paper["id"] in done:
            continue
        start=time.monotonic()
        result=domain.review({"reviewer":entry["source"]},paper,f"endpoint/{paper['id']}")
        out["rows"].append(dict(id=paper["id"],label=paper["label"],correct=int(result["decision"]==paper["label"]),**result))
        out["elapsed"]+=time.monotonic()-start
        out["compute"]=domain.broker.metrics("endpoint")
        out["complete"]=len(out["rows"])==len(papers)
        dump(path,out)
    return out
