# Publishing Duplicate Pair Cleaner

The Windows GUI is released as **v3.0.0**. The portable EXE is built by a GitHub-hosted Windows runner, not cross-compiled on Linux.

1. Run the full core and GUI-model test suite: `python -m unittest -v test_cleaner.py test_gui_logic.py`.
2. Review `gui_app.py`, `gui_logic.py`, `docs/GUI_USER_GUIDE.md`, and `scripts/build_manual.py`.
3. If a new build is needed, select **Actions → Windows GUI v3.0.0 → Run workflow**. It runs Windows/Linux tests, packages the EXE with PyInstaller, builds the nine-page PDF manual, and publishes the portable Windows ZIP.
4. The workflow creates the `v3.0.0` tag and release if they do not already exist. Publish a **new version** for future changes rather than silently overwriting prior releases.
5. Verify the two public assets (Windows-Portable ZIP and PDF) and test the extracted EXE on a real Windows 10/11 desktop.

The previous v2.2.0 command-line release is retained separately, including its historical publishing workflow. The GUI release is unsigned and may trigger Windows SmartScreen.

MIT License — DimitrisLai.
