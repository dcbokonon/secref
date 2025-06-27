# SecRef Test Suite

Comprehensive testing suite for the SecRef cybersecurity resource database system.

## Overview

The test suite covers all aspects of the SecRef system:
- Database operations and integrity
- API endpoints and business logic
- UI components and interactions
- Full integration workflows

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── test_database.py         # Database and schema tests
├── test_api.py              # Flask API endpoint tests
├── test_ui.py               # UI/Frontend component tests
├── test_integration.py      # Full system integration tests
├── requirements.txt         # Test dependencies
└── README.md               # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test module
python run_tests.py test_database

# Run with coverage
python run_tests.py -c

# Run with pytest directly
pytest

# Run specific test file
pytest tests/test_api.py -v
```

### Test Options

- `-v, --verbose`: Detailed test output
- `-q, --quiet`: Minimal output
- `-c, --coverage`: Generate coverage report

### Using pytest

```bash
# Run all tests with coverage
pytest --cov=scripts --cov=admin

# Run tests matching a pattern
pytest -k "test_sync"

# Run tests with specific marker
pytest -m unit
pytest -m integration

# Generate HTML coverage report
pytest --cov-report=html
```

## Test Categories

### Unit Tests
Fast, isolated tests for individual components:
- Database schema validation
- Import/export functions
- Data validation logic
- Utility functions

### API Tests
Tests for all Flask endpoints:
- Resource CRUD operations
- Search and filtering
- Category management
- Sync status detection
- Health monitoring

### UI Tests
Frontend component validation:
- HTML structure verification
- JavaScript function existence
- Form validation logic
- Modal interactions
- Bulk operations UI

### Integration Tests
End-to-end workflow testing:
- Full import → modify → export cycle
- Sync detection and resolution
- Category management workflows
- Health dashboard accuracy
- Audit trail verification

## Test Data

Tests use temporary databases and JSON files to ensure isolation:
- SQLite in-memory databases for speed
- Temporary directories for file operations
- Comprehensive test fixtures with realistic data

## Coverage Goals

Current coverage targets:
- Database operations: 95%+
- API endpoints: 90%+
- Business logic: 90%+
- UI components: 80%+

View coverage reports:
- Terminal: Run with `-c` flag
- HTML: Open `tests/coverage_html/index.html`

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.8-3.11)

See `.github/workflows/test.yml` for CI configuration.

## Writing New Tests

### Test Structure

```python
import unittest
from tests.fixtures import create_test_data

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_data = create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        cleanup_test_data()
    
    def test_feature_behavior(self):
        """Test specific behavior"""
        result = feature_function(self.test_data)
        self.assertEqual(result, expected_value)
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive test names
3. **Cleanup**: Always clean up test data
4. **Assertions**: Use specific assertions
5. **Mocking**: Mock external dependencies

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Database Errors**: Check SECREF_DB_PATH environment variable
3. **Permission Errors**: Ensure write access to temp directories
4. **Coverage Missing**: Install coverage with `pip install coverage`

### Debug Mode

```bash
# Run tests with Python debugger
python -m pdb run_tests.py

# Run single test with verbose output
pytest tests/test_api.py::TestAPI::test_get_resources -vv
```

## Future Improvements

- [ ] Add Selenium tests for full UI testing
- [ ] Implement performance benchmarks
- [ ] Add mutation testing
- [ ] Create test data factories
- [ ] Add API contract tests
- [ ] Implement load testing