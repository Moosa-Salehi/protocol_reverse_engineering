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

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd protocol_re

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt

# Set Python path
export PYTHONPATH=src
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and modular
- Use meaningful variable names

## Project Structure

```
src/protocol_re/
├── clustering/       # Message family discovery
├── corpus/          # Message corpus management
├── evaluation/      # Quality metrics
├── export/          # Report generation
├── features/        # Feature extraction
├── inference/       # Structure inference
├── llm/             # LLM integration
├── model/           # Protocol model
└── utils/           # Utility functions
```

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
pytest tests/test_clustering.py

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

## Documentation

### Updating Documentation

- Update relevant `.md` files in `docs/`
- Keep README.md in sync with major changes
- Update docstrings in code
- Add examples for new features
- Update architecture diagrams if needed

### Documentation Structure

- `docs/getting_started.md` - Installation and quick start
- `docs/how_to_use.md` - Comprehensive usage guide
- `docs/architecture.md` - System design
- `docs/api_reference.md` - Module documentation
- `docs/examples.md` - Protocol-specific examples

### Building Documentation

```bash
# Install MkDocs
pip install mkdocs mkdocs-material mkdocstrings

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

**Examples:**
```
feat(clustering): add adaptive fusion for hybrid features

Implement adaptive fusion method that automatically weights
neural and structural features based on quality metrics.

Closes #123
```

```
fix(boundaries): reduce over-segmentation in enhanced mode

Add anti-fragmentation penalties and multi-pass merging
to reduce false positive boundaries.

Fixes #456
```

## Pull Request Process

1. **Update documentation** - Document new features or changes
2. **Add tests** - Include tests for new functionality
3. **Update CHANGELOG** - Add entry describing changes
4. **Check code style** - Ensure PEP 8 compliance
5. **Run tests** - Verify all tests pass
6. **Update README** - If adding major features
7. **Create PR** - With clear description and examples

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] CHANGELOG updated
```

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

**Review criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Backward compatibility

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

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches considered

## Additional Context
Examples, mockups, references
```

## Development Priorities

See [TODO_COMPREHENSIVE.md](../TODO_COMPREHENSIVE.md) for current priorities:

**Priority 1: Accuracy Improvements**
- Improved semantic labeling (A3)
- Relation false positive reduction (A4)

**Priority 2: Runtime Optimizations**
- Incremental processing (B2)
- Neural model optimization (B3)

**Priority 3: Code Quality**
- Comprehensive unit tests (C1)
- Error handling improvements (C2)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar questions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing! 🎉
