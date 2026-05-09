# BTP Engine Core - Architecture

## Vue d'ensemble

BTP Engine Core est un moteur backend déterministe pour le traitement de documents BTP (Bâtiment et Travaux Publics).

## Principes fondamentaux

### 1. Déterminisme strict
- **Aucun appel IA externe** : Pas d'OpenAI, GPT, Gemini, Vision API, Lovable Gateway
- **Aucune écriture DB** : Mode lecture seule
- **Aucun push DST** : Mapping en dry-run uniquement
- **Aucun accès PROD** : Fail-closed par défaut
- **Coût = 0 USD** : Budget maximum hard-coded à 0

### 2. Fail-closed guardrails
Tous les guardrails sont configurés en mode fail-closed :
- Si une opération interdite est tentée, une `GuardrailViolation` est levée
- Aucun override possible de la configuration
- Configuration hard-coded dans `safety_checks.py`

### 3. Traçabilité complète
- Toutes les opérations sont enregistrées dans le `CostTracker`
- Toutes les sources et evidences sont conservées
- Aucune tâche ne peut être validée sans source et evidence

## Architecture modulaire

```
btp_engine/
├── guardrails/          # Sécurité et guardrails fail-closed
│   ├── safety_checks.py  # Vérificateur de sécurité
│   ├── cost_tracker.py   # Tracker de coûts
│   └── exceptions.py     # Exceptions métier
│
├── extraction/          # Extraction de données
│   ├── pdf_to_text.py    # Extraction texte natif PDF
│   ├── ocr_tesseract.py  # OCR local Tesseract
│   └── text_cleaner.py   # Nettoyage de texte
│
├── classification/      # Classification déterministe
│   ├── document_classifier.py  # Classifieur principal
│   ├── class_patterns.py       # Patterns de classification
│   └── class_priority.py       # Priorités de classes
│
├── analysis/            # Analyse expert BTP
│   ├── problem_detector.py  # Détection de problèmes
│   ├── flag_detector.py     # Détection de flags métier
│   └── expert_rules.py      # Règles métier expert
│
├── tasks/               # Génération de tâches
│   ├── task_generator.py   # Générateur de tâches
│   ├── task_templates.py   # Templates de tâches
│   └── task_merger.py      # Fusion et déduplication
│
├── dst/                 # Mapping DST (dry-run)
│   ├── dst_mapper.py       # Mapper DST
│   └── dst_rules.py        # Règles de mapping
│
├── scoring/             # Scoring et validation
│   ├── quality_scorer.py      # Scoring qualité
│   └── baseline_validator.py  # Validation baseline stricte
│
└── reporting/           # Génération de rapports
    ├── json_reporter.py      # Export JSON
    ├── csv_reporter.py       # Export CSV UTF-8-SIG
    └── markdown_reporter.py  # Export Markdown
```

## Pipeline de traitement

1. **Extraction** : Extraction du texte depuis PDF (natif ou OCR)
2. **Classification** : Classification déterministe par patterns regex
3. **Analyse** : Détection de problèmes et flags métier
4. **Génération de tâches** : Création de tâches actionnables
5. **Mapping DST** : Mapping vers familles FT (dry-run uniquement)
6. **Validation** : Validation baseline stricte (source + evidence)
7. **Reporting** : Export JSON, CSV, Markdown

## Garanties de sécurité

### Guardrails actifs
- `OPENAI_ENABLED = False`
- `GPT_ENABLED = False`
- `GEMINI_ENABLED = False`
- `VISION_API_ENABLED = False`
- `LOVABLE_GATEWAY_ENABLED = False`
- `DB_WRITES_ENABLED = False`
- `DST_PUSH_ENABLED = False`
- `PROD_ACCESS_ENABLED = False`
- `MAX_COST_USD = 0.0`

### Validation stricte
Le `BaselineValidator` refuse :
- Toute tâche sans source
- Toute tâche sans evidence
- Toute classe source incompatible
- Toute document presence baseline sans SHA256 ou filename

## Performance

### Mode déterministe
- Pas d'appel réseau externe
- Pas d'attente API
- Traitement local uniquement
- Latence prévisible

### Scalabilité
- Traitement batch supporté
- Parallélisation possible
- Pas de limite de quota externe

## Conformité réglementaire

Le moteur supporte les classes de documents BTP suivantes :
- Diagnostics techniques (DPE, Amiante, Plomb, Électrique, Termites, Assainissement)
- Sécurité (Incendie, Habitation)
- Urbanisme (PC, Plans, CERFA)
- Risques (ERP, Insalubrité)
- Administration (Courriers, DDT)

## Extensibilité

### Ajout de nouvelles classes
1. Ajouter la classe dans `class_patterns.py`
2. Définir les patterns regex
3. Définir la priorité dans `class_priority.py`
4. Ajouter le mapping DST dans `dst_rules.py`

### Ajout de nouveaux flags
1. Ajouter le flag dans `flag_detector.py`
2. Définir les patterns de détection
3. Définir les règles d'inférence

### Ajout de nouvelles règles métier
1. Enrichir `expert_rules.py`
2. Ajouter les dépendances documentaires
3. Définir les niveaux de criticité
