from typing import Any, List
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer

_analyzer = None

def get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is not None:
        return _analyzer

    analyzer = AnalyzerEngine()

    pass_pattern = Pattern(name="pass_pattern", regex=r"\b\w*(?:p|P)assword\w*\b", score=0.3)
    secr_pattern = Pattern(name="secr_pattern", regex=r"\b\w*(?:s|S)ecret\w*\b", score=0.3)
    cred_pattern = Pattern(name="cred_pattern", regex=r"\b\w*(?:c|C)redential\w*\b", score=0.3)
    org_pattern  = Pattern(name="org_pattern",  regex=r"\bWells\s*Fargo\b|\bWellsFargo\b", score=0.3)

    passwords_recognizer = PatternRecognizer(
        supported_entity="NAME1",
        patterns=[pass_pattern, secr_pattern, cred_pattern, org_pattern],
    )
    analyzer.registry.add_recognizer(passwords_recognizer)

    _analyzer = analyzer
    return analyzer


def analyze(text: str, language: str = "en") -> List[Any]:
    results = get_analyzer().analyze(text=text, language=language)
    return sorted(results, key=lambda r: (r.start, -r.end))
