# Security Policy

## Supported versions

Only the latest version on `main` is actively maintained.

## Reporting a vulnerability

If you discover a security vulnerability, **please do not open a public issue**.

Report it privately via [GitHub's private vulnerability reporting](https://github.com/amirb101/buttonbridge/security/advisories/new) or by emailing the maintainer directly (contact visible on the GitHub profile).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

You can expect an acknowledgement within a few days and a fix or response within a reasonable timeframe depending on severity.

## Scope

ButtonBridge runs locally on macOS and does not transmit data externally. The main security-relevant surface is:

- **Accessibility permission** — the app sends synthetic keystrokes; misuse could affect any app on the system
- **Keybinding config file** — stored at `~/.buttonbridge/keybindings.json`; no remote sync
