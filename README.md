# Bananalyzer

Bananalyzer is a local Python project foundation for our AI Companion.

## Local Operations

This is a personal local MVP. To run automation:
If your virtual environment (`.venv`) is activated:
* Run tests: `pytest`
* Run quality checks: `ruff check .`

If your virtual environment is NOT activated:
* Run tests: `uv run pytest`
* Run quality checks: `uv run ruff check .`

> [!NOTE]
> **CI/CD Scope**
> Mandatory remote CI/CD pipelines are out of scope for this MVP. CI/CD is optional and should only be added post-MVP if Ryan specifically requests it.
