# uv Setup Guide

`uv` is the package manager for this project. It replaces `pip` + `venv` and is significantly faster.

---

## Install uv

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal or run:
```bash
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS with zsh
```

Verify:
```bash
uv --version
```

---

## Core Commands

### Install all dependencies
```bash
uv sync
```

Reads `pyproject.toml` and `uv.lock`, creates `.venv/`, and installs everything. Run this after cloning or after pulling updates.

### Run a script
```bash
uv run python src/bot.py
uv run python scripts/populate_db.py
```

This automatically uses the project's virtual environment — no need to activate it manually.

### Add a new dependency
```bash
uv add package-name
# Example:
uv add httpx
```

This updates `pyproject.toml` and `uv.lock`.

### Remove a dependency
```bash
uv remove package-name
```

### Update dependencies
```bash
uv sync --upgrade
```

---

## Why uv?

- **Fast** — dependency resolution is 10–100× faster than pip
- **Reproducible** — `uv.lock` pins exact versions for everyone
- **No manual venv** — `uv sync` handles it
- **Python version management** — `uv python install 3.12`
- **`pyproject.toml` native** — no separate `requirements.txt`

---

## Project Python Version

The project requires Python 3.12+. The `.python-version` file pins this:

```
3.12
```

If you don't have 3.12, uv can install it:
```bash
uv python install 3.12
uv sync  # will use 3.12 automatically
```

---

## Common Issues

### `uv: command not found`
The install didn't add uv to your PATH. Add it manually:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
Add this line to your `~/.bashrc` or `~/.zshrc` for persistence.

### `.venv` conflicts
If you have a stale virtual environment:
```bash
rm -rf .venv
uv sync
```

### `python-telegram-bot` job queue warning
If you see:
```
WARNING - No job queue. Reminders will not run.
```
Install the scheduler extra:
```bash
uv add "python-telegram-bot[job-queue]"
```
Check `pyproject.toml` — this should already be included.

---

## Makefile Integration

The Makefile uses `uv run` for all Python invocations:

```makefile
start:
    uv run python src/bot.py

populate:
    uv run python scripts/populate_db.py

test:
    uv run python scripts/test_setup.py
```

This means `make start` always uses the correct Python + environment.
