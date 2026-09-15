"""
Run every docstring example in the pure-standard-library packages as a test.

Why this matters: the docstrings in this project *are* the teaching material,
and a teaching example with the wrong number is worse than no example. Running
them as doctests means the numbers in the lessons and the numbers the code
actually produces can never drift apart.

Only ``forex_mastery.core`` and ``forex_mastery.journal`` are covered here -
both are importable without any third-party package.
"""

from __future__ import annotations

import doctest
import importlib
import pkgutil

import pytest

import forex_mastery.core as core_pkg
import forex_mastery.journal as journal_pkg


def _modules(package):
    names = []
    for module in pkgutil.iter_modules(package.__path__):
        names.append(f"{package.__name__}.{module.name}")
    return sorted(names)


@pytest.mark.parametrize("module_name", _modules(core_pkg) + _modules(journal_pkg))
def test_docstring_examples(module_name: str):
    module = importlib.import_module(module_name)
    results = doctest.testmod(module, verbose=False, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert results.failed == 0, f"{results.failed} failing docstring example(s) in {module_name}"
