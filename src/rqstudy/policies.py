"""Published selection formulas and the sole editable dispatch in the experiment.

RQGM October Appendix B.2 selects parents by subtree evidence, and measurement
targets by own evidence. HyperAgents E.5 delegates expansion to the newest valid
owner. Its gl_utils.py lines 571–584 implement the exponential child penalty.
"""
from __future__ import annotations

import math
from .data import digest


def archive_view(archive, epoch: int, n: int, budget: int) -> dict:
    """Build fresh aggregate statistics from retained OpenRQGM utility records."""
    nodes = []
    for node in archive.nodes.values():
        if not node.valid:
            continue
        s, f = archive.counts(node_ids=[node.node_id])
        cs, cf = archive.clade_counts(node.node_id)
        role_means = []
        for role in ("writer", "reviewer"):
            rs, rf = archive.counts(node_ids=[node.node_id], role_id=role)
            role_means.append((1 + rs)/(2 + rs + rf))
        nodes.append(dict(id=node.node_id, parent=node.parent_id, created=node.created_at_step,
                          children=len(archive.children.get(node.node_id, [])), own_s=s, own_f=f,
                          clade_s=cs, clade_f=cf, score=sum(role_means)/len(role_means)))
    return dict(nodes=nodes, epoch=epoch, evaluations=n, budget=budget)


def choose_thompson(view: dict, rng, clade: bool) -> str:
    """Sample Beta posteriors with the remaining-budget cooldown from HGM."""
    prefix = "clade" if clade else "own"
    scale = view["budget"] / max(1, view["budget"] - view["evaluations"])
    return max(view["nodes"], key=lambda n: rng.beta((1+n[prefix+"_s"])*scale, (1+n[prefix+"_f"])*scale))["id"]


def reference_choice(view: dict, quantile: float, paper: bool) -> str:
    """Draw from either published recipe using one common uniform variate."""
    nodes = view["nodes"]
    top = sorted((n["score"] for n in nodes), reverse=True)[:3]
    midpoint = sum(top)/len(top)
    weights = []
    for node in nodes:
        children = node["children"]
        penalty = 1/(1+children) if paper else math.exp(-(children/8)**3)
        weights.append(penalty / (1 + math.exp(-10*(node["score"]-midpoint))))
    total = sum(weights)
    if not total:
        return nodes[min(len(nodes)-1, int(quantile*len(nodes)))]["id"]
    upto = 0.0
    for node, weight in zip(nodes, weights):
        upto += weight
        if quantile * total < upto:
            return node["id"]
    return nodes[-1]["id"]


def choose_parent(arm: str, archive, view: dict, rng, worker) -> dict:
    """Keep actual selector ownership distinct from the descended workspace."""
    draw = float(rng.random())
    released = reference_choice(view, draw, False)
    published = reference_choice(view, draw, True)
    ids = [row["id"] for row in view["nodes"]]
    seed = int(rng.integers(0, 2**31))
    event = dict(owner=None, failures=[], replay_u=draw, released=released, published=published,
                 seed=seed, snapshot=view, source_hash=None)
    if arm == "native":
        event["parent"] = choose_thompson(view, rng, clade=True)
    elif arm == "uniform":
        event["parent"] = ids[int(draw*len(ids))]
    elif arm == "handcrafted":
        event["parent"] = released
    elif arm == "editable":
        for owner in reversed(ids):
            source = archive.nodes[owner].workspace["selector"]
            try:
                result = worker.call(source,"select_parent",view,seed)
                if result not in ids:
                    raise ValueError("Selected an ineligible node")
                event.update(owner=owner,parent=result,source_hash=digest(source))
                break
            except ValueError as exc:
                event["failures"].append(dict(owner=owner,error=str(exc),source_hash=digest(source)))
        else:
            raise RuntimeError("The fixed uniform root failed; restore the worker runtime")
    else:
        raise ValueError(f"Unknown selector {arm}")
    return event
