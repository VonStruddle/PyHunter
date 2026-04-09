# Contributing to PyHunter

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test,dev]
```

## Quality checks

```bash
ruff check .
mypy pyhunter
pytest --cov=pyhunter --cov-report=term-missing
```

## Pull requests

- Keep the public sync API backward compatible unless the PR is explicitly marked breaking.
- Add tests for each bug fix or endpoint behavior change.
- Update `README.md` for user-visible changes.
- Add an entry to `CHANGELOG.md`.

## Release checklist

- Bump version in `pyproject.toml`.
- Ensure CI is green for all supported Python versions.
- Build and verify artifacts:
  - `python -m build`
  - `python -m twine check dist/*`
