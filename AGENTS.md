# AGENTS.md

Agent-focused technical documentation for the schellma project.

> **Note**: This file is designed for AI coding agents. For human-readable documentation, see [README.md](README.md).

## Project Overview

**schellma** is a Python package that converts Pydantic models and JSON Schemas to clean, simplified type definitions optimized for LLM prompts. The project emphasizes token efficiency, readability, and comprehensive type support.

- **Language**: Python 3.11+
- **Package Manager**: `uv`
- **Key Dependencies**: Pydantic 2.0+
- **Build System**: Hatchling
- **Type Checking**: mypy (strict mode)
- **Linting/Formatting**: Ruff
- **Testing**: pytest

## Environment Setup

### Prerequisites
- Python 3.11, 3.12, or 3.13
- `uv` package manager installed (recommended)

### Initial Setup
```bash
# Clone and enter project directory (if needed)
git clone https://github.com/andrader/schellma.git
cd schellma

# Install all dependencies including dev tools
uv sync --dev

# Activate virtual environment (if needed)
source .venv/bin/activate
```

**Important**: Always use `uv run` or `.venv/bin/python` to execute commands within the project context.

## Development Commands

### Running Code
```bash
# Run any Python script
uv run python script.py

# Run the module directly
uv run python -m schellma
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_advanced_arrays.py

# Run with verbose output
uv run pytest -v

# Run specific test by name
uv run pytest tests/test_examples.py::test_enum_support
```

### Type Checking
```bash
# Type check the main source
uv run mypy src/schellma/

# Type check specific file
uv run mypy src/schellma/converters.py
```

### Linting and Formatting
```bash
# Check for linting issues
uv run ruff check src/schellma/

# Auto-fix linting issues
uv run ruff check src/schellma/ --fix

# Format code
uv run ruff format src/schellma/

# Check formatting without changes
uv run ruff format src/schellma/ --check
```

### Building and Publishing
```bash
# Build distribution packages
uv run python -m build

# Check distribution
uv run twine check dist/*

# Upload to PyPI (requires credentials)
uv run twine upload dist/*
```

