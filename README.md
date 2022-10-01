# pygada-runtime

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pygada-runtime)
[![Python package](https://img.shields.io/github/workflow/status/gadalang/pygada-runtime/Python%20package)](https://github.com/gadalang/pygada-runtime/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/pygada-runtime/badge/?version=latest)](https://pygada-runtime.readthedocs.io/en/latest/?badge=latest)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Codecov](https://img.shields.io/codecov/c/gh/gadalang/pygada-runtime?token=4CSJTL1ZML)](https://codecov.io/gh/gadalang/pygada-runtime)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`pygada-runtime` is a package for creating and running [Gada](https://github.com/gadalang/gada) nodes in Python.

## Install

Using pip:

```bash
pip install pygada-runtime
```

## Documentation

Build the doc with:

```bash
make html
```

You can find the latest documentation on [pygada-runtime.readthedocs.io](https://pygada-runtime.readthedocs.io/).

## Testing

The `test` directory contains many tests that you can run with:

```python
tox .
```

## License

Licensed under the [MIT](LICENSE) License.
