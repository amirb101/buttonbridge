# Contributing to ButtonBridge

Thanks for taking the time to contribute.

## Getting started

```bash
git clone https://github.com/amirb101/buttonbridge.git
cd buttonbridge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run the app from source:

```bash
python -m buttonbridge
```

## Ways to contribute

- **Bug reports** — open an issue using the bug report template
- **New modes** — add support for an app you use (see [Adding a mode](README.md#adding-a-mode))
- **Bundle ID corrections** — if a mode doesn't activate for your setup, a PR updating `constants.py` is welcome
- **Documentation** — fixes, clarifications, typos

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Keep changes focused — one feature or fix per PR.
3. Test on macOS with a real controller where possible.
4. Update the README if you're adding a mode or changing behaviour.

## Code style

- Python 3.10+ syntax
- Type hints on public functions
- No third-party dependencies beyond those already in `requirements.txt` unless there's a good reason

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include macOS version, controller model, and steps to reproduce.
