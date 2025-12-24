# 📋 STAGE 1: Agent 1 (Parsing & Raw Extraction)

## Goal
Implement a deterministic, rule-based agent to extract raw text blocks from resumes (PDF/DOCX/TXT) and job postings without using NLP or AI.

## Tasks
- [ ] **Setup Project Structure**
    - [ ] Verify `requirements.txt` includes `pdfminer.six`, `python-docx`, `pymupdf`.
    - [ ] Create `src/agents/agent1_parser.py`.
- [ ] **Implement File Ingestion**
    - [ ] Create function to read PDF files (`extract_text_from_pdf`).
    - [ ] Create function to read DOCX files (`extract_text_from_docx`).
    - [ ] Create function to read TXT files.
- [ ] **Implement Raw Extraction Logic**
    - [ ] Implement regex/layout-based segmentation to identify sections (Header, Experience, Skills, Education).
    - [ ] **CRITICAL**: Ensure NO spaCy/NLTK/AI is used in this stage.
    - [ ] Output raw text blocks for each section.
- [ ] **Output Generation**
    - [ ] Save output as `data/processed/raw_profiles/{id}.json`.
    - [ ] JSON schema: `{"raw_text": "...", "sections": {"experience": "...", "skills": "..."}}`.

## Implementation Notes
- **Tech Stack**: Python, `pdfminer.six`/`pymupdf` (PDF), `python-docx` (DOCX), Regex.
- **Type**: Deterministic, Rule-based.
- **Integration**: Feeds raw text into Agent 2.

## Unit & Integration Testing
- [ ] **Unit Test 1**: Test PDF extraction on sample dummy PDF.
- [ ] **Unit Test 2**: Test DOCX extraction on sample dummy DOCX.
- [ ] **Unit Test 3**: Verify section segmentation regex on known resume formats.
- [ ] **Integration Test**: Run pipeline `File -> Agent 1 -> JSON Output`.

## Deliverables
- `src/agents/agent1_parser.py`
- `tests/test_agent1_parsing.py`
- Sample output JSONs in `data/processed/raw_profiles/`.

## Success Criteria
✅ Successfully reads PDF/DOCX files.
✅ Accurately segments >90% of standard resumes into raw sections.
✅ Output JSON matches defined schema.
✅ No NLP libraries imported.
