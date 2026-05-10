# BTP Engine Core - Limites connues

## Limites techniques

### 1. Extraction de texte

#### PDF scannés
- **Limite** : Les PDF purement image sans couche texte nécessitent OCR
- **Impact** : Latence accrue, précision moindre
- **Mitigation** : OCR Tesseract en fallback
- **Amélioration future** : Tesseract optimisé, preprocessing d'image

#### PDF complexes
- **Limite** : Les PDF avec tableaux complexes, multi-colonnes, ou mise en page non standard peuvent avoir un texte extrait mal ordonné
- **Impact** : Classification et analyse potentiellement dégradées
- **Mitigation** : Nettoyage de texte, patterns robustes
- **Amélioration future** : Extraction layout-aware, segmentation intelligente

### 2. Classification

#### Ambiguïté documentaire
- **Limite** : Certains documents peuvent matcher plusieurs classes
- **Impact** : Confiance de classification réduite, alternatives nombreuses
- **Mitigation** : Système de priorité, seuils de confiance
- **Amélioration future** : Enrichissement des patterns, règles de désambiguïsation

#### Documents hybrides
- **Limite** : Un document peut contenir plusieurs types (ex: DDT avec plusieurs diagnostics)
- **Impact** : Classification unique ne capture pas la richesse
- **Mitigation** : Détection des alternatives, flags multiples
- **Amélioration future** : Classification multi-label, segmentation par section

#### Nouveaux types de documents
- **Limite** : Les types non couverts sont classés UNKNOWN
- **Impact** : Perte d'information métier
- **Mitigation** : Extension facile des patterns
- **Amélioration future** : Détection automatique de nouveaux patterns

### 3. Analyse

#### Patterns regex limités
- **Limite** : Les patterns regex ne capturent pas toutes les variations sémantiques
- **Impact** : Faux négatifs possibles (problème présent mais non détecté)
- **Mitigation** : Enrichissement continu des patterns
- **Amélioration future** : NLP local (sans API), embeddings locaux

#### Contexte local uniquement
- **Limite** : L'analyse ne croise pas les informations entre documents
- **Impact** : Manque de détection de cohérence inter-documents
- **Mitigation** : Règles de dépendances documentaires
- **Amélioration future** : Analyse cross-document, graphe de connaissance

#### Absence de validation métier externe
- **Limite** : Pas de vérification contre référentiel réglementaire externe
- **Impact** : Conformité non garantie
- **Mitigation** : Règles expert intégrées
- **Amélioration future** : Intégration référentiel réglementaire, API légifrance

### 4. Génération de tâches

#### Templates statiques
- **Limite** : Les templates sont prédéfinis et ne s'adaptent pas dynamiquement
- **Impact** : Descriptions potentiellement génériques
- **Mitigation** : Templates riches et détaillés
- **Amélioration future** : Templates dynamiques, génération contextuelle

#### Pas de priorisation intelligente
- **Limite** : Pas de score de priorité métier automatique
- **Impact** : Toutes les tâches ont le même poids
- **Mitigation** : Flags de criticité
- **Amélioration future** : Scoring de priorité, dépendances de tâches

### 5. DST Mapping

#### Mode dry-run uniquement
- **Limite** : Aucun push réel vers DST
- **Impact** : Nécessite action humaine pour finaliser
- **Mitigation** : Mapping préparé et validé
- **Amélioration future** : Mode push avec validation humaine

#### Mapping 1-to-1 simpliste
- **Limite** : Une classe = une famille FT
- **Impact** : Ne capture pas la granularité métier
- **Mitigation** : Règles de mapping explicites
- **Amélioration future** : Mapping multi-niveaux, sous-catégories

### 6. Validation baseline

#### Validation binaire
- **Limite** : PASS ou FAIL uniquement
- **Impact** : Pas de nuances dans la qualité
- **Mitigation** : Warnings pour nuances
- **Amélioration future** : Scoring continu, niveaux de qualité

#### Pas de validation croisée
- **Limite** : Chaque baseline validée indépendamment
- **Impact** : Pas de détection d'incohérences inter-baselines
- **Mitigation** : Règles de dépendances
- **Amélioration future** : Validation holistique, graphe de cohérence

### 7. Performance

#### OCR lent
- **Limite** : OCR Tesseract peut être lent sur gros volumes
- **Impact** : Latence élevée pour PDF scannés
- **Mitigation** : Traitement batch, parallélisation
- **Amélioration future** : OCR GPU, preprocessing optimisé

