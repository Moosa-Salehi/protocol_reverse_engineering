# Contributing to Protocol Reverse Engineering

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run tests (when available)
6. Commit with clear messages
7. Push and create a pull request

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and modular
- Use meaningful variable names

## Adding New Features

### Adding a New Pipeline Stage

1. Create script in `scripts/XX_stage_name.py`
2. Implement logic in appropriate `src/protocol_re/` module
3. Update `main.py` to call the new stage
4. Add output artifact documentation
5. Update schemas if needed
6. Add tests
7. Update documentation

### Adding a New Feature Mode

1. Implement feature extractor in `src/protocol_re/clustering/`
2. Add mode to `scripts/04_discover_families.py`
3. Update documentation
4. Add tests
5. Update README with usage examples

### Adding a New Semantic Role

1. Update taxonomy in `src/protocol_re/inference/semantic_labeling.py`
2. Add detection logic
3. Update `schema/protocol_model.schema.json`
4. Update exporters to handle new role
5. Add tests

## Testing

### Running Tests

```bash
# Set Python path
export PYTHONPATH=src

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_logging.py

# Run with coverage
pytest --cov=src/protocol_re tests/
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Include docstrings explaining what is tested
- Use fixtures for common setup

Example:
```python
def test_boundary_detection_basic():
    """Test basic boundary detection on simple messages."""
    messages = create_test_messages()
    boundaries = detect_boundaries(messages)
    assert len(boundaries) > 0
    assert boundaries[0].offset == 0
```

## Updating Documentation

- Update relevant `.md` files in `docs/`
- Keep README.md in sync with major changes
- Update docstrings in code
- Add examples for new features
- Update architecture diagrams if needed

## Pull Request Process

1. **Update documentation** - Document new features or changes
2. **Add tests** - Include tests for new functionality
3. **Update CHANGELOG** - Add entry describing changes
4. **Check code style** - Ensure PEP 8 compliance
5. **Run tests** - Verify all tests pass
6. **Update README** - If adding major features
7. **Create Pull Request** - With clear description and examples

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify with latest version
3. Collect diagnostic information

### Bug Report Template

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- TShark version: [e.g., 4.2.2]
- Package version: [e.g., 1.0.0]

## Additional Context
- Error messages
- Log files
- PCAP characteristics
- Configuration used
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing!
