# BTP Engine Core

**Moteur canonique de traitement documentaire BTP pour MyHome**

## Vue d'ensemble

BTP Engine Core est le moteur backend de traitement intelligent des documents de chantier pour l'écosystème MyHome. Il transforme des documents bruts (PDF, images) en insights actionnables, tâches candidates et mappings DST.

## Pipeline de traitement

```
PDF/ZIP inputs
    ↓
Extraction texte native (pdftotext/pdfplumber)
    ↓
OCR local Tesseract (si nécessaire)
    ↓
Classification documentaire
    ↓
Détection problèmes/constats/contraintes
    ↓
Préconisations expert BTP
    ↓
Génération task_candidates
    ↓
Mapping DST Chantier (dry-run)
    ↓
Scoring qualité
    ↓
Baseline resolver strict
    ↓
Rapports (JSON/CSV UTF-8-SIG/Markdown)
```

## Architecture

```
src/btp_engine/
├── extraction/       # Extraction texte PDF + OCR local
├── classification/   # Classification documentaire (EDL, DPE, Diagnostics, Plans...)
├── analysis/         # Détection problèmes + flags expert
├── tasks/           # Génération task_candidates
├── dst/             # Mapping DST dry-run
├── scoring/         # Scoring qualité + baseline validator
├── guardrails/      # Guardrails fail-closed + cost tracking
└── reporting/       # Rapports JSON/CSV/MD
```

## Guardrails absolus

Le moteur respecte des guardrails **fail-closed** stricts :

- ❌ **Aucun appel GPT/OpenAI/Gemini/Vision**
- ❌ **Aucune écriture base de données**
- ❌ **Aucun push DST production**
- ❌ **Aucun accès PROD**
- ✅ **Coût total garanti : $0.00**

Toute tentative de violation lève une `GuardrailViolation`.

## Classes documentaires supportées

- EDL (État des lieux avant/après projet)
- Notices sécurité (incendie, habitation)
- DPE (Diagnostic Performance Énergétique)
- DDT (Documents Techniques)
- Diagnostics réglementaires (CREP plomb, DTA amiante, électrique, termites, assainissement)
- ERP (États des Risques et Pollutions)
- Arrêtés insalubrité
- PC (Permis de Construire) + plans
- Courriers administratifs

## Expert flags

Le moteur détecte automatiquement les besoins expert :

- `needs_ABF` : Architecte des Bâtiments de France
- `needs_BET` : Bureau d'Études Techniques
- `needs_diagnostic` : Diagnostic complémentaire
- `needs_plomb`, `needs_amiante` : Traitement matériaux dangereux
- `needs_electricien_qualifie` : Mise en conformité électrique
- `needs_securite_incendie` : Système sécurité incendie
- `needs_insalubrite` : Traitement insalubrité
- `patrimoine_sensitive` : Patrimoine protégé
- `regulatory_required` : Conformité réglementaire
- `human_review_required` : Validation humaine obligatoire

## Baseline validator strict

Le moteur implémente un **baseline resolver strict** inspiré du projet Gambetta :

- ✅ Distinction `TASK_BASELINE` vs `DOCUMENT_PRESENCE_BASELINE`
- ✅ Pas de PASS sans source documentaire
- ✅ Pas de PASS sans evidence textuelle
- ✅ Pas de source incompatible (ex: DPE ne prouve pas une façade)
- ✅ Trigger groups AND-of-OR
- ✅ Document presence via filename + class + sha256
- ✅ Consistency check unique source of truth

## Installation

```bash
# Cloner le repo
git clone https://github.com/phippsou-dev/btp-engine-core.git
cd btp-engine-core

# Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt

# Installer Tesseract (pour OCR local)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-fra poppler-utils

# macOS:
brew install tesseract tesseract-lang poppler

# Windows: télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki
```

## Utilisation

```bash
# Traiter des documents
python scripts/run_engine.py \
  --input /path/to/documents \
  --output /path/to/output \
  --dry-run

# Avec ZIP
python scripts/run_engine.py \
  --input project.zip \
  --output ./results \
  --dry-run
```

## Sorties produites

- `inventory.json` : Inventaire fichiers
- `extraction_report.json` : Résultats extraction
- `classification_report.json` : Classes détectées
- `problems.json` : Problèmes identifiés
- `candidate_tasks.json` : Tâches candidates
- `candidate_tasks.csv` : Export CSV UTF-8-SIG
- `dst_mapping_report.json` : Mapping DST (dry-run)
- `quality_score.json` : Scores qualité
- `final_report.md` : Synthèse Markdown
- `guardrails_report.json` : Rapport guardrails

## Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=src/btp_engine --cov-report=html
```

Coverage minimum attendu : **80%**

## Familles DST supportées

- FT01 : Pilotage & autorisations
- FT02 : Études & diagnostics
- FT03 : Curage & dépose
- FT06 : Structure & gros œuvre
- FT10 : Étanchéité
- FT11 : Façades
- FT13 : Menuiseries extérieures
- FT14 : Serrurerie & garde-corps
- FT16 : Cloisons & plafonds
- FT18 : Escaliers
- FT22 : Peinture
- FT23 : Plomberie
- FT24 : CVC & ECS chauffage
- FT25 : Ventilation
- FT26 : Électricité CFO
- FT27 : Courants faibles & SSI
- FT28 : Cuisines
- FT30 : Verrières & aménagements spéciaux
- PLAN_REFERENCE

## Intégration MyHome

Le moteur s'intègre dans l'écosystème MyHome :

1. **Upload documents** → Lovable UI
2. **Stockage** → Supabase Storage
3. **Traitement** → BTP Engine Core (ce repo)
4. **Validation** → Interface admin Lovable
5. **Push DST** → API DST Chantier (après validation humaine)

## Limitations connues

- OCR local (pas de Vision API) : précision limitée sur documents dégradés
- Classification par patterns : pas de ML supervisé
- Dry-run DST seulement : pas de push automatique
- Pas de traitement temps réel : batch processing

## Roadmap

- [ ] Support images directes (JPG/PNG)
- [ ] Amélioration patterns classification
- [ ] Export Excel
- [ ] API REST FastAPI
- [ ] Mode watch filesystem
- [ ] Intégration Supabase Edge Functions

## Documentation

- [Architecture](docs/architecture.md)
- [Pipeline détaillé](docs/pipeline.md)
- [Intégration Lovable](docs/integration_lovable.md)
- [Limites connues](docs/known_limits.md)

## Sécurité

- ✅ Aucun secret en clair
- ✅ Pas d'appel API externe non autorisé
- ✅ Traitement local uniquement
- ✅ Guardrails fail-closed
- ✅ Audit logs complets

## License

Propriétaire - MyHome

## Contact

MyHome Team
