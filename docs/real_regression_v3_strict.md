# Real Regression v3 — Strict

**Tag:** `btp-engine-core-v3-real-regression-strict`
**Commit:** `ac727830a4737457acd9e20c1aa599da73a3df06`
**Verdict:** `BTP_ENGINE_CORE_REAL_DOCUMENT_REGRESSION_STRICT_VALIDATED`

## Suite
4 real Phase 6 PDFs:
- `notice_securite_habitation.pdf`
- `dpe_projete_archi_home.pdf`
- `edl_projet_beziers.pdf`
- `pieces_pc_demande.pdf`

## Results
- Tests: **50/50 PASS** (incl. 3 Phase 6 regression patterns)
- `run_engine.py` rc: **0**
- Task candidates: **48**
- DST mapping: **48**
- Missing expected flags: **0** across all 4 docs
- OCR triggered: notice (11 373 chars), pieces_pc (6 863 chars)

## Guardrails
All zero. `cost_usd=0.00`. `prod_touched=false`.

## Reproduce
```bash
git checkout btp-engine-core-v3-real-regression-strict
pytest -q                                  # 50 passed
python scripts/run_engine.py \
  --inputs <path-to-4-pdfs> \
  --outputs ./outputs_strict_final
```

## Artifacts
See release directory:
`/mnt/documents/btp_engine_core_release_v3_strict/`
