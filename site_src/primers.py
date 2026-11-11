"""Per-card background, mechanism, and interview focus for every domain topic."""

from primers_backend import BACKEND
from primers_go import GO
from primers_hot import HOT
from primers_java import JAVA
from primers_lbs import LBS
from primers_ml import AGENT, REC, RESUME
from primers_py import ANDROID, PYTHON
from primers_store import ES, MYSQL, REDIS

PRIMERS = {}
for part in (
    GO,
    JAVA,
    PYTHON,
    ANDROID,
    LBS,
    HOT,
    MYSQL,
    REDIS,
    ES,
    BACKEND,
    REC,
    AGENT,
    RESUME,
):
    overlap = set(PRIMERS) & set(part)
    if overlap:
        raise SystemExit(f"duplicate primer keys: {sorted(overlap)}")
    PRIMERS.update(part)
