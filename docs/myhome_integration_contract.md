# MyHome Integration Contract — BTP Engine Core v3

**Engine version:** `btp-engine-core-v3-real-regression-strict`
**Mode:** deterministic_core (no GPT / OpenAI / Gemini / Vision / Lovable Gateway)

## Inputs
| Field | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | yes | MyHome project identifier |
| `documents` | File[] (PDF or ZIP) | yes | Uploaded PDF(s) or ZIP archive |
| `local_storage_path` | string | yes | Absolute working directory for extraction & artifacts |
| `mode` | enum | yes | `dry_run` (default) \| `staging_apply` |

## Outputs (always written to `local_storage_path/outputs/`)
- `extraction_report.json` — text extraction + OCR metrics per file
- `classification_report.json` — class label per file with score
- `problems.json` — detected problems / flags per file
- `candidate_tasks.json` — generated task candidates
- `candidate_tasks.csv` — UTF-8-SIG, Excel-compatible
- `dst_mapping_report.json` — DST family/category/subcategory mapping
- `quality_score.json` — recall / precision / coverage metrics
- `guardrails_report.json` — call counters, cost, prod flag
- `final_report.md` — human-readable synthesis
- `per_doc.json` — per-document audit (flags found / missing / optional absent)
- `inventory.json` — file manifest (sha256, pages_count, native_chars)

## Execution Rules
1. **`dry_run` is default.** No DB writes, no DST push.
2. **DB writes** only when env `DB_WRITES_ENABLED=true` AND `mode=staging_apply`.
3. **DST push** only when env `DST_PUSH_ENABLED=true` AND `mode=staging_apply`.
4. **No external paid call** is allowed in `deterministic_core` mode (enforced by guardrails — process must abort with exit code 2 on any attempt).
5. **OCR insufficient** → the document MUST emit class `NEEDS_MANUAL_REVIEW` with no fabricated tasks. Threshold: `native_chars < 200 AND ocr_chars < 200`.
6. **Production is never touched** by the engine; `prod_touched` MUST remain `false`.

## Exit Codes
- `0` — success, all artifacts produced
- `1` — input error (missing file, invalid project_id)
- `2` — guardrail violation (forbidden external call attempt)
- `3` — extraction failure on all documents

## Versioning
Pin clients to the git tag `btp-engine-core-v3-real-regression-strict`.
