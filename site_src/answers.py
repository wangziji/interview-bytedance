"""Spoken-exam answers, one per focus point, in the same order as the primers."""

from answers_lang import LANG
from answers_lbs import HOT, LBS
from answers_rest import REST
from answers_store import STORE

ANSWERS = {}
for part in (LANG, LBS, HOT, STORE, REST):
    overlap = set(ANSWERS) & set(part)
    if overlap:
        raise SystemExit(f"duplicate answers: {sorted(overlap)}")
    ANSWERS.update(part)
