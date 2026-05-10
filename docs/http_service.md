# BTP Engine HTTP Service

## Overview

HTTP service providing REST API access to the BTP Engine Core for MyHome/Lovable integration.

## Endpoints

### GET /health

Health check endpoint (no authentication required).

**Response:**
```json
{
  "ok": true,
  "service": "btp-engine-core",
  "mode": "deterministic",
  "guardrails_ok": true
}
```

### POST /run

Execute BTP Engine on uploaded file.

**Authentication:**
- If `BTP_ENGINE_TOKEN` environment variable is set, requires `Authorization: Bearer <token>` header
- If `BTP_ENGINE_TOKEN` is not set, no authentication required

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `file`: PDF or ZIP file
  - `mode`: Must be `dry_run`

**Response:**
```json
{
  "engine_version": "BTP_ENGINE_CORE_V3_REAL_REGRESSION_STRICT_RELEASE_FROZEN",
  "repo_sha": "abc123...",
  "pdf_count": 2,
  "task_candidates_count": 48,
  "dst_mapping_count": 48,
  "missing_expected_flags_total": 0,
  "quality_score": {...},
  "guardrails_counters": {
    "openai_calls": 0,
    "gpt_calls": 0,
    "gemini_calls": 0,
    "vision_api_calls": 0,
    "lovable_gateway_calls": 0,
    "db_writes": 0,
    "dst_pushes": 0,
    "prod_touched": false,
    "cost_usd": 0.0
  },
  "files": {
    "inventory.json": "...",
    "extraction_report.json": "...",
    "classification_report.json": "...",
    "problems.json": "...",
    "candidate_tasks.json": "...",
    "candidate_tasks.csv": "...",
    "dst_mapping_report.json": "...",
    "quality_score.json": "...",
    "guardrails_report.json": "...",
    "final_report.md": "...",
    "per_doc.json": "..."
  }
}
```

## Guardrails

The service enforces strict guardrails:
- Only `dry_run` mode allowed
- No database writes
- No DST pushes
- No AI API calls (GPT, OpenAI, Gemini, Vision)
- No Lovable Gateway calls
- No production touches
- Zero cost

## Local Development

Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-service.txt
```

Run the service:
```bash
BTP_ENGINE_TOKEN=test-token uvicorn service.app:app --host 127.0.0.1 --port 8080
```

Test:
```bash
# Health check
curl http://127.0.0.1:8080/health

# Run engine
curl -X POST http://127.0.0.1:8080/run \
  -H "Authorization: Bearer test-token" \
  -F "file=@test.pdf" \
  -F "mode=dry_run"
```

## Docker

Build:
```bash
docker build -t btp-engine-core-http .
```

Run:
```bash
docker run -p 8080:8080 -e BTP_ENGINE_TOKEN=your-token btp-engine-core-http
```

## Testing

Run tests:
```bash
pytest tests/test_http_service.py -v
```
