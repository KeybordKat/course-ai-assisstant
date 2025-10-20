# Test Recommendations for Course AI Assistant

## ✅ Current Test Coverage

### Existing Tests
1. **Installation Tests** (`scripts/test_install.py`)
   - Package imports
   - Ollama installation and models
   - Embeddings model
   - Web search (DuckDuckGo)

2. **System Tests** (`tests/test_system.py`)
   - Vector store operations
   - Embedding generation
   - Document processing
   - Agent functionality
   - Subject filtering
   - API endpoints (basic)
   - Integration test

## 🔧 Additional Tests You Should Create

### 1. **UI Tests** (High Priority)
**File:** `tests/test_ui.py`

Test the Streamlit UI components:
```python
- test_subject_selector_displays_correctly()
- test_web_search_toggle_works()
- test_conversation_history_persists()
- test_clear_conversation_button()
- test_citation_display()
- test_api_connection_status()
```

**Why:** Ensures the UI works correctly and handles edge cases.

### 2. **Performance Tests** (Medium Priority)
**File:** `tests/test_performance.py`

Measure system performance:
```python
- test_query_response_time()  # Should be < 60s
- test_embedding_speed()  # Time to embed 100 chunks
- test_vector_search_speed()  # Time to search database
- test_subject_filter_speedup()  # Filtered vs unfiltered
- test_memory_usage()  # Memory footprint
```

**Why:** Helps identify bottlenecks and regressions.

### 3. **Edge Case Tests** (High Priority)
**File:** `tests/test_edge_cases.py`

Test unusual inputs and scenarios:
```python
- test_empty_query()  # What happens with empty question?
- test_very_long_query()  # 1000+ character question
- test_special_characters()  # Unicode, emojis, etc.
- test_no_relevant_documents()  # Query about unrelated topic
- test_database_empty()  # No PDFs ingested
- test_malformed_pdf()  # Corrupted or password-protected PDF
- test_concurrent_requests()  # Multiple simultaneous queries
```

**Why:** Real-world users will do unexpected things.

### 4. **API Integration Tests** (Medium Priority)
**File:** `tests/test_api_integration.py`

Test full API workflows:
```python
- test_ask_question_endpoint_full_flow()
- test_subject_filtering_via_api()
- test_web_search_toggle_via_api()
- test_error_handling()  # 400, 500 responses
- test_rate_limiting()  # If implemented
- test_cors_headers()
```

**Why:** Ensures frontend-backend integration works.

### 5. **Document Ingestion Tests** (Medium Priority)
**File:** `tests/test_ingestion.py`

Test the document pipeline:
```python
- test_pdf_extraction()  # Can read various PDF formats
- test_chunking_quality()  # Chunks are reasonable size
- test_subject_detection()  # Folder structure → subject
- test_duplicate_detection()  # Same PDF not ingested twice
- test_large_pdf_handling()  # 500+ page PDF
- test_batch_processing()  # Multiple PDFs at once
```

**Why:** Data quality directly affects answer quality.

### 6. **Retrieval Quality Tests** (High Priority)
**File:** `tests/test_retrieval_quality.py`

Test that retrieval is accurate:
```python
- test_relevant_results_returned()  # Known questions
- test_subject_filter_accuracy()  # Only returns correct subject
- test_citation_accuracy()  # Citations match content
- test_relevance_scoring()  # Most relevant first
```

**Example test data:**
```python
KNOWN_QA_PAIRS = [
    ("What is a Turing machine?", "Languages & Theory of Computation"),
    ("What is propositional logic?", "LogicInComputerScience"),
]
```

**Why:** Measures how well the RAG system works.

### 7. **Security Tests** (Low-Medium Priority)
**File:** `tests/test_security.py`

Test security aspects:
```python
- test_no_sql_injection()  # Malicious queries
- test_no_path_traversal()  # ../../../etc/passwd
- test_prompt_injection()  # Malicious prompts to LLM
- test_rate_limiting()  # DOS protection
```

