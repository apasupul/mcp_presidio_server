# MCP Presidio Server (HMAC placeholders + DLP InfoTypes + Built-in Recognizers)

## Install
```bash
pip install -r requirements.txt
# Ensure spaCy model is available: en-core-web-lg==3.8.0 (from internal PyPI)
```

## Run FastAPI
```bash
uvicorn app.main:app --reload
```
- Swagger: http://127.0.0.1:8000/docs

## Run MCP
```bash
python mcp_server/server.py
```

## Features
- Deterministic HMAC placeholders (env: PLACEHOLDER_SECRET)
- Custom DLP recognizers: credit cards, tokens, JWTs, secrets, certs, signed URLs, etc.
- Built-in Presidio recognizers: CreditCardRecognizer, IbanRecognizer, UsBankRecognizer
- SQLite-backed mapping store per session
