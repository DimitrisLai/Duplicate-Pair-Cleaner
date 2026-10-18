# Contributing

Thank you for contributing to Duplicate Pair Cleaner!

1. Search existing issues and confirm the reported behavior is not already documented.
2. Use invented filenames in public reports; don't post personal media libraries or folders.
3. Fork, create a branch and make a focused change.
4. Maintain standard-library-only Python where possible.
5. Add or update regression tests for behavioral changes.
6. Run `python -m unittest -v test_cleaner.py` and open a pull request with results.

Safety priorities: no silent overwriting, preview before applying, backup by default, simple Windows launchers. Changes to matching behavior should be opt-in where practical.
