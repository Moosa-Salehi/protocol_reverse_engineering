# Documentation

This directory contains comprehensive documentation for the Protocol Reverse Engineering pipeline.

## Documentation Structure

- **[index.md](index.md)** - Documentation homepage and overview
- **[getting_started.md](getting_started.md)** - Installation and quick start guide
- **[how_to_use.md](how_to_use.md)** - Comprehensive usage guide with examples
- **[architecture.md](architecture.md)** - System design and components
- **[testing.md](testing.md)** - Testing guide and practices
- **[contributing.md](contributing.md)** - Contribution guidelines

## Building Documentation

This project uses [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

### Install MkDocs

```bash
pip install mkdocs mkdocs-material mkdocstrings mkdocstrings-python
``` 

### Serve Locally

```bash
# From project root
mkdocs serve

# Open browser to http://127.0.0.1:8000
``` 

### Build Static Site

```bash
# From project root
mkdocs build

# Output in site/ directory
```

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## Documentation Guidelines

### Writing Style
 
- Use clear, concise language
- Include code examples for features
- Add command-line examples with expected output
- Use admonitions for warnings and tips
- Keep sections focused and scannable

### Code Examples

Use fenced code blocks with language specification:

````markdown
```bash
python main.py pcaps/ --tshark-filter mbtcp
```

```python
from protocol_re.clustering import discover_families
families = discover_families(messages)
```
````

### Admonitions

Use admonitions for important information:

```markdown
!!! note
    This is a note with additional information.

!!! warning
    This is a warning about potential issues.

!!! tip
    This is a helpful tip for users.
```

### Links

- Use relative links for internal documentation
- Use absolute URLs for external resources
- Make link text descriptive

```markdown
See [Architecture](architecture.md) for system design.
Visit [MkDocs](https://www.mkdocs.org/) for more information.
```

## Updating Documentation

When making changes:

1. Update relevant documentation files
2. Test locally with `mkdocs serve`
3. Verify all links work
4. Check code examples are correct
5. Update navigation in `mkdocs.yml` if needed
6. Commit with descriptive message

## Documentation TODO

- [ ] Add API reference with module documentation
- [ ] Add examples.md with protocol-specific guides
- [ ] Add troubleshooting.md with common issues
- [ ] Add pipeline_stages.md with detailed stage descriptions
- [ ] Add feature_modes.md with feature mode comparisons
- [ ] Add schemas.md with JSON schema documentation
- [ ] Add roadmap.md based on TODO_COMPREHENSIVE.md
- [ ] Generate API docs from docstrings using mkdocstrings

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [MkDocstrings](https://mkdocstrings.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)