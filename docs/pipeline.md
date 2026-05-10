# BTP Engine Pipeline

## Processing Pipeline

### 1. Input Stage
- Document received (PDF, image, text)
- Safety checks performed
- Cost tracking initialized

### 2. Extraction Stage
- PDF text extraction using pdfplumber
- OCR fallback for scanned documents
- Text cleaning and normalization

### 3. Classification Stage
- Pattern-based classification
- Confidence scoring
- Priority assignment

### 4. Analysis Stage
- Problem detection using expert rules
- Flag detection
- Severity assessment

### 5. Task Generation Stage
- Template-based task generation
- Problem-derived tasks
- Priority sorting

### 6. DST Mapping Stage
- Document structure mapping
- Completeness assessment
- Missing section detection

### 7. Scoring Stage
- Extraction quality scoring
- Classification confidence scoring
- Overall quality calculation

### 8. Validation Stage
- Baseline validation
- Threshold checking
- Pass/fail determination

### 9. Reporting Stage
- Multi-format report generation
- JSON, CSV, Markdown outputs
- Customizable templates

## Error Handling

All stages include error handling with appropriate exceptions and rollback mechanisms.