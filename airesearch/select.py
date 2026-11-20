"""Problem selection: rank candidate topics transparently.

Scores are 1-5 and every factor needs a source. Unsourced factors are flagged and capped, because
a fluent but unsourced score is exactly the 'McNamara fallacy / hivemind' risk the literature warns about.
A high harm risk vetoes a topic (author-notes: no conflict with public benefit).
The ranking is advice. The author decides which topic is researched.
"""
from pathlib import Path

from .util import read_json

FACTORS = ("importance", "neglectedness", "tractability_ai", "verifiability")
HARM_VETO = 4
UNSOURCED_CAP = 3


def score(topic: dict) -> dict:
    flags = []
    vals = {}
    sources = topic.get("sources", {})
    for f in FACTORS:
        v = topic["scores"][f]
        if not 1 <= v <= 5:
            raise ValueError(f"{topic['id']}: {f} must be 1-5")
        if not sources.get(f):
            flags.append(f"unsourced:{f}")
            v = min(v, UNSOURCED_CAP)
        vals[f] = v
    base = (vals["importance"] * vals["neglectedness"] * vals["tractability_ai"]) ** (1 / 3)
    total = base * (0.5 + 0.5 * vals["verifiability"] / 5)
    harm = topic["scores"].get("harm_risk", 1)
    vetoed = harm >= HARM_VETO
    if vetoed:
        flags.append("vetoed:harm_risk")
    return {"id": topic["id"], "title": topic["title"], "score": round(total, 2), "flags": flags, "vetoed": vetoed}


def rank(path: Path) -> list:
    topics = read_json(path)["topics"]
    scored = [score(t) for t in topics]
    return sorted(scored, key=lambda s: (s["vetoed"], -s["score"]))
