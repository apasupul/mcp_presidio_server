from app.services.anonymization import anonymize_text, deanonymize_text

SESSION = "test-session"

def test_roundtrip_basic():
    text = "password Secret123 WellsFargo"
    anon, emap, rmap = anonymize_text(SESSION, text)
    assert anon != text
    dean = deanonymize_text(anon, rmap)
    assert dean == text