### Documentation
```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

## Dependency Management

### Adding Dependencies
```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Sync dependencies from pyproject.toml
uv sync
```

## Code Conventions

### File Structure
```
src/schellma/
├── __init__.py         # Package exports and version
├── converters.py       # Core conversion logic
├── constants.py        # Constants and type mappings
├── exceptions.py       # Custom exception classes
├── logger.py           # Logging configuration
├── utils.py            # Utility functions
└── py.typed            # PEP 561 marker for type hints
```

### Coding Standards

#### Type Hints
- **Mandatory**: All functions must have complete type hints
- Use modern syntax: `list[str]` not `List[str]`
- Use `str | None` not `Optional[str]` or `Union[str, None]`
- All module-level code must pass `mypy --strict`

#### Formatting
- Line length: 88 characters (Black-compatible)
- Quote style: Double quotes
- Indentation: 4 spaces
- Follow Ruff configuration in `ruff.toml`

#### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Private members: `_leading_underscore`

#### Imports
- Group imports: stdlib, third-party, local
- Sort alphabetically within groups
- Use absolute imports

#### Docstrings
- Use Google-style docstrings
- Document all public functions, classes, and modules
- Include examples where appropriate

### Error Handling
- Use custom exceptions from `schellma.exceptions`:
  - `SchellmaError`: Base exception
  - `InvalidSchemaError`: Schema validation errors
  - `ConversionError`: Conversion failures
- Always provide descriptive error messages
- Use logging for debugging information

### Testing Standards
- Test files: `test_*.py` in `tests/` directory
- Test functions: `test_*` naming convention
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Aim for high code coverage

## Key Modules

### `converters.py`
Main conversion logic. Key functions:
- `schellma()`: Primary public API, alias for `pydantic_to_schellma()`
- `pydantic_to_schellma()`: Convert Pydantic models to schellma format
- `json_schema_to_schellma()`: Convert JSON Schema to schellma format

### `constants.py`
Type mappings and configuration:
- `TYPE_MAP`: Maps JSON Schema types to schellma types
- `INDENTATION`: Default indentation settings

### `exceptions.py`
Custom exceptions for error handling

### `logger.py`
Logging configuration and utilities

### `utils.py`
Helper functions and utilities

## Common Patterns

### Adding a New Feature
1. Write tests first in `tests/test_*.py`
2. Implement feature in appropriate module
3. Update type hints and docstrings
4. Run `uv run pytest` to verify tests pass
5. Run `uv run mypy src/schellma/` for type checking
6. Run `uv run ruff format src/schellma/` to format
7. Run `uv run ruff check src/schellma/` to lint
8. Update documentation if needed

### Handling JSON Schema Types
When adding support for new JSON Schema constructs:
1. Add mapping in `constants.py` if needed
2. Implement conversion logic in `converters.py`
3. Add comprehensive tests in `tests/`
4. Document behavior in docstrings

### Working with Pydantic Models
- Use Pydantic 2.0+ API exclusively
- Access schema via `model.model_json_schema()`
- Handle both `BaseModel` and `TypeAdapter` inputs

## Testing Strategy

### Test Categories
- `test_examples.py`: Basic usage examples
- `test_type_annotations.py`: Type annotation handling
- `test_advanced_arrays.py`: Array and collection types
- `test_advanced_unions.py`: Union type handling
- `test_constraints.py`: Field constraints (min/max, patterns)
- `test_default_values.py`: Default value handling
- `test_required_optional.py`: Required/optional field logic
- `test_error_handling.py`: Exception scenarios
- `test_indentation.py`: Output formatting
- `test_nested_indentation.py`: Nested structure formatting
- `test_logging.py`: Logging functionality

### Running Specific Test Suites
```bash
# Test all type annotations
uv run pytest tests/test_type_annotations.py

# Test error handling
uv run pytest tests/test_error_handling.py

# Test with coverage
uv run pytest --cov=schellma --cov-report=html
```

## Version Management

- Version specified in: `pyproject.toml` and `src/schellma/__init__.py`
- Version scheme: Semantic Versioning 2.0 (SemVer2)
- Managed via: Commitizen (`cz bump`)

### Updating Version
```bash
# Bump version automatically based on commits
uv run cz bump

# Manual version update (update both files)
# 1. pyproject.toml: [project] version = "X.Y.Z"
# 2. src/schellma/__init__.py: __version__ = "X.Y.Z"
```

## Pre-commit Hooks

The project uses pre-commit for automated checks:
```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

## Troubleshooting

### Common Issues

**Import errors when running tests**
```bash
# Ensure dependencies are synced
uv sync --dev
```

**Type checking failures**
```bash
# Check mypy configuration in mypy.ini
# Ensure all functions have type hints
uv run mypy src/schellma/ --show-error-codes
```

**Ruff linting errors**
```bash
# Auto-fix most issues
uv run ruff check src/schellma/ --fix
```

**Tests failing**
```bash
# Run with verbose output to see details
uv run pytest -v -s
```

## CI/CD Considerations

- All tests must pass before merging
- Type checking must pass (mypy)
- Linting must pass (ruff)
- Code must be formatted (ruff format)
- Minimum Python version: 3.11

## Output Format

schellma generates TypeScript-like syntax:
- Objects: `{ "key": type, ... }`
- Arrays: `type[]`
- Unions: `type1 | type2`
- Nullable: `type | null`
- Enums: `"value1" | "value2"`
- Type definitions: `TypeName { ... }`

## Performance Considerations

- Token efficiency is a primary goal
- Avoid unnecessary whitespace in compact mode
- Cache type definitions when possible
- Handle circular references to prevent infinite loops

## Links to External Documentation

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema Specification](https://json-schema.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)