**Why:** Prevents abuse and attacks.

### 8. **Regression Tests** (Medium Priority)
**File:** `tests/test_regression.py`

Test known bugs don't reappear:
```python
- test_get_stats_shows_all_subjects()  # Bug you just fixed!
- test_second_pdf_stored()  # Bug from earlier
```

**Why:** Prevents old bugs from coming back.

## 📊 Test Organization Strategy

### Test Structure
```
tests/
├── test_system.py          # Core system tests ✅
├── test_ui.py              # UI component tests
├── test_performance.py     # Performance benchmarks
├── test_edge_cases.py      # Edge cases and errors
├── test_api_integration.py # Full API workflows
├── test_ingestion.py       # Document processing
├── test_retrieval_quality.py # RAG accuracy
├── test_security.py        # Security tests
├── test_regression.py      # Known bug prevention
└── fixtures/               # Test data
    ├── sample_pdfs/
    ├── known_qa_pairs.json
    └── test_queries.json
```

## 🚀 Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_system.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run performance tests:
```bash
pytest tests/test_performance.py -v --durations=10
```

## 🎯 Priority Recommendations

### Implement First (High Priority)
1. **Edge Case Tests** - Catch unexpected failures
2. **Retrieval Quality Tests** - Ensure accurate answers
3. **UI Tests** - User-facing functionality

### Implement Second (Medium Priority)
4. **Performance Tests** - Identify bottlenecks
5. **API Integration Tests** - Full workflows
6. **Document Ingestion Tests** - Data quality

### Implement Later (Lower Priority)
7. **Security Tests** - Important but not urgent for development
8. **Regression Tests** - Add as bugs are discovered

## 💡 Testing Best Practices

### 1. Use Fixtures for Common Setup
```python
@pytest.fixture
def sample_pdf():
    """Provide a sample PDF for testing."""
    return Path("tests/fixtures/sample.pdf")
```

### 2. Mock External Dependencies
```python
@pytest.fixture
def mock_ollama(monkeypatch):
    """Mock Ollama responses for faster tests."""
    def mock_invoke(prompt):
        return "Mocked response"
    monkeypatch.setattr(OllamaLLM, "invoke", mock_invoke)
```

### 3. Test Data
Create `tests/fixtures/known_qa_pairs.json`:
```json
{
  "theory": [
    {
      "question": "What is a finite automaton?",
      "expected_source": "Languages & Theory of Computation",
      "keywords": ["states", "transitions", "alphabet"]
    }
  ]
}
```

### 4. Continuous Integration
Add GitHub Actions workflow (`.github/workflows/test.yml`):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/ -v
```

## 📈 Measuring Test Quality

### Code Coverage
- Aim for 80%+ coverage on core components
- Use `pytest --cov` to measure

### Test Speed
- Unit tests: < 1s each
- Integration tests: < 10s each
- Full suite: < 5 minutes

### Test Maintenance
- Keep tests simple and readable
- Update tests when features change
- Delete obsolete tests

## 🔍 Monitoring Test Results

### What to Track
1. **Pass Rate** - Should be 100%
2. **Test Duration** - Watch for slowdowns
3. **Coverage** - Should increase over time
4. **Flaky Tests** - Tests that randomly fail

### When Tests Fail
1. Don't ignore failures!
2. Fix immediately or mark as known issue
3. Add regression test for the bug
4. Update documentation if needed

## 📝 Example Test Template

```python
def test_feature_name():
    """Test that [specific behavior] works correctly."""
    # Arrange - Set up test data
    input_data = "test input"

    # Act - Perform the action
    result = function_to_test(input_data)

    # Assert - Check results
    assert result == expected_output
    assert result.some_property == expected_value
```

## 🎓 Learning Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Testing Best Practices**: https://realpython.com/pytest-python-testing/
- **Mocking Guide**: https://docs.python.org/3/library/unittest.mock.html

---

**Remember:** Good tests catch bugs before users do! 🐛➡️✅
