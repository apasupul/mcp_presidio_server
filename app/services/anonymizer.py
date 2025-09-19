import logging
import logging.config
from collections import defaultdict
from typing import Dict, Tuple, List

from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

def _build_engine() -> AnalyzerEngine:
    engine = AnalyzerEngine()

    # Custom patterns (in addition to Presidio's built-ins if configured)
    pass_pattern = Pattern(name="pass_pattern", regex=r"\w*(p|P)assword\w*", score=0.1)
    secr_pattern = Pattern(name="secr_pattern", regex=r"\w*(s|S)ecret\w*", score=0.1)
    cred_pattern = Pattern(name="cred_pattern", regex=r"\w*(c|C)redential\w*", score=0.1)
    org_pattern  = Pattern(name="org_pattern",  regex=r"\w*(w|W)ellsfargo\w*", score=0.1)

    passwords_recognizer = PatternRecognizer(
        supported_entity="CUSTOM_TOKEN",
        patterns=[pass_pattern, secr_pattern, cred_pattern, org_pattern],
    )
    engine.registry.add_recognizer(passwords_recognizer)
    return engine

_ENGINE = _build_engine()

def content_anonymizer(text: str,
                       entity_mapping: Dict[str, Dict[str, str]],
                       entity_counter: Dict[str, int]) -> Tuple[str, Dict, Dict]:
    result = _ENGINE.analyze(text=text, language="en")
    results = sorted(result, key=lambda r: r.start)
    out_parse: List[str] = []
    cursor = 0
    for r in results:
        if r.start < cursor:
            continue
        out_parse.append(text[cursor:r.start])
        etype = r.entity_type
        original = text[r.start:r.end]
        if etype not in entity_mapping:
            entity_mapping[etype] = {}
            entity_counter[etype] = 0
        if original not in entity_mapping[etype]:
            placeholder = f"<<{etype}_{entity_counter[etype]}>>"
            entity_mapping[etype][original] = placeholder
            entity_counter[etype] += 1
        else:
            placeholder = entity_mapping[etype][original]
        out_parse.append(placeholder)
        cursor = r.end
    out_parse.append(text[cursor:])
    return "".join(out_parse), entity_mapping, entity_counter

def reverse_mapping(entity_mapping: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    return {ph: orig for bucket in entity_mapping.values() for orig, ph in bucket.items()}

def content_deanonymizer(text: str, reverse_map: Dict[str, str]) -> str:
    out = text
    # Replace longest placeholders first to avoid prefixes colliding
    for ph in sorted(reverse_map.keys(), key=len, reverse=True):
        out = out.replace(ph, reverse_map[ph])
    return out
