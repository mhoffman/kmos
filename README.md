# kmos

[![CI](https://github.com/mhoffman/kmos/actions/workflows/ci.yml/badge.svg)](https://github.com/mhoffman/kmos/actions/workflows/ci.yml)

**kMC modeling on steroids**

kmos is a tool for kinetic Monte Carlo (kMC) modeling focused on lattice models for surface science applications.

## Features

- Lattice-based kinetic Monte Carlo simulations
- Support for complex surface chemistry models
- Written in Python with Fortran backend for performance
- Integration with ASE (Atomic Simulation Environment)

## Installation

```bash
pip install kmos
```

## Development

```bash
# Clone the repository
git clone https://github.com/mhoffman/kmos.git
cd kmos

# Install dependencies with uv
uv sync

# Run tests
PYTHONPATH=. uv run pytest tests/
```

## Requirements

- Python >= 3.9
- Tested on Python 3.9, 3.10, 3.11, 3.12, 3.13, and 3.14
- Fortran compiler (gfortran recommended)
- Meson build system (automatically installed with Python >= 3.12)

## Publishing

To publish a new version to PyPI:

```bash
# 1. Bump version
uv run bump-my-version bump patch  # or minor, or major

# 2. Build the package
uv build

# 3. Upload to PyPI (requires PyPI credentials)
uv publish

# Or upload to Test PyPI first
uv publish --publish-url https://test.pypi.org/legacy/
```

After publishing, users can install with:
```bash
pip install kmos
# or
uv add kmos
```

## License

GPL-3.0-or-later