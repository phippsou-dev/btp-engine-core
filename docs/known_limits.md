# Known Limits — BTP Engine Core v3 (strict)

## Extraction
- OCR fallback uses `pdftoppm` (250 DPI) + `tesseract` (fra). Quality depends on Tesseract install.
- CID-dominated native text triggers OCR replacement (threshold: `cid_count / tokens > 0.5`).
- Documents with `< 200` native AND `< 200` OCR chars MUST be flagged `NEEDS_MANUAL_REVIEW`.

## Classification
- Filename hint provides hard override for clear cases (EDL, DPE, Notice, PC).
- Without filename hint, ambiguous documents may be misclassified — manual review required.
- Only Phase 6 classes are validated end-to-end:
  - `NOTICE_SECURITE_HABITATION`
  - `DPE_PROJETE`
  - `EDL_AVANT_PROJET`
  - `PLAN_GRAPHIC_PC_FACADES`

## Flag Detection
- Patterns are tuned to the real Phase 6 corpus. New document variants may need new regex.
- `optional_absent_from_source` is informational, not a failure.

## Task Generation
- `FLAG_TO_TASK` mapping is deterministic and finite. Unmapped flags produce no task.
- 48 tasks on the validated corpus; expect proportional growth on similar documents.

## Out of Scope (v3)
- No LLM summarization
- No semantic deduplication of tasks
- No multilingual support (FR only)
- No incremental/streaming processing
- No DB write path (must be enabled explicitly via env in future release)

## Observability
- All counters in `guardrails_report.json` MUST be zero in `deterministic_core` mode.
- A non-zero counter → release regression, block deploy.
