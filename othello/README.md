# Othello Game - Developer Guide

This guide is for developers who want to contribute to the project. (there might be at least one of them we are almost 8 billions on earth)

## Development Setup

### 1. Prerequisites

Install the system dependencies as described in the user README, plus:

**Debian/Ubuntu (externally-managed default python installation):**
```bash
apt install python3-venv python3-pip
```
Non externally-managed distributions (shouldn't be needed but we never know):
```bash
python -m ensurepip --upgrade
python -mpip install venv
```

### 2. Development Installation

1. Clone the repository:
```bash
git clone git@gitlab.emi.u-bordeaux.fr:pdp-2025/othello-1.git
cd othello-1
```

2. Set up the development environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the package in editable mode:
```bash
python -m pip install -e ./othello
```

4. Install pre-commit hooks:
```bash
pre-commit install --install-hooks
```

## Testing

Run tests from the `othello` directory (where `pyproject.toml` is located):
```bash
pytest
# or
python -m pytest
```

### Important Testing Notes

- Always run tests from the `othello` directory
- If `pytest` fails, verify which version is being used with `which pytest`
- Ensure you're using the virtual environment's pytest, not the system-wide version (might have taken a couple of hours from my life)

## Wayland Configuration

When developing on Wayland, set the XKB configuration path:
```bash
export XKB_CONFIG_ROOT=/usr/share/X11/xkb/rules/
```

## Contributing

1. Make sure all tests pass before submitting changes
2. Ensure pre-commit hooks are running on your commits
3. Follow the existing code style and conventions (PEP8)
4. Submit merge requests with clear descriptions of changes

## Project Structure

```
othello/
├── othello/        # Main package directory
├── tests/          # Test files
└── pyproject.toml  # Project configuration
```