#### Pas de cache
- **Limite** : Pas de cache des résultats d'extraction/classification
- **Impact** : Retraitement complet à chaque run
- **Mitigation** : Architecture sans état
- **Amélioration future** : Cache avec invalidation, incremental processing

## Limites fonctionnelles

### 1. Pas d'IA générative

**Choix de design** : Mode déterministe strict

**Conséquences** :
- ✅ Coût = 0
- ✅ Latence prévisible
- ✅ Pas de dépendance API externe
- ✅ Traçabilité complète
- ❌ Pas de compréhension sémantique profonde
- ❌ Pas de génération de texte riche
- ❌ Pas d'adaptation dynamique

### 2. Pas d'accès DB

**Choix de design** : Fail-closed, lecture seule

**Conséquences** :
- ✅ Aucun risque d'écriture accidentelle
- ✅ Pas de corruption de données
- ❌ Pas de persistance automatique
- ❌ Pas de lookup en base

### 3. Pas de push DST automatique

**Choix de design** : Dry-run uniquement

**Conséquences** :
- ✅ Aucun risque de push erroné
- ✅ Validation humaine obligatoire
- ❌ Pas d'automatisation end-to-end

### 4. Pas d'accès PROD

**Choix de design** : Isolation stricte

**Conséquences** :
- ✅ Aucun risque sur environnement de production
- ❌ Pas de test en conditions réelles

## Limites de scope

### Documents non supportés

**Hors scope actuel** :
- Documents non-PDF (Word, Excel, Images JPEG/PNG standalone)
- Documents audio/vidéo
- Documents chiffrés/protégés par mot de passe
- Documents de plus de 1000 pages (non testé)

### Langues non supportées

**Scope actuel** : Français uniquement

**Langues hors scope** :
- Anglais
- Autres langues européennes
- Langues non-latines

### Domaines métier non couverts

**Scope actuel** : BTP résidentiel et tertiaire

**Hors scope** :
- BTP industriel spécialisé
- Ouvrages d'art
- Génie civil lourd
- Maritime/Aéronautique

## Recommandations d'utilisation

### ✅ Cas d'usage recommandés

1. **Pré-traitement batch de documents BTP**
   - Volume : 10-1000 documents
   - Type : PDF diagnostics, plans, notices
   - Objectif : Classification et extraction initiale

2. **Validation de complétude DDT**
   - Vérifier présence de tous les diagnostics requis
   - Identifier les documents manquants
   - Générer liste de tâches de complétion

3. **Détection de problèmes critiques**
   - Scan rapide de présence amiante/plomb
   - Identification des non-conformités électriques
   - Flagging pour revue humaine urgente

4. **Préparation de dossiers réglementaires**
   - Classification automatique des pièces
   - Vérification des dépendances
   - Export structuré pour archivage

### ❌ Cas d'usage non recommandés

1. **Remplacement de l'expertise humaine**
   - ❌ Ne remplace pas un diagnostiqueur
   - ❌ Ne remplace pas un architecte
   - ❌ Ne remplace pas un juriste

2. **Validation réglementaire finale**
   - ❌ Pas de garantie de conformité légale
   - ❌ Pas de responsabilité juridique
   - ❌ Validation humaine toujours requise

3. **Traitement temps-réel critique**
   - ❌ Latence OCR variable
   - ❌ Pas d'optimisation temps-réel
   - ❌ Préférer batch asynchrone

4. **Documents non-BTP**
   - ❌ Patterns BTP-spécifiques
   - ❌ Taxonomie BTP uniquement
   - ❌ Pas de généralisation hors domaine

## Roadmap des améliorations

### Court terme (1-3 mois)
- [ ] Enrichissement patterns de classification
- [ ] Ajout de nouveaux types de documents
- [ ] Optimisation OCR
- [ ] Cache d'extraction
- [ ] Parallélisation batch

### Moyen terme (3-6 mois)
- [ ] NLP local pour analyse sémantique
- [ ] Classification multi-label
- [ ] Analyse cross-document
- [ ] Scoring de priorité
- [ ] API REST

### Long terme (6-12 mois)
- [ ] Intégration référentiel réglementaire
- [ ] Graphe de connaissance BTP
- [ ] Mode push DST avec validation
- [ ] Support multi-langues
- [ ] Support documents non-PDF
