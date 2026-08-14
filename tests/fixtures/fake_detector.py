import json
import sys


payload = {
    "40_sentence_monotony": {
        "label": "Sentence-length monotony",
        "count": 1,
        "samples": ["cv=0.31 below 0.35 threshold"],
    },
    "_metrics": {
        "ai_tell_score": 38,
        "ai_tell_band": "mixed",
        "patterns_flagged": 1,
        "sentences": 4,
    },
}

json.dump(payload, sys.stdout)
