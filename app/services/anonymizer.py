import logging
import logging.config
from pathlib import Path
from typing import Dict, Tuple, List
from presidio_analyzer import Pattern, PatternRecognizer, AnalyzerEngine
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    IbanRecognizer,
    UsBankRecognizer,
)
import hmac, hashlib, os

try:
    _CONF = Path(__file__).resolve().parents[2] / "logging.conf"
    logging.config.fileConfig(_CONF)
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
_PLACEHOLDER_SECRET = os.getenv("PLACEHOLDER_SECRET", "change-me")

def _ph(etype: str, original: str, session_id: str) -> str:
    msg = (session_id + "|" + original).encode("utf-8")
    digest = hmac.new(_PLACEHOLDER_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return f"<<{etype}_{digest[:12]}>>"

def add_dlp_recognizers(engine: AnalyzerEngine):
    regs = []
    regs.append(PatternRecognizer("CREDIT_CARD_NUMBER",[Pattern("cc_num",r"\b(?:\d[ -]*?){13,19}\b",0.7)],context=["card","credit","visa","mastercard","amex"]))
    regs.append(PatternRecognizer("FINANCIAL_ACCOUNT_NUMBER",[Pattern("acct_num",r"\b(?:acct(?:ount)?[_\s:]*)?\d{7,18}\b",0.5)],context=["account","routing","iban","bank"]))
    regs.append(PatternRecognizer("PASSWORD",[Pattern("password_kv",r"(?i)\b(pass(word|wd)?|pwd)\b\s*[:=]\s*[^,\s\"']{4,}",0.8)]))
    regs.append(PatternRecognizer("AUTH_TOKEN",[Pattern("auth_token",r"\b[A-Za-z0-9_\-]{20,64}\b",0.6)],context=["token","auth","bearer","authorization"]))
    regs.append(PatternRecognizer("JSON_WEB_TOKEN",[Pattern("jwt",r"\beyJ[A-Za-z0-9_\-]+?\.[A-Za-z0-9_\-]+?\.[A-Za-z0-9_\-]+",0.9)]))
    regs.append(PatternRecognizer("AZURE_AUTH_TOKEN",[Pattern("azure_pat",r"\b[0-9A-Za-z]{52}\b",0.8)],context=["azure","ado","devops","pat","token"]))
    regs.append(PatternRecognizer("GCP_CREDENTIALS",[Pattern("gcp_api_key",r"\bAIza[0-9A-Za-z\-_]{35}\b",0.9),Pattern("gcp_priv_key",r"-----BEGIN PRIVATE KEY-----(?:.|\n)+?-----END PRIVATE KEY-----",0.9)],context=["google","gcp","service","account","key","json"]))
    regs.append(PatternRecognizer("OAUTH_CLIENT_SECRET",[Pattern("oauth_client_secret",r"(?i)\b(client_?secret|oauth_?secret)\b\s*[:=]\s*[^\s,'\"]{10,}",0.9)]))
    regs.append(PatternRecognizer("SSL_CERTIFICATE",[Pattern("pem_cert",r"-----BEGIN CERTIFICATE-----(?:.|\n)+?-----END CERTIFICATE-----",0.9),Pattern("pem_key",r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----(?:.|\n)+?-----END (?:RSA |EC )?PRIVATE KEY-----",0.9)]))
    regs.append(PatternRecognizer("XSRF_TOKEN",[Pattern("xsrf",r"(?i)\b(xsrf|csrf)[-_]?token\b\s*[:=]\s*[A-Za-z0-9\-_]{16,}",0.8)]))
    regs.append(PatternRecognizer("STORAGE_SIGNED_URL",[Pattern("gcs_signed",r"https?://(?:storage\.googleapis\.com|storage\.cloud\.google\.com)/[^\s?]+[?][^ ]*(X-Goog-(?:Signature|Credential))=",0.9),Pattern("s3_signed",r"https?://[^/\s]+\.s3[^/\s]*/[^\s?]+[?][^ ]*(X-Amz-Signature)=",0.9),Pattern("azure_sas",r"https?://[^?\s]+[?][^ ]*\b(sig|se|sp|sv|sr)=",0.8)]))
    regs.append(PatternRecognizer("STORAGE_SIGNED_POLICY_DOCUMENT",[Pattern("policy_b64",r"(?i)\bpolicy\s*=\s*[A-Za-z0-9+/=]{20,}",0.8),Pattern("aws_policy",r"(?i)X-Amz-Credential=[^&]+&X-Amz-Algorithm=[^&]+&X-Amz-Date=\d{8}T\d{6}Z",0.8)]))
    regs.append(PatternRecognizer("WF_SAR",[Pattern("wf_sar",r"\bSAR-\d{6,}\b",0.7)]))
    for r in regs: engine.registry.add_recognizer(r)

def _build_engine() -> AnalyzerEngine:
    engine = AnalyzerEngine()
    pass_pattern = Pattern(name="pass_pattern", regex=r"\w*(p|P)assword\w*", score=0.1)
    secr_pattern = Pattern(name="secr_pattern", regex=r"\w*(s|S)ecret\w*", score=0.1)
    cred_pattern = Pattern(name="cred_pattern", regex=r"\w*(c|C)redential\w*", score=0.1)
    org_pattern  = Pattern(name="org_pattern",  regex=r"\w*(w|W)ellsfargo\w*", score=0.1)
    passwords_recognizer = PatternRecognizer(
        supported_entity="CUSTOM_TOKEN",
        patterns=[pass_pattern, secr_pattern, cred_pattern, org_pattern],
    )
    engine.registry.add_recognizer(passwords_recognizer)
    add_dlp_recognizers(engine)
    engine.registry.add_recognizer(CreditCardRecognizer())
    engine.registry.add_recognizer(IbanRecognizer())
    engine.registry.add_recognizer(UsBankRecognizer())
    return engine

_ENGINE = _build_engine()

def content_anonymizer(text: str,
                       entity_mapping: Dict[str, Dict[str, str]],
                       entity_counter: Dict[str, int],
                       session_id: str) -> Tuple[str, Dict, Dict]:
    result = _ENGINE.analyze(text=text, language="en")
    results = sorted(result, key=lambda r: r.start)
    out_parse: List[str] = []
    cursor = 0
    for r in results:
        if r.start < cursor: continue
        out_parse.append(text[cursor:r.start])
        etype = r.entity_type
        original = text[r.start:r.end]
        if etype not in entity_mapping: entity_mapping[etype] = {}
        if original not in entity_mapping[etype]:
            placeholder = _ph(etype, original, session_id)
            entity_mapping[etype][original] = placeholder
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
    for ph in sorted(reverse_map.keys(), key=len, reverse=True):
        out = out.replace(ph, reverse_map[ph])
    return out
