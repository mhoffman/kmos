# kmos

[![CI](https://github.com/mhoffman/kmos/actions/workflows/ci.yml/badge.svg)](https://github.com/mhoffman/kmos/actions/workflows/ci.yml)

**kMC modeling on steroids**

*A vigorous attempt to make lattice kinetic Monte Carlo modeling more accessible.*

kmos is a tool for kinetic Monte Carlo (kMC) modeling focused on lattice models for surface science applications.

Copyright (C) 2009-2025 Max J. Hoffmann <mjhoffmann@gmail.com>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

## Features

- Lattice-based kinetic Monte Carlo simulations
- Support for complex surface chemistry models
- Written in Python with Fortran backend for performance
- Integration with ASE (Atomic Simulation Environment)
- Interactive GUI for model editing and visualization
- High-performance kMC solver with multiple backends

## Installation

```bash
pip install kmos
```

## Quickstart

Create a minimal input file `mini_101.ini`:

```ini
[Meta]
author = Your Name
email = you@server.com
model_dimension = 2
model_name = fcc_100

[Species empty]
color = #FFFFFF

[Species CO]
representation = Atoms("CO", [[0, 0, 0], [0, 0, 1.17]])
color = #FF0000

[Lattice]
cell_size = 3.5 3.5 10.0

[Layer simple_cubic]
site hollow = (0.5, 0.5, 0.5)
color = #FFFFFF

[Parameter k_CO_ads]
value = 100
adjustable = True
min = 1
max = 1e13
scale = log

[Parameter k_CO_des]
value = 100
adjustable = True
min = 1
max = 1e13
scale = log

[Process CO_ads]
rate_constant = k_CO_ads
conditions = empty@hollow
actions = CO@hollow
tof_count = {'adsorption':1}

[Process CO_des]
rate_constant = k_CO_des
conditions = CO@hollow
actions = empty@hollow
tof_count = {'desorption':1}
```

Then run:
```bash
kmos export mini_101.ini
cd mini_101_local_smart
kmos benchmark
```

You should see output like:
```
Using the [local_smart] backend.
1000000 steps took 1.51 seconds
Or 6.62e+05 steps/s
```

Try running `kmos view` to watch the model run, or `kmos shell` to interact with it interactively. Explore more commands with `kmos help`.

## Development

### Quick Start for Contributors

```bash
# Clone the repository
git clone https://github.com/mhoffman/kmos.git
cd kmos

# Install dev dependencies
uv sync --all-extras

# Install pre-commit hooks (automatic code formatting & linting)
uv run pre-commit install

# Run tests
make test
```

### Available Make Commands

The project includes a Makefile for common development tasks:

```bash
make help           # Show all available commands
make test           # Run tests
make test-coverage  # Run tests with coverage report
make lint           # Lint code with ruff
make format         # Format code with ruff
make clean          # Clean build artifacts and caches
make docs           # Build documentation
make all            # Run full CI pipeline locally
```

### Code Quality Tools

This project uses modern Python tooling:

- **ruff** - Fast linting and formatting (replaces black, isort, flake8)
- **mypy** - Type checking
- **pre-commit** - Automatic checks before commits
- **pytest** - Testing framework
- **coverage** - Test coverage reporting

After installing pre-commit hooks with `uv run pre-commit install`, your code will automatically be formatted and linted before each commit.

### Running Tests

```bash
# Quick test run
make test

# Verbose output
make test-verbose

# With coverage report
make test-coverage
```

### Manual Commands (if not using Make)

```bash
# Run tests
PYTHONPATH=. uv run pytest tests/

# Lint code
uv run ruff check kmos/ tests/

# Format code
uv run ruff format kmos/ tests/

# Type check
uv run mypy kmos/
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

## Documentation

For tutorials, user guides, API reference, and troubleshooting:

- [GitHub Pages](http://mhoffman.github.io/kmos/)
- [ReadTheDocs](http://kmos.readthedocs.org/)
- [TU Munich Documentation](https://www.th4.ch.tum.de/index.php?id=1321)
- [Introduction to kMOS](https://github.com/jmlorenzi/intro2kmos)

## Bugs, Issues, Questions

This is research software for scientists by scientists. If you encounter bugs, have feature requests, or need help:

- Open an [issue](https://github.com/mhoffman/kmos/issues/new)
- Join the [mailing list](https://groups.google.com/forum/#!forum/kmos-users)

## Acknowledgments

This project builds upon several excellent open-source Python projects:

- [Python](http://www.python.org)
- [ASE (Atomic Simulation Environment)](https://wiki.fysik.dtu.dk/ase/)
- [NumPy](https://numpy.org/)
- [f2py](http://cens.ioc.ee/projects/f2py2e/)
- [lxml](https://lxml.de/)

## License

GPL-3.0-or-later
